"""Refresh dashboard aggregate data from the reproducible report exports."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
test = pd.read_csv(ROOT / "reports/test_metrics.csv")
cv = pd.read_csv(ROOT / "reports/cross_validation.csv")
content = {
    "models": test.merge(cv, on="model").to_dict(orient="records"),
    "capacity": pd.read_csv(ROOT / "reports/capacity.csv").to_dict(orient="records"),
    "thresholds": pd.read_csv(ROOT / "reports/thresholds.csv").to_dict(orient="records"),
}
(ROOT / "dashboard/data.js").write_text(
    "window.telcoData = " + json.dumps(content, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print("Dashboard aggregate data generated.")
