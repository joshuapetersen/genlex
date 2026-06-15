; Absolute minimum test
[BITS 16]
[ORG 0x7C00]

    cli
    xor ax, ax
    mov ds, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    mov ah, 0x0E
    mov al, 'A'
    mov bx, 7
    int 0x10
    mov al, 'B'
    int 0x10
    mov al, 10
    int 0x10

    ; Now test FPU + interpreter-style fetch
    finit

    ; Store 1.0 at 0x500
    mov word [0x500], 0x0000
    mov word [0x502], 0x3F80

    ; Store ANCHOR at 0x504
    mov word [0x504], 0xE01E
    mov word [0x506], 0x3F8B

    ; Simulate fetch: read program bytes
    mov si, prg
    lodsb               ; AL = opcode (0x18)
    mov ah, [si]        ; AH = 0x00
    mov dl, [si+1]      ; DL = 0x00
    add si, 3           ; SI past header

    ; Simulate LOAD_IMM: copy 4 bytes from [si] to [0x500]
    movzx bx, ah
    shl bx, 2
    add bx, 0x500
    mov di, bx
    movsw               ; copy 2 bytes
    movsw               ; copy 2 bytes

    ; Print 'C' if we got here
    mov ah, 0x0E
    mov al, 'C'
    int 0x10

    ; FPU multiply
    fld dword [0x500]
    fmul dword [0x504]
    fstp dword [0x500]

    ; Print 'D'
    mov ah, 0x0E
    mov al, 'D'
    int 0x10

    cli
    hlt
    jmp $

prg:
    db 0x18, 0x00, 0x00, 0x00
    db 0x00, 0x00, 0x80, 0x3F

    times 510-($-$$) db 0
    dw 0xAA55
