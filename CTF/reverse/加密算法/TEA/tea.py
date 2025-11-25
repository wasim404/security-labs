import struct

DELTA = 0x9E3779B9
MASK32 = 0xFFFFFFFF


def to_uint32_tuple(block8: bytes):
    return struct.unpack(">2I", block8)


def to_bytes(v0, v1):
    return struct.pack(">2I", v0 & MASK32, v1 & MASK32)


def key_to_tuple(key16: bytes):
    return struct.unpack(">4I", key16)


# ========== TEA 单块加密 ==========
def tea_encrypt_block(block8: bytes, key16: bytes):
    v0, v1 = to_uint32_tuple(block8)
    k0, k1, k2, k3 = key_to_tuple(key16)
    sum_val = 0

    for _ in range(32):
        sum_val = (sum_val + DELTA) & MASK32
        v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + sum_val) ^ ((v1 >> 5) + k1))) & MASK32
        v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + sum_val) ^ ((v0 >> 5) + k3))) & MASK32

    return to_bytes(v0, v1)


# ========== TEA 单块解密 ==========
def tea_decrypt_block(block8: bytes, key16: bytes):
    v0, v1 = to_uint32_tuple(block8)
    k0, k1, k2, k3 = key_to_tuple(key16)
    sum_val = (DELTA * 32) & MASK32

    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k2) ^ (v0 + sum_val) ^ ((v0 >> 5) + k3))) & MASK32
        v0 = (v0 - (((v1 << 4) + k0) ^ (v1 + sum_val) ^ ((v1 >> 5) + k1))) & MASK32
        sum_val = (sum_val - DELTA) & MASK32

    return to_bytes(v0, v1)


# ========== 对字符串进行补齐 ==========
def pad(data: bytes):
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes):
    pad_len = data[-1]
    return data[:-pad_len]


# ========== 字符串加密（最终函数） ==========
def tea_encrypt_string(plaintext: str, key: str) -> str:
    data = plaintext.encode()
    data = pad(data)  # 自动补齐

    key16 = (key.encode() * 16)[:16]  # 任意长度 key → 16 字节

    cipher = bytearray()

    for i in range(0, len(data), 8):
        block = data[i:i+8]
        cipher.extend(tea_encrypt_block(block, key16))

    return cipher.hex()


# ========== 字符串解密（最终函数） ==========
def tea_decrypt_string(cipher_hex: str, key: str) -> str:
    ciphertext = bytes.fromhex(cipher_hex)

    key16 = (key.encode() * 16)[:16]  # 任意密钥 → 16 字节

    plaintext = bytearray()

    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i:i+8]
        plaintext.extend(tea_decrypt_block(block, key16))

    return unpad(plaintext).decode(errors="ignore")


# ======================= 测试 =======================
if __name__ == "__main__":
    key = "wasim"
    text = "Hello TEA 加密算法!"

    c = tea_encrypt_string(text, key)
    print("Cipher =", c)

    p = tea_decrypt_string(c, key)
    print("Plain =", p)
