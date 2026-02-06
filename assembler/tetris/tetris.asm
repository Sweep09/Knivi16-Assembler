/*
screen size = 32x32

10x20 tile map array:
 = 200 addresses
stores tile index of locked blocks

tileset:

order = I,J,L,O,S,T,Z
0 = 0 empty
I = 0x0ff
J = 0x03f
L = 0xf90
O = 0xff0
S = 0x4f4
T = 0x84f
Z = 0xf44
8 indices

positions must be stored in memory packed
 ldr r0 [add r1 0]
 nop
 shr r0 r0 4
 and r2 r0 0xff exploit RAW hazard
 shr r0 r0 4
 done.

 7 blocks = 4px per block = 28 total addresses
*/

DATA:
nop
    # game grid 10x20
    .define game_grid 0x200 # - 0x2C8
    # each grid cell consists of tile index

    # mov r14 game_grid


    nop
    GRID_END:

    # next_grid 3x4

    # .define next_grid

    nop
    NEXT_GRID_END:

    # tileset data
    .define tileset_addr 0x100

    mov r1 0
    mov r14 tileset_addr
    nop
    ldr r2 [sub r14 1]
    nop
    cmp r2 0
    nop
    jmp.ne TILESET_END
    nop

    mov r0 0
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0x0ff
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0x03f
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0xf90
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0xff0
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0x4f4
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0x84f
    add r1 r1 1
    str r0 [add r14 0]
    add r14 r14 1

    mov r0 0xf44
    add r1 r1 1
    str r0 [add r14 0]
    nop

    # store length
    mov r14 tileset_addr
    nop
    str r1 [sub r14 1]
    nop

    TILESET_END:

    # Vector UI
    

## DATA END ##
DATA_END:












.define gpu_px 0x10

Draw_GUI:
    # grid border
    .define gui_check 0x4000
    mov r14 gui_check
    nop
    ldr r0 [add r14 0]
    nop
    nop
    cmp r0 0
    nop
    jmp.ne Draw_GUI_end
    nop
    mov r14 gpu_px
    mov r4 0
    mov r2 1
    nop
    str r2 [add r14 4]
    str r4 [add r14 2]
    mov r0 0x10A # top left right
    mov r1 0xFFF # color
    mov r2 1 # pix step
    mov r3 11 # pix length

    str r0 [add r14 0]
    str r1 [add r14 1]
    str r2 [add r14 2]
    nop
    str r3 [add r14 3]
    wait 3
    nop

    mov r0 0xC0A # top right down
    mov r2 32
    mov r3 21
    
    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop

    mov r0 0x10A # top left down
    mov r2 32
    mov r3 21 # pix length
    
    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop

    mov r0 0x11F # bottom left right
    mov r2 1
    mov r3 12

    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop

    # next_block border
    mov r0 0x1011 # top left right
    mov r2 1
    mov r3 10

    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop

    mov r0 0x1A11 # top right down
    mov r2 32
    mov r3 8

    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop

    mov r0 0x1011 # top left down
    mov r2 32
    mov r3 8

    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop


    mov r0 0x1118 # bottom left right
    mov r2 1
    mov r3 9

    str r0 [add r14 0]
    str r2 [add r14 2]
    str r3 [add r14 3]
    wait 3
    nop
    
    # score text
    mov r0 2
    mov r1 4
    str r0 [add r14 4] # text mode
    mov r0 0xFFF
    str r1 [add r14 2] # step
    mov r2 0x700
    str r0 [add r14 1] # color
    str r2 [add r14 0]
    mov r0 S
    mov r1 C
    mov r2 O
    str r0 [add r14 3]
    wait 3
    mov r0 R
    str r1 [add r14 3]
    wait 3
    mov r1 E
    str r2 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    nop
    str r1 [add r14 3]
    wait 3
    nop

    # score number
    mov r1 0x705
    nop
    str r1 [add r14 0]
    mov r0 0
    nop
    str r0 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    nop

    # next
    mov r1 0xF0C
    mov r0 N
    str r1 [add r14 0]
    mov r1 E
    mov r2 X
    str r0 [add r14 3]
    wait 3
    mov r0 T
    str r1 [add r14 3]
    wait 3
    nop
    str r2 [add r14 3]
    wait 3
    nop
    str r0 [add r14 3]
    wait 3
    str 0 [add r14 4]
    # validate
    mov r0 1
    mov r14 gui_check
    nop
    str r0 [add r14 0]

Draw_GUI_end:


# need variables to hold current block type/color and next block

Start:
# start initializing objects

Spawn_next:
# uses case jump table
    nop

Preview_next:
# will use case jump table
    .define preview_offset 0x1413
    mov r14 gpu_px
    mov r0 1
    nop
    str r0 [add r14 4]      # px mode
    call Spawn_L
    mov r0 preview_offset
    nop
    halt
    nop

Spawn_I:
# r0=location_offset
    mov r14 gpu_px
    add r0 r0 (shl 0x80 1)
    mov r1 tileset_addr
    mov r2 32
    ldr r1 [add r1 1]       # I block color
    str r2 [add r14 2]      # step
    str r0 [add r14 0]      # px
    mov r2 3
    str r1 [add r14 1]      # color
    str r2 [add r14 3]      # auto
    ret
    nop

Spawn_J:
# r0=location_offset
    mov r14 gpu_px
    add r0 r0 (shl 0x80 1)
    mov r1 tileset_addr
    add r0 r0 1
    mov r2 0
    ldr r1 [add r1 2]       # J block color
    str r2 [add r14 2]      # step
    str r0 [add r14 0]      # px
    add r0 r0 1
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    add r0 r0 1
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    sub r0 r0 (shl 0x80 1)
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    str r1 [add r14 1]      # color
    ret
    nop

Spawn_L:
# r0=location_offset
    mov r14 gpu_px
    add r0 r0 (shl 0x80 1)
    mov r1 tileset_addr
    add r0 r0 1
    mov r2 0
    ldr r1 [add r1 3]       # L block color
    str r2 [add r14 2]      # step
    str r0 [add r14 0]      # px
    add r0 r0 1
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    add r0 r0 1
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    add r0 r0 (shl 0x80 1)
    str r1 [add r14 1]      # color

    str r0 [add r14 0]      # px
    str r1 [add r14 1]      # color
    ret
    nop

Spawn_O:
# r0=location_offset
# need to figure out which side it should be on
    mov r14 gpu_px
    add r0 r0 (shl 0x80 1)
    mov r1 tileset_addr
    add r0 r0 1
    mov r2 0
    ldr r1 [add r1 4]       # J block color
    str r2 [add r14 2]      # step
    str r0 [add r14 0]      # px
    add r0 r0 1
    str r1 [add r14 1]      # color

    ret
    nop

Spawn_S:
Spawn_T:
Spawn_Z:

Delete_I:
# r0=location_offset
    mov r14 gpu_px
    add r0 r0 (shl 0x80 1)
    mov r2 32
    str r2 [add r14 2]      # step
    str r0 [add r14 0]      # px
    mov r2 3
    str 0 [add r14 1]      # color
    str r2 [add r14 3]      # auto
    ret
    nop

Delete_J:
Delete_L:
Delete_O:
Delete_S:
Delete_T:
Delete_Z:

Draw_line:
# r0=x0,y0, r1=x1,y1, r2=color, r3=step
    nop

halt

SHORT_WAIT:
    nop
    and
    and
    and
    and
    and
    and
    and
    and
    ret
    nop