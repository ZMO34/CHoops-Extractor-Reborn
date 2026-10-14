"""Read-only preview overlay of source-bound staged complete archives."""
import json
from pathlib import Path
from ..archive.manifests import digest
from ..archive.hash_names import replacement_hash


class PreviewArchive:
    def __init__(self,archive,mod):
        self.base=archive;self.path=archive.path;self.entries=[dict(e) for e in archive.entries]
        self.replacements={};self.conditions={}
        root=Path(mod).resolve();manifest=root/'overrides.json'
        if not manifest.is_file():return
        conditions=root/'source_preconditions.json'
        if not conditions.is_file():raise ValueError('Staged previews require source preconditions; stage this mod again')
        self.conditions={e['index']:e for e in json.loads(conditions.read_text(encoding='utf8'))['entries']}
        for row in json.loads(manifest.read_text(encoding='utf8')):
            if row.get('subfile') is not None or row.get('kind')!='archive':raise ValueError('Stage complete archives before previewing this mod')
            matches=[e for e in self.entries if e['hash']==replacement_hash(row['archive'])]
            if len(matches)!=1:raise ValueError('Staged preview archive identity is ambiguous')
            entry=matches[0];target=(root/row['path']).resolve()
            if not target.is_relative_to(root) or not target.is_file():raise ValueError('Staged preview path is invalid')
            if entry['index'] in self.replacements:raise ValueError('Duplicate staged archive')
            self.replacements[entry['index']]=(target,row['sha256'])
            entry['size']=target.stat().st_size

    def read(self,entry):
        index=entry['index']
        if index not in self.replacements:return self.base.read(self.base.entries[index])
        expected=self.conditions.get(index)
        original=self.base.entries[index]
        if not expected or expected['hash']!=original['hash'] or expected['sha256']!=digest(self.base.read(original)):
            raise ValueError('Staged previews belong to another or changed JB source')
        path,checksum=self.replacements[index];data=path.read_bytes()
        if digest(data)!=checksum:raise ValueError('Staged preview asset checksum changed; restage overrides')
        return data

    def chunks(self,entry):
        if entry['index'] in self.replacements:
            data=self.read(entry)
            for offset in range(0,len(data),1024*1024):yield data[offset:offset+1024*1024]
        else:yield from self.base.chunks(self.base.entries[entry['index']])
