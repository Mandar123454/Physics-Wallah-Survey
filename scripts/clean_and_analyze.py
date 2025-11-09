from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd

# Optional dependencies
try:
    from textblob import TextBlob  # type: ignore
except Exception:  # pragma: no cover
    TextBlob = None

try:
    import seaborn as sns  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # pragma: no cover
    sns = None
    plt = None

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
EXCEL_PATH = ROOT / "Physics Wallah Survey  (Responses).xlsx"
CLEAN_CSV = DATA_DIR / "cleaned_responses.csv"
SUMMARY_MD = ARTIFACTS_DIR / "summary.md"
FIG_DIR = ARTIFACTS_DIR / "figures"


PII_PATTERNS = re.compile(r"email|e-mail|mail|name|phone|mobile|contact|roll|address|reg(istration)?|id$|^id", re.I)
LIKERT_PATTERNS = re.compile(r"satisf|rate|overall|experience|quality|usability|value", re.I)
RECOMMEND_PATTERNS = re.compile(r"recommend|nps|likelihood", re.I)
OPEN_TEXT_PATTERNS = re.compile(r"comment|feedback|suggest|why|describe|text|other", re.I)


def load_data() -> pd.DataFrame:
    if EXCEL_PATH.exists():
        df = pd.read_excel(EXCEL_PATH)
    elif CLEAN_CSV.exists():
        df = pd.read_csv(CLEAN_CSV)
    else:
        raise FileNotFoundError(
            f"No input found. Expected Excel at {EXCEL_PATH} or CSV at {CLEAN_CSV}"
        )
    return df


def anonymize(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_drop = [c for c in df.columns if PII_PATTERNS.search(str(c))]
    return df.drop(columns=cols_to_drop, errors="ignore")


def find_candidate_columns(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    # satisfaction-like numeric
    sat_cols = [
        c for c in df.columns
        if LIKERT_PATTERNS.search(str(c)) and pd.api.types.is_numeric_dtype(df[c])
    ]
    # recommend/NPS column
    rec_cols = [
        c for c in df.columns
        if RECOMMEND_PATTERNS.search(str(c)) and pd.api.types.is_numeric_dtype(df[c])
    ]
    # open text
    text_cols = [
        c for c in df.columns
        if pd.api.types.is_object_dtype(df[c]) and OPEN_TEXT_PATTERNS.search(str(c))
    ]
    return sat_cols, rec_cols, text_cols


def compute_basic_stats(df: pd.DataFrame, sat_cols: List[str]) -> pd.DataFrame:
    out = []
    for c in sat_cols[:5]:  # limit to a few
        s = df[c].dropna()
        out.append({
            "metric": c,
            "count": int(s.count()),
            "mean": float(s.mean()),
            "std": float(s.std(ddof=0)),
            "min": float(s.min()),
            "p25": float(s.quantile(0.25)),
            "median": float(s.median()),
            "p75": float(s.quantile(0.75)),
            "max": float(s.max()),
        })
    return pd.DataFrame(out)


def compute_nps(df: pd.DataFrame, rec_cols: List[str]) -> Tuple[str | None, float | None, pd.Series | None]:
    if not rec_cols:
        return None, None, None
    c = rec_cols[0]
    scores = df[c].dropna()
    # normalize to 0-10 if looks like 1-5 scale
    if scores.max() <= 5:
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9) * 10
    promoters = (scores >= 9).mean()
    detractors = (scores <= 6).mean()
    nps = (promoters - detractors) * 100
    buckets = pd.cut(scores, bins=[-1,6,8,10], labels=["Detractor","Passive","Promoter"])
    return c, float(nps), buckets.value_counts(normalize=True).reindex(["Detractor","Passive","Promoter"]).fillna(0)


def analyze_open_text(df: pd.DataFrame, text_cols: List[str]) -> pd.DataFrame | None:
    if not text_cols:
        return None
    if TextBlob is None:
        return None
    col = text_cols[0]
    texts = df[col].dropna().astype(str)
    if texts.empty:
        return None
    sentiment = texts.apply(lambda t: TextBlob(t).sentiment.polarity)
    res = pd.DataFrame({
        "column": col,
        "count": [int(len(texts))],
        "mean_polarity": [float(sentiment.mean())],
        "p25": [float(sentiment.quantile(0.25))],
        "median": [float(sentiment.median())],
        "p75": [float(sentiment.quantile(0.75))],
    })
    return res


def plot_distributions(df: pd.DataFrame, out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    if sns is None or plt is None:
        return paths

    # numeric distributions (up to 4)
    num_cols = [c for c in df.select_dtypes(include="number").columns][:4]
    for c in num_cols:
        ax = sns.histplot(df[c].dropna(), kde=True)
        ax.set_title(f"Distribution: {c}")
        p = out_dir / f"dist_{re.sub(r'[^a-zA-Z0-9_]+','_',c)}.png"
        plt.tight_layout(); plt.savefig(p, dpi=150); plt.clf()
        paths.append(p)

    # top categorical counts (up to 4 with low cardinality)
    cat_cols = [c for c in df.select_dtypes(include="object").columns if df[c].nunique() <= 10][:4]
    for c in cat_cols:
        ax = sns.countplot(y=df[c])
        ax.set_title(f"Counts: {c}")
        p = out_dir / f"counts_{re.sub(r'[^a-zA-Z0-9_]+','_',c)}.png"
        plt.tight_layout(); plt.savefig(p, dpi=150); plt.clf()
        paths.append(p)

    return paths


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df = anonymize(df)

    # persist cleaned data
    try:
        df.to_csv(CLEAN_CSV, index=False)
    except Exception as e:
        print(f"Warning: could not write cleaned CSV: {e}")

    sat_cols, rec_cols, text_cols = find_candidate_columns(df)
    stats_df = compute_basic_stats(df, sat_cols) if sat_cols else pd.DataFrame()
    rec_col, nps, nps_breakdown = compute_nps(df, rec_cols)
    text_df = analyze_open_text(df, text_cols)
    figs = plot_distributions(df, FIG_DIR)

    # write summary
    lines = [
        "# Summary",
        "",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns):,}",
        "",
        "## Basic statistics",
    ]
    if not stats_df.empty:
        lines.append(stats_df.to_markdown(index=False))
    else:
        lines.append("No numeric satisfaction-like columns detected.")

    lines.append("")
    lines.append("## NPS-style score")
    if nps is not None:
        lines.append(f"Column: `{rec_col}` | NPS: {nps:.1f}")
        if nps_breakdown is not None:
            bd = (nps_breakdown * 100).round(1).astype(str) + '%'
            lines.append(bd.to_markdown())
    else:
        lines.append("No recommendation/NPS column detected.")

    lines.append("")
    lines.append("## Open-ended sentiment")
    if text_df is not None and not text_df.empty:
        lines.append(text_df.to_markdown(index=False))
    else:
        lines.append("No open-ended feedback column detected or TextBlob not installed.")

    lines.append("")
    lines.append("## Figures")
    if figs:
        for p in figs:
            rel = p.relative_to(ROOT)
            lines.append(f"- {rel.as_posix()}")
    else:
        lines.append("No figures generated (seaborn/matplotlib not available or no suitable columns).")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote summary to {SUMMARY_MD}")
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
