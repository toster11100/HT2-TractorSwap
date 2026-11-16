"""Exercise Tractor Swap's Steam language query independently of voice INI."""
from pathlib import Path
import struct

import build as b
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (
    UC_X86_REG_EAX, UC_X86_REG_EBP, UC_X86_REG_EBX, UC_X86_REG_EDI,
    UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_ESI,
)

ROOT=Path(__file__).resolve().parent
P=lambda value:struct.pack('<I',value&0xffffffff)
COUNT=0
APIS=b.APIS
IAT=b.IAT
ORDER=b.LANGUAGE_ORDER
PE=pefile.PE(str(ROOT/'build-output'/'HT2_TractorSwap.asi'))

for base in (0x13000000,0x6f000000):
    for version in (8,9):
        for name,language in [
            ('english','en'),('russian','ru'),('french','fr'),('german','de'),
            ('spanish','es'),('italian',None),(None,None),
        ]:
            machine=Uc(UC_ARCH_X86,UC_MODE_32)
            machine.mem_map(base,0x10000)
            machine.mem_write(base,PE.get_memory_mapped_image())
            machine.mem_map(0x1000000,0x10000)

            def read(address):
                return struct.unpack('<I',machine.mem_read(address,4))[0]

            def ret(value,pop=0):
                stack=machine.reg_read(UC_X86_REG_ESP)
                machine.reg_write(UC_X86_REG_EAX,value)
                machine.reg_write(UC_X86_REG_ESP,stack+4+pop)
                machine.reg_write(UC_X86_REG_EIP,read(stack))

            def string(address):
                value=bytearray()
                while machine.mem_read(address,1)!=b'\0':
                    value+=machine.mem_read(address,1)
                    address+=1
                return value.decode()

            def hook(u,address,size,data):
                stack=u.reg_read(UC_X86_REG_ESP)
                if address==0x1000100:
                    assert string(read(stack+4))=='steam_api.dll'
                    ret(0x123400 if name else 0,4)
                elif address==0x1000110:
                    symbol=string(read(stack+8))
                    assert read(stack+4)==0x123400
                    ret(0x1000120 if symbol==f'SteamAPI_SteamApps_v00{version}'
                        else 0x1000130 if symbol=='SteamAPI_ISteamApps_GetCurrentGameLanguage'
                        else 0,8)
                elif address==0x1000120:
                    ret(0x123500)
                elif address==0x1000130:
                    assert read(stack+4)==0x123500
                    u.mem_write(0x1000200,name.encode()+b'\0')
                    ret(0x1000200)

            machine.hook_add(UC_HOOK_CODE,hook)
            machine.mem_write(base+IAT['GetModuleHandleA'],P(0x1000100))
            machine.mem_write(base+IAT['GetProcAddress'],P(0x1000110))
            fallback=ORDER.index('ru')
            machine.mem_write(base+b.DATA+0x240,P(fallback))
            stack,stop=0x100f000,0x1000000
            machine.mem_write(stack,P(stop))
            machine.reg_write(UC_X86_REG_ESP,stack)
            registers={
                UC_X86_REG_EBX:base,UC_X86_REG_ESI:0x11223344,
                UC_X86_REG_EDI:0x55667788,UC_X86_REG_EBP:0x12345678,
            }
            for register,value in registers.items():
                machine.reg_write(register,value)
            machine.emu_start(base+0x3800,stop,count=10000)
            assert machine.reg_read(UC_X86_REG_ESP)==stack+4
            assert all(machine.reg_read(register)==value
                       for register,value in registers.items())
            assert read(base+b.DATA+0x240)==(ORDER.index(language) if language else fallback)
            COUNT+=1

print('PASS:',COUNT,'Steam language and fallback cases')
