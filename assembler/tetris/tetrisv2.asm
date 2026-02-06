section data
# low aligned      Background, I, J, L, O, S, T, Z
tileset_data: int [0,0,0xff,0,0x03f,0,0xf90,0,0xff0,0,0x4f4,0,0x84f,0,0xf44]

I_block: int [
    0,1,0,
    0,1,0,
    0,1,0,
    0,1,0]
J_block: int [
    0,0,0,
    0,2,0,
    0,2,0,
    2,2,0]
L_block: int [
    0,0,0,
    0,3,0,
    0,3,0,
    0,3,3]
O_block: int [
    0,0,0
    0,0,0,
    0,4,4,
    0,4,4]
S_block: int [
    0,0,0,
    0,0,0,
    0,5,5,
    5,5,0]
T_block: int [
    0,0,0,
    0,0,0,
    6,6,6,
    0,6,0]
Z_block: int [
    0,0,0,
    0,0,0,
    7,7,0,
    0,7,7]

next_block_table: int [2,1,2,6,5,3,6,1,4,7,1,1,3,7,7,4,6,4]
next_block_table_len: 18

section text
# 0x400 = game data start

# arrays
# 0x400-0x4C8 = game grid
.define game_grid 0x400

# vars
.define active_block 0x4CA
.define postition 0x4CB
.define rotation 0x4CC
.define table_index 0x4CD


.define screen_coords 0x20B

main:
    call get_next_block
    nop
    halt
    nop
    add
    add
get_next_block:
    mov r14, next_block_table
    mov r13, table_index
    mov r12, next_block_table_len

    ldr r2, [add r13, 0]
    ldcl r3, [add r12, 0]
    nop
    nop
    cmp r2, r3      # if table_index > next_block_table_len
    nop
    mov.gt r0, 0xFFFF  # set to 0 for loop
    halt.gt
    nop
    # determine whether to load value from high or low
    divl r1, r2, 2, r0
    nop
    cmp r0, 0
    nop
    ldcl.eq r0, [add r14, r1]
    ldch.gt r0, [add r14, r1]
    nop
    # update tabel_index
    add r2, r2, 1
    nop
    ret
    nop
        
spawn_preview:
spawn_next:
    # check if active block is valid
    mov r14, active_block
    nop
    ldr r0, [add r14, 0]
    mov r14, 0xffff # instruction overflow


    ret
    nop
    nop
rotate_block:
move_block:
drop_block:


lock_to_grid:
grid_to_screen:
#   r0 = grid x,y
    mov r13, screen_coords
    nop
    add r0, r0, r13

    ret
    nop

update_score:

draw_block:
draw_preview:
draw_score:

restart: