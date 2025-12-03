from app.data_loader import load_csv, normalize_column
import pandas as pd

# Create a temp CSV (no external files needed)
df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
df.to_csv("tmp.csv", index=False)

data = load_csv("tmp.csv")
norm = normalize_column(data, "value")

print("Normalization OK:", norm[:3])
