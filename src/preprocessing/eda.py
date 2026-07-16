"""
HealthAI - Exploratory Data Analysis (EDA)
"""

import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)


def main():

    df = pd.read_csv(DATASET_PATH)

    print("=" * 60)
    print("DATASET INFORMATION")
    print("=" * 60)

    print(df.info())

    print("\n")

    print("=" * 60)
    print("DATA TYPES")
    print("=" * 60)

    print(df.dtypes.value_counts())

    print("\n")

    print("=" * 60)
    print("DISEASE FREQUENCY")
    print("=" * 60)

    print(df["diseases"].value_counts().head(20))

    print("\n")

    print("=" * 60)
    print("CLASS DISTRIBUTION")
    print("=" * 60)

    print(f"Total Diseases : {df['diseases'].nunique()}")

    print(f"Smallest Class : {df['diseases'].value_counts().min()}")

    print(f"Largest Class  : {df['diseases'].value_counts().max()}")

    print("\n")

    print("=" * 60)
    print("CHECK DUPLICATES")
    print("=" * 60)

    duplicates = df.duplicated().sum()

    print(f"Duplicate Rows : {duplicates}")


if __name__ == "__main__":
    main()