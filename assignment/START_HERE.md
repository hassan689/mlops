# Hassan Khan Assignment 3

Roll number: **23L-0800**  
Git identity: **Hassan Khan <l230800@lhr.nu.edu.pk>**  
Repository: https://github.com/hassan689/mlops  
Google Drive: https://drive.google.com/drive/folders/1YHXO_DPFi3IbrMBIzldjwvABL400q8tL

The four scripts implement Fashion-MNIST preparation, stratified splitting,
ANN training, and test evaluation. The supplied workflow performs real Git and
DVC demonstrations and saves their actual output. Read each step before running
it. The scratch reset exercise only resets its dedicated scratch branch.

## Start in normal PowerShell

```powershell
cd 'C:\Users\JT GAMING\Desktop\Mlops'
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe assignment\workflow.py history
```

The `history` step creates the initial main commit, incremental dev commits,
diff and log examples, a stash/pop, README hotfix and rebase, soft/hard reset
examples on a scratch branch, and tracked `git mv` and `git rm` events. It then
initializes DVC on dev and configures your Drive remote. Your system-wide Git
identity is not changed. The scripts are designed to be run **once in order**.
If one fails, save its error and resume from that command after fixing the
problem; do not rerun a partly completed step from the beginning.

The local folder and GitHub repository currently use your existing names
`Mlops` and `mlops`. The handout requests `fashion-ann-pipeline`. If your
instructor enforces that name, rename the project/repository and recreate the
virtual environment in the renamed folder before using these commands.

## Configure Google authentication

If you already have working DVC Google OAuth credentials, retain them.
Otherwise, follow your instructor's guide to:

1. Create/select a Google Cloud project and enable **Google Drive API**.
2. Configure Google Auth Platform's consent screen for an external app.
3. Add the Google account that owns your Drive folder as a **test user**.
4. Create an **OAuth client ID** with application type **Desktop app**.
5. Download its JSON file outside the repository, for example into Downloads.

Configure it locally, replacing the example filename with the downloaded file:

```powershell
.\.venv312\Scripts\python.exe assignment\configure_drive.py 'C:\Users\JT GAMING\Downloads\client_secret_example.json'
```

This helper uses `dvc remote modify --local` so your client secret stays in
the Git-ignored `.dvc/config.local`. This corrects the supplied guide's commands
that would otherwise write credentials to the versioned config. Do not paste
the secret into chat, the README, logs, or your report. DVC's browser sign-in
must be completed by you. See https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive
for the current DVC authentication options. The requirements pin compatible
PyDrive2, pyOpenSSL, cryptography, and AsyncSSH versions because the unrestricted
installer produced the actual `GEN_EMAIL` error during this project's setup.

## Run the assignment experiments

Run these one at a time, checking the output after each:

```powershell
.\.venv312\Scripts\python.exe assignment\workflow.py track
.\.venv312\Scripts\python.exe assignment\workflow.py pipeline
.\.venv312\Scripts\python.exe assignment\workflow.py conflicts
```

`track` runs all scripts independently, creates the standalone `.dvc` pointers
required by Part C, and attempts the first Drive push. It temporarily parks
`dvc.yaml` as `assignment/pipeline.yaml` to avoid duplicate ownership.

`pipeline` transfers artifact ownership to the four pipeline stages, runs a
full baseline, records tag **v1**, then changes only `train.dense_units` from
128 to 256 and runs again for **v2**. It merges both experiments into main.
Read the actual D4 log: prepare/preprocess should be unchanged; train/evaluate
should rerun. No accuracy is assumed in advance. Both measured results are
saved under `evidence/`.

`conflicts` temporarily transfers processed data to a standalone pointer so
Part E produces the requested `.dvc` conflict. It creates two intentionally
incompatible normalization changes, captures the conflicts in code and data,
reconciles them using clipping to [0,255] and division by 255, regenerates the
authoritative data, and checks it out. It then restores the full pipeline and
reproduces it. Raw Fashion-MNIST pixels already lie in [0,255], so the final
normalization preserves the original numerical behavior.

The earlier steps log cloud push failures and allow local work to continue.
**A failed push does not satisfy the assignment.** Resolve all authentication
problems before the required final publish step, which stops if a push fails.

## Upload and verify

```powershell
.\.venv312\Scripts\python.exe assignment\workflow.py publish
```

This uploads DVC objects from all commits, pushes all assignment branches and
tags to your GitHub repository, and records cloud status. GitHub may prompt
you to sign in. No force push is used.

Open your Drive folder and confirm cache objects appear. DVC stores them under
hash-based paths rather than their original dataset filenames. Take the browser
screenshot requested in Part C and share the folder with your instructor.
Save that real screenshot as `evidence/drive_remote.png` (crop to the relevant
folder area so it stays readable in the report).

## Evidence and report

The committed `evidence/` folder contains command-output snapshots. The latest
live logs are in `.cache/evidence/`; this avoids logs changing while Git commits
them. They are real terminal output, not fabricated screenshots. If the rubric
specifically requires screenshots, capture the indicated commands in your own
terminal and the Drive folder in your browser. Keep credentials off screen.

Generate the four-page report only after completing all steps:

```powershell
.\.venv312\Scripts\python.exe assignment\build_report.py
```

This reads your real metrics, conflict output, pipeline logs, and configuration.
It refuses to generate a submission report if the Drive screenshot or required evidence is missing or
if final cloud upload has not succeeded. Review the resulting PDF and attach
your Drive/terminal screenshots where required by the instructor. The report
uses readable output excerpts and embeds the Drive screenshot; the repository
retains the complete logs. Open the PDF and check that all four pages are legible.

## Run the project later

```powershell
.\.venv312\Scripts\Activate.ps1
dvc pull
dvc repro
dvc status
```

The model is `models/model.h5`, history is `models/history.csv`, root metrics
are `metrics.json`, and the confusion matrix is `reports/confusion_matrix.png`.
Root metrics are tracked by Git as DVC metrics with `cache: false`; a duplicate
under `reports/` is DVC-cached and uploaded, satisfying the requirement to store
metrics remotely as well. The test set is never used to fit the model or select
an epoch. Reproducibility uses fixed split/training seeds and deterministic TF
operations; exact floating-point values may still differ across environments.

## Explanations for your report and viva

- `git log --oneline --graph --all`: compact topology for every branch.
- `git log --stat -3`: file-level insertion/deletion summaries for three commits.
- `git log -p -1`: the actual patch introduced by the latest commit.
- `git log main..dev`: commits reachable from dev but not from main.
- `git diff`: working tree versus index; `git diff --staged`: index versus HEAD.
- `git diff main..dev`: compare the two branch-tip trees.
- `git diff main...dev`: compare the merge base with dev. The workflow captures
  these before rebasing so main's independent README fix demonstrates why the
  outputs can differ. After main becomes an ancestor of dev, the diffs coincide.
- Stash saves an unfinished tracked edit; pop reapplies it and removes the stash
  when successful. Rebase replays dev commits onto updated main and changes IDs.
- Soft reset moves HEAD but keeps changes staged. Hard reset also restores the
  index and tracked working tree. Evidence branches preserve the throwaway commits.
- Changing dense units invalidates train's tracked parameters. The changed model
  invalidates evaluate; neither raw data nor preprocessing depends on dense units.
- A `.dvc` file contains content hashes, not the data itself. Resolve its pointer
  and then use `dvc checkout` to synchronize actual files with that decision.

Official references: https://www.tensorflow.org/tutorials/keras/classification
and https://dvc.org/doc/user-guide/project-structure/dvcyaml-files
