# Shared test loader for the five independent service modules.
# It exists because service folder names contain hyphens and are not import names.
# Analogy: this is the common key used to open each test room.
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_service(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
