"""Execute both supported EXEs and the actual ASI in x86 Unicorn.
Native pager enqueue code runs unchanged; only clock/localization and OS calls are stubbed.
"""
from pathlib import Path
import struct,itertools
from functools import lru_cache
HERE=Path(__file__).resolve().parent
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
from keystone import Ks,KS_ARCH_X86,KS_MODE_32
import build
P=lambda v:struct.pack('<I',v&0xffffffff)
BASE=0x12000000
DLL=pefile.PE(str(HERE/'build-output'/'HT2_TractorSwap.asi')).get_memory_mapped_image()
COUNT=0
not_racing=lambda pf,tf:not ((pf|tf)&0x4000)

def r32(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def w32(u,a,v):u.mem_write(a,P(v))
def ret(u,v=1,pop=0):
 s=u.reg_read(UC_X86_REG_ESP);a=r32(u,s);u.reg_write(UC_X86_REG_EAX,v)
 u.reg_write(UC_X86_REG_ESP,s+4+pop);u.reg_write(UC_X86_REG_EIP,a)
def string(u,a):
 b=bytearray()
 while u.mem_read(a,1)!=b'\0':b+=u.mem_read(a,1);a+=1
 return b.decode('cp1251')
@lru_cache(None)
def game_image(path):
 pe=pefile.PE(path);return pe,pe.get_memory_mapped_image()

def machine(p,base=BASE):
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x400000)
 pe,im=game_image(str(p['path']));u.mem_write(0x400000,im)
 u.mem_map(0x2000000,0x100000);u.mem_map(0x1000000,0x1000)
 u.mem_map(base,0x10000);u.mem_write(base,DLL)
 return u,pe

def install(p,base=BASE,reason=1,corrupt=None,protect_fail=False,restore_fail=False,lang="rus"):
 global COUNT
 u,pe=machine(p,base);status={};calls=[]
 for n,name in enumerate(build.APIS):w32(u,base+build.IAT[name],0x1000000+n*16)
 if corrupt is not None:u.mem_write(corrupt,bytes([u.mem_read(corrupt,1)[0]^1]))
 before=bytes(u.mem_read(0x400000,0x3bd000))
 def hook(u,a,n,_):
  if not 0x1000000<=a<0x1000000+len(build.APIS)*16:return
  name=build.APIS[(a-0x1000000)//16];s=u.reg_read(UC_X86_REG_ESP)
  args=[r32(u,s+4+i*4) for i in range(6)];calls.append(name)
  if name=='GetModuleHandleA':ret(u,0x400000,4)
  elif name=='GetModuleFileNameA':
   path=b'C:\\Test Game\\king.exe\0';u.mem_write(args[1],path);ret(u,len(path)-1,12)
  elif name=='GetPrivateProfileStringA':
   assert string(u,args[0])=='ENV' and string(u,args[1])=='langv'
   assert string(u,args[5])=='C:\\Test Game\\TRUCK.INI'
   value=lang.encode()+b'\0';u.mem_write(args[3],value);ret(u,len(value)-1,24)
  elif name=='VirtualProtect':
   which=calls.count(name);w32(u,args[3],0x20)
   assert args[0]==0x400000+p['start'] and args[1]==p['click']+10-p['start']
   ret(u,0 if protect_fail or (restore_fail and which==2) else 1,16)
  elif name=='FlushInstructionCache':ret(u,1,12)
  elif name=='WritePrivateProfileStringA':
   assert string(u,args[0])=='TractorSwap';assert string(u,args[3])=='C:\\Test Game\\HT2_TractorSwap_Status.ini'
   status[string(u,args[1])]=string(u,args[2]);ret(u,1,16)
 h=u.hook_add(UC_HOOK_CODE,hook);sp=0x20ff000
 u.mem_write(sp,P(0x1000800)+P(base)+P(reason)+P(0));u.reg_write(UC_X86_REG_ESP,sp)
 regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
 for r in regs:u.reg_write(r,0xaabbccdd)
 u.emu_start(base+0x1000,0x1000800,count=20000);u.hook_del(h)
 assert u.reg_read(UC_X86_REG_EAX)==1 and u.reg_read(UC_X86_REG_ESP)==sp+16
 assert all(u.reg_read(r)==0xaabbccdd for r in regs)
 after=bytes(u.mem_read(0x400000,0x3bd000));expected=bytearray(before)
 if reason==1 and corrupt is None and not protect_fail:
  for end,hook_rva in [(p['end'],p['hook']),(p['click'],p['click_hook'])]:
   expected[end:end+10]=b'\xe9'+P(base+hook_rva-(0x400000+end+5))+b'\x90'*5
 assert after==expected,(p['name'],hex(corrupt or 0))
 if reason!=1:assert not calls
 else:
  result='UnsupportedExecutableOrConflict' if corrupt is not None else 'VirtualProtectFailed' if protect_fail else 'InstalledProtectionRestoreFailed' if restore_fail else 'Installed'
  assert status['Result']==result and status['Version']==build.VERSION,status
  if corrupt is None:assert status['Profile']==p['name']
  else:assert 'Profile' not in status
 COUNT+=1
 return u

def eligibility(p,pt,tt,pf=0,tf=0,exists=True,patched=True):
 global COUNT
 u,_=machine(p)
 # Tractor range globals are identified directly from the verified instruction bytes.
 r=0x400000+p['start'];lo=r32(u,r+6);hi=r32(u,r+16)
 w32(u,lo,30);w32(u,hi,40);w32(u,0x400000+p['null'],0)
 sp=0x20ff000;ui=0x2010000;button=0x2020000
 u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_ESI,ui)
 w32(u,ui+0x130,button);w32(u,button+0x28,1)
 w32(u,sp+0x6c,tt);w32(u,sp+0x10,0x1234 if exists else 0)
 def hook(u,a,n,_):
  if a==0x400000+p['end']:u.emu_stop();return
  s=u.reg_read(UC_X86_REG_ESP)
  if a==0x400000+p['copy']:
   dst=u.reg_read(UC_X86_REG_ECX);w32(u,dst,r32(u,r32(u,s+4)));ret(u,dst,4)
  elif a==0x400000+p['info']:w32(u,r32(u,s+8)+0xc,pt);ret(u)
  elif a==0x400000+p['player']:w32(u,r32(u,s+4),0x5678);ret(u)
  elif a==0x400000+p['flags']:ret(u,pf if r32(u,s+4)==0x5678 else tf)
 h=u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(r,0x400000+p['start']+146,count=2000);u.hook_del(h)
 assert u.reg_read(UC_X86_REG_ESP)==sp
 if patched:
  w32(u,sp+0x120,0x1000800);w32(u,sp+0x124,0)
  u.emu_start(BASE+p['hook'],0x1000800,count=1000)
  assert u.reg_read(UC_X86_REG_ESP)==sp+0x128
 COUNT+=1
 return r32(u,button+0x28)==0

class Pager:
 def __init__(self,p,base=BASE,lang='rus'):
  self.p=p;self.base=base;self.lang=lang;self.u=install(p,base,lang=lang);u=self.u
  self.ui=0x2010000;self.button=0x2020000;self.player=0x2030000;self.target=0x2040000;self.pager=0x2050000
  w32(u,self.ui+0x130,self.button);w32(u,0x400000+p['pager_obj'],self.pager)
  # The actual pager queue has four 128-byte slots, which must not be overwritten.
  self.sent=[];self.native_clock={'ModifiedCore82':0x6036b0,'SteamOriginal':0x6037e0,'SteamFrench':0x602ea0}[p['name']]
  cvt={'ModifiedCore82':0x61d7b0,'SteamOriginal':0x61d830,'SteamFrench':0x61cee0}[p['name']]
  ks=Ks(KS_ARCH_X86,KS_MODE_32);u.mem_write(0x1000900,struct.pack('<d',100.0))
  u.mem_write(self.native_clock,bytes(ks.asm('fld qword ptr [0x1000900]; ret')[0]))
  u.mem_write(cvt,bytes(ks.asm('fstp st(0); mov eax,100; ret')[0]))
  self.close_events=[]
  self.gameapp=0x2060000;self.vtable=0x2070000
  w32(u,0x400000+p['gameapp'],self.gameapp);w32(u,self.gameapp,self.vtable)
  w32(u,self.ui-0x40,self.vtable+0x100)
  w32(u,self.vtable+0x120,0x1000a00);w32(u,self.vtable+0x24,0x1000a10)
  w32(u,0x400000+p['phone'],0)
  def hook(u,a,n,_):
   s=u.reg_read(UC_X86_REG_ESP)
   if a==0x1000000+build.APIS.index('GetModuleHandleA')*16:ret(u,0,4)
   elif a==0x400000+p['player']:w32(u,r32(u,s+4),self.player);ret(u)
   elif a==0x400000+p['pager']:
    self.sent.append(string(u,r32(u,s+4)));self.close_events.append('message')
   elif a==0x1000a00:
    assert u.reg_read(UC_X86_REG_ECX)==self.ui-0x40
    self.closed=True;self.close_events.append('close');ret(u)
   elif a==0x1000a10:self.close_events.append('resume');ret(u)
   elif a==0x400000+p['input_resume']:ret(u)
   elif a==0x400000+p['unpause']:
    assert r32(u,s+4)==1;self.close_events.append('unpause');ret(u)
  u.hook_add(UC_HOOK_CODE,hook)
 def refresh(self,disabled=1,pf=0,tf=0,selected=None):
  global COUNT
  u=self.u;p=self.p;selected=self.target if selected is None else selected
  w32(u,self.button+0x28,disabled);w32(u,self.player+0x60,pf);w32(u,self.target+0x60,tf)
  sp=0x20fe000;saved=[0x11111111,0x22222222,0x33333333,0x44444444]
  for n,v in enumerate(saved):w32(u,sp+n*4,v)
  w32(u,sp+0x10,selected);w32(u,sp+0x120,0x1000800);w32(u,sp+0x124,0)
  u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_ESI,self.ui)
  u.reg_write(UC_X86_REG_EAX,0x77777777);u.reg_write(UC_X86_REG_ECX,0x88888888);u.reg_write(UC_X86_REG_EDX,0x99999999)
  u.emu_start(0x400000+p['end'],0x1000800,count=10000)
  assert u.reg_read(UC_X86_REG_ESP)==sp+0x128
  for r,v in zip([UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_EBP,UC_X86_REG_EBX],saved):assert u.reg_read(r)==v
  for r,v in [(UC_X86_REG_EAX,0x77777777),(UC_X86_REG_ECX,0x88888888),(UC_X86_REG_EDX,0x99999999)]:assert u.reg_read(r)==v
  assert r32(u,self.player+0x60)==pf and r32(u,self.target+0x60)==tf
  assert r32(u,self.button+0x28)==0
  COUNT+=1
 def click(self,pf=0,tf=0,selected=None,event=0xb9,player_exists=True):
  global COUNT
  u=self.u;p=self.p;selected=self.target if selected is None else selected
  w32(u,self.player+0x60,pf);w32(u,self.target+0x60,tf)
  actual_player=self.player
  if not player_exists:self.player=0
  sp=0x20fd000;saved=[0x11111111,0x22222222,0x33333333,0x44444444]
  for n,v in enumerate(saved):w32(u,sp+n*4,v)
  w32(u,sp+0x24,self.ui);w32(u,sp+0x10,selected);w32(u,sp+0x238,0x1000800);w32(u,sp+0x23c,event)
  regs={UC_X86_REG_EAX:0x77777777,UC_X86_REG_ECX:0x88888888,UC_X86_REG_EDX:0x99999999,
        UC_X86_REG_EBX:0x66666666,UC_X86_REG_ESI:0x55555555,UC_X86_REG_EBP:self.ui,UC_X86_REG_EDI:0x44444444}
  for r,v in regs.items():u.reg_write(r,v)
  u.reg_write(UC_X86_REG_ESP,sp);self.allowed=False;self.closed=False
  def route(u,a,n,_):
   if a==0x400000+p['click']+10:self.allowed=True;u.emu_stop()
   if a==0x400000+p['native']:raise AssertionError('Uncontrolled native swap')
  h=u.hook_add(UC_HOOK_CODE,route);u.emu_start(0x400000+p['click'],0x1000800,count=10000);u.hook_del(h)
  self.player=actual_player
  if self.allowed:
   assert u.reg_read(UC_X86_REG_ESP)==sp
   assert u.reg_read(UC_X86_REG_EAX)==selected and u.reg_read(UC_X86_REG_EDX)==0
   for r,v in regs.items():
    if r not in [UC_X86_REG_EAX,UC_X86_REG_EDX]:assert u.reg_read(r)==v
  else:
   assert u.reg_read(UC_X86_REG_ESP)==sp+0x240
   for r,v in zip([UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_EBP,UC_X86_REG_EBX],saved):assert u.reg_read(r)==v
   if not self.closed:
    for r in [UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX]:assert u.reg_read(r)==regs[r]
  assert r32(u,self.player+0x60)==pf and r32(u,self.target+0x60)==tf
  expected_close=event==0xb9 and selected==self.target and player_exists and bool((pf|tf)&0x4000) and r32(u,0x400000+p['pager_obj'])!=0
  assert self.closed==expected_close
  if self.closed:
   assert self.close_events[-4:]==['message','close','resume','unpause']
   assert r32(u,self.gameapp+0x10)&3==3
   assert r32(u,self.pager+0x4fc)==0
  COUNT+=1
  return self.allowed
 def queue(self):return [string(self.u,self.pager+0x2c+n*128) for n in range(4)]

def native_swap(p,ta,tb):
 global COUNT
 u,_=machine(p);a=0x2010000;b=0x2020000;sp=0x20fe000
 u.mem_write(a,bytes((n*13+9)%256 for n in range(0x400)));u.mem_write(b,bytes((n*7+21)%256 for n in range(0x400)))
 w32(u,a+0x204,0x2030000);w32(u,b+0x204,0x2040000);w32(u,a+0x208,ta);w32(u,b+0x208,tb)
 olda=bytes(u.mem_read(a,0x400));oldb=bytes(u.mem_read(b,0x400))
 u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_EBX,a);u.reg_write(UC_X86_REG_EBP,b)
 def hook(u,addr,n,_):
  if addr==0x400000+p['swap_copy']:
   ss=u.reg_read(UC_X86_REG_ESP);u.mem_write(u.reg_read(UC_X86_REG_ECX)+0x20,bytes(u.mem_read(r32(u,ss+4),32)));ret(u,0,4)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x400000+p['swap'],0x400000+p['swap_end'],count=1000)
 for o,n in [(0x28,32),(0x228,96),(0x54,4),(0x204,8),(0x120,24),(0x150,16),(0x178,40),(0x1a0,40),(0xc8,72)]:
  assert bytes(u.mem_read(a+o,n))==oldb[o:o+n],hex(o);assert bytes(u.mem_read(b+o,n))==olda[o:o+n],hex(o)
 assert u.reg_read(UC_X86_REG_ESP)==sp+8
 COUNT+=1

if __name__=='__main__':
 # Populate verified profile metadata without altering the installed ASI.
 build.build()
 DLL=pefile.PE(str(HERE/'build-output'/'HT2_TractorSwap.asi')).get_memory_mapped_image()
 for p in build.PROFILES:
  for base in [BASE,0x18000000]:install(p,base)
  for reason in [0,2,3]:install(p,reason=reason)
  pe=pefile.PE(str(p['path']));h=0x400000+pe.DOS_HEADER.e_lfanew
  for a in [0x400000,0x40003c,h+4,h+0x50,h+8,0x400000+p['pager'],0x400000+p['enqueue'],0x400000+p['player'],0x400000+p['click'],0x400000+p['close'],0x400000+p['pager_resume']]+list(range(0x400000+p['start'],0x400000+p['end']+13)):
   install(p,corrupt=a)
  install(p,protect_fail=True);install(p,restore_fail=True)
  for pt,tt,pf,tf,exists in itertools.product([0,29,30,39,40,100],[0,29,30,39,40,100],[0,0x4000],[0,0x4000],[False,True]):
   allowed=exists and not((pf|tf)&0x4000)
   assert eligibility(p,pt,tt,pf,tf,exists),(p['name'],pt,tt,pf,tf,exists)
   assert eligibility(p,pt,tt,pf,tf,exists,False)==(allowed and not(30<=pt<40 or 30<=tt<40))
  for lang,expected_lang in [('rus','ru'),('eng','en'),('fra','fr'),('ger','de'),('spa','es'),
                              ('fre','fr'),('deu','de'),('esp','es'),('FRA','fr'),('GER','de'),
                              ('SPA','es'),('RUS','ru'),('ENG','en'),('zzz','en')]:
   for pf,tf,index in [(0x4000,0,1),(0,0x4000,2),(0x4000,0x4000,3)]:
    z=Pager(p,lang=lang)
    for _ in range(8):z.refresh(pf=pf,tf=tf)
    assert not z.sent
    assert not z.click(pf=pf,tf=tf)
    assert len(z.sent)==1 and z.sent[0]==z.queue()[0]
    assert z.sent[0]==build.MESSAGES[expected_lang][index],(lang,z.sent[0])
    assert len(z.sent[0].encode('cp1251'))<128
    if expected_lang!='ru':assert z.sent[0].isascii()
    for _ in range(8):assert not z.click(pf=pf,tf=tf)
    assert r32(z.u,z.pager+0x4b0)==1  # native duplicate suppression
   z=Pager(p,lang=lang);assert not z.click(selected=0)
   assert z.sent==[build.MESSAGES[expected_lang][0]] and not z.closed
   z=Pager(p,lang=lang);assert not z.click(player_exists=False)
   assert z.sent==[build.MESSAGES[expected_lang][4]] and not z.closed
  z=Pager(p);z.refresh();assert not z.sent;assert z.click();assert not z.sent
  assert not z.click(tf=0x4000);assert len(z.sent)==1
  z=Pager(p);assert not z.click(player_exists=False);assert 'НЕ УДАЛОСЬ ОПРЕДЕЛИТЬ ВОДИТЕЛЯ' in z.sent[0]
  # Conditions are read again at click time, regardless of the previous row.
  for old_pf,old_tf,new_pf,new_tf in [(0,0,0,0x4000),(0x4000,0,0,0),(0,0x4000,0,0)]:
   z=Pager(p);z.refresh(pf=old_pf,tf=old_tf)
   assert z.click(pf=new_pf,tf=new_tf)==not_racing(new_pf,new_tf)
  # Dismiss and unrelated events retain the original route even for racers.
  for event in [0xba,0,0xff]:
   z=Pager(p);assert z.click(tf=0x4000,event=event);assert not z.sent
  z=Pager(p);w32(z.u,0x400000+p['pager_obj'],0)
  assert not z.click(tf=0x4000);assert not any(z.queue())
  z=Pager(p)
  for n in range(4):z.u.mem_write(z.pager+0x2c+n*128,b'existing message\0')
  before=bytes(z.u.mem_read(z.pager,0x500));assert not z.click(tf=0x4000)
  assert bytes(z.u.mem_read(z.pager,0x500))==before
  z.u.mem_write(z.pager+0x2c,b'\0');assert not z.click(tf=0x4000)
  assert z.queue()[1:]==['existing message']*3
  z=Pager(p,base=0x18000000);assert not z.click(tf=0x4000);assert len(z.sent)==1
  for ta,tb in itertools.product([0,0x2050000],[0,0x2060000]):native_swap(p,ta,tb)
  print('PASS',p['name'],flush=True)
 print(f'PASS: {COUNT} x86 checks; no driving simulation.')
