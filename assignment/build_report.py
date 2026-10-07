"""Build a four-page PDF from completed, real assignment evidence."""
import json
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak, Image,
)

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "evidence"
LIVE = ROOT / ".cache/evidence"


def read(name):
    path = LIVE / name
    if not path.exists():
        path = E / name
    if not path.exists():
        raise SystemExit(f"Missing evidence: {name}. Complete the workflow before making a submission report.")
    return path.read_text(encoding="utf-8")


def excerpt(name, lines=9, pattern=None, width=104):
    selected = read(name).splitlines()
    if pattern:
        selected = [line for line in selected if re.search(pattern, line)]
    selected = [line for line in selected if line.strip()][:lines]
    return "\n".join(line[:width] for line in selected)


def main():
    drive_image = E / "drive_remote.png"
    if not drive_image.exists():
        raise SystemExit("Save your real Google Drive verification screenshot as evidence/drive_remote.png first.")
    for name in ["A3_graph.txt", "A3_stat.txt", "A3_patch.txt", "A3_main_dev.txt",
                 "A4_diff.txt", "A4_two_dot_before_rebase.txt", "A4_three_dot_before_rebase.txt",
                 "A5_stash.txt", "A6_rebase_before.txt", "A6_rebase_after.txt",
                 "A7_reset.txt", "A8_rm.txt", "B_standalone.txt", "C_tracking.txt",
                 "D3_repro_v1.txt", "D4_repro_v2.txt", "E3_code_conflict.txt",
                 "E3_data_conflict.txt", "E4_resolution.txt", "E5_final_repro.txt",
                 "E5_final_status.txt", "submission_push.txt", "submission_cloud_status.txt"]:
        read(name)
    for name in ["submission_push.txt", "submission_cloud_status.txt"]:
        if not read(name).rstrip().endswith("[exit code 0]"):
            raise SystemExit(f"Final cloud command did not succeed: {name}")
    publishing = read("submission_git.txt")
    if ("origin --all" not in publishing or "origin --tags" not in publishing
            or not publishing.rstrip().endswith("[exit code 0]")):
        raise SystemExit("GitHub publication has not completed successfully.")
    results = [json.loads((E / f"{version}_metrics.json").read_text(encoding="utf-8"))
               for version in ("v1", "v2", "final")]
    params = (ROOT / "params.yaml").read_text(encoding="utf-8")
    pipeline = (ROOT / "dvc.yaml").read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodySmall", fontName="Helvetica", fontSize=8.3,
                              leading=11.2, spaceAfter=5))
    styles.add(ParagraphStyle(name="SectionSmall", fontName="Helvetica-Bold", fontSize=10,
                              leading=13, spaceBefore=7, spaceAfter=4))
    code_style = ParagraphStyle("CodeSmall", fontName="Courier", fontSize=6.7, leading=8.3,
                                spaceAfter=4, alignment=TA_LEFT)
    story = []

    def text(value):
        story.append(Paragraph(value, styles["BodySmall"]))

    def heading(value):
        story.append(Paragraph(value, styles["SectionSmall"]))

    def code(value):
        story.append(Preformatted(value, code_style))

    story.append(Paragraph("Fashion MNIST versioning with Git and DVC", styles["Title"]))
    text("Hassan Khan | Roll number 23L-0800 | Assignment 3")
    text('Repository: <link href="https://github.com/hassan689/mlops">github.com/hassan689/mlops</link><br/>'
         'Drive: <link href="https://drive.google.com/drive/folders/1YHXO_DPFi3IbrMBIzldjwvABL400q8tL">DVC remote folder</link>')
    text("The project classifies Fashion-MNIST using a fully connected ANN. Raw images, normalized splits, "
         "the trained model, and evaluation artifacts are versioned through DVC. Four independent scripts "
         "form a reproducible pipeline; Git records the code, parameters, locks, and small metric file.")
    heading("Model and measured results")
    text("Architecture: Flatten, Dense with ReLU, Dropout, Dense with 10-way softmax. Training uses Adam "
         "and sparse categorical cross-entropy. A stratified 20% of the 60,000 training examples is reserved "
         "for validation; all 10,000 test examples remain held out. Both split and training seeds are 42.")
    table = Table([["Version", "Dense units", "Test accuracy", "Test loss", "Meets 85%"]] +
                  [[label, str(units), f"{r['test_accuracy']:.2%}", f"{r['test_loss']:.4f}",
                    "Yes" if r["test_accuracy"] >= .85 else "No"]
                   for label, units, r in zip(["v1", "v2", "Final"], [128, 256, 256], results)],
                  colWidths=[70, 78, 98, 88, 85])
    table.setStyle(TableStyle([("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                               ("FONTSIZE", (0,0), (-1,-1), 8),
                               ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eef2f5")),
                               ("TOPPADDING", (0,0), (-1,-1), 6),
                               ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    story.append(table)
    heading("Git logs and incremental work")
    text("The first main commit contains README and ignore rules. Feature work is committed incrementally "
         "on dev. The graph view exposes branch and merge topology; --stat -3 summarizes changed files in "
         "three commits; -p -1 shows the last patch; main..dev lists commits reachable only from dev.")
    code(excerpt("A3_graph.txt", 10))
    code(excerpt("A3_stat.txt", 5, r"file|insertion|deletion|\.py|\.yaml"))
    code(excerpt("A3_patch.txt", 5, r"^diff|^@@|^\+[^+]"))
    text("The complete outputs, including git log main..dev and individual standalone script runs, are "
         "retained in evidence/A3_*.txt and evidence/B_standalone.txt.")

    story.append(PageBreak())
    heading("Git differences stash rebase and reset")
    text("git diff compares the working tree to the index; git diff --staged compares the index to HEAD. "
         "The same unfinished preprocessing edit demonstrates both views.")
    code(excerpt("A4_diff.txt", 10, r"^\$|^diff|^@@|^\+[^+]"))
    text("Two-dot branch diff compares the main and dev tip trees. Three-dot compares their merge base "
         "to dev. Before rebase, main has an independent README fix: the two-dot diff includes that "
         "difference, while the three-dot diff isolates dev's changes. Once main is an ancestor of dev, "
         "these comparisons coincide.")
    code(excerpt("A4_two_dot_before_rebase.txt", 4, r"^\$|^diff"))
    code(excerpt("A4_three_dot_before_rebase.txt", 4, r"^\$|^diff"))
    text("Stash saved the unfinished preprocessing change, allowing a switch to main and back. stash list "
         "confirmed the saved entry before stash pop restored it.")
    code(excerpt("A5_stash.txt", 7, r"^\$|stash@|Dropped"))
    text("A hotfix branch changed README and was merged into main. Rebase replayed dev's commits on "
         "updated main, changing their commit IDs while preserving the incremental feature changes.")
    code(excerpt("A6_rebase_before.txt", 4))
    code(excerpt("A6_rebase_after.txt", 4))
    text("Soft reset moved HEAD back and left the scratch edit staged. Hard reset moved HEAD, index, "
         "and tracked working files back, discarding the second throwaway edit. Evidence branches preserve "
         "both throwaway commits. git mv reorganized prepare.py into src; git rm removed an obsolete file.")
    code(excerpt("A7_reset.txt", 9, r"^\$.*reset|^A |scratch-reset|HEAD is now"))
    code(excerpt("A8_rm.txt", 4, r"^\$|^rm |delete mode"))

    story.append(PageBreak())
    heading("Final parameters and pipeline")
    text("Each stage declares its inputs, outputs, and parameter dependencies. metrics.json is a DVC "
         "metric stored in Git with cache false. reports/ includes a cached copy of metrics and the "
         "confusion matrix, so evaluation artifacts are also uploaded to Drive.")
    config_table = Table([[Preformatted("params.yaml\n" + params, code_style),
                           Preformatted("dvc.yaml\n" + pipeline, code_style)]],
                         colWidths=[170, 345])
    config_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LEFTPADDING", (0,0), (-1,-1), 0)]))
    story.append(config_table)
    heading("Reproduction and selective rerun")
    code(excerpt("D3_repro_v1.txt", 4, r"Running stage"))
    code(excerpt("D4_repro_v2.txt", 5, r"Running stage|didn.t change|skipping"))
    text("Only train.dense_units changed from 128 to 256. Train reran because a declared parameter changed; "
         "evaluate reran because its model dependency changed. Prepare and preprocess were unchanged. "
         "dvc.lock records the resulting hashes and tracked parameter values. Tags v1 and v2 identify the runs.")

    story.append(PageBreak())
    heading("Google Drive tracking and conflict resolution")
    text("DVC was initialized on dev after the initial Git commit. The default remote is gdrive_storage. "
         "Standalone dvc add pointers first tracked raw data, processed data, models, and reports. Those "
         "pointers were removed when pipeline stages took ownership, preventing duplicate outputs. "
         "OAuth secrets are kept in ignored local config.")
    code(excerpt("C_tracking.txt", 5, r"^\$|Setting|remote"))
    text("For the required pointer-file conflict, processed data temporarily moved out of the preprocess "
         "pipeline stage into data/processed.dvc. teammate-sim divided pixels by 256; main capped them "
         "at 250 before division by 255. The same source line and data hash changed on both branches.")
    conflict = read("E3_code_conflict.txt").splitlines()
    begin = next(i for i, line in enumerate(conflict) if line.startswith("<<<<<<<"))
    end = next(i for i in range(begin, len(conflict)) if conflict[i].startswith(">>>>>>>"))
    code("src/preprocess.py\n" + "\n".join(conflict[begin:end+1]))
    code("data/processed.dvc\n" + read("E3_data_conflict.txt").strip())
    text("Resolution retains the canonical 255 divisor and adds defensive clipping to [0,255]. The merged "
         "code regenerates processed arrays; dvc add records their authoritative hash and dvc checkout "
         "synchronizes the working data. The full pipeline is then restored and reproduced.")
    code(excerpt("E4_resolution.txt", 5, r"^\$.*checkout|^\$.*status|up to date"))
    code(excerpt("E5_final_repro.txt", 4, r"Running stage|didn.t change|skipping"))
    code(excerpt("E5_final_status.txt", 3))
    heading("Final remote verification")
    code(excerpt("submission_cloud_status.txt", 4))
    screenshot = Image(str(drive_image))
    factor = min(460 / screenshot.imageWidth, 110 / screenshot.imageHeight)
    screenshot.drawWidth = screenshot.imageWidth * factor
    screenshot.drawHeight = screenshot.imageHeight * factor
    story.append(screenshot)
    text("The final publish step uploads DVC objects across all commits and pushes every assignment branch "
         "and tag to GitHub. The repository retains full console logs. The screenshot shows the verified "
         "Drive folder; instructor access must also be granted.")
    text("References: tensorflow.org/tutorials/keras/classification; "
         "dvc.org/doc/user-guide/project-structure/dvcyaml-files; "
         "dvc.org/doc/user-guide/data-management/remote-storage/google-drive.")

    output = ROOT / "submission/Assignment3_Hassan_Khan_23L-0800.pdf"
    output.parent.mkdir(exist_ok=True)

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(16*mm, 12*mm, "Hassan Khan | 23L-0800 | Assignment 3")
        canvas.drawRightString(A4[0]-16*mm, 12*mm, str(doc.page))

    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=16*mm,
                            rightMargin=16*mm, topMargin=14*mm, bottomMargin=20*mm,
                            title="Assignment 3 Fashion MNIST versioning", author="Hassan Khan")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    if doc.page != 4:
        raise SystemExit(f"Report has {doc.page} pages; adjust layout to meet the four-page limit before submitting.")
    print(f"Created {output}. Review every page and add the required screenshots before submission.")


if __name__ == "__main__":
    main()
