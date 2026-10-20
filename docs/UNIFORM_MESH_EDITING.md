# Experimental editable uniforms and modern fit

Models / Courts now has **Uniform meshes…** with export-all, experimental modern
fit and collection reimport actions. Export uses the global **Preview source**
selection, including source-bound complete overrides. Outputs are separate
collections under `output/uniform-models/`; imports create a new
`output/uniform-imports/` folder. Sources and existing outputs are never replaced.

## Coverage and preset

Read-only inventory of the supplied College Hoops 2K8 PS3 source found:

- Five necklines: U, V, V triangle, triangle and wishbone.
- Thin, regular and fat builds for each neckline, plus three shorts builds.
- 21 IFF containers / 33 SCNE–Clth record pairs. This includes the aggregate
  containers and the individual build containers, so both existing resource
  routes are represented. These are 18 distinct garment/build combinations;
  the duplicated routes are not additional jersey styles or new team alternates.

`modern-fit-1` raises the shorts hem by 20% of that mesh's original vertical
extent, fading to zero displacement at 65% of its height so the waist and upper
hips remain fixed. The deformation is monotonic in height; no rows are cut off.
Jersey torso X/Z are reduced by up to 7%, with smooth fades at the bottom and
above the mid torso. The upper 28% stays fixed, preserving the collar/upper
armhole region. This changes existing shared meshes for all schools using them;
it does not change team artwork, body/build selectors, roster records or EBOOT.

## Editing and reimport

The collection contains `originals/` IFF copies, editable `models/` OBJ cages and
source-bound manifests. Modern-fit collections also include untouched
`original-models/` OBJ cages and ready experimental replacements in `overrides/`.
Select **only `overrides/`** in Explorer to prepare the edited game assets. The
collection root includes originals and must not be used as an overrides folder.
Do not mix complete cloth IFF replacements with a different cloth geometry mod.

The OBJ preserves original vertex indices, per-vertex UVs and expanded strip
triangles. Coordinates are unchanged native units, Y up. In a DCC editor, preserve
vertex order and axis conversion on export. Do an untouched roundtrip before
editing: DCC versions may reorder faces or vertices. No welding, subdivision,
triangulation, decimation, vertex deletion or UV editing is supported. Move
coincident seam duplicates together. OBJ normals are ignored; native packed
normal/tangent attributes remain byte-exact. No external DCC application has
been certified by this change.

Choose **Reimport edited uniform models…**, selecting the collection root.
The importer checks the original IFF hash, manifest identities, ordered triangles,
vertex count, UV identity, sewn particle agreement, finite coordinates, a maximum
20-unit displacement and collapsed/flipped triangles. It updates only XYZ in
SCNE vertices and their exact matching Clth rest particles. Unknown attributes,
UVs, skinning-associated stream bytes, indices, constraints and helper particles
are retained. Unsupported declarations and ambiguous matches fail explicitly.
Collection operations are cancellable; a failed/cancelled collection may contain
completed files but has no final success report. Choose a new empty destination
for retry. Each individual IFF is fully validated before writing.

CLI equivalents, always writing under project `output/`:

```powershell
python -m choops_py.cli export-uniform-models SOURCE_JB output/uniform-export
python -m choops_py.cli modern-fit-uniforms SOURCE_JB output/modern-fit
python -m choops_py.cli import-uniform-models output/modern-fit output/edited-cloth
python -m choops_py.cli export-uniform-iff cloth_u.iff output/u-models
python -m choops_py.cli import-uniform-iff cloth_u.iff output/u-models output/new-cloth_u.iff
```

## Confirmed binary evidence and limits

The observed embedded SCNE has one mesh/instance, three streams with strides
4/24/4 and six exact declarations. Float32 big-endian XYZ occupies the first 12
bytes of each 24-byte vertex in stream 1. Stream 0 holds signed-normalized UVs;
stream 2 and the remaining vertex bytes are preserved. Existing triangle-strip
indices and draw data stay unchanged. No general-purpose SCNE writer is enabled.

In matching Clth records, the first big-endian uint16 is the rest-particle byte
extent. Absolute offsets at `0xc0` and `0xc8` bound that table; their difference
equals this extent. Each particle is 16 bytes: matching float32 XYZ plus 1.0.
All 33 supplied graphic records have unambiguous exact matches to this bounded
table. Several rendered seam vertices share a particle. Unmatched helper
particles and zero-initialized workspace are retained. This mapping establishes
rest-position editing, not the semantics of every Clth byte.

Writers preserve logical record addresses and sizes. Physical compressed sizes
can grow; the existing archive relocation workflow handles a larger replacement.
Every written IFF is reparsed; all changed and unchanged record slices are
compared against the expected bytes. No-op OBJ roundtrips are byte-identical.

**This is experimental.** Packed solver constraints, collision geometry, cloth
simulation and normal/tangent regeneration have not been retargeted. Existing
constraints may pull edited vertices toward their previous fit; animation may
show stretching, body clipping or shading differences. Rest-pose comparisons and
successful import/preflight cannot establish the animated result. Do not call
this a finished cloth-simulation port. No RPCS3/gameplay or real JB build is run.
NBA garment layouts and arbitrary new topology remain unsupported.
