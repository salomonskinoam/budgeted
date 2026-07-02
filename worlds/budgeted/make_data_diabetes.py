"""One-off: build the committed anonymized Diabetes-130 npz (binary 30-day readmission).

Mirrors make_data.py (TEP). Loader + costs reuse scratch/bakeoff/acq_gate_diabetes.py.
Grouped acquisition -> per-feature: each feature costs group_cost / group_size, so buying a
whole group costs exactly the group cost. No free features (all 6 groups acquirable).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 0
BUDGET = 3
HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "diabetes130" / "diabetic_data.csv"

GROUPS = {                                        # group -> (cost, columns)
    "admin":   (1, ["admission_type_id", "admission_source_id", "discharge_disposition_id",
                    "time_in_hospital", "medical_specialty", "payer_code"]),
    "util":    (1, ["number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses"]),
    "meds":    (1, ["metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
                    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
                    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide", "examide",
                    "citoglipton", "insulin", "glyburide-metformin", "glipizide-metformin",
                    "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone",
                    "change", "diabetesMed"]),
    "process": (3, ["num_lab_procedures", "num_procedures", "num_medications"]),
    "diag":    (3, ["diag_1", "diag_2", "diag_3"]),     # GATE (cheaper than labs)
    "labs":    (9, ["max_glu_serum", "A1Cresult"]),     # GATED expensive lab
}


def icd_bucket(code):
    if pd.isna(code) or code in ("?",):
        return "NA"
    s = str(code)
    if s.startswith(("V", "E")):
        return "Other"
    try:
        v = float(s)
    except ValueError:
        return "Other"
    if int(v) == 250:
        return "Diabetes"
    if 390 <= v <= 459 or v == 785: return "Circulatory"
    if 460 <= v <= 519 or v == 786: return "Respiratory"
    if 520 <= v <= 579 or v == 787: return "Digestive"
    if 580 <= v <= 629 or v == 788: return "Genitourinary"
    if 800 <= v <= 999: return "Injury"
    if 710 <= v <= 739: return "Musculoskeletal"
    if 140 <= v <= 239: return "Neoplasm"
    return "Other"


def main():
    # --- load via the gate loader (raw group member features only, no FREE) ---
    df = pd.read_csv(DATA, na_values=["?"], low_memory=False)
    df = df[~df["discharge_disposition_id"].isin([11, 13, 14, 19, 20, 21])]   # drop death/hospice
    y = (df["readmitted"] == "<30").astype(int).to_numpy()
    for d in ("diag_1", "diag_2", "diag_3"):
        df[d] = df[d].map(icd_bucket)

    all_cols = [c for _, cols in GROUPS.values() for c in cols]
    X = df[all_cols].copy()
    for c in X.columns:                            # factorize categoricals -> numeric codes
        if not pd.api.types.is_numeric_dtype(X[c]):
            codes, _ = pd.factorize(X[c], use_na_sentinel=True)
            X[c] = np.where(codes < 0, np.nan, codes).astype(np.float32)
        else:
            X[c] = X[c].astype(np.float32)
    X = X.to_numpy(np.float32)

    # --- per-feature cost = group_cost / group_size (buying a full group == group cost) ---
    costs = np.concatenate([
        np.full(len(cols), cost / len(cols), np.float32) for cost, cols in GROUPS.values()
    ])
    assert costs.shape[0] == X.shape[1]

    # --- subsample to a manageable size, stratified, keeping the ~11-12% positive rate ---
    n_keep = 75000 + 12000 + 12000
    X, _, y, _ = train_test_split(X, y, train_size=n_keep, stratify=y, random_state=SEED)

    # --- anonymize: col_perm (costs travel), relabel classes ---
    rng = np.random.default_rng(SEED)
    col_perm = rng.permutation(X.shape[1])
    X = X[:, col_perm]; costs = costs[col_perm]
    y = rng.permutation(2)[y]

    # --- split 75k / 12k / 12k, stratified ---
    Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=75000, stratify=y, random_state=SEED)
    Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, test_size=12000, stratify=ytmp, random_state=SEED)

    out = HERE / "data" / "diabetes_anon.npz"
    np.savez_compressed(out,
        train_features=Xtr, train_labels=ytr.astype(np.int64),
        val_features=Xva, val_labels=yva.astype(np.int64),
        test_features=Xte, test_labels=yte.astype(np.int64),
        costs=costs.astype(np.float32), budget=np.float32(BUDGET))

    uc, cnt = np.unique(np.round(costs, 6), return_counts=True)
    # minority (readmit-<30) class after the anonymizing relabel
    minlab = int(np.bincount(ytr).argmin())
    print(f"wrote {out.name}: train={len(ytr)} val={len(yva)} test={len(yte)} "
          f"n_features={X.shape[1]} n_classes={len(np.unique(y))} budget={BUDGET}")
    print("  distinct costs (value: count): " + ", ".join(f"{v:.4f}:{c}" for v, c in zip(uc, cnt)))
    print(f"  positive (readmit-<30, relabeled={minlab}) rate: "
          f"train={(ytr == minlab).mean():.3f} val={(yva == minlab).mean():.3f} "
          f"test={(yte == minlab).mean():.3f}  test positive count={int((yte == minlab).sum())}")


if __name__ == "__main__":
    main()
