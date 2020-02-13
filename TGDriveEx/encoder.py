import sys
import struct
import math
import secrets
from PIL import Image
from io import BytesIO

class Encoder:

    def __init__(self):
        self.minw = 10
        self.minh = 10
        self.dep = 3
        self.mode = 'RGB'

    @staticmethod
    def bmp_header(data):
        return b"BM" \
            + struct.pack("<l", 14 + 40 + 8 + len(data)) \
            + b"\x00\x00" \
            + b"\x00\x00" \
            + b"\x3e\x00\x00\x00" \
            + b"\x28\x00\x00\x00" \
            + struct.pack("<l", len(data)) \
            + b"\x01\x00\x00\x00" \
            + b"\x01\x00" \
            + b"\x01\x00" \
            + b"\x00\x00\x00\x00" \
            + struct.pack("<l", math.ceil(len(data) / 8)) \
            + b"\x00\x00\x00\x00" \
            + b"\x00\x00\x00\x00" \
            + b"\x00\x00\x00\x00" \
            + b"\x00\x00\x00\x00" \
            + b"\x00\x00\x00\x00\xff\xff\xff\x00"

    def encode_bmp(self, data):
        return Encoder.bmp_header(data) + data

    def decode_bmp(self, data):
        return data[62:]

    @staticmethod
    def png_header(data):
        return b"\x89PNG\x0d\x0a\x1a\x0a" \
            + b"\x00\x00\x00\x0d" \
            + b"IHDR" \
            + b"\x00\x00\x00\x01\x00\x00\x00\x01" \
            + b"\x08\x06\x00\x00\x00" \
            + b"\x1f\x15\xc4\x89" \
            + b"\x00\x00\x00\x0a" \
            + b"IDAT" \
            + b"\x78\x9c\x63\x00\x01\x00\x00\x05\x00\x01" \
            + b"\x0d\x0a\x2d\xb4" \
            + b"\x00\x00\x00\xff\xff\xff\x00"

    def encode_png2(self, data):
        return Encoder.png_header(data) + data

    def decode_png2(self, data):
        return data[62:]

    def encode_png(self, data):
        minw = self.minw
        minh = self.minh
        dep = self.dep
        mode = self.mode
    
        data = struct.pack('<I', len(data)) + data
        
        minsz = minw * minh * dep
        if len(data) < minsz:
            data = data + secrets.token_bytes(minsz - len(data))
        
        rem = len(data) % (minw * dep)
        if rem != 0:
            data = data + secrets.token_bytes(minw * dep - rem)
        hei = len(data) // (minw * dep)
        
        img = Image.frombytes(mode, (minw, hei), data)
        bio = BytesIO()
        img.save(bio, 'png')
        return bio.getvalue()
    
    def decode_png(self, data):
        img = Image.open(BytesIO(data))
        data = img.tobytes()
        
        sz = struct.unpack('<I', data[:4])[0]
        data = data[4:4+sz]
        return data
    
    encode = encode_png
    
    def decode(self, data):
        if data[:4] == b'\x89PNG':
            return self.decode_png(data)
        elif data[:2] == b'BM':
            return self.decode_bmp(data)
        else: raise ValueError('unknown format')
    

def main():
    op = sys.argv[1]
    if op not in ['d', 'e']: return
    fname = sys.argv[2]
    data = open(fname, 'rb').read()
    encoder = Encoder()
    if op == 'e':
        data = encoder.encode(data)
        fname = fname + '.png'
    else:
        data = encoder.decode(data)
        fname = fname + '.data'
    
    with open(fname, 'wb') as f:
        f.write(data)
        
if __name__ == '__main__': main()