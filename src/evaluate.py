"""Evaluate the held-out test set and save metrics and a confusion matrix."""
import json
import os
from pathlib import Path

os.environ.setdefault("KERAS_HOME", str(Path(".cache/keras").resolve()))
os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache/matplotlib").resolve()))
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "2")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import yaml
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

CLASSES = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
           "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]


def main():
    with open("params.yaml", encoding="utf-8") as stream:
        params = yaml.safe_load(stream)["evaluate"]
    x_test = np.load("data/processed/x_test.npy", allow_pickle=False)
    y_test = np.load("data/processed/y_test.npy", allow_pickle=False)
    model = tf.keras.models.load_model("models/model.h5", compile=False)
    model.compile(loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    loss, accuracy = model.evaluate(x_test, y_test, batch_size=params["batch_size"], verbose=0)
    predicted = model.predict(x_test, batch_size=params["batch_size"], verbose=0).argmax(axis=1)
    matrix = confusion_matrix(y_test, predicted, labels=np.arange(len(CLASSES)))
    metrics = {"test_loss": float(loss), "test_accuracy": float(accuracy),
               "test_samples": int(len(y_test)), "target_met": bool(accuracy >= 0.85)}
    output = Path("reports")
    output.mkdir(parents=True, exist_ok=True)
    # The root copy is a Git-tracked DVC metric; reports/ is cached and pushed by DVC.
    text = json.dumps(metrics, indent=2, allow_nan=False) + "\n"
    Path("metrics.json").write_text(text, encoding="utf-8")
    (output / "metrics.json").write_text(text, encoding="utf-8")
    np.savetxt(output / "confusion_matrix.csv", matrix, delimiter=",", fmt="%d")
    fig, ax = plt.subplots(figsize=(11, 9))
    ConfusionMatrixDisplay(matrix, display_labels=CLASSES).plot(
        ax=ax, cmap="Blues", xticks_rotation=45, colorbar=False,
    )
    ax.set_title("Fashion-MNIST test set confusion matrix")
    fig.tight_layout()
    fig.savefig(output / "confusion_matrix.png", dpi=160)
    plt.close(fig)
    print(text)


if __name__ == "__main__":
    main()
