"""
===========================================
HealthAI - Data Loader
Author : Vansh Chopra
===========================================

Purpose:
Loads the disease prediction dataset and performs
basic validation before preprocessing.
"""

import pandas as pd
from pathlib import Path


class DataLoader:
    """
    Loads the disease dataset.
    """

    def __init__(self):
        self.dataset_path = Path(
            "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
        )

    def load_dataset(self):
        """
        Load dataset from CSV.
        """

        try:
            df = pd.read_csv(self.dataset_path)

            print("\n" + "=" * 60)
            print("✅ DATASET LOADED SUCCESSFULLY")
            print("=" * 60)

            return df

        except FileNotFoundError:
            print("\n❌ Dataset not found.")
            print(f"Expected location:\n{self.dataset_path}")
            return None


def dataset_summary(df):
    """
    Display important dataset information.
    """

    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print(f"Rows               : {df.shape[0]}")
    print(f"Columns            : {df.shape[1]}")
    print(f"Missing Values     : {df.isnull().sum().sum()}")
    print(f"Duplicate Rows     : {df.duplicated().sum()}")

    print("\nTarget Column")
    print("-" * 60)
    print(df.columns[0])

    print("\nNumber of Diseases")
    print("-" * 60)
    print(df.iloc[:, 0].nunique())

    print("\nFirst Five Diseases")
    print("-" * 60)
    print(df.iloc[:, 0].unique()[:5])

    print("\nFirst Five Rows")
    print("-" * 60)
    print(df.head())


def main():

    loader = DataLoader()

    df = loader.load_dataset()

    if df is not None:
        dataset_summary(df)


if __name__ == "__main__":
    main()