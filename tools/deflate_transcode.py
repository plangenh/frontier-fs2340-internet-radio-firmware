"""Lossless token transcode between RFC1951 and Frontier MSB-first DEFLATE.

Only the representation of numeric bitfields and byte bit-order changes.
Huffman trees, symbols, match lengths/distances, and block choices are retained.
Trailing alignment bits are recorded separately for exact no-op round trips.
This module never executes any firmware code.
"""
from dataclasses import dataclass

ORDER = [16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]
LENGTH_EXTRA = [0]*8 + [i//4 for i in range(4,24)] + [0]
DISTANCE_EXTRA = [0,0,0,0] + [i//2-1 for i in range(4,30)]
REVERSE15 = [int(f'{i:015b}'[::-1],2) for i in range(1<<15)]

class Reader:
    def __init__(self, data, mode):
        self.data=data+b'\0\0\0'; self.bits=len(data)*8; self.pos=0; self.mode=mode
    def peek(self,n):
        byte,bit=divmod(self.pos,8)
        raw=self.data[byte:byte+3]
        if self.mode=='lsb': return (int.from_bytes(raw,'little')>>bit)&((1<<n)-1)
        return (int.from_bytes(raw,'big')>>(24-bit-n))&((1<<n)-1)
    def get(self,n):
        if self.pos+n>self.bits: raise ValueError('Truncated numeric field')
        value=self.peek(n);self.pos+=n;return value
    def canonical_peek(self):
        value=self.peek(15)
        return REVERSE15[value] if self.mode=='lsb' else value

class Writer:
    def __init__(self,mode): self.mode=mode;self.data=bytearray();self.value=0;self.used=0;self.total=0
    def put(self,value,n):
        if not 0<=value<(1<<n):raise ValueError('Field overflow')
        self.total+=n
        while n:
            take=min(8-self.used,n)
            if self.mode=='msb':
                bits=(value>>(n-take))&((1<<take)-1)
                self.value|=bits<<(8-self.used-take)
            else:
                bits=value&((1<<take)-1);value>>=take
                self.value|=bits<<self.used
            self.used+=take;n-=take
            if self.used==8:
                self.data.append(self.value);self.value=0;self.used=0
    def code(self,value,n):
        if self.mode=='lsb': value=REVERSE15[value]>>(15-n)
        self.put(value,n)
    def finish(self):
        if self.used:self.data.append(self.value);self.used=0;self.value=0
        return bytes(self.data)

def huffman(lengths):
    lookup=[None]*(1<<15);codes={};code=0
    for size in range(1,16):
        for symbol,length in enumerate(lengths):
            if length!=size:continue
            if code >= (1<<size):raise ValueError('Oversubscribed Huffman tree')
            codes[symbol]=(code,size)
            lookup[code<<(15-size):(code+1)<<(15-size)]=[(symbol,size)]*(1<<(15-size))
            code+=1
        code<<=1
    return lookup,codes

FIXED_LITERAL=huffman([8]*144+[9]*112+[7]*24+[8]*8)
FIXED_DISTANCE=huffman([5]*32)

@dataclass
class Result:
    data:bytes
    consumed_bits:int
    trailing_bits:int
    trailing_value:int
    blocks:list

def transcode(data,source,target,restore_padding=None):
    if source not in ('lsb','msb') or target not in ('lsb','msb'):raise ValueError('Invalid bit mode')
    r=Reader(data,source);w=Writer(target);blocks=[]
    def field(n):
        value=r.get(n);w.put(value,n);return value
    def symbol(tree):
        found=tree[0][r.canonical_peek()]
        if found is None:raise ValueError('Invalid Huffman code')
        value,n=found
        if r.pos+n>r.bits:raise ValueError('Truncated Huffman code')
        r.pos+=n;code,size=tree[1][value];w.code(code,size);return value
    final=0
    while not final:
        final=field(1);kind=field(2)
        blocks.append({'kind':kind,'final':final})
        if kind==0:
            align=(-r.pos)%8
            if align:field(align)
            count=field(16);inverse=field(16)
            if inverse != (count^65535):raise ValueError('Invalid stored-block length complement')
            if r.pos+count*8>r.bits:raise ValueError('Truncated stored block')
            start=r.pos//8
            # Aligned payload bytes are octets, not endian numeric bitfields.
            for byte in r.data[start:start+count]:
                w.put(byte,8)
            r.pos+=count*8
            continue
        if kind==1:lt,dt=FIXED_LITERAL,FIXED_DISTANCE
        elif kind==2:
            nlit=field(5)+257;ndist=field(5)+1;ncl=field(4)+4
            cl=[0]*19
            for i in range(ncl):cl[ORDER[i]]=field(3)
            ct=huffman(cl);lengths=[]
            while len(lengths)<nlit+ndist:
                s=symbol(ct)
                if s<16:lengths.append(s)
                elif s==16:
                    if not lengths:raise ValueError('Repeat without previous code length')
                    lengths += [lengths[-1]]*(field(2)+3)
                elif s==17:lengths += [0]*(field(3)+3)
                else:lengths += [0]*(field(7)+11)
            if len(lengths)!=nlit+ndist:raise ValueError('Code length run overflow')
            lt=huffman(lengths[:nlit]);dt=huffman(lengths[nlit:])
        else:raise ValueError('Reserved DEFLATE block type')
        while True:
            s=symbol(lt)
            if s<256:continue
            if s==256:break
            if s>285:raise ValueError('Reserved length symbol')
            field(LENGTH_EXTRA[s-257])
            d=symbol(dt)
            if d>=30:raise ValueError('Reserved distance symbol')
            field(DISTANCE_EXTRA[d])
    consumed=r.pos
    trailing=r.bits-r.pos
    if trailing>7:raise ValueError('Unexpected bytes after final DEFLATE block')
    pad_value=r.get(trailing) if trailing else 0
    padding=pad_value if restore_padding is None else restore_padding
    if trailing:w.put(padding,trailing)
    return Result(w.finish(),consumed,trailing,pad_value,blocks)
