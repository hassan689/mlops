"""Normalize raw pixels and create a reproducible, stratified validation split."""
from pathlib import Path

import numpy as np
import yaml
from sklearn.model_selection import train_test_split


def normalize(images):
    return images.astype(np.float32) / np.float32(255.0)


def main():
    with open("params.yaml", encoding="utf-8") as stream:
        params = yaml.safe_load(stream)["preprocess"]
    raw, output = Path("data/raw"), Path("data/processed")
    x_all = normalize(np.load(raw / "x_train.npy", allow_pickle=False))
    y_all = np.load(raw / "y_train.npy", allow_pickle=False)
    x_train, x_val, y_train, y_val = train_test_split(
        x_all, y_all, test_size=params["test_size"],
        random_state=params["seed"], stratify=y_all,
    )
    arrays = dict(x_train=x_train, y_train=y_train, x_val=x_val, y_val=y_val,
                  x_test=normalize(np.load(raw / "x_test.npy", allow_pickle=False)),
                  y_test=np.load(raw / "y_test.npy", allow_pickle=False))
    output.mkdir(parents=True, exist_ok=True)
    for name, values in arrays.items():
        np.save(output / f"{name}.npy", values, allow_pickle=False)
    print(f"Saved train={len(y_train)}, validation={len(y_val)}, test={len(arrays['y_test'])}.")


if __name__ == "__main__":
    main()
