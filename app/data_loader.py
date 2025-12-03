import csv
import numpy as np
from pathlib import Path


def load_csv(path: str):
    """Load CSV using the csv module and return as list of dicts with column order."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [row for row in reader]
    if not rows:
        raise ValueError("CSV cannot be empty")
    columns = reader.fieldnames or []
    return {"columns": columns, "rows": rows}


def load_config(path: str) -> dict:
    """Load YAML config file. Import PyYAML only when this function is called."""
    try:
        import yaml
    except Exception as ex:
        raise RuntimeError("PyYAML is not installed; install pyyaml to use load_config") from ex
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_column(data, col: str) -> np.ndarray:
    """Normalize a column from the data returned by load_csv.

    data: dictionary {"columns": [...], "rows": [dict, ...]}
    """
    columns = data.get("columns", [])
    if col not in columns:
        raise KeyError(f"Column {col} not found in data.")
    x = np.array([float(r[col]) for r in data["rows"]], dtype=float)
    return (x - np.mean(x)) / np.std(x)
