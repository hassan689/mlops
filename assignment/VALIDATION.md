# Local validation results

Hassan Khan | 23L-0800 | 5 October 2026

The four standalone scripts were executed successfully in the project's
Python 3.12 environment with TensorFlow 2.20.0.

| Check | Observed result |
| --- | --- |
| Raw Fashion-MNIST data | 60,000 training images and 10,000 test images |
| Processed split | 48,000 training, 12,000 validation, 10,000 test |
| Pixel representation | float32, range 0 to 1 |
| Training | 10 epochs, 128 hidden units, dropout 0.2, Adam 0.001 |
| Test accuracy | **87.93%** |
| Test loss | 0.3469882607460022 |
| Required 85% threshold | Met |
| Model and history | models/model.h5 and models/history.csv generated |
| Confusion matrix | Counts sum to 10,000; diagonal matches accuracy |
| Dependency checks | TensorFlow/Drive imports pass; pip check passes |

The source files, workflow helper, and report builder passed Python syntax
checks. A clearly marked scratch layout fixture verified that the PDF builder
can produce four pages; that fixture is not submission evidence and is not
included in the deliverable.

These are **standalone validation results**, not a completed DVC v1/v2
experiment. The session could not write Git metadata even after folder access
was granted, so the supplied workflow still needs to run in the user's own
PowerShell terminal. Its Git/DVC branch and conflict sequence has been reviewed
but has not been executed end to end. DVC reproduction, Git commits and tags,
Google OAuth sign-in, cloud uploads, screenshots, and the final report remain
pending. No submission-ready PDF or successful upload is claimed.
