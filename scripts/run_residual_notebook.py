"""Thực thi T11 từ kernel mới và lưu bằng chứng chạy thật."""
import json
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def run():
    runtime = ROOT / '.ipynb_checkpoints/residual_runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ.update(JUPYTER_RUNTIME_DIR=str(runtime / 'jupyter'), IPYTHONDIR=str(runtime / 'ipython'),
                      JUPYTER_PATH=str(Path(sys.prefix) / 'share/jupyter'), MPLBACKEND='Agg',
                      OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    path = ROOT / 'notebooks/05_residual_analysis.ipynb'
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=False,
                   resources={'metadata': {'path': str(ROOT / 'notebooks')}}).execute()
    nbformat.write(nb, path)
    report = {'notebook': path.name, 'success': True, 'fresh_kernel': True,
              'executed_code_cells': sum(c.cell_type == 'code' for c in nb.cells),
              'model_fit_performed': False, 'holdout_tuning_performed': False}
    (ROOT / 'reports/b_residual_notebook_run.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run()
