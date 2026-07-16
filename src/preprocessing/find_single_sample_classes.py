import pandas as pd
from pathlib import Path

DATASET_PATH = Path(
    "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)

df = pd.read_csv(DATASET_PATH)

counts = df["diseases"].value_counts()

single_sample = counts[counts == 1]

print("=" * 60)
print("DISEASES WITH ONLY ONE SAMPLE")
print("=" * 60)

print(single_sample)

print("\n")

print(f"Total Diseases with One Sample : {len(single_sample)}")