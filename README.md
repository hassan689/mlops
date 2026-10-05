# Fashion-MNIST ANN pipeline

Hassan Khan | 23L-0800 | Assignment 3

This project classifies Fashion-MNIST clothing images using a fully connected
TensorFlow ANN and versions its code, data, model, and metrics with Git and DVC.
The required test-accuracy target is 85%; measured results are written to
`metrics.json` after evaluation.

Repository: https://github.com/hassan689/mlops  
DVC remote: `gdrive://1YHXO_DPFi3IbrMBIzldjwvABL400q8tL`

## Start the assignment

Read [assignment/START_HERE.md](assignment/START_HERE.md) for the full workflow,
Google OAuth setup, Git demonstrations, conflict exercise, and report creation.
Use a normal PowerShell window, beginning in this project folder:

```powershell
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe assignment\workflow.py history
```

The existing `venv/` was created with Python 3.14. This project uses the separate
Python 3.12 environment `.venv312/`. On another computer, create a compatible
environment using `py -3.12 -m venv .venv312`, then install the requirements.

## Pipeline

| Stage | Responsibility | Outputs |
| --- | --- | --- |
| prepare | Download the original 60,000 train and 10,000 test examples | data/raw |
| preprocess | Normalize to [0,1] and stratify a validation split | data/processed |
| train | Fit Flatten, Dense ReLU, Dropout, Dense softmax | models/model.h5, models/history.csv |
| evaluate | Measure test loss/accuracy and generate confusion matrix | metrics.json, reports |

Each script runs independently from the repository root. `params.yaml` controls
the split, model width, dropout, learning rate, epochs, batch sizes, and seeds.
The test set is kept separate from training and validation. The model is an ANN,
with no convolutional layers.

After DVC initialization and pipeline setup:

```powershell
.\.venv312\Scripts\Activate.ps1
dvc pull
dvc repro
dvc status
```

`dvc repro` skips unchanged work. Altering `train.dense_units` reruns training
and, when the resulting model changes, evaluation. Root `metrics.json` is a
DVC metric committed to Git; `reports/metrics.json` is its cached remote copy.

## Evidence

The workflow saves real command output under `evidence/` and live logs under
the ignored `.cache/evidence/`. It preserves unsquashed incremental commits,
v1/v2 tags, and the simulated collaboration branches. It temporarily changes
processed-data ownership for the `.dvc` pointer conflict exercise, then restores
the full four-stage pipeline. Read the guide before running each step.

Secrets belong only in ignored local files. `assignment/configure_drive.py`
stores OAuth client settings in `.dvc/config.local` using DVC's `--local` option.

## References

- https://www.tensorflow.org/tutorials/keras/classification
- https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive
- https://dvc.org/doc/user-guide/project-structure/dvcyaml-files
