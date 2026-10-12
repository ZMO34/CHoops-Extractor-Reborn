# Experimental audio command-line workflow

Audio GUI controls are not present yet. These commands use the Python backend;
title/artist changes and EBOOT writes are unavailable. They build no JB folder
and never launch RPCS3.

From a checkout or the release's **audio-workspace** directory:

```powershell
python tools/dev/setup.py --audio-encoder
.\.venv\Scripts\python.exe -m choops_py.cli --help
```

Python 3.12 x64 and Git must already be available. Setup installs the Python
prerequisites, fetches pinned LGPL AtracDEnc sources into ignored .private/vendor,
and builds the helper with Zig. Decoder-only exports need PyAV, not the encoder.

```powershell
.\.venv\Scripts\python.exe -m choops_py.cli audio-catalog "YOUR_JB_ROOT" output/reports/audio.json
.\.venv\Scripts\python.exe -m choops_py.cli export-soundtrack "YOUR_JB_ROOT" output/rips/licensed
.\.venv\Scripts\python.exe -m choops_py.cli export-soundtrack "YOUR_JB_ROOT" output/rips/fight_songs --category fight-songs
.\.venv\Scripts\python.exe -m choops_py.cli replace-song "YOUR_JB_ROOT" cribmusic 0 "MY_EDIT.wav" output/audio/song_edit
.\.venv\Scripts\python.exe -m choops_py.cli import-audio-folder "YOUR_JB_ROOT" output/rips/licensed output/audio/batch_edit
.\.venv\Scripts\python.exe -m choops_py.cli export-audo "RIPPED_SOUND.audo.block0" output/audio/sound.wav
.\.venv\Scripts\python.exe -m choops_py.cli replace-audo "RIPPED_SOUND.audo" "MY_EDIT.wav" output/audio/replaced.audo
.\.venv\Scripts\python.exe -m choops_py.cli export-jukebox-art "YOUR_JB_ROOT" 000 output/audio/cover.dds
.\.venv\Scripts\python.exe -m choops_py.cli replace-jukebox-art "YOUR_JB_ROOT" 000 "MY_COVER.png" output/audio/jukebox.iff
```

Choose a new output name/folder each time. Export defaults to 23 licensed tracks;
fight songs are a separate batch. WAVs are PCM16 at the source bank rate/channels.
Import resamples and ATRAC3-encodes compatible WAVs. Maximum duration is 30 minutes.
Manifests hold bank/index and original WAV checksums; unchanged files are skipped.
Changing manifest title/artist text does not rename game songs. No changed WAVs
means no replacement folder is created.

Song replacement outputs global.iff and affected .bin files, preserving other
streams and ordering. Stage that folder and manually build your JB when ready.
Standalone AUDO output is a raw/wrapped asset copy, not a complete replacement of
its parent IFF/CDF. Do not stage it as a complete archive. Unknown looped AUDO
replacement and general CDF audio growth remain blocked/pending.

Cover replacement outputs complete jukebox.iff for manual staging. Record 021 is
shared by all fight songs; 002 by both Strange Fruit tracks. DDS or Pillow-readable
artwork such as PNG is normalized to the selected JB's base texture layout.

The v1.08 development bundle includes the established standalone Windows GUI
and a Python **audio-workspace**. Audio commands run from that workspace, not the
GUI executable. PyAV/encoder build dependencies are installed by setup, not
distributed as native codec DLLs. Self-contained audio GUI packaging is pending.
See AUDIO_RESEARCH.md for evidence and limits.
