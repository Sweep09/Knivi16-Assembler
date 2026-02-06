import base64
import zlib
import pyperclip

def list_to_huge_string(data):
    if len(data) != 1<<16:
        raise ValueError(f'expected table size of 65536 '
                         f'but got {len(data)}')
    lower_16 = bytearray()

    for value in data:
        lower = value & 0xFFFF
        lower_16.append(lower & 0xFF)
        lower_16.append((lower >> 8) & 0xFF)

    compressed_lower = zlib.compress(lower_16, level=2, wbits=-15)
    encoded_lower = base64.b64encode(compressed_lower).decode('utf-8').strip('=')
    return encoded_lower

a = [0]*(1<<16)
a[0] = (1<<16)-1
a[1] = (1<<16)-1
a[2] = (1<<16)-1
pyperclip.copy(list_to_huge_string(a))
print('done')
