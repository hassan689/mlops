"""Train the fully connected ANN using only params.yaml hyperparameters."""
import csv
import os
from pathlib import Path

os.environ.setdefault("KERAS_HOME", str(Path(".cache/keras").resolve()))
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "2")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")

import numpy as np
import tensorflow as tf
import yaml


def main():
    with open("params.yaml", encoding="utf-8") as stream:
        params = yaml.safe_load(stream)["train"]
    tf.keras.utils.set_random_seed(params["seed"])
    tf.config.experimental.enable_op_determinism()
    data = Path("data/processed")
    x_train, y_train, x_val, y_val = (
        np.load(data / f"{name}.npy", allow_pickle=False)
        for name in ("x_train", "y_train", "x_val", "y_val")
    )
    model = tf.keras.Sequential([
        tf.keras.Input(shape=x_train.shape[1:]),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(params["dense_units"], activation="relu"),
        tf.keras.layers.Dropout(params["dropout_rate"]),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=params["learning_rate"]),
        loss="sparse_categorical_crossentropy", metrics=["accuracy"],
    )
    model.summary()
    history = model.fit(
        x_train, y_train, validation_data=(x_val, y_val),
        epochs=params["epochs"], batch_size=params["batch_size"], verbose=2,
    )
    output = Path("models")
    output.mkdir(parents=True, exist_ok=True)
    model.save(output / "model.h5")
    with (output / "history.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["epoch", *history.history])
        for epoch, values in enumerate(zip(*history.history.values()), start=1):
            writer.writerow([epoch, *values])


if __name__ == "__main__":
    main()
