"""
====================================================
HealthAI - Disease Class Distribution Analysis
Author : Vansh Chopra
====================================================

Purpose:
Analyze the number of samples available for each disease
before training ML models.
"""

import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)


def main():

    print("=" * 70)
    print("LOADING DATASET...")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)

    disease_counts = df["diseases"].value_counts()

    print("\n")
    print("=" * 70)
    print("DATASET OVERVIEW")
    print("=" * 70)

    print(f"Total Records   : {len(df):,}")
    print(f"Total Diseases  : {disease_counts.shape[0]}")

    print("\n")
    print("=" * 70)
    print("CLASS STATISTICS")
    print("=" * 70)

    print(f"Largest Class   : {disease_counts.max()}")
    print(f"Smallest Class  : {disease_counts.min()}")
    print(f"Average Samples : {disease_counts.mean():.2f}")
    print(f"Median Samples  : {disease_counts.median()}")

    print("\n")
    print("=" * 70)
    print("DISEASES BELOW DIFFERENT THRESHOLDS")
    print("=" * 70)

    thresholds = [5, 10, 20, 50, 100, 200, 500, 1000]

    for threshold in thresholds:
        count = (disease_counts < threshold).sum()
        print(f"Less than {threshold:>4} samples : {count}")

    print("\n")
    print("=" * 70)
    print("TOP 20 MOST COMMON DISEASES")
    print("=" * 70)

    print(disease_counts.head(20))

    print("\n")
    print("=" * 70)
    print("TOP 20 RAREST DISEASES")
    print("=" * 70)

    print(disease_counts.tail(20))

    print("\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("Describe() Statistics:\n")
    print(disease_counts.describe())


if __name__ == "__main__":
    main()