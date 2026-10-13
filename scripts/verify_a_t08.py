"""Kịch bản kiểm thử nghiệm thu toàn diện Task T08 (Thành viên A).

Kiểm toán 5 Cổng Kỹ thuật (5 Audit Gates):
1. Tệp tin Sản phẩm (Artifacts Integrity Gate)
2. Bảo vệ Tập Test (Holdout Isolation & Anti-Leakage Gate)
3. Đẳng thức Toán học (Mathematical Consistency Gate)
4. Thứ bậc Cải thiện & Quá khớp (Monotonic Improvement & Overfitting Gate)
5. Tính Tái lập Notebook (Notebook Reproducibility Gate)

Sử dụng: python scripts/verify_a_t08.py
"""
import json
import sys
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.experiment import load_protocol


def run_gate(gate_name, test_func):
    """Chạy một cổng kiểm toán và in kết quả chi tiết."""
    print(f"\n========================================================")
    print(f"BẮT ĐẦU {gate_name.upper()}")
    print(f"========================================================")
    try:
        details = test_func()
        print(f"-> KẾT QUẢ: [PASSED] 100% ĐẠT TIÊU CHUẨN")
        return {"gate": gate_name, "status": "PASSED", "details": details}
    except Exception as e:
        print(f"-> KẾT QUẢ: [FAILED] LỖI: {e}")
        return {"gate": gate_name, "status": "FAILED", "error": str(e)}


def test_gate_1_artifacts():
    """Cổng 1: Kiểm tra sự tồn tại và kích thước của các file sản phẩm đầu ra."""
    required_files = [
        # Bảng dữ liệu CV
        ROOT / "outputs/tables/a_models_cv_summary.csv",
        ROOT / "outputs/tables/a_models_cv_folds.csv",
        ROOT / "outputs/tables/a_m2_coefficients.csv",
        # Hình ảnh trực quan hóa
        ROOT / "outputs/figures/fig_04_m1_regression_plot.png",
        ROOT / "outputs/figures/fig_05_m2_coefficients.png",
        # Mô hình huấn luyện
        ROOT / "models/M0_A_train_only.joblib",
        ROOT / "models/M1_A_train_only.joblib",
        ROOT / "models/M2_A_train_only.joblib",
        # Cấu hình & Báo cáo
        ROOT / "config/a_selected_models.json",
        ROOT / "reports/a_model_findings.md",
        ROOT / "reports/a_notebook_runs.json",
        ROOT / "notebooks/03a_linear_regression_models.ipynb"
    ]
    
    file_stats = []
    for f in required_files:
        assert f.exists(), f"Thiếu file sản phẩm: {f.relative_to(ROOT)}"
        size = f.stat().st_size
        assert size > 0, f"File rỗng (0 bytes): {f.relative_to(ROOT)}"
        file_stats.append({"file": str(f.relative_to(ROOT)), "size_bytes": size})
        print(f"  [OK] {f.relative_to(ROOT)} ({size:,} bytes)")
        
    return file_stats


def test_gate_2_anti_leakage():
    """Cổng 2: Kiểm tra chống rò rỉ tập Test và tính cô lập dữ liệu."""
    config, train, heldout_test, cv = load_protocol(ROOT)
    summary_path = ROOT / "outputs/tables/a_models_cv_summary.csv"
    folds_path = ROOT / "outputs/tables/a_models_cv_folds.csv"
    
    summary_df = pd.read_csv(summary_path)
    folds_df = pd.read_csv(folds_path)
    
    # 1. Số dòng train đúng chuẩn
    assert summary_df['n_train'].iloc[0] == 41365, f"Sai số mẫu train: {summary_df['n_train'].iloc[0]}"
    assert len(train) == 41365
    assert len(heldout_test) == 10342
    
    # 2. Không chứa cột test evaluation
    for col in summary_df.columns:
        assert not col.startswith('test_'), f"Bảng summary chứa cột test rò rỉ: {col}"
    for col in folds_df.columns:
        assert not col.startswith('test_'), f"Bảng folds chứa cột test rò rỉ: {col}"
        
    # 3. Kích thước từng fold
    assert len(folds_df) == 15, f"Số dòng folds phải là 15, thực tế: {len(folds_df)}"
    assert (folds_df['n_fold_train'] == 33092).all(), "Kích thước fold train phải là 33.092"
    assert (folds_df['n_fold_validation'] == 8273).all(), "Kích thước fold validation phải là 8.273"
    
    print(f"  [OK] Kích thước tập Train: {len(train):,} dòng | Tập Test cô lập: {len(heldout_test):,} dòng")
    print(f"  [OK] Không có bất kỳ cột/chỉ số nào của Holdout Test bị rò rỉ vào bảng của A")
    print(f"  [OK] Kích thước từng Fold CV: Train={33092:,}, Validation={8273:,} (Tổng={41365:,})")
    
    return {"n_train": 41365, "n_test_isolated": 10342, "n_folds": 5}


def test_gate_3_math_identities():
    """Cổng 3: Kiểm tra đẳng thức toán học RMSE^2 == MSE và thống kê chuẩn."""
    folds_path = ROOT / "outputs/tables/a_models_cv_folds.csv"
    summary_path = ROOT / "outputs/tables/a_models_cv_summary.csv"
    
    folds_df = pd.read_csv(folds_path)
    summary_df = pd.read_csv(summary_path)
    
    max_val_rmse_diff = 0.0
    max_train_rmse_diff = 0.0
    
    for idx, row in folds_df.iterrows():
        # Validation
        val_mse = row['validation_mse']
        val_rmse = row['validation_rmse']
        diff_val = abs(val_rmse**2 - val_mse)
        if diff_val > max_val_rmse_diff:
            max_val_rmse_diff = diff_val
        assert diff_val < 1e-4, f"Sai lệch RMSE^2 != MSE tại dòng {idx}: {diff_val}"
        
        # Train
        tr_mse = row['train_mse']
        tr_rmse = row['train_rmse']
        diff_tr = abs(tr_rmse**2 - tr_mse)
        if diff_tr > max_train_rmse_diff:
            max_train_rmse_diff = diff_tr
        assert diff_tr < 1e-4, f"Sai lệch train RMSE^2 != MSE tại dòng {idx}: {diff_tr}"
        
    print(f"  [OK] Đẳng thức validation RMSE² == MSE tuyệt đối trên 15 folds (sai số tối đa: {max_val_rmse_diff:.2e})")
    print(f"  [OK] Đẳng thức train RMSE² == MSE tuyệt đối trên 15 folds (sai số tối đa: {max_train_rmse_diff:.2e})")
    
    # Kiểm tra quy tắc thống kê Bài 7: mean(RMSE) != sqrt(mean(MSE))
    for _, row in summary_df.iterrows():
        mean_rmse = row['cv_rmse_mean']
        sqrt_mean_mse = np.sqrt(row['cv_mse_mean'])
        assert abs(mean_rmse - sqrt_mean_mse) > 1e-6, \
            f"Lỗi: mean(RMSE) không được gán bằng sqrt(mean(MSE)) theo lý thuyết Bài 7 cho model {row['model_id']}"
        print(f"  [OK] Mô hình {row['model_id']}: cv_rmse_mean = {mean_rmse:.4f} != sqrt(cv_mse_mean) = {sqrt_mean_mse:.4f}")
        
    return {"max_val_rmse_diff": max_val_rmse_diff, "max_train_rmse_diff": max_train_rmse_diff}


def test_gate_4_progression_and_overfitting():
    """Cổng 4: Kiểm tra tính tiến bộ thứ bậc và kiểm soát hiện tượng quá khớp."""
    summary_path = ROOT / "outputs/tables/a_models_cv_summary.csv"
    summary_df = pd.read_csv(summary_path)
    
    m0 = summary_df[summary_df.model_id == 'M0'].iloc[0]
    m1 = summary_df[summary_df.model_id == 'M1'].iloc[0]
    m2 = summary_df[summary_df.model_id == 'M2'].iloc[0]
    
    # 1. Thứ bậc MSE: M2 < M1 < M0
    assert m2['cv_mse_mean'] < m1['cv_mse_mean'] < m0['cv_mse_mean'], \
        f"Vi phạm thứ bậc MSE: {m2['cv_mse_mean']} < {m1['cv_mse_mean']} < {m0['cv_mse_mean']}"
    print(f"  [OK] Thứ bậc MSE hoàn hảo: M2 ({m2['cv_mse_mean']:,.2f}) < M1 ({m1['cv_mse_mean']:,.2f}) < M0 ({m0['cv_mse_mean']:,.2f})")
    
    # 2. Thứ bậc R²: M2 > M1 > M0 >= 0
    assert m2['cv_r2_mean'] > m1['cv_r2_mean'] > m0['cv_r2_mean'], \
        f"Vi phạm thứ bậc R²: {m2['cv_r2_mean']} > {m1['cv_r2_mean']} > {m0['cv_r2_mean']}"
    assert abs(m0['cv_r2_mean']) < 1e-3, f"M0 phải xấp xỉ 0, thực tế: {m0['cv_r2_mean']}"
    print(f"  [OK] Thứ bậc R² hoàn hảo: M2 ({m2['cv_r2_mean']:.4f}) > M1 ({m1['cv_r2_mean']:.4f}) > M0 ({m0['cv_r2_mean']:.4f})")
    
    # 3. Kiểm tra Overfitting trên M2
    overfitting_gap = m2['cv_mse_mean'] - m2['fold_train_mse_mean']
    rel_gap = overfitting_gap / m2['fold_train_mse_mean']
    assert rel_gap < 0.05, f"Chênh lệch Train vs Validation vượt ngưỡng 5%: {rel_gap * 100:.2f}%"
    print(f"  [OK] Kiểm tra Overfitting M2: Validation MSE ({m2['cv_mse_mean']:,.2f}) vs Train MSE ({m2['fold_train_mse_mean']:,.2f}) "
          f"-> Chênh lệch chỉ {overfitting_gap:.2f} đơn vị ({rel_gap * 100:.3f}% << 5%)")
    
    return {
        "m0_cv_mse": m0['cv_mse_mean'],
        "m1_cv_mse": m1['cv_mse_mean'],
        "m2_cv_mse": m2['cv_mse_mean'],
        "overfitting_gap_mse": overfitting_gap
    }


def test_gate_5_notebook_reproducibility():
    """Cổng 5: Kiểm tra tính tái lập và kết quả thực thi của notebook."""
    nb_path = ROOT / "notebooks/03a_linear_regression_models.ipynb"
    nb = nbformat.read(nb_path, as_version=4)
    
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(code_cells) >= 5, f"Số code cells quá ít: {len(code_cells)}"
    
    for idx, cell in enumerate(code_cells):
        assert cell.execution_count is not None, f"Code cell {idx} chưa được thực thi!"
        assert len(cell.outputs) > 0 or "display" not in cell.source, f"Code cell {idx} thiếu outputs!"
        # Kiểm tra không có cell nào bị crash / error
        for out in cell.outputs:
            assert out.get('output_type') != 'error', \
                f"Lỗi thực thi trong code cell {idx}: {out.get('ename')}: {out.get('evalue')}"
                
    print(f"  [OK] Notebook {nb_path.name} có tổng cộng {len(nb.cells)} cells ({len(code_cells)} code cells)")
    print(f"  [OK] 100% code cells đã thực thi thành công, lưu đầy đủ outputs và KHÔNG có ngoại lệ (0 errors)")
    
    return {"total_cells": len(nb.cells), "code_cells": len(code_cells), "executed_cells": len(code_cells)}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=================================================================")
    print("KIỂM TOÁN VÀ NGHIỆM THU TỰ ĐỘNG TASK T08 (THÀNH VIÊN A: M0, M1, M2)")
    print("=================================================================")
    
    gates = [
        ("Cổng 1: Kiểm toán Tệp tin Sản phẩm", test_gate_1_artifacts),
        ("Cổng 2: Kiểm toán Bảo vệ Tập Test (Anti-Leakage)", test_gate_2_anti_leakage),
        ("Cổng 3: Kiểm toán Đẳng thức Toán học & Thống kê", test_gate_3_math_identities),
        ("Cổng 4: Kiểm toán Thứ bậc Tiến bộ & Quá khớp", test_gate_4_progression_and_overfitting),
        ("Cổng 5: Kiểm toán Tính Tái lập Notebook", test_gate_5_notebook_reproducibility),
    ]
    
    results = []
    all_passed = True
    
    for name, func in gates:
        res = run_gate(name, func)
        results.append(res)
        if res['status'] != 'PASSED':
            all_passed = False
            
    print("\n=================================================================")
    print("TỔNG KẾT NGHIỆM THU TASK T08")
    print("=================================================================")
    for r in results:
        status_symbol = "✔ [PASSED]" if r['status'] == 'PASSED' else "✖ [FAILED]"
        print(f"  {status_symbol} {r['gate']}")
        
    audit_report = {
        "task": "T08",
        "title": "Mô hình Hồi quy Tuyến tính M0, M1, M2",
        "responsible_member": "Thành viên A",
        "peer_reviewer": "Thành viên B (Quang Huy)",
        "protocol_id": "ie313_raw_v1_seed0_cv5",
        "timestamp": pd.Timestamp.now().isoformat(),
        "all_passed": all_passed,
        "gates": results
    }
    
    report_json_path = ROOT / "reports/a_t08_verification.json"
    report_json_path.write_text(json.dumps(audit_report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nĐã ghi kết quả kiểm toán vào: {report_json_path.relative_to(ROOT)}")
    
    if all_passed:
        print("\n🎉 XÁC NHẬN: TASK T08 ĐÃ VƯỢT QUA 100% CÁC CỔNG KIỂM TOÁN CHÍNH THỨC!")
        print("Sẵn sàng bàn giao cho Task T10 (So chiếu chung và đánh giá trên tập Test).")
        return 0
    else:
        print("\n❌ CẢNH BÁO: TASK T08 CÒN CỔNG CHƯA ĐẠT. VUI LÒNG KIỂM TRA LẠI.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
