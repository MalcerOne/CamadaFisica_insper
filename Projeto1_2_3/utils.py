def transform_int(bytes):
    return int.from_bytes(bytes, byteorder='big')

def transform_byte(n):
    return int(n).to_bytes(1, byteorder='big')

