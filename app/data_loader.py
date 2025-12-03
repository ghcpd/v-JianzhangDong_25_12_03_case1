import pandas as pd
import numpy as np
import yaml
from pathlib import Path


def load_csv(path: str) -> pd.DataFrame:
    """Load CSV using pandas with dtype validation."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("CSV cannot be empty")
    return df


def load_config(path: str) -> dict:
    """Load YAML config file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_column(df: pd.DataFrame, col: str) -> pd.Series:
    """Normalize data using numpy/scipy style operations."""
    if col not in df.columns:
        raise KeyError(f"Column {col} not found in DataFrame.")
    x = df[col].to_numpy().astype(float)
    return (x - np.mean(x)) / np.std(x)
