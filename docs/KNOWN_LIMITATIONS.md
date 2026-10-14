# Current limitations

The scale branch remains incomplete semantic reverse engineering. School and
conference engine text caps, arena shader channels, number geometry/colour and
independent secondary positions remain unresolved. CSV/comparison use supported
writers and exclude ambiguous references. Text growth is structurally tested;
game runtime remains unverified. See ROSTER_SCALE_AND_PREVIEWS.md.

v1.11 transfers/brand propagation reject shared or inconsistent ownership and full
18-player destinations. Whole-table older 16-slot JSON exports need refreshing.
Static jersey preview has no runtime cloth, skinning, body or name/number overlays.
No automatic Legacy eligibility/scholarship enforcement or gameplay guarantee.

v1.10 removes D1 conversion and new alternate/independent-asset actions from the
public editor/CLI. Single position and Scholarship/Walk-on are confirmed; secondary
position is unproven and not exposed. See PLAYER_QOL_RESEARCH.md for evidence.

Updated 2026-10-11. CURRENT_STATUS.md and TEST_REPORT.md are the living evidence.

- Python/Qt checks do not establish game behavior. Agents never open RPCS3 or
  create testing JB folders; users build/test their own copies.
- DDS/GTF conversion is built in. Unknown TXTR layouts, DX10 and true volumes
  remain unsupported. Unused stored depth on declared 2D/cubes is tolerated.
- Validated standard IFF/TXTR/SCNE growth and archive relocation exist. Unknown
  pointers and aliases remain blocked; general CDF virtual/physical growth is
  unresolved. Do not apply obsolete same-size rules to every supported writer.
- Six team palette words and full arena shader masks remain unresolved. Preview
  lighting, cloth/skinning, jersey glyphs and material effects are simplified.
- Roster names generally need equal encoded length/unshared storage. Encrypted
  saves need external decryption. Community wrappers are preserved; invalid
  pointers/new corruption remain fatal. Unchanged bad name characters are warnings.
- Alternate/linking operations and optional D1 conversion exist, but complete
  game/profile unlock behavior and independent decloned IDs need validation.
- Shoe editing uses verified brand/style/color ranges and artwork IDs; commercial
  style names and the exact special-family manufacturer caption are unresolved.
- 4096 is a court texture dimension ceiling, not a tested safe GPU allocation.
  Floor template preparation disables only extra floor draws, preserving arena.
- Audio has an experimental Python backend/CLI and a shared-backend Qt workspace
  for Licensed Music, Fight Songs, WAV workflows and mapped cover art. Title/artist
  editing remains unavailable because archive-only routing is unproven; EBOOT
  writes are prohibited. Unknown AUDO loops are blocked and CDF audio growth is
  unsupported. The LGPL helper package has passed Windows CI on PR #6's current
  head; it remains an unreleased branch until review and publication.
- Outputs are constrained to output/. Game assets, exported music/art, private
  paths, logs, fixtures and EBOOT are not supplied publicly.
