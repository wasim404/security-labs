def KSA(key_bytes):
    S = list(range(256))
    j = 0
    key_length = len(key_bytes)

    for i in range(256):
        j = (j + S[i] + key_bytes[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]

    return S

def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        yield S[(S[i] + S[j]) % 256]

def rc4_encrypt(key_string, plaintext_string):
    key = key_string.encode("utf-8")
    plaintext = plaintext_string.encode("utf-8")
    S = KSA(key)
    keystream = PRGA(S)
    ciphertext = bytearray()
    for p in plaintext:
        ciphertext.append(p ^ next(keystream))
    return bytes(ciphertext)

def rc4_decrypt(key_string, ciphertext_bytes):
    key = key_string.encode("utf-8")
    S = KSA(key)
    keystream = PRGA(S)

    plaintext = []
    for c in ciphertext_bytes:
        plaintext.append(c ^ next(keystream))

    return bytes(plaintext).decode("utf-8")


def main():
    key = "securekey"           # 输入普通字符串即可
    plaintext = "Hello, RC4!"   # 明文也是普通字符串

    ciphertext = rc4_encrypt(key, plaintext)
    print("Ciphertext (hex):", ciphertext.hex())
    decrypted = rc4_decrypt(key, ciphertext)
    print("Decrypted:", decrypted)


if __name__ == "__main__":
    main()