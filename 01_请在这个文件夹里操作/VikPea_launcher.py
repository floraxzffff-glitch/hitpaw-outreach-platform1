import runpy
from pathlib import Path


base = Path(__file__).resolve().parent
target = base / "VikPea_工作台.py"

if not target.exists():
    raise FileNotFoundError(f"Missing file: {target}")

runpy.run_path(str(target), run_name="__main__")
