from choops_py.gui import COMMAND_REGISTRY,PANELS
from choops_py.cli import SPECS
def test_registry():assert COMMAND_REGISTRY==SPECS;assert len(PANELS)==22
