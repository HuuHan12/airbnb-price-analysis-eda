"""Kiểm chứng T11: truy vết, đối chiếu metrics, nhóm và các đầu vào hỏng."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import nbformat
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.residual_tasks import load_checked_predictions, metrics


def verify():
    config, comparison, predictions, winner = load_checked_predictions(ROOT)
    selected = predictions.loc[predictions.model_id.eq(winner)]
    groups = pd.read_csv(ROOT / 'outputs/tables/b_residual_group_metrics.csv')
    summary = json.loads((ROOT / 'reports/b_residual_summary.json').read_text(encoding='utf-8'))
    checks = ['All five predictions match raw holdout, actual values, residuals and T10 metrics']
    for field, value in metrics(selected).items():
        assert np.isclose(summary[field], value), field
    checks.append('Summary metrics recomputed from checked predictions')
    for grouping in groups.grouping.unique():
        part = groups.loc[groups.grouping.eq(grouping)]
        assert part.n.sum() == len(selected), grouping
        assert np.isclose((part.mse * part.n).sum() / part.n.sum(), summary['mse'])
        assert np.isclose((part.mae * part.n).sum() / part.n.sum(), summary['mae'])
        for _, row in part.iterrows():
            actual_group = selected
            for col in grouping.split('+'):
                actual_group = actual_group.loc[actual_group[col].eq(row[col])]
            for metric, expected in metrics(actual_group).items():
                assert np.isclose(row[metric], expected, equal_nan=True), (grouping, metric)
        checks.append('Group n/weighted errors/per-group metrics reconcile: ' + grouping)
    cases = pd.read_csv(ROOT / 'outputs/tables/b_residual_cases.csv')
    expected = selected.nlargest(10, 'abs_residual')
    assert cases[config['trace_keys']].values.tolist() == expected[config['trace_keys']].values.tolist()
    checks.append('Top ten cases are correct with original source keys')
    concentration = pd.read_csv(ROOT / 'outputs/tables/b_residual_error_concentration.csv')
    ordered = selected.sort_values('squared_residual', ascending=False)
    for row in concentration.itertuples():
        assert row.n == int(np.ceil(len(selected) * row.largest_error_percent / 100))
        assert np.isclose(row.share_total_sse, ordered.head(row.n).squared_residual.sum() / ordered.squared_residual.sum())
    checks.append('Error concentration recomputed with all test rows retained')
    original_read = pd.read_csv
    raw_preds = original_read(ROOT / 'outputs/tables/test_predictions.csv')
    for defect in ['actual', 'residual', 'protocol', 'duplicate_key', 'nonfinite', 'selection']:
        corrupt = raw_preds.copy()
        comparison_corrupt = comparison.copy()
        if defect == 'actual': corrupt.loc[0, 'actual'] += 1
        elif defect == 'residual': corrupt.loc[0, 'residual'] += 1
        elif defect == 'protocol': corrupt.loc[0, 'protocol_id'] = 'bad'
        elif defect == 'duplicate_key': corrupt.loc[0, config['trace_keys']] = corrupt.loc[1, config['trace_keys']].values
        elif defect == 'nonfinite': corrupt.loc[0, 'predicted'] = np.inf
        else:
            comparison_corrupt['selected_winning_model'] = comparison_corrupt.model_id.eq('M0')
        def fake_read(path, *args, **kwargs):
            if Path(path).name == 'test_predictions.csv': return corrupt.copy()
            if Path(path).name == 'model_comparison_cv_vs_test.csv': return comparison_corrupt.copy()
            return original_read(path, *args, **kwargs)
        with patch('pandas.read_csv', side_effect=fake_read):
            try:
                load_checked_predictions(ROOT)
            except ValueError:
                checks.append('Rejected corrupt input: ' + defect)
            else:
                raise AssertionError('Failed to reject ' + defect)
    nb = nbformat.read(ROOT / 'notebooks/05_residual_analysis.ipynb', as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            assert cell.execution_count is not None
            assert not any(o.output_type == 'error' for o in cell.outputs)
    checks.append('T11 notebook code cells executed without errors')
    result = {'task': 'T11', 'all_passed': True, 'checks': checks,
              'scope': 'Snapshot verification and negative-input guards; not instructor acceptance'}
    (ROOT / 'reports/b_residual_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    verify()
