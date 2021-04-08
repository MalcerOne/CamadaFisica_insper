def transform_int(b):
    return int.from_bytes(b, byteorder='big')

def transform_byte(n):
    return int(n).to_bytes(1, byteorder='big')

