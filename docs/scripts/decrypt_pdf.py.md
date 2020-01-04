# decrypt_pdf.py
**Purpose**: decrypt the PDF in the [Recover Cleartext Document](../challenges/c10.md) challenge.

```python
#!/usr/bin/env python3
"""Decrypt Encrypted PDF.""" 
from Crypto.Cipher import DES

seed = 0


def rand():
    """Generate random value."""
    # 1. get seed value
    # 2. multiply seed by 214013
    # 3. add 2531011 (this is our new seed value)
    # 4. right shift seed by 16
    # 5. bitwise AND with 32767
    global seed
    seed = (214013 * seed + 2531011)
    val = seed >> 16
    return (val & 32767)


def generate_key(val):
    """Generate encryption key."""
    global seed
    seed = val
    encrypted = []
    for _x in range(8):
        tmp = hex(rand())
        if len(str(tmp)) == 6:
            encrypted.append(str(tmp)[4:])
        elif len(str(tmp)) == 5:
            encrypted.append(str(tmp)[3:])
        elif len(str(tmp)) == 4:
            encrypted.append(str(tmp)[2:])
        elif len(str(tmp)) == 3:
            encrypted.append(f"0{str(tmp)[-1]}")
    return ''.join(encrypted)


def main():
    """Execute."""
    # File names
    encinfile = 'ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf.enc'
    pdfoutfile = 'ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf'

    # Friday, December 6, 2019 7:00:00 PM
    start = 1575658800

    # Loop over 2 hours and generate the key for each
    for x in range(7200):
        keyseed = start + x
        key = generate_key(keyseed)
        bytekey = bytearray.fromhex(key)

        # Prep for decrypting DES-CBC
        cipher = DES.new(
            bytekey,
            DES.MODE_CBC,
            iv=bytearray.fromhex('0000000000000000')
        )

        # Read encrypted file
        f = open(encinfile, 'rb')
        encrypted = f.read()

        # Decrypt using the current key
        msg = (cipher.iv + cipher.decrypt(encrypted))

        # Check if decryption was successful
        if msg[9:12] == b'PDF':
            # Yes, we got a PDF!
            print(f'Pass {x}: {key} decrypts to a PDF!')
            f = open(pdfoutfile, 'wb')
            f.write(msg)
            break
        else:
            # Womp womp! On to the next.
            print(f'Pass {x}: {key} is no bueno!')


if __name__ == "__main__":
    main()
```
