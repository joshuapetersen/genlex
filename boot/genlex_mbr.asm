; GENLEX METAL v1 — Bare x86 Glyph Interpreter (MBR 512B)
; nasm -f bin genlex_mbr.asm -o genlex_mbr.bin
; qemu-system-x86_64 -drive file=genlex_mbr.bin,format=raw

[BITS 16]
[ORG 0x7C00]

R equ 0x500
A equ 0x540
S equ 0x544

    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti
    finit
    mov di, R
    mov cx, 32
    rep stosw
    mov word [A], 0xE01E
    mov word [A+2], 0x3F8B
    mov word [S], 0xD70A
    mov word [S+2], 0x3C23
    mov si, ban
    call ps
    mov si, prg
    xor cx, cx

fe: cmp cx, 4096
    jge dn
    lodsb
    mov ah, [si]
    mov dl, [si+1]
    mov dh, [si+2]
    add si, 3
    inc cx
    and ah, 0xF
    and dl, 0xF
    and dh, 0xF
    cmp al, 0xFF
    je dn
    or al, al
    jz fe
    cmp al, 0x18
    je li
    cmp al, 0x17
    je pu
    cmp al, 0x11
    je ad
    cmp al, 0x10
    je lc
    cmp al, 0x20
    je cg
    cmp al, 0x23
    je ji
    cmp al, 0x22
    je jm
    cmp al, 0x35
    je de
    jmp fe

; LOAD_IMM: r[a] = next 4 bytes
li: movzx bx, ah
    shl bx, 2
    add bx, R
    mov di, bx
    movsw
    movsw
    jmp fe

; PULSE: r[a] *= ANCHOR
pu: movzx bx, ah
    shl bx, 2
    add bx, R
    fld dword [bx]
    fmul dword [A]
    fstp dword [bx]
    jmp fe

; ADD: r[a] += r[b]
ad: movzx bx, ah
    shl bx, 2
    add bx, R
    push bx
    movzx di, dl
    shl di, 2
    add di, R
    fld dword [di]
    pop bx
    fld dword [bx]
    faddp
    fstp dword [bx]
    jmp fe

; LOAD_CONST: r[a] = (b|f<<8)*0.01
lc: movzx bx, ah
    shl bx, 2
    add bx, R
    movzx ax, dl
    push dx
    movzx dx, dh
    shl dx, 8
    or ax, dx
    pop dx
    mov [S+4], ax
    fild word [S+4]
    fmul dword [S]
    fstp dword [bx]
    jmp fe

; CMP_GT: r[a] = r[a]>r[b] ? 1:0
cg: movzx di, dl
    shl di, 2
    add di, R
    fld dword [di]
    movzx bx, ah
    shl bx, 2
    add bx, R
    fld dword [bx]
    fcomip st0, st1
    fstp st0
    ja .t
    mov word [bx], 0
    mov word [bx+2], 0
    jmp fe
.t: mov word [bx], 0
    mov word [bx+2], 0x3F80
    jmp fe

; JUMP: pc = a|(b<<8)
jm: movzx bx, ah
    movzx di, dl
    shl di, 8
    or bx, di
    shl bx, 2
    lea si, [prg]
    add si, bx
    jmp fe

; JUMP_IF: if r[flags]!=0 jump
ji: push ax              ; save AH (target addr)
    push dx              ; save DL (target addr high)
    movzx di, dh
    shl di, 2
    add di, R
    fld dword [di]
    ftst
    fnstsw ax
    fstp st0
    sahf
    pop dx               ; restore DL
    pop ax               ; restore AH
    jz fe
    jmp jm

; DENSITY: r[a] = |r[a]|*ANCHOR
de: movzx bx, ah
    shl bx, 2
    add bx, R
    fld dword [bx]
    fabs
    fmul dword [A]
    fstp dword [bx]
    jmp fe

; HALT
dn: mov si, nl
    call ps
    mov ax, [R+2]
    cmp ax, 0x3F80
    je .p
    mov si, mf
    jmp .r
.p: mov si, mp
.r: call ps
    cli
    hlt
    jmp .r

ps: push ax
    push bx
.l: lodsb
    or al, al
    jz .d
    mov ah, 0x0E
    mov bx, 7
    int 0x10
    jmp .l
.d: pop bx
    pop ax
    ret

ban: db 'GLX',13,10,0
nl:  db 13,10,0
mp:  db 'OK',13,10,0
mf:  db 'FL',13,10,0

prg:
    db 0x18,0x00,0x00,0x00, 0x00,0x00,0x80,0x3F  ; r0=1.0
    db 0x18,0x01,0x00,0x00, 0x00,0x00,0xA8,0x41  ; r1=21.0
    db 0x18,0x02,0x00,0x00, 0x00,0x00,0x80,0x3F  ; r2=1.0
    db 0x18,0x03,0x00,0x00, 0x1E,0xE0,0x8B,0x3F  ; r3=ANCHOR
    db 0x17,0x00,0x00,0x00                         ; PULSE r0
    db 0x10,0x04,0x01,0x00                         ; LOAD_CONST r4 1
    db 0x11,0x02,0x04,0x00                         ; ADD r2 r4
    db 0x20,0x01,0x02,0x00                         ; CMP_GT r1 r2
    db 0x23,0x08,0x00,0x01                         ; JUMP_IF :8 r1
    db 0x35,0x00,0x00,0x00                         ; DENSITY r0
    db 0x20,0x00,0x02,0x00                         ; CMP_GT r0 r2 (density>counter?)
    db 0xFF,0x00,0x00,0x00                         ; HALT

    times 510-($-$$) db 0
    dw 0xAA55

