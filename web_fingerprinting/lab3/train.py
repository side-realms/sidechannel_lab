#!/usr/bin/env python3

import hashlib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from keras.models import Sequential
from keras.layers import (
    Input, Conv1D, MaxPooling1D, Flatten,
    Dense, Dropout, BatchNormalization,
)
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.utils import to_categorical

def preprocess(X: np.ndarray) -> np.ndarray:
    X = X.copy().astype("float32")
    for i in range(len(X)):
        seq = X[i, :, 0]
        X[i, :, 0] = (seq - seq.mean()) / (seq.std() + 1e-6)
    return X

def build_model(input_len: int, num_classes: int) -> Sequential:
    m = Sequential([
        Input(shape=(input_len, 1)),
        Conv1D(64, 8, activation="relu", padding="same"),
        BatchNormalization(), MaxPooling1D(4), Dropout(0.3),
        Conv1D(64, 4, activation="relu", padding="same"),
        BatchNormalization(), MaxPooling1D(4), Dropout(0.3),
        Flatten(),
        Dense(32, activation="relu", kernel_regularizer="l2"),
        Dropout(0.5),
        Dense(num_classes, activation="softmax"),
    ])
    m.compile(optimizer=Adam(1e-4),
              loss="categorical_crossentropy",
              metrics=["accuracy"])
    return m

d_tr = np.load("train.npz", allow_pickle=True)
d_va = np.load("val.npz",   allow_pickle=True)
d_te = np.load("test.npz",  allow_pickle=True)

X_train, y_train = preprocess(d_tr["X"]), d_tr["y"]
X_val,   y_val   = preprocess(d_va["X"]),   d_va["y"]
X_test,  y_test  = preprocess(d_te["X"]),  d_te["y"]

le = LabelEncoder().fit(np.concatenate([y_train, y_val, y_test]))
classes = le.classes_
n_cls   = len(classes)

ytr_cat = to_categorical(le.transform(y_train), n_cls).astype("float32")
yva_cat = to_categorical(le.transform(y_val), n_cls).astype("float32")
yte_int = le.transform(y_test)
yte_cat = to_categorical(yte_int, n_cls).astype("float32")

batch = min(64, len(X_train))
model = build_model(X_train.shape[1], n_cls)
es = EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True)
rl = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3)

model.fit(
    X_train, ytr_cat,
    epochs=50,
    batch_size=batch,
    validation_data=(X_val, yva_cat),
    callbacks=[es, rl],
    verbose=2,
)

val_acc = model.evaluate(X_val, yva_cat, verbose=0)[1]
print(f"\n=== VALIDATION ACCURACY: {val_acc:.3f} ===\n")

test_loss, test_acc = model.evaluate(X_test, yte_cat, verbose=0)
print(f"=== TEST ACCURACY = {test_acc:.3f} (N={len(X_test)}) ===\n")

y_prob = model.predict(X_test, verbose=0)
y_pred = y_prob.argmax(axis=1)

print("=== CLASSIFICATION REPORT ===")
print(classification_report(
    yte_int, y_pred,
    target_names=classes,
    zero_division=0
))

