"""
==========================================================
HealthAI - Model Training
Author : Vansh Chopra
==========================================================
"""

import time
# pyrefly: ignore [missing-import]
import joblib
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import accuracy_score


DATASET_PATH = Path(
    "data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)

MODEL_PATH = Path("models/general")

MODEL_PATH.mkdir(parents=True, exist_ok=True)


def load_data():

    df = pd.read_csv(DATASET_PATH)

    counts = df["diseases"].value_counts()

    valid = counts[counts >= 2].index

    df = df[df["diseases"].isin(valid)].copy()

    X = df.drop(columns=["diseases"])

    y = df["diseases"]

    encoder = LabelEncoder()

    y = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    return X_train, X_test, y_train, y_test, encoder


def train_model(name, model, X_train, X_test, y_train, y_test):

    print(f"\nTraining {name}...")

    start = time.time()

    model.fit(X_train, y_train)

    end = time.time()

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"Accuracy : {accuracy:.4f}")

    print(f"Training Time : {end-start:.2f} sec")

    joblib.dump(model, MODEL_PATH / f"{name}.pkl")

    return accuracy


def main():

    X_train, X_test, y_train, y_test, encoder = load_data()

    models = {

        "LogisticRegression":

            LogisticRegression(
                max_iter=1000,
                solver="lbfgs",
                random_state=42
            ),

        "KNN":

            KNeighborsClassifier(
                n_neighbors=5
            ),

        "DecisionTree":

            DecisionTreeClassifier(
                random_state=42
            )
    }

    results = {}

    for name, model in models.items():

        results[name] = train_model(
            name,
            model,
            X_train,
            X_test,
            y_train,
            y_test
        )

    print("\n")

    print("="*60)

    print("MODEL COMPARISON")

    print("="*60)

    for k,v in results.items():

        print(f"{k:25} {v:.4f}")

    best = max(results,key=results.get)

    print("\nBest Model :",best)

    joblib.dump(
        encoder,
        MODEL_PATH/"label_encoder.pkl"
    )


if __name__=="__main__":
    main()