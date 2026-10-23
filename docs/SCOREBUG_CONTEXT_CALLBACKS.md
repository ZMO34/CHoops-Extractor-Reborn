# Installed native scorebug context provider

The owner requested installation after the context investigation. A separate local
v5 experimental package now contains an installed PowerPC provider for the far-
right `home_ABL` text binding. The public files contain newly authored assembly,
its address/string profile, synthetic instruction tests and documentation. They
contain no game binaries, game asset bytes or public executable-patching command.

## Selection and ownership

The callback recomputes context on each native update; it keeps no cached Legacy
team, calendar date or previous message. Its precedence is:

1. Native timeout caller text through 0x719E98 when the same native timeout state
   and suppression gates used by that routine permit it.
2. March / Madness for a verified scheduled game in brackets 0x5A..0x5F.
3. NIT / Tournament for a verified game in brackets 0x55..0x59.
4. The current conference abbreviation / Tournament when the verified game's
   bracket matches that conference's native tournament selector.
5. Current conference abbreviation / Matchup for both active teams in the same
   validated conference, with no identified tournament bracket.
6. College Hoops / Reborn when context is missing, ambiguous or unsupported.

The mode-4 route and the mode-7/8 +0xD0==2 route fall back rather than claim a
college conference context. Missing teams, missing roster conference, differing
conferences, an empty or longer-than-24-code-unit abbreviation and control
characters also fall back. Other tournament groups do not get an invented name.

The installed tournament route supersedes the earlier speculative calendar-day
route. Native 0x57F49C obtains the active home team's scheduled-game reference;
the provider reads its nonzero game key. 0x5AAB80 resolves that exact key to its
20-byte native game record. Both U16 participant fields (+4/+6), normalized with
0x4A3174, must resolve to exactly the active home/away pointers, in either order.
Only then does 0x58BC60 search its 97 bracket groups, each containing up to 32 game
keys, for this game. No postseason decision is made solely from month/date or
from the selected Legacy school. If runtime copies do not satisfy exact pointer
identity, the label deliberately falls back instead of weakening that guard.

Conference membership comes from each active team's +0x18 pointer, as used by
0x75F9B0. Both pointers must agree. The conference +0x0C index must resolve back
to the same pointer through 0x4A1FF4; its +0x1A tournament selector and +4
abbreviation then supply the context. Realigned current membership is used;
there are no hardcoded SEC/ACC school lists or logo-ID assumptions. A custom
conference sort/index arrangement that fails this roundtrip also falls back.

## String lifetime and native rendering

The existing `home_ABL` update-provider registration at 0x4EF760 branches to a
small initialization stub. That stores a new PPC64 function descriptor for the
provider. The descriptor uses the existing HUD TOC. The registration name, draw
callback, other providers and every event queue remain intact.

The corresponding SCNE style clears **only** the 0x10 forced-literal bit. Without
this edit the old branding literal could override the newly provided string.
The font, shadow, center alignment, max-width fitting and geometry remain native.
The callback doesn't add a new draw pass or new text/bone identities.

Native string construction at 0x1E2634 creates a wrapper borrowing a UTF-16
character pointer. Copy at 0x1E0EA4 retains its node through 0x1E25C8; it does not
deep-copy the borrowed character buffer. Therefore a stack-built conference
label must not escape through that route.

The installed provider instead uses persistent source strings: the loaded roster
abbreviation and a constant suffix in the mapped executable extension. It wraps
both as temporary native strings, applies the existing English two-string newline
format **0x36A37FBF**, with native string formatter descriptor **0xA18CD8**, and
releases the temporary wrappers. That descriptor resolves to 0x1E2C64; its
0x1E29E0 route retains the underlying nodes before linking the format graph.
No returned character pointer refers to the provider's stack. Static fallback,
NCAA and NIT text also refer to mapped constant storage. The existing English
archive already has the correct placeholder/newline tokens; no localization
extension or parameter-template rewrite is needed.

Provider source and profile:
[PowerPC source](examples/scorebug-context-provider.ppc),
[address/string profile](examples/scorebug-context-provider.json).
The source is an experiment bound to the observed executable family. The profile
is documentation and test input, not a supported arbitrary-ELF installer.

## Validation

The assembled callback is 860 bytes. A strict-memory synthetic instruction
harness covers 34 paths plus nine sequential label changes, including both
participant orders, wrong ownership, NCAA/NIT boundaries, conference tournament,
missing context, ABL gates, timeout caller/suppression, long/empty names and stale
prior output. It checks stack, TOC, LR, nonvolatile registers, CR and balanced
temporary wrappers. It rejects a character source in the callback's stack.
External native functions are stubbed; this does not execute the native formatter
or renderer. Original disassembly separately establishes the string-lifetime and
key/participant lookup contracts described above.

`python -m pytest tests/test_scorebug_context_provider.py tests/test_scorebug_layout.py tests/test_scorebug_text.py tests/test_scorebug_runtime.py -q -o addopts= --basetemp output/temp/context-callback-focused`:
**64 passed**. The callback harness uses optional Capstone/Keystone packages and
skips when those research dependencies are absent. They are not added to the
normal editor runtime. Ruff E/F/I passes for the new test file.

Private package verification checks the exact registration instruction before
changing it, new code/data only in zero file padding, the first load extent
without crossing the next load segment, aligned function descriptor, all internal
branch targets, unchanged ELF length and all non-allowlisted bytes, and SELF
payload roundtrip. All original game inputs and previous published candidates
remain unchanged.

Only one gamedata record changes from geometry v2: the four-byte home_ABL flags
property. All 261 other records, every vertex/index buffer, meter draw and English
archive remain identical. Two IFFs stage and preflight without a JB build.
The v2 geometry suppression remains included.

## Limits

The callbacks are installed in the separate matching local executable/IFF set;
they have not been runtime-certified. Timeout strings can shrink to fit the
existing right panel. Schedule ownership may be unavailable in some modes, where
branding is the intended fallback. Native allocation/frame cost, all pause/replay
transitions, console debug-SELF acceptance and in-game appearance remain untested.

This update does not add missing `text1/text2/text3/text3_b` statistics/injury
scene bindings, change popup timing/priorities or certify every reported line is
fixed. Original sixth-man/event visibility behavior is retained. No emulator or
gameplay test was run; no automatic/testing JB was built.
