# Arena shader colour and alpha routing

The stadium SCNE contains embedded Cg programs; it is unnecessary to modify EBOOT
or load a complete game to inspect these shader families. The sampled source
programs establish these operations (RGBA multiplication, not guessed school
colours):

| SCNE shader hash | Embedded fragment program | Static preview |
|---|---|---|
| 0x9BF5D4AE | BasePrelitPixelShader | Diffuse × vertex RGBA |
| 0x9BF5D4AE | BaseLightmapPixelShader | Diffuse × vertex RGBA × lightmap RGBA |
| 0xAD91D4DE | GlowSignsPixelShader | RGB = diffuse RGB × vertex RGB × (1 + diffuse alpha); alpha = vertex alpha |
| 0xB3DC3294 | LightFlarePixelShader | RGB = diffuse RGB × vertex RGB; alpha = diffuse alpha |

Float4 COLOR declarations (usage 3) are preserved including HDR values. The
second signed-normalized TEXCOORD channel (usage 9) supplies lightmap coordinates;
base UVs are not reused when the second declaration is present. For the verified
prelit family, sampler 0xAB0D0064 is a lightmap, **not a normal map**. Other shader
families do not acquire that role merely by having the same sampler hash.
Material CPU offsets still select DiffuseColor; confirmed court palette uniforms
continue to follow loaded roster/selected school state. Prelit materials do not
receive a second artificial directional-light multiplier.

Source/selected overrides supply SCNE and all sampled texture records through the
same snapshot. Single archives remain usable. Tests verify declared attribute
bounds and actual rendered lightmap/colour/alpha pixels. Hidden read-only S256
inspection rendered 119 supported parts and 180 lightmapped batches without
shader errors. No RPCS3 or testing JB was involved.

This is static preview support. Reflection/environment lighting, full fake-bump
lighting, screen-space AO, dynamic arena illumination, cloth and every runtime
palette mode are not reproduced. Palette slots 24–26 must not be assigned to
seating from colour similarity: Edit Schools also includes cheerleader colours.
Unproved channel-to-roster links remain unassigned. Complete GPU/game shader
emulation and full roster reverse engineering are not claimed.

## Floor line layers

Preview toggles use existing draw batches routed by the game's court initializer:
slot 18 has materials 2310823066 / 2600458314 (3-point lines); slot 4 has material
2218775043 (outer line). Only floor draws are filtered; arena geometry stays
intact. The controls do not generate lines from floor/apron bounds or change
vertex heights. Camera position is retained when toggling layers.

When a replacement sXXX floor omits these draws, the preview reads its matching
source JB floor and copies only those authored batches, coordinates and UVs.
Copied texture bindings have distinct names; roster palette association still
uses the confirmed material routes. Standalone files without matching source
geometry do not acquire guessed line dimensions. Controls are disabled for absent
routes. Lines baked into one floor texture cannot be erased independently by a
mesh-layer toggle. This is preview-only and changes no SCNE/build data.
