from Crypto.Cipher import AES
from typing import Union

_default_key = b"1111222233334444" # this is K3
_default_iv = b"5555666677778888"

confirmation_message = b'This message is to confirm key receival ' + bytes([10,100,200,15,17,19,5,4,3,2,1])

def xor(a,b):
    l = len(a)
    return bytes([a[i]^b[i] for i in range(l)])

def _enc_aes(block:bytes, key:bytes):

    cipher = AES.new(key)
    return cipher.encrypt(block)

def _dec_aes(block:bytes, key:bytes):

    cipher = AES.new(key)
    return cipher.decrypt(block)

def _enc_cbc(blocks,key:bytes,iv:bytes):

    c_blocks = []

    cipher = AES.new(key)

    for b in blocks:
        iv = xor(b,iv)
        iv = cipher.encrypt(iv)
        c_blocks.append(iv)
    
    return c_blocks

def _enc_cfb(blocks,key,iv):

    c_blocks = []

    cipher = AES.new(key)

    for b in blocks:
        iv = cipher.encrypt(iv)
        iv = xor(b,iv)
        c_blocks.append(iv)
    
    return c_blocks

def _dec_cbc(blocks,key,iv):

    d_blocks = []

    cipher = AES.new(key)

    for b in blocks:
        next_iv = b
        b = cipher.decrypt(b)
        b = xor(b,iv)
        d_blocks.append(b)
        iv = next_iv
    
    return d_blocks

def _dec_cfb(blocks,key,iv):

    d_blocks = []

    cipher = AES.new(key)

    for b in blocks:
        next_iv = b
        iv = cipher.encrypt(iv)
        b = xor(b,iv)
        d_blocks.append(b)
        iv = next_iv
    
    return d_blocks

def _get_blocks(content):

    if type(content) == str:
        content = bytes(content,'ascii')

    l = len(content)

    excess = l%16
    padding = 16 - excess
    #print(f"padding = {padding}")

    content = content + bytes([padding])*padding

    #print(content)

    return [content[i:i+16] for i in range(0,len(content),16)]

def enc_cbc(message,key,iv):

    blocks = _get_blocks(message)
    c_blocks = _enc_cbc(blocks,key,iv)
    #print(type(c_blocks[0]))
    return bytes().join(c_blocks)

def enc_cfb(message,key,iv):

    blocks = _get_blocks(message)
    c_blocks = _enc_cfb(blocks,key,iv)
    #print(type(c_blocks[0]))
    return bytes().join(c_blocks)

def dec_cbc(cph_text,key,iv, is_string = False):

    blocks = [cph_text[i:i+16] for i in range(0,len(cph_text),16)]
    d_blocks = _dec_cbc(blocks,key,iv)
    dec_text = bytes().join(d_blocks)
    padding = int(dec_text[-1])
    dec_text = dec_text[:-padding]
    if is_string: dec_text = dec_text.decode('ascii')
    return dec_text

def dec_cfb(cph_text,key,iv, is_string = False):

    blocks = [cph_text[i:i+16] for i in range(0,len(cph_text),16)]
    d_blocks = _dec_cfb(blocks,key,iv)
    dec_text = bytes().join(d_blocks)
    padding = int(dec_text[-1])
    dec_text = dec_text[:-padding]
    if is_string: dec_text = dec_text.decode('ascii')
    return dec_text

def enc_aes(message: Union[str, bytes] ,key = _default_key):
    
    if len(message) > 16: raise ValueError("message cannot be longer than 16 bytes")
    
    if type(message) is str:
        message = message + " "*(16 - len(message))
        message = message.encode('utf-8')
    elif type(message) is bytes:
        if len(message) < 16:
            raise ValueError("bytes type message must have len = 16")
    else:
        raise ValueError("message must be str or bytes")
    
    return _enc_aes(message,key)

def dec_aes(cph_text, key = _default_key, is_string = False):

    message = _dec_aes(cph_text,key)

    return message.decode('ascii') if is_string else message
    

if __name__ == "__main__":
    print("mycrypt")    

    print(confirmation_message)

    text = "ala bala portocala cine mi-a furat banana sa mi-o dea inapoi daca nu e vai"
    enc_text = enc_cfb(text,_default_key,_default_iv)
    dec_text = dec_cfb(enc_text,_default_key,_default_iv)

    print(enc_text)
    print(dec_text)

    text2 = "abcdef"
    text3 = bytes([12,13,15,17,19,100,105,208,109,10,0,1,2,8,7,6])

    tx2c = enc_aes(text2)
    tx3c = enc_aes(text3)
    print("tx2c",tx2c)
    print("tx3c",tx3c)

    tx2d = dec_aes(tx2c)
    tx3d = dec_aes(tx3c)
    print(tx2d)
    print(tx3d)
