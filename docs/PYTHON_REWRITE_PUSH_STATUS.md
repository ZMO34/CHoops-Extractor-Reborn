# Python Rewrite Push Status

This branch was created from the current GitHub `master` after first preserving that state on the remote `legacy` branch.

The full Python-first rewrite has been built and packaged in ChatGPT as:

```text
CHoops-Extractor-python-main-gui-expanded.zip
```

The GitHub connector available in this chat can create branches and commit individual UTF-8 files, but it cannot perform a normal bulk `git push` of the local repository archive. The local packaged repo contains the Python-first implementation with git history:

```text
main   = Python-first rewrite with expanded GUI
legacy = preserved JavaScript/Node tool
```

Expected local push commands from the unpacked archive:

```bash
git remote set-url origin https://github.com/ZMO34/CHoops-Extractor-Reborn.git
git push origin legacy:legacy
git push origin main:python-main --force-with-lease
```

After review, make `python-main` the default branch or merge it into `master`.

Python rewrite summary:

- Tkinter GUI command center
- raw-preserving rip/cache tools
- standard IFF inspection/validation/round-trip foundation
- CDF-backed IFF/CDF inspection/validation/round-trip foundation
- safe override import and build-copy workflow
- TXTR inspection and uniform atlas research commands
- roster decode/compare foundation
- SCNE/floor inspection foundation
- audio payload preservation tools
- 26 passing tests in the packaged repo
