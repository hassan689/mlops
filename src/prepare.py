"""Download Fashion-MNIST and save the original arrays (run from project root)."""
import os
from pathlib import Path

# Keep download caches inside the project; the directory is ignored by Git.
os.environ.setdefault("KERAS_HOME", str(Path(".cache/keras").resolve()))
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
from tensorflow.keras.datasets import fashion_mnist


def main():
    (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
    output = Path("data/raw")
    output.mkdir(parents=True, exist_ok=True)
    for name, values in dict(x_train=x_train, y_train=y_train,
                             x_test=x_test, y_test=y_test).items():
        np.save(output / f"{name}.npy", values, allow_pickle=False)
    print(f"Saved {len(x_train)} training and {len(x_test)} test images.")


if __name__ == "__main__":
    main()
