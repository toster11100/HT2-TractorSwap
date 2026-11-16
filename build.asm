
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
        lea eax, [ebx+32768]
        push 512
        push eax
        push 0
        call dword ptr [ebx+24720]
        test eax,eax
        jz success
        cmp eax,470
        jae success
        lea edi,[ebx+32768]
        lea ecx,[edi+eax]
    slash:
        cmp ecx,edi
        je success
        dec ecx
        cmp byte ptr [ecx],0x5c
        jne slash
        lea edi,[ecx+1]
        mov [ebp-16],edi
        lea esi,[ebx+20644]
    copy_ini:
        lodsb
        stosb
        test al,al
        jnz copy_ini
        lea eax,[ebx+32768]
        push eax
        push 16
        lea eax,[ebx+33360]
        push eax
        lea eax,[ebx+20664]
        push eax
        lea eax,[ebx+20658]
        push eax
        lea eax,[ebx+20654]
        push eax
        call dword ptr [ebx+24724]
        mov eax,[ebx+33360]
 and eax,0xffffff
 or eax,0x202020
cmp eax,6778469
 je lang_en
cmp eax,7566706
 je lang_ru
cmp eax,6386278
 je lang_fr
cmp eax,6648422
 je lang_fr
cmp eax,7497063
 je lang_de
cmp eax,7693668
 je lang_de
cmp eax,6385779
 je lang_es
cmp eax,7369573
 je lang_es
jmp ini_done
lang_en:
 mov dword ptr [ebx+33344],0
 jmp ini_done
lang_ru:
 mov dword ptr [ebx+33344],1
 jmp ini_done
lang_fr:
 mov dword ptr [ebx+33344],2
 jmp ini_done
lang_de:
 mov dword ptr [ebx+33344],3
 jmp ini_done
lang_es:
 mov dword ptr [ebx+33344],4
 jmp ini_done

    ini_done:
        mov edi,[ebp-16]
        lea esi,[ebx+20617]
    copy_name:
        lodsb
        stosb
        test al,al
        jnz copy_name
        push 0
        call dword ptr [ebx+24704]
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

    profile_0:
        cmp dword ptr [edx+0x50],3919872
        jne profile_1
        cmp dword ptr [edx+8],1197537196
        jne profile_1
        jmp check_0

    profile_1:
        cmp dword ptr [edx+0x50],3919872
        jne profile_2
        cmp dword ptr [edx+8],1074070250
        jne profile_2
        jmp check_1

    profile_2:
        cmp dword ptr [edx+0x50],3915776
        jne unsupported
        cmp dword ptr [edx+8],1016532983
        jne unsupported
        jmp check_2

 check_0:

                lea esi,[ebx+22064]
                mov edi,[ebp-16]
                add edi,1208516
                mov ecx,256
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22320]
                mov edi,[ebp-16]
                add edi,1208784
                mov ecx,16
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22336]
                mov edi,[ebp-16]
                add edi,1209320
                mov ecx,44
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22380]
                mov edi,[ebp-16]
                add edi,474048
                mov ecx,24
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22404]
                mov edi,[ebp-16]
                add edi,475077
                mov ecx,32
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22436]
                mov edi,[ebp-16]
                add edi,1478384
                mov ecx,45
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22481]
                mov edi,[ebp-16]
                add edi,1209008
                mov ecx,10
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22491]
                mov edi,[ebp-16]
                add edi,1210191
                mov ecx,13
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22504]
                mov edi,[ebp-16]
                add edi,1486320
                mov ecx,21
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22525]
                mov edi,[ebp-16]
                add edi,1481024
                mov ecx,246
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22771]
                mov edi,[ebp-16]
                add edi,1210113
                mov ecx,78
                repe cmpsb
                jne unsupported

                lea esi,[ebx+22849]
                mov edi,[ebp-16]
                add edi,1480352
                mov ecx,16
                repe cmpsb
                jne unsupported

            mov eax,22049
            mov [ebx+33312],eax
            mov esi,[ebp-16]
            lea edi,[esi+1208516]
            lea eax,[ebp-20]
            push eax
            push 0x40
            push 502
            push edi
            call dword ptr [ebx+24708]
            test eax,eax
            jz protect_failed
            lea eax,[ebx+10240]
            lea ecx,[esi+1208764]
            sub eax,ecx
            mov byte ptr [esi+1208759],0xe9
            mov [esi+1208760],eax
            mov dword ptr [esi+1208764],0x90909090
            mov byte ptr [esi+1208768],0x90
            lea eax,[ebx+12288]
            lea ecx,[esi+1209013]
            sub eax,ecx
            mov byte ptr [esi+1209008],0xe9
            mov [esi+1209009],eax
            mov dword ptr [esi+1209013],0x90909090
            mov byte ptr [esi+1209017],0x90
            lea eax,[ebp-16]
            push eax
            push dword ptr [ebp-20]
            push 502
            push edi
            call dword ptr [ebx+24708]
            mov esi,20521
            test eax,eax
            jnz flush_0
            mov esi,20584
        flush_0:
            push 502
            push edi
            push -1
            call dword ptr [ebx+24712]
            jmp status

 check_1:

                lea esi,[ebx+22879]
                mov edi,[ebp-16]
                add edi,1208628
                mov ecx,256
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23135]
                mov edi,[ebp-16]
                add edi,1208896
                mov ecx,16
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23151]
                mov edi,[ebp-16]
                add edi,1209432
                mov ecx,44
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23195]
                mov edi,[ebp-16]
                add edi,473280
                mov ecx,24
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23219]
                mov edi,[ebp-16]
                add edi,474309
                mov ecx,32
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23251]
                mov edi,[ebp-16]
                add edi,1478496
                mov ecx,45
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23296]
                mov edi,[ebp-16]
                add edi,1209120
                mov ecx,10
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23306]
                mov edi,[ebp-16]
                add edi,1210303
                mov ecx,13
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23319]
                mov edi,[ebp-16]
                add edi,1486432
                mov ecx,21
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23340]
                mov edi,[ebp-16]
                add edi,1481136
                mov ecx,246
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23586]
                mov edi,[ebp-16]
                add edi,1210225
                mov ecx,78
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23664]
                mov edi,[ebp-16]
                add edi,1480464
                mov ecx,16
                repe cmpsb
                jne unsupported

            mov eax,22865
            mov [ebx+33312],eax
            mov esi,[ebp-16]
            lea edi,[esi+1208628]
            lea eax,[ebp-20]
            push eax
            push 0x40
            push 502
            push edi
            call dword ptr [ebx+24708]
            test eax,eax
            jz protect_failed
            lea eax,[ebx+10752]
            lea ecx,[esi+1208876]
            sub eax,ecx
            mov byte ptr [esi+1208871],0xe9
            mov [esi+1208872],eax
            mov dword ptr [esi+1208876],0x90909090
            mov byte ptr [esi+1208880],0x90
            lea eax,[ebx+13312]
            lea ecx,[esi+1209125]
            sub eax,ecx
            mov byte ptr [esi+1209120],0xe9
            mov [esi+1209121],eax
            mov dword ptr [esi+1209125],0x90909090
            mov byte ptr [esi+1209129],0x90
            lea eax,[ebp-16]
            push eax
            push dword ptr [ebp-20]
            push 502
            push edi
            call dword ptr [ebx+24708]
            mov esi,20521
            test eax,eax
            jnz flush_1
            mov esi,20584
        flush_1:
            push 502
            push edi
            push -1
            call dword ptr [ebx+24712]
            jmp status

 check_2:

                lea esi,[ebx+23692]
                mov edi,[ebp-16]
                add edi,1206548
                mov ecx,256
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23948]
                mov edi,[ebp-16]
                add edi,1206816
                mov ecx,16
                repe cmpsb
                jne unsupported

                lea esi,[ebx+23964]
                mov edi,[ebp-16]
                add edi,1207352
                mov ecx,44
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24008]
                mov edi,[ebp-16]
                add edi,473360
                mov ecx,24
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24032]
                mov edi,[ebp-16]
                add edi,474389
                mov ecx,32
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24064]
                mov edi,[ebp-16]
                add edi,1476208
                mov ecx,45
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24109]
                mov edi,[ebp-16]
                add edi,1207040
                mov ecx,10
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24119]
                mov edi,[ebp-16]
                add edi,1208223
                mov ecx,13
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24132]
                mov edi,[ebp-16]
                add edi,1484144
                mov ecx,21
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24153]
                mov edi,[ebp-16]
                add edi,1478848
                mov ecx,246
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24399]
                mov edi,[ebp-16]
                add edi,1208145
                mov ecx,78
                repe cmpsb
                jne unsupported

                lea esi,[ebx+24477]
                mov edi,[ebp-16]
                add edi,1478176
                mov ecx,16
                repe cmpsb
                jne unsupported

            mov eax,23680
            mov [ebx+33312],eax
            mov esi,[ebp-16]
            lea edi,[esi+1206548]
            lea eax,[ebp-20]
            push eax
            push 0x40
            push 502
            push edi
            call dword ptr [ebx+24708]
            test eax,eax
            jz protect_failed
            lea eax,[ebx+11264]
            lea ecx,[esi+1206796]
            sub eax,ecx
            mov byte ptr [esi+1206791],0xe9
            mov [esi+1206792],eax
            mov dword ptr [esi+1206796],0x90909090
            mov byte ptr [esi+1206800],0x90
            lea eax,[ebx+15360]
            lea ecx,[esi+1207045]
            sub eax,ecx
            mov byte ptr [esi+1207040],0xe9
            mov [esi+1207041],eax
            mov dword ptr [esi+1207045],0x90909090
            mov byte ptr [esi+1207049],0x90
            lea eax,[ebp-16]
            push eax
            push dword ptr [ebp-20]
            push 502
            push edi
            call dword ptr [ebx+24708]
            mov esi,20521
            test eax,eax
            jnz flush_2
            mov esi,20584
        flush_2:
            push 502
            push edi
            push -1
            call dword ptr [ebx+24712]
            jmp status

    protect_failed:
        mov esi,20563
        jmp status
    unsupported:
        mov esi,20531
    status:
        add esi,ebx
        lea edi,[ebx+32768]
        push edi
        push esi
        lea eax,[ebx+20492]
        push eax
        lea eax,[ebx+20480]
        push eax
        call dword ptr [ebx+24716]
        push edi
        lea eax,[ebx+20507]
        push eax
        lea eax,[ebx+20499]
        push eax
        lea eax,[ebx+20480]
        push eax
        call dword ptr [ebx+24716]
        mov eax,[ebx+33312]
        test eax,eax
        jz success
        add eax,ebx
        push edi
        push eax
        lea eax,[ebx+20513]
        push eax
        lea eax,[ebx+20480]
        push eax
        call dword ptr [ebx+24716]
    success:
        mov eax,1
        add esp,8
        pop edi
        pop esi
        pop ebx
        pop ebp
        ret 12

; hook at RVA 2800

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

; hook at RVA 2A00

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

; hook at RVA 2C00

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

; hook at RVA 3000

            pushfd
            pushad
            call click_base
        click_base:
            pop ebx
            sub ebx,12295
            cld
            cmp dword ptr [esp+0x260],0xb9
            jne native
            mov ebp,[esp+52]
            mov edi,1
            cmp ebp,dword ptr [6863280]
            je notify
            mov edi,5
            cmp ebp,0x10000
            jb notify
            sub esp,4
            push esp
            mov eax,5672688
            call eax
            add esp,4
            pop eax
            cmp eax,dword ptr [6863280]
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
            mov eax,[ebx+33344]
            cmp eax,4
            jbe valid_language
            xor eax,eax
        valid_language:
            imul eax,eax,20
            lea edx,[ebx+21949]
            add edx,eax
            lea ecx,[edi-1]
            cmp ecx,4
            ja blocked
            mov eax,[edx+ecx*4]
            add eax,ebx

        send:
            push eax
            mov eax,5680624
            call eax
            add esp,4
            cmp edi,2
            jb blocked
            cmp edi,4
            ja blocked
            cmp dword ptr [7287896],0
            je blocked
            popad
            popfd
            push 5404417
            ret
        blocked:
            popad
            popfd
            push 5404495
            ret
        native:
            popad
            popfd
            mov edx,dword ptr [6863280]
            mov eax,[esp+0x10]
            push 5403322
            ret

; hook at RVA 3400

            pushfd
            pushad
            call click_base
        click_base:
            pop ebx
            sub ebx,13319
            cld
            cmp dword ptr [esp+0x260],0xb9
            jne native
            mov ebp,[esp+52]
            mov edi,1
            cmp ebp,dword ptr [6863248]
            je notify
            mov edi,5
            cmp ebp,0x10000
            jb notify
            sub esp,4
            push esp
            mov eax,5672800
            call eax
            add esp,4
            pop eax
            cmp eax,dword ptr [6863248]
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
            mov eax,[ebx+33344]
            cmp eax,4
            jbe valid_language
            xor eax,eax
        valid_language:
            imul eax,eax,20
            lea edx,[ebx+21949]
            add edx,eax
            lea ecx,[edi-1]
            cmp ecx,4
            ja blocked
            mov eax,[edx+ecx*4]
            add eax,ebx

        send:
            push eax
            mov eax,5680736
            call eax
            add esp,4
            cmp edi,2
            jb blocked
            cmp edi,4
            ja blocked
            cmp dword ptr [7287864],0
            je blocked
            popad
            popfd
            push 5404529
            ret
        blocked:
            popad
            popfd
            push 5404607
            ret
        native:
            popad
            popfd
            mov edx,dword ptr [6863248]
            mov eax,[esp+0x10]
            push 5403434
            ret

; hook at RVA 3800

        push esi
        push edi
        lea eax,[ebx+20668]
        push eax
        call dword ptr [ebx+24704]
        test eax,eax
        jz steam_done
        mov esi,eax
        lea eax,[ebx+20682]
        push eax
        push esi
        call dword ptr [ebx+24728]
        test eax,eax
        jnz steam_getter_found
        lea eax,[ebx+20706]
        push eax
        push esi
        call dword ptr [ebx+24728]
        test eax,eax
        jz steam_done
    steam_getter_found:
        mov edi,eax
        lea eax,[ebx+20730]
        push eax
        push esi
        call dword ptr [ebx+24728]
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
    cmp eax,6778469
 jne steam_next_eng
 mov dword ptr [ebx+33344],0
 jmp steam_done
 steam_next_eng:
cmp eax,7566706
 jne steam_next_rus
 mov dword ptr [ebx+33344],1
 jmp steam_done
 steam_next_rus:
cmp eax,6648422
 jne steam_next_fre
 mov dword ptr [ebx+33344],2
 jmp steam_done
 steam_next_fre:
cmp eax,7497063
 jne steam_next_ger
 mov dword ptr [ebx+33344],3
 jmp steam_done
 steam_next_ger:
cmp eax,6385779
 jne steam_next_spa
 mov dword ptr [ebx+33344],4
 jmp steam_done
 steam_next_spa:
steam_done:
 pop edi
 pop esi
 ret

; hook at RVA 3C00

            pushfd
            pushad
            call click_base
        click_base:
            pop ebx
            sub ebx,15367
            cld
            cmp dword ptr [esp+0x260],0xb9
            jne native
            mov ebp,[esp+52]
            mov edi,1
            cmp ebp,dword ptr [6858992]
            je notify
            mov edi,5
            cmp ebp,0x10000
            jb notify
            sub esp,4
            push esp
            mov eax,5670512
            call eax
            add esp,4
            pop eax
            cmp eax,dword ptr [6858992]
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
            mov eax,[ebx+33344]
            cmp eax,4
            jbe valid_language
            xor eax,eax
        valid_language:
            imul eax,eax,20
            lea edx,[ebx+21949]
            add edx,eax
            lea ecx,[edi-1]
            cmp ecx,4
            ja blocked
            mov eax,[edx+ecx*4]
            add eax,ebx

        send:
            push eax
            mov eax,5678448
            call eax
            add esp,4
            cmp edi,2
            jb blocked
            cmp edi,4
            ja blocked
            cmp dword ptr [7283608],0
            je blocked
            popad
            popfd
            push 5402449
            ret
        blocked:
            popad
            popfd
            push 5402527
            ret
        native:
            popad
            popfd
            mov edx,dword ptr [6858992]
            mov eax,[esp+0x10]
            push 5401354
            ret
