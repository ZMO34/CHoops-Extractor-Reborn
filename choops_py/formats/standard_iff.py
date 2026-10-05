from .binary import Binary
from ..archive.manifests import safe_name, write_bytes, report
MAGIC=0xFF3BEF94
TYPES={0x5C369069:"TXTR",0xE26C9B5D:"SCNE",0x86A1AC9E:"LAYT",0xC61649B2:"ROST",0x1AEDDA1F:"AUDO",0x68B693B2:"NAME",0xA7701F00:"CDAN"}
def names(data,offset,count):
    b=Binary(data)
    if offset+8>len(data) or b.u32(offset)!=0xAA171516: return []
    body=Binary(b.slice(offset+8,b.u32(offset+4,"<")))
    n=body.u32(0,"<"); table=body.relative(4,"<"); result=[]
    for i in range(min(n,count)):
        entry=body.relative(table+i*4,"<")
        result.append((body.utf16(body.relative(entry,"<")),body.utf16(body.relative(entry+4,"<"))))
    return result
def decompress(raw,expected):
    b=Binary(raw)
    if len(raw)<4 or b.u32(0)!=0x0E4837C3:
        if len(raw)!=expected: raise ValueError("Uncompressed block size mismatch")
        return raw
    if b.u32(4)!=expected or b.u32(8)!=len(raw): raise ValueError("H7A wrapper length mismatch")
    shift=b.u32(16)
    if not 1<=shift<=16 or expected>512*1024*1024: raise ValueError("Unsupported H7A allocation/shift")
    out=bytearray(); pos=20
    while len(out)<expected:
        descriptor=b.slice(pos,1)[0];pos+=1
        for bit in range(8):
            if len(out)==expected: break
            if descriptor & (1<<bit):
                token=b.u16(pos);pos+=2;distance=token&((1<<shift)-1);length=(token>>shift)+3
                if not distance or distance>len(out): raise ValueError("Invalid H7A backreference")
                for _ in range(min(length,expected-len(out))): out.append(out[-distance])
            else: out.extend(b.slice(pos,1));pos+=1
    return bytes(out)
class StandardIFF:
    def __init__(self,data):
        self.raw=data;b=Binary(data)
        if b.u32(0)!=MAGIC: raise ValueError("Not a standard PS3 IFF")
        self.header_size=b.u32(4);self.file_length=b.u32(8);bc=b.u32(16);fc=b.u32(24)
        if not 32<=self.header_size<=self.file_length<=len(data): raise ValueError("Invalid IFF boundaries")
        b.slice(32,bc*32+fc*4);self.blocks=[];self.records=[]
        for i in range(bc):
            off=32+i*32;values=[b.u32(off+j*4) for j in range(8)]
            start,size=values[5:7]
            if start<self.header_size or start+size>self.file_length: raise ValueError("Invalid block range")
            self.blocks.append(dict(index=i,fields=values,start=start,size=size,logical_size=values[3],compressed=data[start:start+4]==bytes.fromhex('0e4837c3')))
        ns=names(data,self.file_length,fc)
        for i in range(fc):
            field=32+bc*32+i*4;off=b.relative(field);n=b.u32(off+8)
            if off<32+bc*32+fc*4 or off+12+n*4>self.header_size or n>bc: raise ValueError("Invalid file record")
            offsets=[b.u32(off+12+j*4) for j in range(n)]
            for j,v in enumerate(offsets):
                if v!=0xffffffff and v>self.blocks[j]['logical_size']: raise ValueError("Subfile offset out of bounds")
            name,typ=ns[i] if i<len(ns) else (str(i),TYPES.get(b.u32(off+4),'UNKNOWN'))
            self.records.append(dict(index=i,name=name,type=typ,id=b.u32(off),type_hash=b.u32(off+4),offsets=offsets))
    def manifest(self): return dict(family='standard-iff',header_size=self.header_size,file_length=self.file_length,blocks=self.blocks,records=self.records)
    def spans(self,record):
        for j,start in enumerate(record['offsets']):
            if start==0xffffffff: continue
            offsets=[r['offsets'][j] for r in self.records if len(r['offsets'])>j and r['offsets'][j]!=0xffffffff and r['offsets'][j]>start]
            end=min(offsets,default=self.blocks[j]['logical_size'])
            yield j,start,end
    def dump(self,output,types=()):
        decoded={};items=[]
        for r in self.records:
            if types and r['type'] not in types: continue
            for j,start,end in self.spans(r):
                block=self.blocks[j]
                if j not in decoded: decoded[j]=decompress(self.raw[block['start']:block['start']+block['size']],block['logical_size'])
                name=f"{r['index']:04d}_{safe_name(r['name'])}.{r['type'].lower()}.block{j}"
                write_bytes(output/name,decoded[j][start:end]);items.append(name)
        report(output/'manifest.json',self.manifest());return items
    def replace(self,selector,payload):
        matches=[r for r in self.records if str(r['index'])==selector or r['name']==selector]
        if len(matches)!=1: raise ValueError("Subfile selector must match exactly one record")
        spans=list(self.spans(matches[0]))
        if len(spans)!=1: raise ValueError("Multi-block subfiles require a validated block-aware writer")
        j,start,end=spans[0];block=self.blocks[j]
        for other in self.records:
            if other is matches[0]: continue
            for bj,bs,be in self.spans(other):
                if bj==j and start<be and bs<end: raise ValueError("Subfile shares a preserved byte range")
        if block['compressed']: raise ValueError("Compressed subfile replacement blocked: no size-preserving compressor")
        if len(payload)!=end-start: raise ValueError("Replacement must be same size")
        out=bytearray(self.raw);off=block['start']+start;out[off:off+len(payload)]=payload
        StandardIFF(bytes(out));return bytes(out)
