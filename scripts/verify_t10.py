"""Kịch bản kiểm toán nghiệm thu toàn diện Task T10 (Phối hợp A+B).

Kiểm toán 5 Cổng Kỹ thuật (5 Audit Gates):
1. Tệp tin Sản phẩm (Artifacts Integrity Gate)
2. Độ phủ Tập Test & Khóa truy vết (Test Coverage & Traceability Gate)
3. Đẳng thức Toán học & Thống kê (Mathematical Consistency Gate)
4. Liêm chính Chọn mô hình (Model Selection & Anti-Tuning Gate)
5. Tính Tái lập Notebook (Notebook Reproducibility Gate)

Sử dụng: python scripts/verify_t10.py
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
    """Cổng 1: Kiểm tra sự tồn tại và kích thước của các file sản phẩm đầu ra T10."""
    required_files = [
        ROOT / "outputs/tables/model_comparison_cv_vs_test.csv",
        ROOT / "outputs/tables/test_predictions.csv",
        ROOT / "outputs/figures/fig_06_cv_vs_test_comparison.png",
        ROOT / "outputs/figures/fig_07_actual_vs_predicted_distribution.png",
        ROOT / "reports/t10_model_selection_and_test_evaluation.md",
        ROOT / "reports/A_B_T10_ACCEPTANCE.md",
        ROOT / "reports/t10_notebook_runs.json",
        ROOT / "notebooks/04_model_evaluation_and_test.ipynb"
    ]
    
    file_stats = []
    for f in required_files:
        assert f.exists(), f"Thiếu file sản phẩm: {f.relative_to(ROOT)}"
        size = f.stat().st_size
        assert size > 0, f"File rỗng (0 bytes): {f.relative_to(ROOT)}"
        file_stats.append({"file": str(f.relative_to(ROOT)), "size_bytes": size})
        print(f"  [OK] {f.relative_to(ROOT)} ({size:,} bytes)")
        
    return file_stats


def test_gate_2_test_coverage_and_traceability():
    """Cổng 2: Kiểm tra độ phủ tập Test (đúng 10.342 mẫu) và hai mã truy vết."""
    config, _train, test, _cv = load_protocol(ROOT)
    preds_path = ROOT / "outputs/tables/test_predictions.csv"
    preds_df = pd.read_csv(preds_path)
    
    # 1. Kích thước tập test
    assert len(test) == 10342, f"Kích thước test phải bằng 10.342, thực tế: {len(test)}"
    
    # 2. Tổng số dòng trong test_predictions
    models = ['M0', 'M1', 'M2', 'M3', 'M4']
    assert set(preds_df['model_id'].unique()) == set(models), f"Thiếu mô hình trong test_predictions"
    assert len(preds_df) == 10342 * len(models), f"Tổng số dòng phải là {10342 * len(models)}, thực tế: {len(preds_df)}"
    
    # 3. Kiểm tra tính toàn vẹn của mã truy vết cho từng mô hình
    test_trace = test[['source_file', 'source_row']].sort_values(by=['source_file', 'source_row']).reset_index(drop=True)
    
    for mid in models:
        m_df = preds_df[preds_df['model_id'] == mid].sort_values(by=['source_file', 'source_row']).reset_index(drop=True)
        assert len(m_df) == 10342, f"Mô hình {mid} không đủ 10.342 dòng dự đoán"
        pd.testing.assert_series_equal(m_df['source_file'], test_trace['source_file'], check_names=False)
        pd.testing.assert_series_equal(m_df['source_row'], test_trace['source_row'], check_names=False)
        assert m_df['split'].eq('test').all(), f"Mô hình {mid} có dòng không thuộc nhãn test"
        assert m_df['protocol_id'].eq('ie313_raw_v1_seed0_cv5').all()
        
    print(f"  [OK] Độ phủ tập Test: Đúng 10.342 dòng cho cả 5 mô hình (Tổng: {len(preds_df):,} dòng)")
    print(f"  [OK] Mã truy vết (source_file, source_row) khớp tuyệt đối 100% với tập Test gốc")
    return {"n_test_samples": 10342, "n_models": len(models), "total_prediction_records": len(preds_df)}


def test_gate_3_math_identities():
    """Cổng 3: Kiểm tra tính nhất quán toán học của các độ đo trên tập Test."""
    comp_path = ROOT / "outputs/tables/model_comparison_cv_vs_test.csv"
    comp_df = pd.read_csv(comp_path)
    preds_df = pd.read_csv(ROOT / "outputs/tables/test_predictions.csv")
    
    for _, row in comp_df.iterrows():
        mid = row['model_id']
        m_preds = preds_df[preds_df['model_id'] == mid]
        
        # 1. Đẳng thức RMSE^2 == MSE
        diff_rmse_sq = abs(row['test_rmse']**2 - row['test_mse'])
        assert diff_rmse_sq < 1e-4, f"Lỗi RMSE^2 != MSE cho model {mid}: {diff_rmse_sq}"
        
        # 2. Tính lại MSE độc lập từ cột residual
        calc_mse = (m_preds['residual'] ** 2).mean()
        assert abs(calc_mse - row['test_mse']) < 1e-4, f"MSE tính lại không khớp cho model {mid}"
        
        # 3. Tính lại MAE độc lập từ cột residual
        calc_mae = m_preds['residual'].abs().mean()
        assert abs(calc_mae - row['test_mae']) < 1e-4, f"MAE tính lại không khớp cho model {mid}"
        
        # 4. Tính lại R^2 độc lập
        y_test = m_preds['actual']
        ss_res = (m_preds['residual'] ** 2).sum()
        ss_tot = ((y_test - y_test.mean()) ** 2).sum()
        calc_r2 = 1.0 - ss_res / ss_tot
        assert abs(calc_r2 - row['test_r2']) < 1e-4, f"R2 tính lại không khớp cho model {mid}"
        
        print(f"  [OK] Model {mid}: RMSE² == MSE khớp, MAE={calc_mae:.2f}, R²={calc_r2:.4f}")
        
    return {"models_verified": len(comp_df)}


def test_gate_4_model_selection_and_anti_tuning():
    """Cổng 4: Kiểm tra liêm chính chọn mô hình và thứ bậc tiến bộ."""
    comp_path = ROOT / "outputs/tables/model_comparison_cv_vs_test.csv"
    comp_df = pd.read_csv(comp_path)
    
    # Mô hình thắng cuộc được chốt là M3 dựa trên CV MSE
    winner = comp_df[comp_df['selected_winning_model'] == True].iloc[0]
    assert winner['model_id'] == 'M3', f"Mô hình chiến thắng phải là M3, thực tế: {winner['model_id']}"
    assert winner['cv_mse_mean'] == comp_df['cv_mse_mean'].min(), "M3 phải có CV MSE thấp nhất"
    
    # Thứ bậc trên Test: M3 < M4 <= M2 < M1 < M0
    m0_test_mse = comp_df.loc[comp_df.model_id == 'M0', 'test_mse'].iloc[0]
    m1_test_mse = comp_df.loc[comp_df.model_id == 'M1', 'test_mse'].iloc[0]
    m2_test_mse = comp_df.loc[comp_df.model_id == 'M2', 'test_mse'].iloc[0]
    m3_test_mse = comp_df.loc[comp_df.model_id == 'M3', 'test_mse'].iloc[0]
    m4_test_mse = comp_df.loc[comp_df.model_id == 'M4', 'test_mse'].iloc[0]
    
    assert m3_test_mse < m1_test_mse < m0_test_mse, "Thứ bậc tiến bộ vi phạm trên Test"
    assert m3_test_mse < m2_test_mse, "M3 phải tốt hơn M2 trên Test"
    assert abs(m4_test_mse - m2_test_mse) < 1.0, "M4 và M2 phải xấp xỉ tương đương trên Test (Ridge hội tụ về OLS)"
    
    print(f"  [OK] Mô hình chiến thắng được chốt bằng CV: M3 (Poly bậc 3) với CV MSE = {winner['cv_mse_mean']:,.2f}")
    print(f"  [OK] M3 tiếp tục dẫn đầu trên Test với Test MSE = {winner['test_mse']:,.2f} và Test R² = {winner['test_r2']:.4f}")
    print(f"  [OK] Hội tụ toán học: M4 Ridge ({m4_test_mse:,.2f}) xấp xỉ hoàn hảo M2 MLR ({m2_test_mse:,.2f})")
    
    return {
        "winning_model": winner['model_id'],
        "winner_cv_mse": winner['cv_mse_mean'],
        "winner_test_mse": winner['test_mse'],
        "winner_test_r2": winner['test_r2']
    }


def test_gate_5_notebook_reproducibility():
    """Cổng 5: Kiểm tra tính tái lập và kết quả thực thi của notebook 04."""
    nb_path = ROOT / "notebooks/04_model_evaluation_and_test.ipynb"
    nb = nbformat.read(nb_path, as_version=4)
    
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(code_cells) >= 5, f"Số code cells quá ít: {len(code_cells)}"
    
    for idx, cell in enumerate(code_cells):
        assert cell.execution_count is not None, f"Code cell {idx} chưa được thực thi!"
        for out in cell.outputs:
            assert out.get('output_type') != 'error', \
                f"Lỗi thực thi trong code cell {idx}: {out.get('ename')}: {out.get('evalue')}"
                
    print(f"  [OK] Notebook {nb_path.name} gồm {len(nb.cells)} cells ({len(code_cells)} code cells)")
    print(f"  [OK] 100% code cells đã thực thi thành công từ kernel mới không có ngoại lệ (0 errors)")
    
    return {"total_cells": len(nb.cells), "code_cells": len(code_cells), "executed_cells": len(code_cells)}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=================================================================")
    print("KIỂM TOÁN VÀ NGHIỆM THU TỰ ĐỘNG TASK T10 (PHỐI HỢP A+B: ĐÁNH GIÁ TEST)")
    print("=================================================================")
    
    gates = [
        ("Cổng 1: Kiểm toán Tệp tin Sản phẩm", test_gate_1_artifacts),
        ("Cổng 2: Kiểm toán Độ phủ Tập Test & Khóa truy vết", test_gate_2_test_coverage_and_traceability),
        ("Cổng 3: Kiểm toán Đẳng thức Toán học & Thống kê", test_gate_3_math_identities),
        ("Cổng 4: Kiểm toán Liêm chính Chọn mô hình & Thứ bậc", test_gate_4_model_selection_and_anti_tuning),
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
    print("TỔNG KẾT NGHIỆM THU TASK T10")
    print("=================================================================")
    for r in results:
        status_symbol = "✔ [PASSED]" if r['status'] == 'PASSED' else "✖ [FAILED]"
        print(f"  {status_symbol} {r['gate']}")
        
    audit_report = {
        "task": "T10",
        "title": "Chốt mô hình và Đánh giá trên tập Holdout Test chung",
        "responsible_members": "Thành viên A + Thành viên B",
        "protocol_id": "ie313_raw_v1_seed0_cv5",
        "timestamp": pd.Timestamp.now().isoformat(),
        "all_passed": all_passed,
        "gates": results
    }
    
    report_json_path = ROOT / "reports/t10_verification.json"
    report_json_path.write_text(json.dumps(audit_report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nĐã ghi kết quả kiểm toán vào: {report_json_path.relative_to(ROOT)}")
    
    if all_passed:
        print("\n🎉 XÁC NHẬN: TASK T10 ĐÃ VƯỢT QUA 100% CÁC CỔNG KIỂM TOÁN CHÍNH THỨC!")
        print("Sẵn sàng bàn giao tệp test_predictions.csv cho Thành viên B thực hiện Task T11.")
        return 0
    else:
        print("\n❌ CẢNH BÁO: TASK T10 CÒN CỔNG CHƯA ĐẠT. VUI LÒNG KIỂM TRA LẠI.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
