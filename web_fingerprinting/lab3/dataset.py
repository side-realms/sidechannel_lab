#!/usr/bin/env python3

import argparse
import hashlib
import numpy as np
from sklearn.model_selection import train_test_split

def preprocess(X: np.ndarray) -> np.ndarray:
    X = X.copy().astype("float32")
    for i in range(len(X)):
        seq = X[i, :, 0]
        X[i, :, 0] = (seq - seq.mean()) / (seq.std() + 1e-6)
    return X

def deduplicate(X: np.ndarray, y: np.ndarray):
    seen = set()
    keep = []
    for i, s in enumerate(X):
        h = hashlib.md5(s.tobytes()).hexdigest()
        if h not in seen:
            seen.add(h)
            keep.append(i)
    return X[keep], y[keep]

def make_splits(raw_path, out_dir, test_ratio, val_ratio, seed):
    data = np.load(raw_path, allow_pickle=True)
    X_raw, y_raw = data["X"], data["y"]

    X_prep = preprocess(X_raw)
    X_u, y_u = deduplicate(X_prep, y_raw)
    removed = len(X_raw) - len(X_u)
    print(f"After dedup: {len(X_u)} samples ({removed} removed)")

    X_tmp, X_test, y_tmp, y_test = train_test_split(
        X_u, y_u,
        test_size=test_ratio,
        stratify=y_u,
        random_state=seed
    )

    val_size = val_ratio / (1 - test_ratio)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tmp, y_tmp,
        test_size=val_size,
        stratify=y_tmp,
        random_state=seed
    )

    np.savez(f"{out_dir}/train.npz", X=X_train, y=y_train)
    np.savez(f"{out_dir}/val.npz",   X=X_val,   y=y_val)
    np.savez(f"{out_dir}/test.npz",  X=X_test,  y=y_test)
    print(f"Saved: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

if __name__ == "__main__":

    make_splits(
        raw_path="closed.npz",
        out_dir=".",
        test_ratio=0.30,
        val_ratio=0.10,
        seed=42,
    )

