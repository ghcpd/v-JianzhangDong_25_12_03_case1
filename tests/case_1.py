from app.data_loader import load_csv, normalize_column

# Create a temp CSV (no external files needed) using stdlib csv
import csv

with open("tmp.csv", "w", newline="", encoding="utf-8") as fh:
	writer = csv.writer(fh)
	writer.writerow(["value"])
	for v in [1, 2, 3, 4, 5]:
		writer.writerow([v])

data = load_csv("tmp.csv")
norm = normalize_column(data, "value")

print("Normalization OK:", norm[:3])
