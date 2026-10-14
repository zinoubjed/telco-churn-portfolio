"""Execute the portfolio notebook with the current Python environment."""
from pathlib import Path
import asyncio
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / ".runtime"
runtime.mkdir(exist_ok=True)
tempfile.tempdir = str(runtime)
os.environ["IPYTHONDIR"] = str(runtime / "ipython")
os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime)
os.environ["MPLCONFIGDIR"] = str(runtime / "matplotlib")
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

path = ROOT / "notebooks/telco_churn.ipynb"
nb = nbformat.read(path, as_version=4)
km = KernelManager(kernel_name="python3")
# Avoid accidentally selecting a different, globally registered environment.
km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
client = NotebookClient(nb, km=km, timeout=180,
                        resources={"metadata": {"path": str(ROOT)}})
client.execute()
nbformat.validate(nb)
if any(output.output_type == "error" for cell in nb.cells if cell.cell_type == "code"
       for output in cell.outputs):
    raise RuntimeError("Notebook contains an execution error.")
nbformat.write(nb, path)
print("Notebook executed completely with", sys.executable)
