"""Evidence-based archive categories and roster references, without invented names."""
import re
from collections import defaultdict
from .hash_names import hash_name
from ..roster.uniforms import asset_name


def category(entry):
    if entry['hash']==4175903001:return 'Shoes'
    name=(entry.get('name') or '').lower()
    hint=(entry.get('name_hint') or '').lower()
    if re.match(r'shoe_',name):return 'Shoes'
    if re.match(r'(?:sel)?u[haxyz]\d+',name):return 'Uniforms'
    if name.startswith('cloth'):return 'Cloth geometry'
    if re.fullmatch(r's\d+n?\.(iff|cdf|bin)',name):return 'Stadiums'
    if 'logo' in name or 'logo' in hint:return 'Logos'
    if name.startswith(('p','h')) and re.fullmatch(r'[ph]\d+\.(iff|cdf|bin)',name):return 'Players'
    if any(word in name for word in ('music','jukebox','chant','sfx')):return 'Audio'
    if any(word in name for word in ('frontend','teamselect','loading','legalpage')):return 'Menus'
    if 'roster' in name:return 'Rosters'
    if name in ('crowd.iff', 'gumbel.iff', 'kellogg.iff', 'gameintro_cameras.iff', 'playercreate.iff'):
        return 'Animation banks'
    if 'singlemocap' in hint:return 'Animation banks'
    return 'Other / unresolved'


def catalog(entries,model=None):
    references=defaultdict(set)
    if model:
        for school in model.rows.get('teams',[]):
            name=school['school_name']
            arena_index=school.get('arena_index')
            arenas=model.rows.get('arenas',[])
            if isinstance(arena_index,int) and 0<=arena_index<len(arenas):
                code=arenas[arena_index].get('arena_code')
                if code and str(code).isdigit():
                    for file in (f's{code}.iff',f's{code}n.iff'):
                        references[hash_name(file)].add(name+' — stadium')
            for role in ('home_shoe_texture','away_shoe_texture'):
                if school.get(role):references[hash_name(school[role])].add(name+' — '+role.replace('_',' '))
            references[hash_name('teamselectlogo.iff')].add(name+f" — menu logo ID {school['menu_logo_id']} (bank)")
            for uniform in model.rows.get('uniforms',[]):
                if uniform['team_asset_id']!=school['uniform_owner_id']:continue
                try:references[hash_name(asset_name(uniform))].add(name+' — uniform')
                except ValueError:continue
    rows=[]
    for entry in entries:
        row=dict(entry,category=category(entry),references='; '.join(sorted(references[entry['hash']])))
        if entry['hash']==4175903001 and not row.get('name') and not row.get('name_hint'):row['name_hint']='SCNE shoe mesh: hi_shoe1 (verified internal record)'
        rows.append(row)
    return rows


def record_references(archive_name, records, model):
    """Confirmed school menu logo IDs resolve to exact logoNNN bank records."""
    owners=defaultdict(set)
    if model and archive_name.lower()=='teamselectlogo.iff':
        for school in model.rows.get('teams',[]):
            if school.get('menu_logo_id') is not None:
                owners[f"logo{school['menu_logo_id']:03d}"].add(school['school_name'])
        from ..roster.conference_assets import logo_record
        for conference in model.rows.get('conferences', []):
            if 0 <= conference['index'] < 39:
                owners[logo_record(conference['index'])].add(conference['conference_name'] or f"Conference #{conference['index']}")
    return [{**record,'references':'; '.join(sorted(owners[record.get('name','')]))} for record in records]
