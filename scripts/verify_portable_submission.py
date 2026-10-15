"""Developer-side checks; the delivered notebook needs only its adjacent CSV."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import time
from datetime import datetime
from importlib.metadata import version

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAME = 'IE313_Airbnb_Final.ipynb'
CSV = 'airbnb_combined.csv'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(path):
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs, cell.execution_count = [], None
    return nb


def execute(nb, folder):
    return NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=False,
                          resources={'metadata': {'path': str(folder)}}).execute()


def full_check(folder, name, raw_hash):
    assert {p.name for p in folder.iterdir()} == {name, CSV}
    nb = clean(folder / name)
    # Verifier-only probe is discarded before saving the submission notebook.
    nb.cells.append(nbformat.v4.new_code_cell('''display(JSON({
        'manifest': manifest.to_csv(index=False, lineterminator='\\n'),
        'groups': group_summary.to_csv(index=False),
        'predictions': predictions[['model_id','source_file','source_row','actual','predicted','residual']].to_csv(index=False)
    }))'''))
    start = time.time()
    execute(nb, folder)
    payload = next(o['data']['application/json'] for o in nb.cells[-1].outputs
                   if 'application/json' in o.get('data', {}))
    nb.cells.pop()
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert [c.execution_count for c in code_cells] == list(range(1, len(code_cells)+1))
    assert not any(o.output_type == 'error' for c in code_cells for o in c.outputs)
    evidence = next(o['data']['application/json'] for c in reversed(code_cells) for o in c.outputs
                    if 'application/json' in o.get('data', {}) and 'all_assertions_passed' in o['data']['application/json'])
    assert evidence['all_assertions_passed']
    comparison = pd.DataFrame(evidence['comparison']).set_index('model_id').sort_index()
    reference = pd.read_csv(ROOT / 'outputs/tables/model_comparison_cv_vs_test.csv').set_index('model_id').sort_index()
    metrics = [c for c in reference.columns if c.startswith(('cv_', 'test_'))]
    np.testing.assert_allclose(comparison[metrics], reference[metrics], rtol=1e-8, atol=1e-6)
    pd.testing.assert_frame_equal(pd.read_csv(io.StringIO(payload['manifest'])),
                                  pd.read_csv(ROOT / 'data/processed/split_manifest.csv'))
    pd.testing.assert_frame_equal(pd.read_csv(io.StringIO(payload['groups'])),
                                  pd.read_csv(ROOT / 'outputs/tables/eda_group_summary.csv'),
                                  check_exact=False, rtol=1e-9, atol=1e-8)
    predictions = pd.read_csv(io.StringIO(payload['predictions']))
    keys = ['model_id', 'source_file', 'source_row']
    expected = pd.read_csv(ROOT / 'outputs/tables/test_predictions.csv')
    assert not predictions.duplicated(keys).any() and len(predictions) == 51710
    aligned = predictions.merge(expected[keys + ['actual','predicted','residual']],
                                on=keys, how='outer', validate='one_to_one', indicator=True)
    assert aligned['_merge'].eq('both').all()
    for metric in ['actual', 'predicted', 'residual']:
        np.testing.assert_allclose(aligned[metric+'_x'], aligned[metric+'_y'], rtol=1e-8, atol=1e-6)
    assert {p.name for p in folder.iterdir()} == {name, CSV}, 'Notebook created extra files'
    assert digest(folder / CSV) == raw_hash
    images = sum('image/png' in o.get('data', {}) for c in code_cells for o in c.outputs)
    assert images >= 8
    nbformat.write(nb, folder / name)
    return nb, evidence, {'folder': str(folder), 'notebook': name,
        'fresh_kernel': True, 'code_cells': len(code_cells), 'inline_figures': images,
        'exactly_two_files_before_and_after': True, 'csv_unchanged': True,
        'all_51710_predictions_match': True, 'manifest_and_groups_match': True,
        'all_cv_test_metrics_match': True, 'seconds': round(time.time()-start, 2)}


def negative_check(folder, template, corrupt=False):
    folder.mkdir(parents=True)
    nb = clean(template)
    nb.cells = [c for c in nb.cells if c.cell_type == 'code'][:2]
    if corrupt:
        shutil.copy2(ROOT / 'data/processed' / CSV, folder / CSV)
        with (folder / CSV).open('ab') as f:
            f.write(b'\n')
    try:
        execute(nb, folder)
    except CellExecutionError as error:
        expected = 'CSV không khớp snapshot' if corrupt else 'Thiếu airbnb_combined.csv'
        assert expected in str(error), str(error)[-1000:]
        return {'case': 'changed_csv' if corrupt else 'missing_csv', 'clear_early_error': True}
    raise AssertionError('Invalid input did not fail early')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    runtime = ROOT / '.ipynb_checkpoints/final_runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    for key, value in {'JUPYTER_RUNTIME_DIR': runtime / 'jupyter', 'IPYTHONDIR': runtime / 'ipython',
                       'JUPYTER_PATH': Path(sys.prefix) / 'share/jupyter'}.items():
        os.environ[key] = str(value)
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    os.environ['OMP_NUM_THREADS'] = os.environ['OPENBLAS_NUM_THREADS'] = '1'
    template = ROOT / 'notebooks' / NAME
    csv_path = ROOT / 'data/processed' / CSV
    raw_hash = digest(csv_path)
    check_root = ROOT.parent / '_review' / ('portable_check_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    source = '\n'.join(c.source for c in nbformat.read(template, as_version=4).cells if c.cell_type == 'code')
    for forbidden in ['read_text(', 'write_text(', 'to_csv(path', 'data/raw', 'config/', 'read_csv(ROOT', 'from src', 'import src', 'mkdir(']:
        assert forbidden not in source, forbidden
    assert source.count('pd.read_csv(') == 1
    results = []
    for directory, name in [('only_two_files', NAME), ('Bài nộp đổi tên và dấu cách', 'Bai nop doi ten.ipynb')]:
        folder = check_root / directory
        folder.mkdir(parents=True)
        shutil.copy2(template, folder / name)
        shutil.copy2(csv_path, folder / CSV)
        print('Fresh isolated run:', directory, flush=True)
        nb, evidence, record = full_check(folder, name, raw_hash)
        results.append(record)
        if directory == 'only_two_files':
            nbformat.write(nb, template)
            final_evidence = evidence
    print('Checking missing/changed CSV guards...', flush=True)
    negatives = [negative_check(check_root / 'missing_csv', template),
                 negative_check(check_root / 'changed_csv', template, corrupt=True)]
    assert digest(csv_path) == raw_hash
    submission = ROOT / 'submission'
    submission.mkdir(exist_ok=True)
    assert not set(p.name for p in submission.iterdir()) - {NAME, CSV}, 'Unexpected submission files'
    shutil.copy2(template, submission / NAME)
    shutil.copy2(csv_path, submission / CSV)
    shutil.copy2(csv_path, ROOT / 'notebooks' / CSV)
    log = {'success': True, 'submission_files': [NAME, CSV], 'external_json_required': False,
           'runtime_writes_files': False, 'data_sha256_bytes': raw_hash,
           'runs': results, 'negative_checks': negatives,
           'versions': {p: version(p) for p in ['numpy','pandas','matplotlib','seaborn',
                                               'scipy','scikit-learn','nbformat','nbclient','ipykernel']},
           'evidence': final_evidence}
    (ROOT / 'reports/final_notebook_runs.json').write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'success': True, 'full_runs': len(results), 'negative_checks': negatives,
                      'submission_folder': str(submission)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
