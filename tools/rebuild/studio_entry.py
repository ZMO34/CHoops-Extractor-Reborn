"""Standalone entrypoint includes the same public CLI as the source package."""
import sys
from choops_py.studio import main
from choops_py.cli import main as cli_main
if sys.argv[1:2]==['--cli']:
    raise SystemExit(cli_main(sys.argv[2:]))
raise SystemExit(main())
