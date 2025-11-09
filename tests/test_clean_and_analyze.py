import pandas as pd

from scripts.clean_and_analyze import compute_nps, compute_basic_stats


def test_compute_basic_stats():
    df = pd.DataFrame({
        'satisfaction_score': [8, 7, 9, 6, 8, None],
        'other_num': [1, 2, 3, 4, 5, 6]
    })
    stats = compute_basic_stats(df, ['satisfaction_score'])
    assert 'metric' in stats.columns
    assert stats.loc[0, 'metric'] == 'satisfaction_score'
    mean_val = stats.loc[0, 'mean']
    assert 6.0 <= mean_val <= 9.0


def test_compute_nps():
    df = pd.DataFrame({'recommend_score': [10, 9, 8, 6, 5, 9, 10]})
    col, nps, breakdown = compute_nps(df, ['recommend_score'])
    assert col == 'recommend_score'
    assert isinstance(nps, float)
    assert -100.0 <= nps <= 100.0
    assert set(breakdown.index.tolist()) == {"Detractor", "Passive", "Promoter"}
