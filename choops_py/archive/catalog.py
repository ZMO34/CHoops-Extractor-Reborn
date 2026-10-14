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
    return 'Other / unresolved'


def catalog(entries,model=None):
    references=defaultdict(set)
    if model:
        for school in model.rows.get('teams',[]):
            name=school['school_name']
            for file in (f"s{school['asset_id']:03d}.iff",f"s{school['asset_id']:03d}n.iff"):
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
