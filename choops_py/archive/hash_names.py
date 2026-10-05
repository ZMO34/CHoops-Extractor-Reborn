import json,zlib
from pathlib import Path
from functools import lru_cache
def hash_name(name): return zlib.crc32(name.upper().encode('ascii')) & 0xffffffff
def namespace():
    banks='frontend frontend_sync global gamedata gamedataextra loading legalpage loc fonts online playercreate playeditor teamselectlogo arenapics overlaycache jukebox roster_english streetdata studio studio_preview studio_pontiac dornas crowd sfx_inside facegen ababall basket chantcreate chantcreate_drums chantcreate_sounds gameintro gameintro_cameras gameintro_drums gameintro_playerspeech halftimeadjustments legacy powerbar reelmanual weeklyshow tutorial drilldata shrine shrine_trophies statefarm kellogg gumbel Director'.split()
    for name in banks:
        for ext in ('.iff','.cdf','.bin'): yield name+ext
    for prefix in ('ua','uh','ux','selua','seluh','selux','s','m','p','coach','h'):
        for i in range(10000 if prefix=='h' else 1000):
            for ext in ('.iff','.cdf','.bin'):yield f"{prefix}{i:0{4 if prefix=='h' else 3}d}{ext}"
@lru_cache
def lookup():
    result={hash_name(n):n for n in namespace()}
    result.update({int(k):v for k,v in json.loads(Path(__file__).with_name('names.json').read_text()).items()});return result
def resolve(value):
    try:h=int(value,0)
    except ValueError:h=hash_name(value)
    return dict(hash=h,name=lookup().get(h),hex=f'0x{h:08x}')
