"""Run from the repository root: python -m src.analysis."""
from pathlib import Path
import hashlib
import json
import platform
import urllib.request
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
    confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score,
    RocCurveDisplay, PrecisionRecallDisplay)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/Telco-Customer-Churn.csv"
URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/1fd6fd70906479be1712e64cfc0ea89f58466629/data/Telco-Customer-Churn.csv"
SHA256 = "16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91"
SEED = 42
NUM = ["tenure", "MonthlyCharges", "TotalCharges"]

def load_data():
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=60) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest() != SHA256:
            raise ValueError("Source checksum mismatch; review upstream data.")
        DATA.write_bytes(payload)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Local dataset checksum mismatch.")
    df = pd.read_csv(DATA)
    for col in df.select_dtypes("object"):
        df[col] = df[col].str.strip()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    if df.shape != (7043, 21) or df.customerID.duplicated().any() or df.duplicated().any():
        raise ValueError("Unexpected dataset structure or duplicated customers.")
    if set(df.Churn) != {"Yes", "No"}:
        raise ValueError("Unexpected target labels.")
    missing = df.TotalCharges.isna()
    if missing.sum() != 11 or not df.loc[missing, "tenure"].eq(0).all():
        raise ValueError("Unexpected missing-value pattern.")
    # Preserve unknown charges. Median is learned inside each training fold.
    return df

def make_pipeline(X, estimator):
    cats = [c for c in X.columns if c not in NUM]
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scale", StandardScaler())])
    prep = ColumnTransformer([
        ("numeric", numeric, NUM),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats)])
    return Pipeline([("prepare", prep), ("model", estimator)])

def metrics(y, scores, threshold=0.5):
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(accuracy=float(accuracy_score(y, pred)), roc_auc=float(roc_auc_score(y, scores)),
        average_precision=float(average_precision_score(y, scores)),
        brier=float(brier_score_loss(y, scores)), precision=float(precision_score(y, pred, zero_division=0)),
        recall=float(recall_score(y, pred)), f1=float(f1_score(y, pred, zero_division=0)),
        contacts=int(pred.sum()), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))

def auc_interval(y, scores):
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    values = []
    for _ in range(1000):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) == 2:
            values.append(roc_auc_score(y[idx], scores[idx]))
    return np.quantile(values, [0.025, 0.975]).tolist()

def save_figure(fig, name, folder):
    fig.tight_layout()
    fig.savefig(folder / (name + ".png"), dpi=170, bbox_inches="tight")
    plt.close(fig)

def split_data(df):
    X, y = df.drop(columns=["customerID", "Churn"]), df.Churn.eq("Yes").astype(int)
    X_dev, X_test, y_dev, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, test_size=0.25, stratify=y_dev, random_state=SEED)
    assert not (set(X_train.index) & set(X_val.index) or set(X_train.index) & set(X_test.index)
                or set(X_val.index) & set(X_test.index))
    return X, y, X_train, X_val, X_test, y_train, y_val, y_test

def fit_candidates(X, X_train, y_train):
    warnings.filterwarnings("error", category=ConvergenceWarning)
    estimators = {
        "Dummy": DummyClassifier(strategy="prior"),
        "Logistic regression": LogisticRegression(max_iter=3000, random_state=SEED),
        "Random forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=5,
                                               random_state=SEED, n_jobs=1)}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_rows, fitted = [], {}
    for name, estimator in estimators.items():
        pipe = make_pipeline(X, estimator)
        scores = cross_validate(pipe, X_train, y_train, cv=cv,
            scoring={"auc": "roc_auc", "ap": "average_precision"}, error_score="raise", n_jobs=1)
        cv_rows.append({"model": name, "cv_auc_mean": float(scores["test_auc"].mean()),
                       "cv_auc_sd": float(scores["test_auc"].std(ddof=1)),
                       "cv_ap_mean": float(scores["test_ap"].mean())})
        fitted[name] = pipe.fit(X_train, y_train)
    return pd.DataFrame(cv_rows).set_index("model"), fitted

def run(df=None, prepared=None, trained=None):
    df = load_data() if df is None else df
    prepared = split_data(df) if prepared is None else prepared
    X, y, X_train, X_val, X_test, y_train, y_val, y_test = prepared
    cv_table, fitted = fit_candidates(X, X_train, y_train) if trained is None else trained
    selected = cv_table.drop(index="Dummy").cv_auc_mean.idxmax()
    # Freeze illustrative threshold on validation scores before looking at test.
    # 30% is an example contact capacity, not an observed client requirement.
    val_scores = fitted[selected].predict_proba(X_val)[:, 1]
    threshold = float(np.quantile(val_scores, 0.7, method="higher"))
    rows, test_scores = [], {}
    for name, model in fitted.items():
        p = model.predict_proba(X_test)[:, 1]
        test_scores[name] = p
        rows.append({"model": name, **metrics(y_test, p)})
    test_table = pd.DataFrame(rows).set_index("model")
    p = test_scores[selected]
    threshold_table = pd.DataFrame([{"policy": name, "threshold": t, **metrics(y_test, p, t)}
        for name, t in [("Default 0.5", 0.5), ("Illustrative 0.4", 0.4),
                        ("Validation capacity 30%", threshold)]])
    # Budget-constrained ranking evaluated at fixed, predeclared fractions.
    ranking = []
    order = np.argsort(-p, kind="stable")
    for share in [0.1, 0.2, 0.3]:
        k = int(np.ceil(len(y_test) * share))
        tp = int(y_test.iloc[order[:k]].sum())
        ranking.append({"capacity": share, "contacts": k, "churners_captured": tp,
            "precision": tp / k, "recall": tp / int(y_test.sum()),
            "lift_vs_random": (tp / k) / float(y_test.mean())})
    report = ROOT / "reports"
    figures = ROOT / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
        "axes.spines.right": False, "axes.titleweight": "bold", "figure.facecolor": "white"})
    # EDA on training only, so holdout is reserved for final evaluation.
    eda = df.loc[X_train.index].assign(churn=y_train)
    contract = eda.groupby("Contract").churn.agg(["mean", "count"]).sort_values("mean")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    bars = axes[0].barh(contract.index, contract["mean"], color="#167d9a")
    axes[0].set(xlabel="Observed churn proportion", title="Contract association — training sample", xlim=(0, .6))
    for bar, (_, row) in zip(bars, contract.iterrows()):
        axes[0].text(bar.get_width()+.01, bar.get_y()+bar.get_height()/2,
                     f"{row['mean']:.1%} (n={int(row['count'])})", va="center", fontsize=9)
    axes[1].hist([eda.loc[eda.churn.eq(0), "tenure"], eda.loc[eda.churn.eq(1), "tenure"]],
                 bins=12, label=["No churn", "Churn"], color=["#167d9a", "#ef9651"])
    axes[1].set(xlabel="Tenure (months)", ylabel="Customers", title="Tenure distribution — training sample")
    axes[1].legend()
    save_figure(fig, "customer_patterns", figures)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for name in fitted:
        RocCurveDisplay.from_predictions(y_test, test_scores[name], name=name, ax=axes[0])
        PrecisionRecallDisplay.from_predictions(y_test, test_scores[name], name=name, ax=axes[1])
    axes[0].set_title("Ranking quality — untouched test")
    axes[1].axhline(y_test.mean(), ls="--", color="grey", label="Churn prevalence")
    axes[1].set_title("Precision / recall trade-off")
    axes[1].legend(fontsize=8)
    save_figure(fig, "model_comparison", figures)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    observed, predicted = calibration_curve(y_test, p, n_bins=8, strategy="quantile")
    axes[0].plot(predicted, observed, "o-", color="#167d9a", label=selected)
    axes[0].plot([0, 1], [0, 1], "--", color="grey")
    axes[0].set(xlabel="Mean predicted score", ylabel="Observed churn rate",
                title="Calibration diagnostic")
    axes[1].bar(threshold_table.policy, threshold_table.contacts, color="#167d9a", label="Contacts")
    axes[1].bar(threshold_table.policy, threshold_table.tp, color="#ef9651", label="True positives")
    axes[1].tick_params(axis="x", labelsize=8)
    axes[1].set(ylabel="Customers in test sample", title="Workload is a decision constraint")
    axes[1].legend()
    save_figure(fig, "decision_tradeoffs", figures)
    logistic = fitted["Logistic regression"]
    coefficients = pd.Series(logistic["model"].coef_[0],
                             index=logistic["prepare"].get_feature_names_out()).sort_values()
    coefficients.rename("coefficient").to_csv(report / "logistic_coefficients.csv")
    cv_table.to_csv(report / "cross_validation.csv")
    test_table.to_csv(report / "test_metrics.csv")
    threshold_table.to_csv(report / "thresholds.csv", index=False)
    pd.DataFrame(ranking).to_csv(report / "capacity.csv", index=False)
    result = {
        "dataset_sha256": SHA256, "rows": len(df), "churn_count": int(y.sum()),
        "churn_rate": float(y.mean()), "missing_TotalCharges": 11,
        "split": {"train": len(X_train), "validation": len(X_val), "test": len(X_test)},
        "seed": SEED, "selected_by_training_cv": selected,
        "validation_capacity_threshold": threshold,
        "test_auc_bootstrap_95_interval": auc_interval(y_test, p),
        "validation_capacity_metrics": metrics(y_val, val_scores, threshold),
        "test_capacity_metrics": metrics(y_test, p, threshold),
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "pandas": pd.__version__, "sklearn": sklearn.__version__,
                     "matplotlib": matplotlib.__version__}}
    (report / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return dict(data=df, cv=cv_table, test=test_table, thresholds=threshold_table,
                capacity=pd.DataFrame(ranking), summary=result, coefficients=coefficients)

if __name__ == "__main__":
    result = run()
    print(result["cv"].round(4).to_string())
    print(result["test"].round(4).to_string())
    print(json.dumps(result["summary"], indent=2))
