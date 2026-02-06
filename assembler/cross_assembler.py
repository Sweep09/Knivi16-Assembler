import os
from time import perf_counter
from pathlib import Path
import hugemem_encoder as hme

os.path.dirname(os.path.abspath(__file__))
grandparent_dir = Path(__file__).parent.parent

OPCODES = {
    'nop': 0b00000,
    'and': 0b00001,
    'or': 0b00010,
    'xor': 0b00011,
    'xnor': 0b00100,

    'add': 0b00101,
    'addc': (0b00101, 0b001),
    'sub': (0b00110,0b001),
    'subb': 0b00110,
    'rsb': (0b00110,0b011),

    'abs': 0b00111,

    'shr': (0b01000,0b000),
    'sar': (0b01000,0b001),
    'ror': (0b01000,0b010),
    'shl': 0b01001,
    'rol': 0b01001,

    'mul': 0b01010,
    'mull': 0b01010,
    'div': 0b01011,
    'rdiv': (0b01011,0b010),
    'divl': 0b01011,
    'rdivl': (0b01011,0b010),

    'bic': 0b01100,

    'cmp': 0b01101,
    'scmp': (0b01101,0,0b0001),

    'mov': 0b01110,

    'ldr': (0b01111,0b000),
    'ldh': (0b01111,0b010),
    'ldl': (0b01111,0b001),
    'str': (0b10000,0b000),
    'sth': (0b10000,0b010),
    'stl': (0b10000,0b001),

    'jmp': 0b10001,
    'call': 0b10010,

    'push': 0b10011,
    'pop': (0b10011,0b001),
    'ret': (0b10011,0b011),

    #'loop': 0b10100,

    'ldch': (0b11010, 0b001),
    'ldcl': (0b11010, 0),

    'wait': 0b11110,
    'halt': 0b11111
}

ALU_OPS = {
    'and','or','xor','xnor','add','addc','sub',
            'subb','bic' ,'rsb'
}
SHIFT_OPS = {
    'shr','sar','ror','shl','rol'
}
SHORT_MATH_OPS = {
    'mul','div','rdiv'
}
LONG_MATH_OPS = {
    'mull','divl','rdivl'
}
MEMORY_MEM_OPS = {
    'ldr','ldh','ldl','str','sth','stl','ldch','ldcl'
}
BRANCH_OPS = {
    'jmp','call'
}
SYS_OPS = {
    'nop','halt', 'wait'
}
STACK_OPS = {
    'push','pop', 'ret'
}
CMP_OPS = {
    'cmp','scmp'
}
UNIQUE_OPS = {
    'abs','mov'
}
COPROCESSOR_OPS = {} # TODO not yet implemented

REGISTERS = {
    'r0': 0b0001,
    'r1': 0b0010,
    'r2': 0b0011,
    'r3': 0b0100,
    'r4': 0b0101,
    'r5': 0b0110,
    'r6': 0b0111,
    'r7': 0b1000,
    'r8': 0b1001,
    'r9': 0b1010,
    'r10': 0b1011,
    'r11': 0b1100,
    'r12': 0b1101,
    'r13': 0b1110,
    'r14': 0b1111,
}

CONDITIONS = {
    'gt': 0b0001,
    'ge': 0b0010,
    'eq': 0b0011,
    'le': 0b0100,
    'lt': 0b0101,
    'ne': 0b0110,
    'sign': 0b0111,
    'z': 0b1000,
    'nz': 0b1001,
    'cy': 0b1010,
    'bw': 0b1011,
    'hc': 0b1100,
    'hb': 0b1101,
}

ALU_2 = {
    'add': 0b0000,
    'sub': 0b0001,
}

def encode_instruction(code, fn=0, cond=None, tgt=None, src=None,
                        code2=None, src2=None, imm=0):
    opcode = OPCODES[code]
    opcode2 = 0

    if code2 is not None:
        if str(code2)[0] == 'r':
            opcode2 = REGISTERS.get(code2,0)
        elif str(code2).isnumeric():
            opcode2 = int(code2)
        else:
            opcode2 = ALU_2.get(code2,0)

    source1 = REGISTERS.get(src, 0)
    source2 = REGISTERS.get(src2, 0)
    target = REGISTERS.get(tgt, 0)
    cond = CONDITIONS.get(cond,0)

    if isinstance(opcode,tuple):
        if len(opcode) == 2:
            opcode, op_fn = opcode
            fn |= op_fn
        elif len(opcode) == 3:
            opcode,_,tgt_fn = opcode
            target = tgt_fn
        else:
            pass
    if imm != 0 and src2 is not None:
        assert False, f'Error: immediate {imm} and src2 {src2} in single instruction'

    instruction = (
        opcode << 27 |
        (fn & 0x7) << 24 |
        (cond & 0xF) << 20 |
        (target & 0xF) << 16 |
        (source1 & 0xF) << 12 |
        (opcode2 & 0xF) << 8 |
        ((source2 & 0xF) if src2 is not None else (imm & 0xFFFF))
    )
    assert 0 <= instruction < (1<<32), (f'instruction exceeds 32 bit: {code}, {instruction}\n'
                                   f'{opcode<<27}')

    return instruction

def resolve_alu_ops(opcode:str,operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if len(operands) <= 2 or len(operands) > 3:
        raise ValueError(f'invalid length of operands. '
                        f'{opcode}, {operands}')

    if operands[0][0] == 'r':
        tgt = operands[0]
    if operands[1][0] == 'r':
        src = operands[1]
    elif int(operands[1],0) == 0:
        imm = 0
    else:
        src = operands[1]
        fn = 6

    operand3 = operands[2].split(' ')
    if operand3[0][0] == '(':
        if operand3[0][1:].lower() in ('shl', 'lsh'):
            if operand3[1][0] == 'r':
                src2 = operand3[1]
            else:
                imm = int(operand3[1],0)
                fn = 4
            if len(operand3[2]) > 2:
                raise ValueError(f'operand shift amount too high. {opcode}, {operands}')
            if imm >= (1<<8):
                raise ValueError(f'immediate value too high. {opcode}, {operands}')
            code2 = operand3[2][0]
        else:
            raise ValueError(f'invalid shift. {opcode}, {operands}')

    elif operands[2][0] == 'r':
        src2 = operands[2]
    else:
        if fn != 0:
            raise ValueError(f'double immediate detected. {opcode}, {operands}')
        if int(operands[2],0) < (1<<8):
            imm = int(operands[2],0)
            fn = 4
        else:
            raise ValueError(f'immediate value too high. {opcode}, {operands}')

    if code2 is not None:
        code2 = int(code2,0)
        if code2 > 3 or code2 < 0:
            raise ValueError(f'can"t shift 2nd operand '
                            f'more than 3. {opcode}, {operands}')

    return (fn,tgt,src,code2,src2,imm)

def resolve_shift_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) > 3:
            raise ValueError(f'invalid length of operands. '
                        f'{opcode}, {operands}')
        if operands[0][0] == 'r':
            tgt = operands[0]
        if operands[1][0] =='r':
            src = operands[1]
        if operands[2].isnumeric():
            if int(operands[2],0) <= 4:
                code2 = str(int(operands[2],0) & 0x7)
            else:
                raise ValueError(f'shift amount too high. {opcode}, {operands}')
    return (fn,tgt,src,code2,src2,imm)

def resolve_smath_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) <= 2 or len(operands) > 3:
            raise ValueError(f'invalid length of operands. '
                            f'{opcode}, {operands}')
        for opd in operands:
            if opd.find('(') != -1:
                raise ValueError(f'cant shift big math operands. {opcode}, {operands}')
        fn,tgt,src,code2,src2,imm = resolve_alu_ops(opcode,operands)
    return (fn,tgt,src,code2,src2,imm)

def resolve_lmath_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    tgt2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) <= 3 or len(operands) > 4:
            raise ValueError(f'invalid length of operands. '
                            f'{opcode}, {operands}')
        for opd in operands:
            if opd.find('(') != -1:
                raise ValueError(f'cant shift big math operands. {opcode}, {operands}')

        if operands[0][0] =='r':
            tgt = operands[0]
        if operands[1][0] =='r':
            src = operands[1]

        if operands[2][0] =='r':
            src2 = operands[2]
        else:
            if fn != 0:
                raise ValueError(f'double immediate detected. {opcode}, {operands}')
            if int(operands[2],0) < (1<<8):
                imm = int(operands[2],0)
                fn = 4
            else:
                raise ValueError(f'immediate value too high. {opcode}, {operands}')

        if operands[3][0] =='r':
            tgt2 = operands[3]

    return (fn,tgt,src,tgt2,src2,imm)


def resolve_mem_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if operands[0][0] =='r':
            tgt = operands[0]

        operand3 = operands[1].split(' ')
        if operand3[0][0] =='[':
            if operand3[0][1:].lower() in ALU_2:
                code2 = operand3[0][1:]
                if operand3[1][0] =='r':
                    src = operand3[1]
                if operand3[2][0] =='r':
                    src2 = operand3[2][:-1]
                else:
                    if int(operand3[2][:-1],0) < (1<<8):
                        imm = int(operand3[2][:-1],0)
                        fn = 4
                    else:
                        raise ValueError(f'immediate '
                                    f'value too high. {opcode}, {operands}')
            else:
                raise ValueError(f'unknown alu memory opcode. {opcode}, {operands}')
        else:
            if len(operands) == 3:
                if operands[1][0] =='r':
                    src = operands[1]

                if operands[2][0] =='r':
                    src2 = operands[2]
                else:
                    if int(operands[2],0) < (1<<8):
                        imm = int(operands[2],0)
                        fn = 4
                    else:
                        raise ValueError(f'immediate value '
                                         f'too high. {opcode}, {operands}')
            else:
                raise ValueError(f'unknown syntax. {opcode}, {operands}')

    return (fn,tgt,src,code2,src2,imm)

def resolve_branch_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) > 1:
            raise ValueError(f'Too many operands. {opcode}, {operands}')

        if operands[0][0] =='r':
            src2 = operands[0]
        else:
            if int(operands[0],0) < (1<<16):
                imm = int(operands[0],0)
                fn = 4
            else:
                raise ValueError(f'immediate value too high. {opcode}, {operands}')

    return (fn,tgt,src,code2,src2,imm)

def resolve_sys_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if opcode == 'wait':
            if len(operands) == 1 and int(operands[0],0) < 256:
                fn = 4
                imm = int(operands[0],0)
            else:
                raise ValueError(f'too many/high operand/s. {opcode} {operands}')

    return (fn,tgt,src,code2,src2,imm)


def resolve_stack_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) > 1:
            raise ValueError(f'Too many operands. {opcode}, {operands}')

        if operands[0][0] =='r':
            if opcode.lower() == 'push':
                src2 = operands[0]
            else:
                tgt = operands[0]
        elif operands[0].lower() == 'pc':
            fn = 2
        else:
            if opcode.lower() not in ('pop', 'ret'):
                if int(operands[0],0) < (1<<16):
                    imm = int(operands[0],0)
                    fn = 4
                else:
                    raise ValueError(f'immediate value too high. {opcode}, {operands}')

    return (fn,tgt,src,code2,src2,imm)


def resolve_cmp_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) != 2:
            raise ValueError(f'too many/little operands. {opcode}, {operands}')
        if operands[0][0] =='r':
            src = operands[0]

        operand3 = operands[1].split(' ')
        if operand3[0][0] =='(':
            if operand3[0][1:].lower() in ('shl', 'lsh'):
                if operand3[1][0] =='r':
                    src2 = operand3[1]
                else:
                    imm = int(operand3[1])
                    fn = 4
                if len(operand3[2]) > 2:
                    raise ValueError(f'operand shift amount too high. {opcode}, {operands}')
                if imm >= (1<<8):
                    raise ValueError(f'immediate value too high. {opcode}, {operands}')
                code2 = operand3[2][0]
            else:
                raise ValueError(f'invalid shift. {opcode}, {operands}')

        elif operands[1][0] =='r':
            src2 = operands[1]
        else:
            if int(operands[1],0) < (1<<8):
                imm = int(operands[1],0)
                fn = 4
            else:
                raise ValueError(f'immediate value too high. {opcode}, {operands}')

    if code2 is not None:
        code2 = int(code2,0)
        if code2 > 3 or code2 < 0:
            raise ValueError(f'can"t shift 2nd operand '
                            f'more than 3. {opcode}, {operands}')

    return (fn,tgt,src,code2,src2,imm)

def resolve_unique_ops(opcode: str, operands: list[str,int]) -> tuple:
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if operands:
        if len(operands) != 2:
            raise ValueError(f'invalid operand amount. {opcode}, {operands}')
        if operands[0][0] =='r':
            tgt = operands[0]

        if opcode == 'mov':
            if operands[1][0] =='r':
                src2 = operands[1]
            elif operands[1].isalpha():
                if len(operands[1]) > 1:
                    raise ValueError(f'string too big. {opcode}, {operands}')
                if not is_ascii(operands[1]):
                    raise ValueError(f'invalid ascii character. {opcode}, {operands}')

                imm = ord(operands[1]) # TODO: move to parse part 2
                fn = 4
            elif operands[1][0] in ('"',"'"):
                imm = ord(operands[1][1])
                fn = 4
            else:
                imm = int(operands[1],0) & 0xffff
                fn = 4
        elif opcode == 'abs':
            if operands[1][0] =='r':
                src2 = operands[1]
            else:
                if int(operands[1],0) < (1<<8):
                    imm = int(operands[1],0)
                    fn = 4
                else:
                    raise ValueError(f'immediate value too high. {opcode}, {operands}')
    return (fn,tgt,src,code2,src2,imm)

def resolve_copr_ops(opcode: str, operands: list[str,int]) -> tuple:
    raise NotImplementedError(f'operation not implemented. {opcode}')

def is_ascii(s: str) -> bool:
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def resolve_operands(opcode: str, operands: list[str,int]):
    fn = 0
    tgt = None
    src = None
    code2 = None
    src2 = None
    imm = 0

    if opcode == 'ldc':
        raise SyntaxError(f'instruction width is 32 bit. '
            f'specify upper or lower word using ldch,ldcl. {opcode}, {operands}')
    if operands:
        if opcode in ALU_OPS:
            fn,tgt,src,code2,src2,imm = resolve_alu_ops(opcode,operands)
        elif opcode in SHIFT_OPS:
            fn,tgt,src,code2,src2,imm = resolve_shift_ops(opcode,operands)
        elif opcode in SHORT_MATH_OPS:
            fn,tgt,src,code2,src2,imm = resolve_smath_ops(opcode,operands)
        elif opcode in LONG_MATH_OPS:
            fn,tgt,src,code2,src2,imm = resolve_lmath_ops(opcode,operands)
        elif opcode in MEMORY_MEM_OPS:
            fn,tgt,src,code2,src2,imm = resolve_mem_ops(opcode,operands)
        elif opcode in BRANCH_OPS:
            fn,tgt,src,code2,src2,imm = resolve_branch_ops(opcode,operands)
        elif opcode in SYS_OPS:
            fn,tgt,src,code2,src2,imm = resolve_sys_ops(opcode,operands)
        elif opcode in STACK_OPS:
            fn,tgt,src,code2,src2,imm = resolve_stack_ops(opcode,operands)
        elif opcode in CMP_OPS:
            fn,tgt,src,code2,src2,imm = resolve_cmp_ops(opcode,operands)
        elif opcode in UNIQUE_OPS:
            fn,tgt,src,code2,src2,imm = resolve_unique_ops(opcode,operands)
        elif opcode in COPROCESSOR_OPS:
            # not yet implemented
            resolve_copr_ops(opcode,operands)

    return (fn,tgt,src,code2,src2,imm)

def smart_split(line:str, line_num = 0):
    tokens = []
    token = ''
    depth = 0
    for char in line:
        if char in '([':
            depth += 1
            token += char
        elif char in ')]':
            depth -= 1
            token += char
        elif char == ',':
            if depth == 0:
                if token.strip():
                    tokens.append(token.strip())
                token = ''
            else:
                if depth > 0 and char == ',':
                    continue
                token += char
        elif char == ' ' and depth == 0:
            if token.strip():
                tokens.append(token.strip())
            token = ''
        else:
            token += char

    if depth < 0 or depth > 0:
        raise ValueError(f'unresolved brackets. line {line_num}: {line}')

    if token.strip():
        if token[-1] in ')]':
            token = ' '.join(token.strip().split())
        tokens.append(token.strip())

    def clean_expr(tok: str):
        if tok[0] in '([' and tok[-1] in ')]':
            inner = tok[1:-1]
            inner_clean = ' '.join(inner.split())
            return f'{tok[0]}{inner_clean}{tok[-1]}'
        return tok

    return [clean_expr(t) for t in tokens]

def resolve_lv(opd: str, labels: dict, variables: dict) -> str:
    operand = opd
    if opd in labels:
        operand = str(labels[opd])
    elif opd in variables:
        operand = str(variables[opd])

    if opd[0] =='(' and opd[-1] == ')':
        inner = opd[1:-1].strip()
        parts = inner.split()
        new_parts = [resolve_lv(p, labels, variables) for p in parts]
        operand = '(' + ' '.join(str(item) for item in new_parts) + ')'
    elif opd[0] =='[' and opd[-1] == ']':
        inner = opd[1:-1].strip()
        parts = inner.split()
        new_parts = [resolve_lv(p, labels, variables) for p in parts]
        operand = '[' + ' '.join(str(item) for item in new_parts) + ']'

    return operand

def resolve_mods(tokens: str):
    fn = 0
    parts = tokens[0].split('.')
    code = parts[0]
    mod = None # for instructions like cmp,push,pop
    cond = None

    if len(parts) == 2:
        cond = parts[1]
    elif len(parts) == 3:
        mod = parts[1]
        cond = parts[2]
    else:
        if len(parts) != 1:
            raise ValueError('opcode has too many modifiers.')

    if code in CMP_OPS and (cond or mod):
        force = ('f', 'force')
        if cond and cond.lower() in force:
            fn = 1
        elif cond and cond not in CONDITIONS:
            print(f'Warning: {cond} in {tokens[0]} is not valid.')
        if mod and mod.lower() in force:
            fn = 1

    elif code in STACK_OPS and (cond or mod):
        if cond and cond not in CONDITIONS:
            if cond == 'pc':
                raise ValueError(f'{cond} in {tokens[0]} is not valid.')
            print(f'Warning: {cond} in {tokens[0]} is not valid.')
        if mod:
            raise ValueError(f'{mod} in {tokens[0]} is not valid.')
        if code == 'pop':
            print(f'Warning: conditional operations '
                  f'have not been implemented for "{code}".')

    else:
        if mod:
            print(f'Warning: {mod} in {tokens[0]} is not valid.')
        if cond and cond not in CONDITIONS:
            print(f'Warning: {cond} in {tokens[0]} is not valid.')

    return code,fn,cond

def parse_data(tokens,data_pc,d_type):
    index = None
    if d_type == 'str':
        for i,_ in enumerate(tokens):
            if tokens[i][-1] in ('"',"'"):
                tokens[i] = tokens[i][:-1]
                index = i+1
                break

        var =  ' '.join(tokens[:index])
        for char in var:
            program.append((data_pc,(char,'str')))
            data_content.append((data_pc,char,'str'))
            data_pc += 0.5
        data_pc = int(data_pc) + 1

    elif d_type == 'int':
        var = tokens[0]
        program.append((data_pc,(var,'int')))
        data_content.append((data_pc,var,'int'))
        data_pc += 1

    elif d_type == 'array':
        new_toks = []
        if len(tokens) > 1:
            for token in tokens:
                new_toks += token.split(',')
        for i in new_toks:
            if len(i) > 1 and i[-1] == ']':
                i = i[:-1]
            program.append((data_pc,(i,'array')))
            data_content.append((data_pc,i,'array'))
            data_pc += 0.5
        data_pc = int(data_pc) + 1
    else:
        raise ValueError('invalid data type')

    return data_pc

data_content = []
program = []

def parse_part1(lines: list[str], debug=False):
    labels = {}
    variables = {}
    data_pc = 0xE000

    line_num = 0
    pc = 0
    mul_comment = False
    data_section = None
    text_section = None
    curr_section = 't'

    d_type = None
    array_type = None
    new_toks = []

    lines = lines.split('\n')

    for line in lines:

        if line.strip().startswith('/*'):
            mul_comment = True
        if mul_comment:
            #ignore lines
            if line.strip().endswith('*/'):
                mul_comment = False
            line_num += 1
            continue

        line = line.split('#')[0].strip()
        if not line:
            line_num += 1
            continue

        line = line.split('//')[0].strip()
        if not line:
            line_num += 1
            continue

        tokens = [token.strip(',') for token in line.split()]

        if tokens[0].lower() == 'section' and tokens[1].lower() == 'data':
            if not data_section:
                curr_section = 'd'
                data_section = pc
                tokens = tokens[1:]
                line_num += 1
                continue
            raise ValueError('data section already defined.')

        if tokens[0].lower() == 'section' and tokens[1].lower() == 'text':
            if not text_section:
                curr_section = 't'
                text_section = pc
                tokens = tokens[1:]
                line_num += 1
                continue
            raise ValueError('text section already defined.')

        if d_type != 'array' and len(tokens) > 1: # for types like floats, etc.
            if tokens[1].lower().startswith('int'):
                array_type = 'int'
                tokens = [tokens[0]] + tokens[2:]

        if tokens[0] == '.define':
            if len(tokens) < 3:
                raise ValueError(f'definition value not defined. {tokens}')
            if tokens[1][0].isalpha():
                var = tokens[1]
                if var in labels or var in variables:
                    raise ValueError(f'redefining global. '
                                     f'Line: {line_num+1} {tokens}')

                variables[var] = tokens[2]
                tokens = tokens[1:]
                line_num += 1
                continue
            raise ValueError(f'invalid definition name. Line: {line_num+1} {tokens}')

        if d_type == 'array':
            if array_type != 'int':
                raise NotImplementedError('not int array')
            if tokens[-1].endswith(']'): # single or last line
                tokens[-1] = tokens[-1][:-1]
                new_toks += tokens
                data_pc = parse_data(new_toks,data_pc, d_type)

                d_type = None
                array_type = None
                new_toks = []
                tokens = []
                line_num += 1
                continue

            new_toks += tokens
            line_num += 1
            continue

        if tokens[0][-1] == ':':
            if tokens[0][0].isalpha():
                name = tokens[0][:-1]
                if name in variables or name in labels:
                    raise ValueError(f'redefining global. '
                                    f' Line: {line_num+1} {tokens}')
                if curr_section == 't':
                    labels[name] = pc
                    tokens = tokens[1:]
                    if not tokens:
                        line_num += 1
                        continue
                elif curr_section == 'd':
                    if array_type != 'array':
                        labels[name] = data_pc
                    tokens = tokens[1:]

                    if tokens[0][0] in ('"',"'"):
                        tokens[0] = tokens[0][1:]
                        d_type = 'str'
                        data_pc = float(data_pc) # for 16 bit grouping

                    elif tokens[0][0] == '[':
                        tokens[0] = tokens[0][1:]
                        data_pc = float(data_pc)
                        d_type = 'array'

                    elif tokens[0][0].isnumeric():
                        d_type = 'int'

                    if d_type == 'array':
                        if array_type != 'int':
                            raise NotImplementedError('not int array')
                        if not tokens[-1].endswith(']'):
                            if tokens[0] != '':
                                new_toks += tokens
                                line_num += 1
                                continue
                            continue
                        if len(tokens) == 1:
                            tokens = tokens[0].split(',')
                        elif len(tokens) > 1 and (',' in tokens[0] or ',' in tokens[1]):
                            raise ValueError('bruhhhhhhhhhhhhhhhhhhh no spacessss')
                    new_toks = tokens
                    data_pc = parse_data(new_toks,data_pc, d_type)
                    d_type = None
                    array_type = None
                    new_toks=[]
                    tokens = []
                    line_num += 1
                    continue

            raise ValueError(f'invalid label name. Line: {line_num+1} {tokens}')

        tokens = smart_split(line, line_num)
        packed_lv = [labels, variables]
        packed_sections = [data_section, text_section]
        program.append((pc,tokens))
        line_num += 1
        pc += 1

    if debug:
        print(f'labels: {labels} \n'
            f'variables: {variables} \n'
            f'data: {data_content}')
        print(f'file lines (considering arrays as single objects): {line_num} \n'
            f'compiled text lines: {pc}')
        print(f'data_pc_offset: {data_pc}')
        #print(f'unfiltered program content: {program}')

    return packed_lv, packed_sections # TODO

def parse_part2(packed_globals, debug=False, nop=False):
    binary_data = [0]*(1<<16)
    data_data = []

    labels = packed_globals[0]
    variables = packed_globals[1]

    for pc, tokens in program:
        if pc >= 0xE000:
            # add to separate dictionary
            data_data.append((pc,tokens))
            continue
        operands = tokens[1:]
        code,fn,cond = resolve_mods(tokens)

        for i,_ in enumerate(operands):
            operands[i] = resolve_lv(operands[i],
                                    labels, variables)

        fn2,tgt,src,code2,src2,imm = resolve_operands(code,operands)

        fn |= fn2
        binary_data[pc] = encode_instruction(code,
                            fn,cond,tgt,src,code2,src2,imm)

    last_index = 0
    for k,(i,(v,t)) in enumerate(data_data):
        if v == '':
            raise ValueError(f'null string: {data_data[k]}')
        if isinstance(i, float):
            i = int(i)

        if t == 'str':
            v = ord(v)
        elif t == 'int':
            v = int(v,0)
        elif t == 'array':
            v = int(v,0)
        else:
            raise ValueError(f'unknown data type: {data_data[k]}')

        if i != last_index:
            binary_data[i] = v
        else:
            binary_data[i] |= v<<16

        last_index = i

    return binary_data if not nop else None

def parse_full(file_content, debug=False):
    time1 = perf_counter()
    glbl, sects = parse_part1(file_content,debug)
    time2 = perf_counter()
    bee = parse_part2(glbl)
    time3 = perf_counter()
    print(f'first pass: {time2-time1}')
    print(f'second pass: {time3-time2}')
    return bee

#f'{grandparent_dir}/...'
# tetris/tetrisv2.asm
if __name__ == '__main__':
    E = 'example.asm'
    E2 = 'example2.asm'
    BTB16 = 'bin_to_b16.asm'
    TET = 'tetris/tetris.asm'
    TET2 = 'tetris/tetrisv2.asm'
    TEST = 'tetris/test.asm'
    with open(TET2, 'r', encoding='utf-8') as file:
        text = file.read()

    a = parse_full(text, True)
    #print(a[:500])
    time4 = perf_counter()
    b = hme.list_to_huge_string(a)
    time5 = perf_counter()
    print(f'hugemem encoding time: {time5-time4}')
    print(b)
