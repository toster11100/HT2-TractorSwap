"""Build a small position-independent PE32 ASI without a C toolchain.

Python 3 + keystone-engine + pefile. The installed game is never modified.
The emitted assembly is retained next to this file for review.
"""
from pathlib import Path
import os
import struct, hashlib
HERE = Path(__file__).resolve().parent
ROOT = HERE


def input_file(name):
    root=os.environ.get('HT2_BUILD_INPUTS')
    if not root:
        raise RuntimeError('Set HT2_BUILD_INPUTS to the private game-reference directory.')
    if Path(name).name!=name:
        raise ValueError('Build input must be a filename.')
    path=(Path(root)/name).resolve()
    try:
        path.relative_to(HERE.resolve())
    except ValueError:
        return path
    raise ValueError('Private build inputs must be outside the repository.')


from keystone import Ks, KS_ARCH_X86, KS_MODE_32
import pefile

VERSION = '1.1.4'
PROFILE_ALIASES={
    'KOTR81':'KOTR81','KOTR13':'KOTR13',
    'SteamOriginal':'KOTR81','SteamRU':'KOTR81',
    'SteamFrench':'KOTR13','SteamWW':'KOTR13',
}


def canonical_profile(name):
    return PROFILE_ALIASES.get(name,name)


RDATA, IDATA, RELOC, DATA = 0x5000, 0x6000, 0x7000, 0x8000
APIS = ['GetModuleHandleA', 'VirtualProtect', 'FlushInstructionCache',
        'WritePrivateProfileStringA', 'GetModuleFileNameA', 'GetPrivateProfileStringA', 'GetProcAddress']
IAT = {name: IDATA + 0x80 + n*4 for n,name in enumerate(APIS)}
# Latin-language messages deliberately use ordinary ASCII words, avoiding
# assumptions about accented glyphs in old localized pager font assets.
LANGUAGE_ORDER = ('en','ru','fr','de','es')
LANGUAGE_ALIASES = {'eng':'en','rus':'ru','fra':'fr','fre':'fr',
                    'ger':'de','deu':'de','spa':'es','esp':'es'}
MESSAGES = {'en': ('SWAP: SELECT A HIRED DRIVER',
        'CANNOT SWAP: YOU ARE TAKING PART IN A RACE',
        'CANNOT SWAP: THE HIRED DRIVER IS TAKING PART IN A RACE',
        'CANNOT SWAP: BOTH DRIVERS ARE TAKING PART IN A RACE',
        'CANNOT SWAP: DRIVER DATA IS UNAVAILABLE'),
 'ru': ('ОБМЕН: ВЫБЕРИТЕ НАЁМНОГО ВОДИТЕЛЯ',
        'ОБМЕН НЕДОСТУПЕН: ВЫ УЧАСТВУЕТЕ В ГОНКЕ',
        'ОБМЕН НЕДОСТУПЕН: НАЁМНИК УЧАСТВУЕТ В ГОНКЕ',
        'ОБМЕН НЕДОСТУПЕН: ОБА ВОДИТЕЛЯ УЧАСТВУЮТ В ГОНКЕ',
        'ОБМЕН НЕДОСТУПЕН: НЕ УДАЛОСЬ ОПРЕДЕЛИТЬ ВОДИТЕЛЯ'),
 'fr': ('CHANGEMENT : CHOISISSEZ UN CHAUFFEUR',
        'CHANGEMENT IMPOSSIBLE : VOUS DISPUTEZ UNE COURSE',
        'CHANGEMENT IMPOSSIBLE : LE CHAUFFEUR DISPUTE UNE COURSE',
        'CHANGEMENT IMPOSSIBLE : LES DEUX CHAUFFEURS DISPUTENT UNE COURSE',
        'CHANGEMENT IMPOSSIBLE : CHAUFFEUR INTROUVABLE'),
 'de': ('TAUSCH: BITTE EINEN FAHRER MARKIEREN',
        'TAUSCH GESPERRT: SIE NEHMEN AN EINEM RENNEN TEIL',
        'TAUSCH GESPERRT: DER FAHRER NIMMT AN EINEM RENNEN TEIL',
        'TAUSCH GESPERRT: BEIDE FAHRER NEHMEN AN EINEM RENNEN TEIL',
        'TAUSCH GESPERRT: FAHRERDATEN FEHLEN'),
 'es': ('CAMBIO: SELECCIONA UN CONDUCTOR CONTRATADO',
        'CAMBIO BLOQUEADO: PARTICIPAS EN UNA CARRERA',
        'CAMBIO BLOQUEADO: EL CONDUCTOR PARTICIPA EN UNA CARRERA',
        'CAMBIO BLOQUEADO: AMBOS CONDUCTORES PARTICIPAN EN UNA CARRERA',
        'CAMBIO BLOQUEADO: FALTAN LOS DATOS DEL CONDUCTOR')}
PROFILES = [
    dict(name='ModifiedCore82', path=input_file('ModifiedCore82.exe'),
         sha='b57eb1e34dd00c6c5270ca42ada931039d9baed488dee5bb33f46ffa2a6097d6',
         start=0x1270c4, end=0x1271b7, null=0x28b9b0,
         player=0x168ef0, flags=0x3f890, language=0x168f60,
         pager=0x16adf0, pager_obj=0x2f3458, enqueue=0x169940,
         copy=0x54c10, info=0x3feb0, native=0x73bc0, swap=0x73fc5,
         swap_end=0x741a1, swap_copy=0x74590, hook=0x2800,
         click=0x1272b0, click_exit=0x12774f, click_hook=0x3000,
         close=0x127701, gameapp=0x296cc0, phone=0x2ce514,
         pager_resume=0x1696a0, input_resume=0x10bde0, unpause=0xe1330),
    dict(name='SteamOriginal', path=input_file('KOTR81.exe'),
         sha='31fbd1dbbe7706183f09a3688482791255db2bfb557c02675374b96796ce2ebd',
         start=0x127134, end=0x127227, null=0x28b990,
         player=0x168f60, flags=0x3f620, language=0x168fd0,
         pager=0x16ae60, pager_obj=0x2f3438, enqueue=0x1699b0,
         copy=0x1d300, info=0x3fc40, native=0x738c0, swap=0x73cc5,
         swap_end=0x73ea1, swap_copy=0x74290, hook=0x2a00,
         click=0x127320, click_exit=0x1277bf, click_hook=0x3400,
         close=0x127771, gameapp=0x296ca0, phone=0x2ce4f4,
         pager_resume=0x169710, input_resume=0x10bd60, unpause=0xe12b0),
]

# KOTR13 reference executable was verified independently.
PROFILES.append(dict(name='SteamFrench',
    path=input_file('KOTR13.exe'),
    sha='0df6861c9e67c2a2ae373cff8d765ae41cc76079d8f84b9340e609263edd983f',
    start=0x126914,end=0x126a07,null=0x28a8f0,
    player=0x168670,flags=0x3f700,language=0x1686e0,
    pager=0x16a570,pager_obj=0x2f2398,enqueue=0x1690c0,
    copy=0x1d3f0,info=0x3fd20,native=0x73910,swap=0x73d15,
    swap_end=0x73ef1,swap_copy=0x742e0,hook=0x2c00,
    click=0x126b00,click_exit=0x126f9f,click_hook=0x3c00,
    close=0x126f51,gameapp=0x295c00,phone=0x2cd454,
    pager_resume=0x168e20,input_resume=0x10b5d0,unpause=0xe1230))

def u32(x): return struct.pack('<I', x)
def align(x,a): return (x+a-1)//a*a

def make_pe(sections, entry=0x1000, imports=(0x3000,40), reloc=(0x4000,12),
            base=0x12000000, dll=True, image_size=None, timestamp=0):
    header=bytearray(0x400)
    header[:2]=b'MZ'; struct.pack_into('<I',header,0x3c,0x80)
    header[0x80:0x84]=b'PE\0\0'
    struct.pack_into('<HHIIIHH',header,0x84,0x14c,len(sections),timestamp,0,0,224,0x2102 if dll else 0x102)
    opt=0x98
    struct.pack_into('<HBBIIIIII',header,opt,0x10b,1,0,0x1000,0x2000,0,entry,0x1000,0x2000)
    struct.pack_into('<IIIHHHHHH',header,opt+28,base,0x1000,0x200,4,0,0,0,4,0)
    size=image_size or align(max(rva+len(data) for _,rva,data,_ in sections),0x1000)
    struct.pack_into('<IIIIHHIIIIII',header,opt+52,0,size,0x400,0,3,0x140,0x100000,0x1000,0x100000,0x1000,0,16)
    struct.pack_into('<II',header,opt+96+8,*imports)
    struct.pack_into('<II',header,opt+96+5*8,*reloc)
    out=bytearray(header)
    for n,(name,rva,data,flags) in enumerate(sections):
        rawpos=len(out); rawsize=align(len(data),0x200)
        struct.pack_into('<8sIIIIIIHHI',out,0x178+n*40,name.encode(),len(data),rva,rawsize,rawpos,0,0,0,0,flags)
        out.extend(data);out.extend(bytes(rawsize-len(data)))
    return bytes(out)

def build():
    data=bytearray()
    def blob(b):
        r=RDATA+len(data);data.extend(b);return r
    def string(s,encoding='ascii'):return blob(s.encode(encoding)+b'\0')
    strings={s:string(s) for s in ['TractorSwap','Result','Version',VERSION,'Profile',
        'Installed','UnsupportedExecutableOrConflict','VirtualProtectFailed',
        'InstalledProtectionRestoreFailed','HT2_TractorSwap_Status.ini',
        'TRUCK.INI','ENV','langv','rus']}
    steam_dll,steam_getter,steam_getter_old,steam_language = map(string, (
        'steam_api.dll','SteamAPI_SteamApps_v009','SteamAPI_SteamApps_v008',
        'SteamAPI_ISteamApps_GetCurrentGameLanguage'))
    messages={}
    for lang in LANGUAGE_ORDER:
        texts=MESSAGES[lang]
        assert len(texts)==5
        assert all(0<len(t.encode('cp1251'))<128 for t in texts)
        if lang!='ru':assert all(t.isascii() for t in texts)
        messages[lang]=[string(t,'cp1251') for t in texts]
    message_table=blob(b''.join(u32(r) for lang in LANGUAGE_ORDER for r in messages[lang]))
    language_detect=f'mov eax,[ebx+{DATA+0x250}]\n and eax,0xffffff\n or eax,0x202020\n'
    for alias,lang in LANGUAGE_ALIASES.items():
        language_detect+=f'cmp eax,{int.from_bytes(alias.encode(),"little")}\n je lang_{lang}\n'
    language_detect+='jmp ini_done\n'
    for index,lang in enumerate(LANGUAGE_ORDER):
        language_detect+=f'lang_{lang}:\n mov dword ptr [ebx+{DATA+0x240}],{index}\n jmp ini_done\n'
    signatures={}
    for p in PROFILES:
        raw=p['path'].read_bytes()
        assert hashlib.sha256(raw).hexdigest()==p['sha'],p['path']
        pe=pefile.PE(data=raw)
        p['timestamp']=pe.FILE_HEADER.TimeDateStamp
        p['size']=pe.OPTIONAL_HEADER.SizeOfImage
        p['branches']=(p['start']+12,p['start']+78)
        p['profile_string']=string(p['name'])
        ranges=[(p['start'],p['end']+13-p['start']),
                (p['end']+25,16),(p['start']+0x324,44),
                (p['native'],24),(p['swap'],32),
                (p['player'],45),(p['click'],10),(p['click_exit'],13),
                (p['pager'],21),(p['enqueue'],246),
                (p['close'],p['click_exit']-p['close']),
                (p['pager_resume'],16)]
        signatures[p['name']]=[(r,blob(pe.get_data(r,n)),n) for r,n in ranges]
        assert pe.get_data(p['end'],13)==bytes.fromhex('5f5e5d5b81c410010000c20400')
        assert all(pe.get_data(r,2)==b'\x7c\x08' for r in p['branches'])
    imp=bytearray(0x300)
    struct.pack_into('<IIIII',imp,0,IDATA+0x40,0,0,IDATA+0xc0,IDATA+0x80)
    imp[0xc0:0xcd]=b'KERNEL32.dll\0';pos=0x100
    for n,name in enumerate(APIS):
        struct.pack_into('<I',imp,0x40+n*4,IDATA+pos)
        struct.pack_into('<I',imp,0x80+n*4,IDATA+pos)
        v=b'\0\0'+name.encode()+b'\0';imp[pos:pos+len(v)]=v;pos=align(pos+len(v),2)
    src=f'''
        push ebp
        mov ebp, esp
        push ebx
        push esi
        push edi
        sub esp, 8
        call get_base
    get_base:
        pop ebx
        sub ebx, 0x100e
        cmp dword ptr [ebp+12], 1
        jne success
        cld
        lea eax, [ebx+{DATA}]
        push 512
        push eax
        push 0
        call dword ptr [ebx+{IAT['GetModuleFileNameA']}]
        test eax,eax
        jz success
        cmp eax,470
        jae success
        lea edi,[ebx+{DATA}]
        lea ecx,[edi+eax]
    slash:
        cmp ecx,edi
        je success
        dec ecx
        cmp byte ptr [ecx],0x5c
        jne slash
        lea edi,[ecx+1]
        mov [ebp-16],edi
        lea esi,[ebx+{strings['TRUCK.INI']}]
    copy_ini:
        lodsb
        stosb
        test al,al
        jnz copy_ini
        lea eax,[ebx+{DATA}]
        push eax
        push 16
        lea eax,[ebx+{DATA+0x250}]
        push eax
        lea eax,[ebx+{strings['rus']}]
        push eax
        lea eax,[ebx+{strings['langv']}]
        push eax
        lea eax,[ebx+{strings['ENV']}]
        push eax
        call dword ptr [ebx+{IAT['GetPrivateProfileStringA']}]
        {language_detect}
    ini_done:
        mov edi,[ebp-16]
        lea esi,[ebx+{strings['HT2_TractorSwap_Status.ini']}]
    copy_name:
        lodsb
        stosb
        test al,al
        jnz copy_name
        push 0
        call dword ptr [ebx+{IAT['GetModuleHandleA']}]
        test eax,eax
        jz unsupported
        cmp eax,0x400000
        jne unsupported
        mov esi,eax
        cmp word ptr [esi],0x5a4d
        jne unsupported
        mov edx,[esi+0x3c]
        cmp edx,0x1000
        ja unsupported
        add edx,esi
        cmp dword ptr [edx],0x4550
        jne unsupported
        cmp word ptr [edx+4],0x14c
        jne unsupported
        mov [ebp-16],esi
    '''
    for idx,p in enumerate(PROFILES):
        name=p['name'];nxt=f'profile_{idx+1}' if idx+1<len(PROFILES) else 'unsupported'
        src+=f'''
    profile_{idx}:
        cmp dword ptr [edx+0x50],{p['size']}
        jne {nxt}
        cmp dword ptr [edx+8],{p['timestamp']}
        jne {nxt}
        jmp check_{idx}
    '''
        # Keep the header dispatch together; validation never falls through.
    for idx,p in enumerate(PROFILES):
        src+=f'\n check_{idx}:\n'
        for r,s,n in signatures[p['name']]:
            src+=f'''
                lea esi,[ebx+{s}]
                mov edi,[ebp-16]
                add edi,{r}
                mov ecx,{n}
                repe cmpsb
                jne unsupported
            '''
        src+=f'''
            mov eax,{p['profile_string']}
            mov [ebx+{DATA+0x220}],eax
            mov esi,[ebp-16]
            lea edi,[esi+{p['start']}]
            lea eax,[ebp-20]
            push eax
            push 0x40
            push {p['click']+10-p['start']}
            push edi
            call dword ptr [ebx+{IAT['VirtualProtect']}]
            test eax,eax
            jz protect_failed
            lea eax,[ebx+{p['hook']}]
            lea ecx,[esi+{p['end']+5}]
            sub eax,ecx
            mov byte ptr [esi+{p['end']}],0xe9
            mov [esi+{p['end']+1}],eax
            mov dword ptr [esi+{p['end']+5}],0x90909090
            mov byte ptr [esi+{p['end']+9}],0x90
            lea eax,[ebx+{p['click_hook']}]
            lea ecx,[esi+{p['click']+5}]
            sub eax,ecx
            mov byte ptr [esi+{p['click']}],0xe9
            mov [esi+{p['click']+1}],eax
            mov dword ptr [esi+{p['click']+5}],0x90909090
            mov byte ptr [esi+{p['click']+9}],0x90
            lea eax,[ebp-16]
            push eax
            push dword ptr [ebp-20]
            push {p['click']+10-p['start']}
            push edi
            call dword ptr [ebx+{IAT['VirtualProtect']}]
            mov esi,{strings['Installed']}
            test eax,eax
            jnz flush_{idx}
            mov esi,{strings['InstalledProtectionRestoreFailed']}
        flush_{idx}:
            push {p['click']+10-p['start']}
            push edi
            push -1
            call dword ptr [ebx+{IAT['FlushInstructionCache']}]
            jmp status
        '''
    src+=f'''
    protect_failed:
        mov esi,{strings['VirtualProtectFailed']}
        jmp status
    unsupported:
        mov esi,{strings['UnsupportedExecutableOrConflict']}
    status:
        add esi,ebx
        lea edi,[ebx+{DATA}]
        push edi
        push esi
        lea eax,[ebx+{strings['Result']}]
        push eax
        lea eax,[ebx+{strings['TractorSwap']}]
        push eax
        call dword ptr [ebx+{IAT['WritePrivateProfileStringA']}]
        push edi
        lea eax,[ebx+{strings[VERSION]}]
        push eax
        lea eax,[ebx+{strings['Version']}]
        push eax
        lea eax,[ebx+{strings['TractorSwap']}]
        push eax
        call dword ptr [ebx+{IAT['WritePrivateProfileStringA']}]
        mov eax,[ebx+{DATA+0x220}]
        test eax,eax
        jz success
        add eax,ebx
        push edi
        push eax
        lea eax,[ebx+{strings['Profile']}]
        push eax
        lea eax,[ebx+{strings['TractorSwap']}]
        push eax
        call dword ptr [ebx+{IAT['WritePrivateProfileStringA']}]
    success:
        mov eax,1
        add esp,8
        pop edi
        pop esi
        pop ebx
        pop ebp
        ret 12
    '''
    ks=Ks(KS_ARCH_X86,KS_MODE_32)
    code=bytearray(ks.asm(src,addr=0x1000)[0]);assert len(code)<0x2000
    assemblies=[src]
    chunks=[]
    for p in PROFILES:
        # Keep the button clickable; refresh itself never emits messages.
        ui="""
            pushfd
            push eax
            mov eax,[esi+0x130]
            test eax,eax
            jz button_done
            mov dword ptr [eax+0x28],0
        button_done:
            pop eax
            popfd
            pop edi
            pop esi
            pop ebp
            pop ebx
            add esp,0x110
            ret 4
        """
        chunks.append((p['hook'],ui))
        # At this site the original handler has resolved the current employee.
        # PUSHFD/PUSHAD adds 36 bytes: selected PlayerId is ESP+52,
        # button event id is ESP+0x260. Only swap (0xB9) is intercepted.
        h=f'''
            pushfd
            pushad
            call click_base
        click_base:
            pop ebx
            sub ebx,{p['click_hook']+7}
            cld
            cmp dword ptr [esp+0x260],0xb9
            jne native
            mov ebp,[esp+52]
            mov edi,1
            cmp ebp,dword ptr [{0x400000+p['null']}]
            je notify
            mov edi,5
            cmp ebp,0x10000
            jb notify
            sub esp,4
            push esp
            mov eax,{0x400000+p['player']}
            call eax
            add esp,4
            pop eax
            cmp eax,dword ptr [{0x400000+p['null']}]
            je notify
            cmp eax,0x10000
            jb notify
            xor edx,edx
            test dword ptr [eax+0x60],0x4000
            jz target_flags
            or edx,1
        target_flags:
            test dword ptr [ebp+0x60],0x4000
            jz classify
            or edx,2
        classify:
            test edx,edx
            jz native
            lea edi,[edx+1]
        notify:
            call 0x3800
            mov eax,[ebx+{DATA+0x240}]
            cmp eax,4
            jbe valid_language
            xor eax,eax
        valid_language:
            imul eax,eax,20
            lea edx,[ebx+{message_table}]
            add edx,eax
            lea ecx,[edi-1]
            cmp ecx,4
            ja blocked
            mov eax,[edx+ecx*4]
            add eax,ebx
        '''
        h+=f'''
        send:
            push eax
            mov eax,{0x400000+p['pager']}
            call eax
            add esp,4
            cmp edi,2
            jb blocked
            cmp edi,4
            ja blocked
            cmp dword ptr [{0x400000+p['pager_obj']}],0
            je blocked
            popad
            popfd
            push {0x400000+p['close']}
            ret
        blocked:
            popad
            popfd
            push {0x400000+p['click_exit']}
            ret
        native:
            popad
            popfd
            mov edx,dword ptr [{0x400000+p['null']}]
            mov eax,[esp+0x10]
            push {0x400000+p['click']+10}
            ret
        '''
        chunks.append((p['click_hook'],h))
    language_src=f'''
        push esi
        push edi
        lea eax,[ebx+{steam_dll}]
        push eax
        call dword ptr [ebx+{IAT['GetModuleHandleA']}]
        test eax,eax
        jz steam_done
        mov esi,eax
        lea eax,[ebx+{steam_getter}]
        push eax
        push esi
        call dword ptr [ebx+{IAT['GetProcAddress']}]
        test eax,eax
        jnz steam_getter_found
        lea eax,[ebx+{steam_getter_old}]
        push eax
        push esi
        call dword ptr [ebx+{IAT['GetProcAddress']}]
        test eax,eax
        jz steam_done
    steam_getter_found:
        mov edi,eax
        lea eax,[ebx+{steam_language}]
        push eax
        push esi
        call dword ptr [ebx+{IAT['GetProcAddress']}]
        test eax,eax
        jz steam_done
        mov esi,eax
        call edi
        test eax,eax
        jz steam_done
        push eax
        call esi
        add esp,4
        test eax,eax
        jz steam_done
        mov eax,[eax]
        and eax,0xffffff
        or eax,0x202020
    '''
    for alias,lang in [('eng','en'),('rus','ru'),('fre','fr'),('ger','de'),('spa','es')]:
        language_src+=f'cmp eax,{int.from_bytes(alias.encode(),"little")}\n jne steam_next_{alias}\n mov dword ptr [ebx+{DATA+0x240}],{LANGUAGE_ORDER.index(lang)}\n jmp steam_done\n steam_next_{alias}:\n'
    language_src+='steam_done:\n pop edi\n pop esi\n ret\n'
    chunks.append((0x3800,language_src))
    for rva,assembly in sorted(chunks):
        b=bytes(ks.asm(assembly,addr=rva)[0]);assert len(b)<0x400
        assert rva>=0x1000+len(code)
        code.extend(bytes(rva-0x1000-len(code)));code.extend(b)
        assemblies.append(f'; hook at RVA {rva:X}\n'+assembly)
    assert len(code)<RDATA-0x1000 and len(data)<IDATA-RDATA
    result=make_pe([
        ('.text',0x1000,bytes(code).ljust(RDATA-0x1000,b'\0'),0x60000020),
        ('.rdata',RDATA,bytes(data),0x40000040),
        ('.idata',IDATA,bytes(imp),0xc0000040),
        ('.reloc',RELOC,struct.pack('<IIHH',0x1000,12,0,0),0x42000040),
        ('.data',DATA,bytes(0x400),0xc0000040)],imports=(IDATA,40),reloc=(RELOC,12))
    output=HERE/'build-output'
    output.mkdir(exist_ok=True)
    out=output/'HT2_TractorSwap.asi';out.write_bytes(result)
    (output/'HT2_TractorSwap.asm').write_text('\n'.join(assemblies),encoding='utf-8')
    print(out,len(result),'bytes',hashlib.sha256(result).hexdigest())
    return result

if __name__=='__main__':build()
