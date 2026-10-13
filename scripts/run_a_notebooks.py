"""Chạy lại notebook 03a_linear_regression_models.ipynb từ kernel mới và lưu output.

Từ root repo: python scripts/run_a_notebooks.py
Sau đó: python scripts/verify_a_t08.py
"""
import json
import os
import sys
import time
from importlib.metadata import version
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def run():
    runtime = ROOT / '.ipynb_checkpoints/a_runtime'
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
    
    target_notebook = '03a_linear_regression_models.ipynb'
    path = ROOT / 'notebooks' / target_notebook
    
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            
    start = time.time()
    print(f'Executing fresh kernel: {target_notebook}', flush=True)
    NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=False,
                   resources={'metadata': {'path': str(ROOT / 'notebooks')}}).execute()
    nbformat.write(nb, path)
    
    executed_cells = sum(c.cell_type == 'code' and c.execution_count is not None for c in nb.cells)
    records.append({
        'notebook': target_notebook,
        'success': True,
        'executed_code_cells': executed_cells,
        'total_cells': len(nb.cells),
        'seconds': round(time.time() - start, 2)
    })
    
    report = {
        'runs': records,
        'versions': {p: version(p) for p in packages},
        'test_model_metrics_computed': False,
        'protocol_id': 'ie313_raw_v1_seed0_cv5'
    }
    
    report_path = ROOT / 'reports/a_notebook_runs.json'
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    return report


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run()
