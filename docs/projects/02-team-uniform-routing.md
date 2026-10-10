# Team and uniform routing

The ROST header at +0x70 describes an eight-byte uniform table. The engine's uniform lookup counts records belonging to a team, then selects the requested matching record in table order. It compares the record's owner with the team's asset identity.

| Uniform field | Storage | Evidence |
|---|---|---|
| Team owner | First word, bits 22–31 | Runtime uniform lookup and getter |
| Uniform asset selector | First word, bits 12–21 | Packed getter/setter |
| Variant code | First word, bits 8–10 | Packed getter; complete filename-bank meaning still under investigation |
| Jersey shape | Second word, bits 27–29 | Packed getter/setter and cloth filename dispatch table |

Shape dispatch: 0 U, 1 V, 2 V triangle, 3 triangle, 4 wishbone. The game's dispatch falls back to U for out-of-range codes. The Uniforms roster tab exposes the table, allows known shapes and existing asset selectors, and preserves all other bits. Save a roster copy and stage it normally. Offline structural validation does not establish gameplay consumption of an edited shape.

Filename prefixes `uh`, `ua` and `ux` organize the current archive's home, away and alternate artwork in the preview list. Complete runtime bank selection, unlocking and extra alternate behavior remain under investigation. The preview selector changes only preview images.
