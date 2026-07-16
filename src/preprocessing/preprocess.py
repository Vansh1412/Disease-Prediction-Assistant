"""
==========================================================
HealthAI - Data Preprocessing
Author : Vansh Chopra
==========================================================
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DATASET_PATH = Path(
    "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)


def load_dataset():
    """Load the dataset."""
    return pd.read_csv(DATASET_PATH)


def remove_single_sample_classes(df):
    """
    Remove diseases that appear only once.
    """

    counts = df["diseases"].value_counts()

    valid_classes = counts[counts >= 2].index

    filtered_df = df[df["diseases"].isin(valid_classes)].copy()

    removed = len(counts) - len(valid_classes)

    print("=" * 60)
    print("CLASS FILTERING")
    print("=" * 60)

    print(f"Original Diseases : {len(counts)}")
    print(f"Removed Diseases  : {removed}")
    print(f"Remaining Diseases: {len(valid_classes)}")

    return filtered_df


def prepare_features(df):
    """
    Prepare X and y.
    """

    X = df.drop(columns=["diseases"])

    y = df["diseases"]

    encoder = LabelEncoder()

    y = encoder.fit_transform(y)

    return X, y, encoder


def split_dataset(X, y):
    """
    Perform train-test split.
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\nDataset Split Successful")

    print(f"Training Samples : {len(X_train):,}")
    print(f"Testing Samples  : {len(X_test):,}")

    return X_train, X_test, y_train, y_test


def main():

    df = load_dataset()

    df = remove_single_sample_classes(df)

    X, y, encoder = prepare_features(df)

    split_dataset(X, y)


if __name__ == "__main__":
    main()