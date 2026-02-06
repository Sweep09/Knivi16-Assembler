.define px_offset 0x10
.define px_color 0x11
.define px_step 0x12
.define px_length 0x13

main:
    call smile
    mov r1 0xc8

    call sleep
    mov r14 3

    call smile
    mov r1 0xf44

    call sleep
    mov r14 3
    jmp main
    nop
smile:
    mov r0 0xc0f
    mov r2 5
    mov r3 8
    str r0 0 px_offset
    str r2 0 px_step
    str r1 0 px_color
    str r1 0 px_color

    mov r2 9
    mov r0 0xa11
    str r0 0 px_offset
    str r2 0 px_step
    str r1 0 px_color
    str r1 0 px_color

    mov r0 0xb12
    mov r2 1
    str r0 0 px_offset
    str r2 0 px_step
    str r3 0 px_length
    ret
    nop
sleep:
    cmp r14 0
    nop
    jmp.eq sleep_end
    nop
    nop
    nop
    nop
    nop
    sub r14 r14 1
    jmp sleep
    nop
sleep_end:
    ret
    nop