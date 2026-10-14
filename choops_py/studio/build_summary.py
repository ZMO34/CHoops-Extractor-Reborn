"""Succinct GUI-only staging/build diagnostics; no separate display report file."""

def summary(result):
    imports=[item for group in result.get('imports',[]) for item in group.get('dds_imports',[])]
    resized=[item for item in imports if item.get('artwork_resampled')]
    cached=sum(bool(item.get('cache_hit')) for item in imports)
    problems=result.get('unapplied_overrides',[])
    lines=[f"Status: {result.get('status','complete')}",f"Replacements: {result.get('staged',result.get('patched_entries',0))} archives",f"Textures: {sum('width' in item for item in imports)} imported · {cached} cached · {len(resized)} resized",f"Compatibility: {len(problems)} unapplied overrides"]
    groups=result.get('imports',[])
    for group in groups[:50]:
        changed=group.get('dds_imports',[])
        count=sum('width' in item for item in changed)
        resize=sum(bool(item.get('artwork_resampled')) for item in changed)
        lines.append(f"{group['archive']}: {group.get('binary_records',0)} records, {count} textures"+(f", {resize} resized to base layout" if resize else ''))
    if len(groups)>50:lines.append(f"… {len(groups)-50} more replaced archives")
    for item in problems[:30]:lines.append(f"Issue: {item.get('archive','')} / {item.get('selector','')}: {item.get('reason','unapplied')}")
    if len(problems)>30:lines.append(f"… {len(problems)-30} more unapplied overrides")
    if result.get('output'):lines.append('Output: '+str(result['output']))
    return '\n'.join(lines)
