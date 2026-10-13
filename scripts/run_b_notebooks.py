"""Chạy lại notebook B từ kernel mới, không cần mở giao diện Jupyter.

Từ root repo: python scripts/run_b_notebooks.py
Sau đó: python scripts/verify_b_handoff.py
"""
from pathlib import Path
from importlib.metadata import version
import os
import sys
import json
import time

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def run():
    runtime = ROOT / '.ipynb_checkpoints/b_runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime / 'jupyter')
    os.environ['IPYTHONDIR'] = str(runtime / 'ipython')
    os.environ['JUPYTER_PATH'] = str(Path(sys.prefix) / 'share/jupyter')
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    packages = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'scikit-learn',
                'joblib', 'nbformat', 'nbclient', 'ipykernel']
    records = []
    for name in ['02_exploratory_data_analysis.ipynb', '03b_polynomial_ridge.ipynb']:
        path = ROOT / 'notebooks' / name
        nb = nbformat.read(path, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
        start = time.time()
        print('Executing fresh kernel:', name, flush=True)
        NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=False,
                       resources={'metadata': {'path': str(ROOT / 'notebooks')}}).execute()
        nbformat.write(nb, path)
        records.append({'notebook': name, 'success': True,
                        'executed_code_cells': sum(c.cell_type == 'code' and c.execution_count is not None for c in nb.cells),
                        'seconds': round(time.time() - start, 2)})
    report = {'runs': records, 'versions': {p: version(p) for p in packages},
              'test_model_metrics_computed': False}
    (ROOT / 'reports/b_notebook_runs.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run()
