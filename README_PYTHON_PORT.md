# Python port

The current tree is Python-first. Only the two original texture converter executables are bundled from the old tool. No JavaScript source, Node packages or desktop editor builds are required.

Related workflows share one implementation: archive readers/cache/ripper, a preservation-first IFF writer, package parsing, one texture container pipeline, one roster model, and one transactional JB builder. The CLI and Tkinter GUI consume the same command registry and backends. See docs/OLD_TOOL_ARCHITECTURE_AUDIT.md for parity and remaining restrictions.
