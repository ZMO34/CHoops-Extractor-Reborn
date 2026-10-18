"""Bounded PS3 SCNE text bindings and authored font-style properties.

Style entries serialize a 16-byte value followed by type/key/reserved words.
They are not key/value records starting at the type word. Runtime text callbacks
select by text-record name; bone names stay independent of those bindings.
"""
import struct

from ..formats.binary import Binary


FONT = 0xbf045bdb
COLOR = (0x6109ea5a, 0x97de0310, 0x6814845a)
SHADOW = (0x53c67207, 0x661f09b0, 0x7dfc668b)


def _records(header):
    b=Binary(header);count=b.u32(0x4c)
    if count>4096:raise ValueError('SCNE text count exceeds limit')
    table=b.relative(0x50) if count else 0;b.slice(table,count*144)
    records={}
    for i in range(count):
        at=table+i*144;name=b.utf16(b.relative(at+64),'be')
        if name in records:raise ValueError('Ambiguous SCNE text binding')
        style=b.relative(at+80);n=b.u32(style)
        if n>1024:raise ValueError('SCNE text property count exceeds limit')
        b.slice(style+16,n*32);properties={}
        for j in range(n):
            value=style+16+j*32;kind=b.u32(value+16);key=b.u32(value+20)
            if key in properties:raise ValueError('Ambiguous SCNE text property')
            properties[key]=(value,kind)
        records[name]=(at,properties)
    return b,records


def inspect_styles(header):
    b,records=_records(header);rows=[]
    for name,(at,properties) in records.items():
        font=None
        if FONT in properties:
            value,kind=properties[FONT]
            if kind!=3:raise ValueError('Font alias is not a string property')
            font=b.utf16(b.relative(value),'be') if b.u32(value) else ''
        def values(keys):
            return [b.u32(properties[k][0]) if k in properties and properties[k][1]==0 else None for k in keys]
        rows.append(dict(binding=name,font=font,color=values(COLOR),shadow=values(SHADOW)))
    return rows


def edit_styles(parts, changes):
    if len(parts)!=2:raise ValueError('Text styles require a split SCNE')
    b,records=_records(parts[0]);out=bytearray(parts[0]);names=set(records);report=[]
    for name,change in changes.items():
        if name not in records:raise ValueError('Unknown SCNE text binding '+name)
        if set(change)-{'font','binding'}:raise ValueError('Unsupported SCNE text style edit')
        at,properties=records[name]
        for option in ('font','binding'):
            if option not in change:continue
            value=change[option]
            if not isinstance(value,str) or not 1<=len(value)<=128 or any(ord(c)<32 for c in value):raise ValueError('Invalid SCNE text string')
            if option=='font':
                if FONT not in properties or properties[FONT][1]!=3:raise ValueError('Missing string font property')
                field=properties[FONT][0]
                if sum(1 for _,props in records.values() if FONT in props and props[FONT][0]==field)!=1:raise ValueError('Font property is shared by another text record')
            else:
                if value in names and value!=name:raise ValueError('SCNE text binding already exists')
                names.discard(name);names.add(value);field=at+64
            out.extend(bytes((-len(out))%4));target=len(out);out.extend(value.encode('utf-16-be')+bytes(2))
            struct.pack_into('>I',out,field,target-field+1)
        report.append(dict(source=name,**change))
    if len(out)>len(parts[0]):out.extend(bytes((-len(out))%4))
    result=[bytes(out),parts[1]]
    # Reparse, including duplicate-name and property-layout guards.
    inspect_styles(result[0])
    return result,report
