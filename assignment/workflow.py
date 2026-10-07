r"""Run assignment demonstrations from a normal Windows PowerShell terminal.

Usage: .\.venv312\Scripts\python.exe assignment\workflow.py history
Steps: history, track, pipeline, conflicts, publish
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["DVC_NO_ANALYTICS"] = "1"
os.environ["MPLCONFIGDIR"] = str(ROOT / ".cache/matplotlib")
# Scoped to this process and its children, not a global Git setting.
os.environ["GIT_CONFIG_COUNT"] = "1"
os.environ["GIT_CONFIG_KEY_0"] = "safe.directory"
os.environ["GIT_CONFIG_VALUE_0"] = ROOT.as_posix()
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)
(ROOT / ".cache").mkdir(exist_ok=True)
LOGDIR = ROOT / ".cache/evidence"
LOGDIR.mkdir(exist_ok=True)


def run(*args, log, check=True):
    command = [str(arg) for arg in args]
    with (LOGDIR / log).open("a", encoding="utf-8") as stream:
        heading = "\n$ " + subprocess.list2cmdline(command) + "\n"
        print(heading, end="")
        stream.write(heading)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True,
                                   encoding="utf-8", errors="replace")
        output = []
        for line in process.stdout:
            print(line, end="")
            stream.write(line)
            stream.flush()
            output.append(line)
        code = process.wait()
        stream.write(f"[exit code {code}]\n")
    if check and code:
        raise RuntimeError(f"Command failed ({code}); see .cache/evidence/{log}. Do not restart the whole step blindly.")
    return code, "".join(output)


def git(*args, log="A_history.txt", check=True):
    return run("git", *args, log=log, check=check)


def dvc(*args, log="C_tracking.txt", check=True):
    return run(sys.executable, "-m", "dvc", *args, log=log, check=check)


def commit(message, *paths, log="A_history.txt"):
    if "evidence" in paths:
        for source in LOGDIR.glob("*.txt"):
            shutil.copy2(source, EVIDENCE / source.name)
    git("add", "--", *paths, log=log)
    git("commit", "-m", message, log=log)


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def require_clean():
    _, tracked = git("status", "--porcelain", "--untracked-files=no", log="workflow_checks.txt")
    if tracked.strip():
        raise RuntimeError("Commit or save existing tracked changes before continuing.")


def history():
    code, _ = git("rev-parse", "--verify", "HEAD", check=False)
    if code == 0:
        raise RuntimeError("History already exists. Do not rerun this first step.")
    git("init", "-b", "main")
    git("symbolic-ref", "HEAD", "refs/heads/main")
    git("config", "user.name", "Hassan Khan")
    git("config", "user.email", "l230800@lhr.nu.edu.pk")
    git("config", "core.autocrlf", "false")
    _, remotes = git("remote")
    if "origin" not in remotes.split():
        git("remote", "add", "origin", "https://github.com/hassan689/mlops.git")
    commit("Initialize Fashion-MNIST assignment with README and ignore rules", "README.md", ".gitignore")
    git("checkout", "-b", "dev")

    # A real tracked move, with both sides represented in commit history.
    shutil.copy2("src/prepare.py", "prepare.py")
    Path("src/prepare.py").unlink()
    commit("Implement Fashion-MNIST download", "prepare.py")
    git("mv", "prepare.py", "src/prepare.py")
    git("commit", "-m", "Move preparation script into src with git mv")
    for name, message in [
        ("preprocess", "Implement reproducible normalization and validation split"),
        ("train", "Implement parameter-driven fully connected ANN training"),
        ("evaluate", "Implement test metrics and confusion matrix"),
    ]:
        commit(message, f"src/{name}.py")
    commit("Centralize preprocessing training and evaluation parameters", "params.yaml")
    requirement_files = ["requirements.txt"]
    if Path("requirements-lock.txt").exists():
        requirement_files.append("requirements-lock.txt")
    commit("Declare TensorFlow and Google Drive DVC dependencies", *requirement_files)
    commit("Define four-stage DVC pipeline", "dvc.yaml")

    original = Path("src/preprocess.py").read_text(encoding="utf-8")
    write("src/preprocess.py", original + "\n# Validate the split before running the next experiment.\n")
    git("diff", log="A4_diff.txt")
    git("add", "src/preprocess.py", log="A4_diff.txt")
    git("diff", "--staged", log="A4_diff.txt")
    git("restore", "--staged", "src/preprocess.py")
    git("stash", "push", "-m", "Pause preprocessing edit to inspect main", "--", "src/preprocess.py", log="A5_stash.txt")
    git("checkout", "main", log="A5_stash.txt")
    git("log", "-1", "--oneline", log="A5_stash.txt")
    git("checkout", "dev", log="A5_stash.txt")
    git("stash", "list", log="A5_stash.txt")
    git("stash", "pop", log="A5_stash.txt")
    commit("Resume preprocessing edit after stashing", "src/preprocess.py")

    git("log", "--oneline", "--graph", "--all", log="A6_rebase_before.txt")
    git("checkout", "-b", "hotfix", "main")
    with Path("README.md").open("a", encoding="utf-8") as stream:
        stream.write("\nRun all pipeline commands from the repository root.\n")
    commit("Clarify repository-root execution in README", "README.md")
    git("checkout", "main")
    git("merge", "--no-ff", "hotfix", "-m", "Merge README hotfix")
    git("checkout", "dev")
    git("diff", "main..dev", log="A4_two_dot_before_rebase.txt")
    git("diff", "main...dev", log="A4_three_dot_before_rebase.txt")
    git("rebase", "main", log="A6_rebase.txt")
    git("log", "--oneline", "--graph", "--all", log="A6_rebase_after.txt")
    for args, filename in [
        (("log", "--oneline", "--graph", "--all"), "A3_graph.txt"),
        (("log", "--stat", "-3"), "A3_stat.txt"),
        (("log", "-p", "-1"), "A3_patch.txt"),
        (("log", "main..dev"), "A3_main_dev.txt"),
    ]:
        git(*args, log=filename)

    git("checkout", "-b", "scratch-reset", log="A7_reset.txt")
    write("scratch-reset.txt", "Throwaway commit one.\n")
    commit("Scratch commit for soft reset", "scratch-reset.txt", log="A7_reset.txt")
    git("branch", "reset-soft-evidence", log="A7_reset.txt")
    git("reset", "--soft", "HEAD~1", log="A7_reset.txt")
    git("status", "--short", log="A7_reset.txt")
    git("diff", "--staged", log="A7_reset.txt")
    write("scratch-reset.txt", "Throwaway commit two.\n")
    commit("Scratch commit for hard reset", "scratch-reset.txt", log="A7_reset.txt")
    git("branch", "reset-hard-evidence", log="A7_reset.txt")
    git("reset", "--hard", "HEAD~1", log="A7_reset.txt")
    git("status", "--short", log="A7_reset.txt")
    if Path("scratch-reset.txt").exists():
        raise RuntimeError("Hard reset did not discard the scratch file.")
    git("checkout", "dev")
    write("obsolete-scratch.txt", "Temporary file for the required git rm demonstration.\n")
    commit("Add obsolete scratch file for removal demonstration", "obsolete-scratch.txt")
    git("rm", "obsolete-scratch.txt", log="A8_rm.txt")
    git("commit", "-m", "Remove obsolete scratch file with git rm", log="A8_rm.txt")
    dvc("init")
    dvc("remote", "add", "-d", "gdrive_storage", "gdrive://1YHXO_DPFi3IbrMBIzldjwvABL400q8tL")
    commit("Initialize DVC and configure Google Drive remote on dev", ".dvc", ".dvcignore")
    commit("Save assignment workflow and Git command evidence", "assignment", "evidence")


def track():
    require_clean()
    # Park dvc.yaml before dvc add; two stages cannot own the same outputs.
    git("mv", "dvc.yaml", "assignment/pipeline.yaml", log="C_tracking.txt")
    git("commit", "-m", "Park pipeline definition for standalone DVC tracking", log="C_tracking.txt")
    for name in ("prepare", "preprocess", "train", "evaluate"):
        run(sys.executable, f"src/{name}.py", log="B_standalone.txt")
    dvc("add", "data/raw", "data/processed", "models", "reports")
    commit("Track raw data processed data model and report artifacts with DVC",
           "data", "models.dvc", "reports.dvc", ".gitignore", "metrics.json")
    dvc("push", log="C_push.txt", check=False)
    commit("Record standalone pipeline and DVC tracking evidence", "evidence")


def pipeline():
    import yaml
    require_clean()
    git("rm", "data/raw.dvc", "data/processed.dvc", "models.dvc", "reports.dvc", log="D_migration.txt")
    git("mv", "assignment/pipeline.yaml", "dvc.yaml", log="D_migration.txt")
    git("commit", "-m", "Transfer DVC artifact ownership to four pipeline stages", log="D_migration.txt")
    dvc("repro", "--force", log="D3_repro_v1.txt")
    shutil.copy2("metrics.json", EVIDENCE / "v1_metrics.json")
    commit("Record reproducible v1 ANN pipeline and metrics", "dvc.yaml", "dvc.lock", "params.yaml", "metrics.json", "evidence")
    git("tag", "v1")
    dvc("push", log="D3_push_v1.txt", check=False)
    git("checkout", "main")
    git("merge", "--no-ff", "dev", "-m", "Merge v1 ANN pipeline")
    git("checkout", "dev")
    config = yaml.safe_load(Path("params.yaml").read_text(encoding="utf-8"))
    config["train"]["dense_units"] = 256
    write("params.yaml", yaml.safe_dump(config, sort_keys=False))
    dvc("repro", log="D4_repro_v2.txt")
    shutil.copy2("metrics.json", EVIDENCE / "v2_metrics.json")
    commit("Increase dense units to 256 and record v2 results", "params.yaml", "dvc.yaml", "dvc.lock", "metrics.json", "evidence")
    git("tag", "v2")
    dvc("push", log="D5_push_v2.txt", check=False)
    git("checkout", "main")
    git("merge", "--no-ff", "dev", "-m", "Merge v2 ANN experiment")


def conflicts():
    require_clean()
    git("checkout", "main")
    original_pipeline = Path("dvc.yaml").read_text(encoding="utf-8")
    original_code = Path("src/preprocess.py").read_text(encoding="utf-8")
    write(".cache/pipeline-before-conflict.yaml", original_pipeline)
    write(".cache/preprocess-before-conflict.py", original_code)
    needle = "return images.astype(np.float32) / np.float32(255.0)"
    if needle not in original_code:
        raise RuntimeError("Expected baseline normalization was not found; inspect before continuing.")
    dvc("remove", "preprocess", log="E_pointer_transition.txt")
    dvc("add", "data/processed", log="E_pointer_transition.txt")
    commit("Temporarily use a processed-data pointer for the required conflict exercise",
           "dvc.yaml", "dvc.lock", "data/processed.dvc", log="E_pointer_transition.txt")
    git("checkout", "-b", "teammate-sim", log="E_branches.txt")
    write("src/preprocess.py", original_code.replace(needle,
          "return images.astype(np.float32) / np.float32(256.0)"))
    run(sys.executable, "src/preprocess.py", log="E1_teammate.txt")
    dvc("add", "data/processed", log="E1_teammate.txt")
    dvc("push", log="E1_push.txt", check=False)
    commit("Simulate teammate normalization and processed-data update",
           "src/preprocess.py", "data/processed.dvc", log="E1_teammate.txt")
    git("checkout", "main", log="E_branches.txt")
    write("src/preprocess.py", original_code.replace(needle,
          "return np.minimum(images, 250).astype(np.float32) / np.float32(255.0)"))
    run(sys.executable, "src/preprocess.py", log="E2_main.txt")
    dvc("add", "data/processed", log="E2_main.txt")
    dvc("push", log="E2_push.txt", check=False)
    commit("Simulate independent main normalization and data update",
           "src/preprocess.py", "data/processed.dvc", log="E2_main.txt")
    code, _ = git("merge", "teammate-sim", "-m", "Merge simulated teammate changes", log="E3_merge_conflicts.txt", check=False)
    if code == 0:
        raise RuntimeError("Expected merge conflicts did not occur.")
    _, paths = git("diff", "--name-only", "--diff-filter=U", log="E3_merge_conflicts.txt")
    if set(paths.splitlines()) != {"src/preprocess.py", "data/processed.dvc"}:
        raise RuntimeError("Unexpected conflicts; inspect the repository before resolving.")
    for source, target in [("src/preprocess.py", "E3_code_conflict.txt"),
                           ("data/processed.dvc", "E3_data_conflict.txt")]:
        shutil.copy2(source, EVIDENCE / target)
    # Keep the original 255 scale and defensively clip to the valid pixel range.
    write("src/preprocess.py", original_code.replace(needle,
          "return np.clip(images, 0, 255).astype(np.float32) / np.float32(255.0)"))
    git("checkout", "--ours", "data/processed.dvc", log="E4_resolution.txt")
    run(sys.executable, "src/preprocess.py", log="E4_resolution.txt")
    dvc("add", "data/processed", log="E4_resolution.txt")
    dvc("checkout", "data/processed.dvc", log="E4_resolution.txt")
    dvc("status", log="E4_resolution.txt")
    git("add", "src/preprocess.py", "data/processed.dvc", log="E4_resolution.txt")
    git("commit", "-m", "Resolve code and data conflicts by regenerating canonical normalization", log="E4_resolution.txt")
    git("rm", "data/processed.dvc", log="E5_pipeline_restore.txt")
    write("dvc.yaml", original_pipeline)
    dvc("repro", log="E5_final_repro.txt")
    dvc("status", log="E5_final_status.txt")
    shutil.copy2("metrics.json", EVIDENCE / "final_metrics.json")
    commit("Restore automatic preprocessing and verify the merged pipeline",
           "dvc.yaml", "dvc.lock", "src/preprocess.py", "metrics.json", "evidence", log="E5_pipeline_restore.txt")
    dvc("push", "--all-commits", log="E5_final_push.txt", check=False)


def publish():
    # Cloud completion is a hard gate here, unlike the earlier local exercises.
    dvc("push", "--all-commits", log="submission_push.txt")
    dvc("status", "--cloud", log="submission_cloud_status.txt")
    commit("Record final DVC upload evidence", "evidence", log="submission_git.txt")
    git("push", "-u", "origin", "--all", log="submission_git.txt")
    git("push", "origin", "--tags", log="submission_git.txt")
    commit("Preserve successful GitHub publication output", "evidence", log="submission_receipt.txt")
    git("push", "origin", "main", log="submission_receipt.txt")
    print("Open Google Drive, verify the cache objects, and capture the required browser screenshot.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["history", "track", "pipeline", "conflicts", "publish"])
    args = parser.parse_args()
    getattr(sys.modules[__name__], args.step)()
    print(f"Completed local step: {args.step}. Read its evidence logs; cloud errors must be resolved before submission.")
