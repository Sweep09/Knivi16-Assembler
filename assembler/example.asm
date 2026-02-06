section data 
helloStr: "Hello World 123"
helloLen: 15
arrayThing: int [
0 ,1 
,2 ,3
,4]

section text
.define text_output 4

main:
mov r14, helloStr
mov r12, helloLen
mov r13, text_output
ldcl r12, [add r12, 0] # get value at pointer
mov r2, 0
nop
add r4, r12, 1
div r12, r12, 2
nop

loop:
cmp r2, r12
nop
ldcl.le r1, [add r14, r2]
nop
nop
str.le r1, [add r13, 0]

ldch.le r1, [add r14, r2]
nop
nop
str.le r1, [add r13, 0]
add.le r2, r2 1

jmp.le loop
nop
/*
add r2, r2, 1
jmp 
*/
halt