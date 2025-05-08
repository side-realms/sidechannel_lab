import os, glob, json
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def load_dataset(dir_path):
    X, y = [], []
    for label in ('idle','load','ny'):
        for path in glob.glob(os.path.join(dir_path, f'{label}_*.json')):
            data = json.load(open(path))
            X.append(data)
            y.append(label)
    return np.array(X), np.array(y)

def load_tests(dir_path):
    test_files = sorted(glob.glob(os.path.join(dir_path, 'test_*.json')))
    X_test = []
    for path in test_files:
        X_test.append(json.load(open(path)))
    return np.array(X_test), test_files

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--train_dir', default='traces/train')
    p.add_argument('--test_dir',  default='traces/test')
    args = p.parse_args()


    X, y = load_dataset(args.train_dir)

    minlen = min(len(x) for x in X)
    X = np.array([x[:minlen] for x in X])

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    clf = SVC(kernel='rbf', probability=True)
    clf.fit(X, y_enc)

    X_test, files = load_tests(args.test_dir)
    X_test = np.array([x[:minlen] for x in X_test])

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)

    for i, f in enumerate(files):
        label = le.inverse_transform([y_pred[i]])[0]
        prob  = y_prob[i, y_pred[i]]
        print(f'{os.path.basename(f)} → {label}')

if __name__ == '__main__':
    main()
