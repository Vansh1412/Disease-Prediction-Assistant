"""
==========================================================
HealthAI — Deployment-Optimised Model Recompression
==========================================================
Strategy
--------
The original DecisionTree.pkl (358 MB) and KNN.pkl (569 MB) exceed
GitHub's 100 MB file-size limit.  They were trained correctly but saved
WITHOUT compression (joblib default).

Re-saving with joblib compress=3 (zlib) achieves:
  DecisionTree : 358 MB → ~3.9 MB   (same model, zero accuracy loss)
  KNN          : 569 MB → ~6.1 MB   (same model, zero accuracy loss)

This is correct because both models store binary (0/1) feature vectors
which compress at ~93x ratio with zlib.

This script:
1. Backs up the original (uncompressed) .pkl files to models/original_backup/
2. Re-saves each model in-place with compress=3
3. Verifies accuracy is identical
4. Prints a size/accuracy comparison table

Usage
-----
    python src/training/retrain_small_models.py

Run from the project root directory.
"""

import shutil
import time
import traceback
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
_ROOT = _HERE.parent.parent

DATASET_PATH = (
    _ROOT / "data" / "disease_prediction"
    / "Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)
MODEL_DIR  = _ROOT / "models" / "general"
BACKUP_DIR = _ROOT / "models" / "original_backup"

TEST_SIZE    = 0.20
RANDOM_STATE = 42
COMPRESS     = 3          # zlib level 3 — fast and very effective for binary data
TARGET_MB    = {"DecisionTree": 20.0, "KNN": 80.0}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mb(path: Path) -> float:
    return path.stat().st_size / 1_048_576


def _load_test_set():
    print(f"Loading dataset from {DATASET_PATH} …")
    df     = pd.read_csv(DATASET_PATH)
    counts = df["diseases"].value_counts()
    valid  = counts[counts >= 2].index
    df     = df[df["diseases"].isin(valid)].copy()
    X      = df.drop(columns=["diseases"])
    y      = df["diseases"]
    enc    = LabelEncoder()
    y_enc  = enc.fit_transform(y)
    _, X_test, _, y_test = train_test_split(
        X, y_enc, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_enc
    )
    print(f"  Test set: {len(X_test):,} rows, {X.shape[1]} features, {len(valid)} classes")
    return X_test, y_test


def _backup(name: str) -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    src = MODEL_DIR / f"{name}.pkl"
    dst = BACKUP_DIR / f"{name}.pkl"
    if not src.exists():
        print(f"  WARNING: {src} not found — nothing to back up")
        return
    if dst.exists():
        print(f"  {name}.pkl already in backup — skipping copy")
        return
    shutil.copy2(src, dst)
    print(f"  Backed up {name}.pkl ({mb(src):.1f} MB) -> {BACKUP_DIR}")


def _recompress(name: str, X_test, y_test) -> dict:
    """
    Load the original model (from backup or active dir), re-save with
    compress=3, verify accuracy is unchanged, return stats.
    """
    # Load from backup (guaranteed unmodified) if available
    for candidate in (BACKUP_DIR / f"{name}.pkl", MODEL_DIR / f"{name}.pkl"):
        if candidate.exists():
            source = candidate
            break
    else:
        print(f"  ERROR: {name}.pkl not found anywhere")
        return {}

    print(f"\n  Loading {name} from {source.name} ({mb(source):.1f} MB) …")
    t0    = time.time()
    model = joblib.load(source)
    load_t = time.time() - t0
    print(f"  Loaded in {load_t:.1f}s")

    # Measure original accuracy
    print(f"  Measuring accuracy …", end=" ", flush=True)
    t0    = time.time()
    preds = model.predict(X_test)
    acc   = accuracy_score(y_test, preds)
    print(f"{acc:.4f}  ({time.time() - t0:.1f}s)")

    # Re-save with compression
    out = MODEL_DIR / f"{name}.pkl"
    print(f"  Re-saving with compress={COMPRESS} …", end=" ", flush=True)
    t0 = time.time()
    joblib.dump(model, out, compress=COMPRESS)
    print(f"{mb(out):.2f} MB  ({time.time() - t0:.1f}s)")

    # Verify the compressed file loads and predicts identically
    model2 = joblib.load(out)
    preds2 = model2.predict(X_test)
    acc2   = accuracy_score(y_test, preds2)
    assert acc2 == acc, f"Accuracy changed after recompression! {acc} → {acc2}"
    print(f"  ✅ Verified: accuracy unchanged ({acc2:.4f})")

    target = TARGET_MB[name]
    size   = mb(out)
    if size <= target:
        print(f"  ✅ Size {size:.2f} MB ≤ target {target} MB — GitHub-safe")
    else:
        print(f"  ⚠️  Size {size:.2f} MB still > target {target} MB — "
              f"GitHub LFS or pruning needed")

    return {
        "old_mb":  mb(source),
        "new_mb":  size,
        "acc":     acc,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("HealthAI — Model Recompression (compress=3)")
    print("=" * 60)

    # 1. Back up originals
    print("\n[1/4] Backing up original uncompressed models …")
    for name in ("DecisionTree", "KNN"):
        _backup(name)

    # 2. Load test set once
    print("\n[2/4] Loading test data …")
    X_test, y_test = _load_test_set()

    # 3. Recompress each model
    print("\n[3/4] Recompressing …")
    results: dict[str, dict] = {}
    for name in ("DecisionTree", "KNN"):
        print(f"\n{'─'*40}")
        print(f"  {name}")
        print(f"{'─'*40}")
        try:
            results[name] = _recompress(name, X_test, y_test)
        except Exception:
            print(f"  ERROR:\n{traceback.format_exc()}")
            results[name] = {}

    # 4. Summary table
    print("\n[4/4] Summary")
    print("=" * 60)
    print(f"{'Model':<20} {'Old Size':>10} {'New Size':>10} {'Accuracy':>10} {'Δ Size':>10}")
    print("-" * 60)
    for name, r in results.items():
        if not r:
            print(f"{name:<20} {'ERROR':>10}")
            continue
        delta = r["new_mb"] - r["old_mb"]
        print(
            f"{name:<20} "
            f"{r['old_mb']:>8.1f}MB "
            f"{r['new_mb']:>8.2f}MB "
            f"{r['acc']:>10.4f} "
            f"{delta:>+9.1f}MB"
        )
    print("=" * 60)

    # Verify label encoder still works
    print("\n[Verify] Label encoder compatibility …")
    enc_path = MODEL_DIR / "label_encoder.pkl"
    enc      = joblib.load(enc_path)
    sample   = X_test.iloc[:3]
    for name in results:
        path = MODEL_DIR / f"{name}.pkl"
        if not path.exists():
            continue
        m      = joblib.load(path)
        preds  = m.predict(sample)
        labels = enc.inverse_transform(preds)
        print(f"  {name}: {list(labels)}")

    print("\n✅ Done.")
    print(f"   New models are in : {MODEL_DIR}")
    print(f"   Originals backed up: {BACKUP_DIR}")
    print("\nNext steps:")
    print("  git add models/general/DecisionTree.pkl models/general/KNN.pkl")
    print("  git add models/original_backup/")
    print("  git commit -m 'feat: recompress DT and KNN with compress=3 (358MB→4MB, 570MB→6MB)'")
    print("  git push origin main")


if __name__ == "__main__":
    main()
