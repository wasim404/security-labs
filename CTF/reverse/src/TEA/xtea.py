import struct

DELTA = 0x9E3779B9

def key_to_u32(key_str: str):
    """把任意字符串密钥补齐/截断到16字节，并转成4个uint32"""
    k = key_str.encode('utf-8')
    if len(k) < 16:
        k = k.ljust(16, b'\0')
    else:
        k = k[:16]
    return list(struct.unpack("<4I", k))


def pkcs7_pad(data: bytes, block_size: int) -> bytes:
    pad = block_size - (len(data) % block_size)
    if pad == 0:
        pad = block_size
    return data + bytes([pad]) * pad


def pkcs7_unpad(data: bytes) -> bytes:
    pad = data[-1]
    return data[:-pad]


def xtea_encipher_block(v0, v1, key, rounds=32):
    sum_ = 0
    for _ in range(rounds):
        v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum_ + key[sum_ & 3]))) & 0xffffffff
        sum_ = (sum_ + DELTA) & 0xffffffff
        v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum_ + key[(sum_ >> 11) & 3]))) & 0xffffffff
    return v0, v1


def xtea_decipher_block(v0, v1, key, rounds=32):
    sum_ = (DELTA * rounds) & 0xffffffff
    for _ in range(rounds):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum_ + key[(sum_ >> 11) & 3]))) & 0xffffffff
        sum_ = (sum_ - DELTA) & 0xffffffff
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum_ + key[sum_ & 3]))) & 0xffffffff
    return v0, v1


def xtea_encrypt(plaintext: str, key_str: str) -> bytes:
    key = key_to_u32(key_str)
    data = pkcs7_pad(plaintext.encode(), 8)

    out = bytearray()
    for i in range(0, len(data), 8):
        v0, v1 = struct.unpack("<2I", data[i:i+8])
        v0, v1 = xtea_encipher_block(v0, v1, key)
        out.extend(struct.pack("<2I", v0, v1))
    return bytes(out)


def xtea_decrypt(cipher: bytes, key_str: str) -> str:
    key = key_to_u32(key_str)

    out = bytearray()
    for i in range(0, len(cipher), 8):
        v0, v1 = struct.unpack("<2I", cipher[i:i+8])
        v0, v1 = xtea_decipher_block(v0, v1, key)
        out.extend(struct.pack("<2I", v0, v1))

    data = pkcs7_unpad(out)
    return data.decode()


if __name__ == "__main__":
    msg = "hello xtea"
    key = "xteaxteaxteaxtea"
    ct = xtea_encrypt(msg, key)
    print("\n密文(hex):", ct.hex())
    print("解密结果:", xtea_decrypt(ct, key))
