"""One-off: build the committed anonymized-UNSW npz from the raw UNSW-NB15 csvs.
Run once; commits worlds/budgeted/data/unsw_anon.npz. setup_data.py loads it at build time.
Loader + cost tiers mirror scratch/bakeoff/acq_gate_unsw.py. Structure mirrors make_data.py (TEP).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 0; BUDGET = 2
HERE = Path(__file__).resolve().parent
UNSW = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "unsw"

FREE = ['proto', 'service', 'state']
CONTENT = ['dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit', 'djit', 'swin',
           'stcpb', 'dtcpb', 'dwin', 'tcprtt', 'synack', 'ackdat', 'smean', 'dmean', 'trans_depth', 'response_body_len']
AGG = ['ct_srv_src', 'ct_state_ttl', 'ct_dst_ltm', 'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm',
       'is_ftp_login', 'ct_ftp_cmd', 'ct_flw_http_mthd', 'ct_src_ltm', 'ct_srv_dst', 'is_sm_ips_ports']

# --- load via the gate loader ---
tr = pd.read_csv(UNSW / "train.csv"); te = pd.read_csv(UNSW / "test.csv")
df = pd.concat([tr, te], ignore_index=True)
keep = {'Normal', 'Generic', 'Exploits', 'Fuzzers', 'DoS', 'Reconnaissance'}
df = df[df['attack_cat'].isin(keep)].reset_index(drop=True)
y, cls = pd.factorize(df['attack_cat']); n_classes = len(cls)
cols = FREE + CONTENT + AGG
for c in FREE:
    codes, _ = pd.factorize(df[c], use_na_sentinel=True); df[c] = np.where(codes < 0, np.nan, codes)
X = df[cols].astype(np.float32).to_numpy()
n_features = X.shape[1]

# --- per-feature cost vector: FREE=0, CONTENT=2, AGG=4 (individual features) ---
tier = {c: 0.0 for c in FREE}; tier.update({c: 2.0 for c in CONTENT}); tier.update({c: 4.0 for c in AGG})
costs = np.array([tier[c] for c in cols], dtype=float)

# --- subsample to a manageable stratified image (~12k/4k/4k) before anonymizing ---
N_TOTAL = 20000
if len(y) > N_TOTAL:
    X, _, y, _ = train_test_split(X, y, train_size=N_TOTAL, stratify=y, random_state=SEED)

# --- anonymize ---
rng = np.random.default_rng(SEED)
col_perm = rng.permutation(n_features)
X = X[:, col_perm]; costs = costs[col_perm]
y = rng.permutation(n_classes)[y]

# --- stratified split: 0.55 train, then 50/50 val/test of the remainder ---
strat = y if np.bincount(y).min() >= 2 else None
Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=0.55, stratify=strat, random_state=SEED)
strat2 = ytmp if np.bincount(ytmp).min() >= 2 else None
Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, train_size=0.5, stratify=strat2, random_state=SEED)

np.savez_compressed(HERE / "data" / "unsw_anon.npz",
    train_features=Xtr, train_labels=ytr.astype(np.int64),
    val_features=Xva, val_labels=yva.astype(np.int64),
    test_features=Xte, test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))

n0 = int((costs == 0).sum()); n2 = int((costs == 2).sum()); n4 = int((costs == 4).sum())
rarest = int(np.bincount(yte, minlength=n_classes)[np.bincount(yte, minlength=n_classes) > 0].min())
print(f"wrote unsw_anon.npz: train={len(ytr)} val={len(yva)} test={len(yte)} "
      f"feat={n_features} classes={n_classes} budget={BUDGET}")
print(f"  costs: free(0)={n0} content(2)={n2} agg(4)={n4}  rarest-test-class={rarest}")
