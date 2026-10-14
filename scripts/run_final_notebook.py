"""Execute the single final notebook in a fresh kernel and verify the run."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from importlib.metadata import version

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def raw_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'data/raw').glob('*.csv'))}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    runtime = ROOT / '.ipynb_checkpoints/final_runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime / 'jupyter')
    os.environ['IPYTHONDIR'] = str(runtime / 'ipython')
    os.environ['JUPYTER_PATH'] = str(Path(sys.prefix) / 'share/jupyter')
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    path = ROOT / 'notebooks/IE313_Airbnb_Final.ipynb'
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    before = raw_hashes()
    start = time.time()
    print('Chạy notebook cuối từ kernel mới...', flush=True)
    NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=False,
                   resources={'metadata': {'path': str(ROOT / 'notebooks')}}).execute()
    nbformat.write(nb, path)
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert [c.execution_count for c in code_cells] == list(range(1, len(code_cells) + 1))
    assert not any(o.output_type == 'error' for c in code_cells for o in c.outputs)
    assert raw_hashes() == before, 'Raw CSV changed while running'
    evidence = json.loads((ROOT / 'outputs/final_notebook/run_evidence.json').read_text(encoding='utf-8'))
    assert evidence['all_assertions_passed'] and evidence['raw_csv_sha256'] == before
    images = sum('image/png' in o.get('data', {}) for c in code_cells for o in c.outputs)
    assert images >= 8, 'Missing inline figures'
    log = {'notebook': path.name, 'fresh_kernel': True, 'success': True,
           'code_cells': len(code_cells), 'inline_figures': images,
           'raw_data_unchanged': True, 'seconds': round(time.time()-start, 2),
           'versions': {p: version(p) for p in ['numpy', 'pandas', 'matplotlib',
                        'seaborn', 'scipy', 'scikit-learn', 'nbformat', 'nbclient', 'ipykernel']},
           'evidence': evidence}
    (ROOT / 'reports/final_notebook_runs.json').write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in log.items() if k not in ['evidence', 'versions']},
                     ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
