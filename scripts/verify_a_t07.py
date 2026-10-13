"""Kịch bản kiểm thử độc lập nghiệm thu Giao thức Thực nghiệm Task T07 (Thành viên A).

Căn cứ:
- Skill/SKILL.md
- Skill/KE_HOACH_DO_AN_IE313.md
- reports/HANDOFF_B_TO_A.md
- plan_T07.md

Chạy từ thư mục gốc:
.venv\\Scripts\\python.exe scripts/verify_a_t07.py
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, train_test_split

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment import build_pipeline, evaluate_cv, load_data, load_protocol, predictor_names


def sha256_normalized(file_path):
    raw_bytes = Path(file_path).read_bytes()
    normalized = raw_bytes.replace(b'\r\n', b'\n')
    return hashlib.sha256(normalized).hexdigest()


def run_a_verification():
    print("=" * 80)
    print("BẮT ĐẦU KIỂM TOÁN ĐỘC LẬP GIAO THỨC T07 (THÀNH VIÊN A REVIEW GÓI BÀN GIAO)")
    print("=" * 80)

    audit_records = []

    def log_check(gate, name, condition, details=""):
        status = "PASSED" if condition else "FAILED"
        print(f"[{status}] {gate} - {name}")
        if details:
            print(f"        -> {details}")
        audit_records.append({
            "gate": gate,
            "check": name,
            "status": status,
            "details": details
        })
        if not condition:
            raise AssertionError(f"VI PHẠM NGHIÊM TRỌNG tại {gate}: {name} ({details})")

    # =========================================================================
    # CỔNG 1: KIỂM TRA TÍNH TOÀN VẸN VÀ BẤT BIẾN CỦA DỮ LIỆU GỐC
    # =========================================================================
    print("\n>>> CỔNG 1: Kiểm tra tính toàn vẹn và mã băm SHA-256 dữ liệu...")
    df = load_data(ROOT)
    config_path = ROOT / "config/experiment_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    log_check("Gate 1", "Quy mô dữ liệu đúng 51.707 dòng × 24 cột",
              df.shape == (51707, 24),
              f"Quan sát: {df.shape[0]} dòng, {df.shape[1]} cột")

    calculated_hash = sha256_normalized(ROOT / config["data_file"])
    expected_hash = config["data_sha256"]
    log_check("Gate 1", "Mã băm SHA-256 khớp tuyệt đối với cấu hình protocol",
              calculated_hash == expected_hash,
              f"Hash: {calculated_hash}")

    log_check("Gate 1", "Biến mục tiêu realSum hợp lệ (dương, không khuyết, không vô hạn)",
              df["realSum"].gt(0).all() and df["realSum"].notna().all() and np.isfinite(df["realSum"]).all(),
              f"realSum min: {df['realSum'].min():.2f} EUR, max: {df['realSum'].max():.2f} EUR")

    # =========================================================================
    # CỔNG 2: KIỂM TRA PHÂN CHIA HOLDOUT 80/20 & ĐÓNG BĂNG TẬP TEST
    # =========================================================================
    print("\n>>> CỔNG 2: Kiểm tra phân chia Holdout 80/20 & Đóng băng tập Test...")
    manifest_path = ROOT / config["split"]["manifest"]
    manifest = pd.read_csv(manifest_path)

    log_check("Gate 2", "Manifest đủ 51.707 dòng và khóa truy vết duy nhất",
              len(manifest) == 51707 and not manifest.duplicated(subset=["source_file", "source_row"]).any(),
              f"Số bản ghi: {len(manifest)}, Khóa (source_file, source_row) duy nhất 100%")

    n_train = (manifest["split"] == "train").sum()
    n_test = (manifest["split"] == "test").sum()
    log_check("Gate 2", "Quy mô phân chia chính xác 80% Train (41.365) / 20% Test (10.342)",
              n_train == 41365 and n_test == 10342,
              f"Train: {n_train:,} dòng ({n_train/len(manifest)*100:.2f}%), Test: {n_test:,} dòng ({n_test/len(manifest)*100:.2f}%)")

    # Tái lập kiểm chứng ngẫu nhiên bằng sklearn
    exp_train_idx, exp_test_idx = train_test_split(np.arange(len(df)), test_size=0.2, random_state=0)
    manifest_train_idx = np.flatnonzero(manifest["split"] == "train")
    manifest_test_idx = np.flatnonzero(manifest["split"] == "test")
    log_check("Gate 2", "Khớp 100% kết quả train_test_split ngẫu nhiên (seed 0), không chọn lọc thiên vị",
              set(exp_train_idx) == set(manifest_train_idx) and set(exp_test_idx) == set(manifest_test_idx),
              "Chứng minh tập chia độc lập hoàn toàn với giá trị target")

    test_folds = manifest.loc[manifest["split"] == "test", "cv_fold"].unique()
    log_check("Gate 2", "Tập Test được đóng băng tuyệt đối (cv_fold = -1)",
              len(test_folds) == 1 and test_folds[0] == -1,
              f"Các giá trị cv_fold quan sát trên tập Test: {test_folds.tolist()}")

    # =========================================================================
    # CỔNG 3: KIỂM TRA CẤU TRÚC 5-FOLD CROSS-VALIDATION TRÊN TẬP TRAIN
    # =========================================================================
    print("\n>>> CỔNG 3: Kiểm tra tính phủ và độc lập của 5-Fold Cross-Validation...")
    config, train, test, cv = load_protocol(ROOT)

    log_check("Gate 3", "Số lượng folds bằng đúng 5 và chỉ hoạt động trên tập Train (41.365 dòng)",
              len(cv) == 5 and len(train) == 41365 and len(test) == 10342,
              f"Số folds: {len(cv)}, Train: {len(train):,}, Test: {len(test):,}")

    validation_indices_all = []
    for fold_idx, (fold_train_pos, fold_val_pos) in enumerate(cv):
        validation_indices_all.extend(fold_val_pos)
        overlap = set(fold_train_pos).intersection(set(fold_val_pos))
        log_check("Gate 3", f"Fold {fold_idx}: Tập huấn luyện và tập kiểm định hoàn toàn tách biệt",
                  len(overlap) == 0,
                  f"Train fold: {len(fold_train_pos):,}, Valid fold: {len(fold_val_pos):,}, Giao nhau = 0")

    validation_indices_all = np.array(validation_indices_all)
    log_check("Gate 3", "5 Validation Folds phủ kín đúng 1 lần toàn bộ 41.365 dòng tập Train (Disjoint & Exhaustive)",
              len(validation_indices_all) == 41365 and np.array_equal(np.sort(validation_indices_all), np.arange(41365)),
              "Không có bất kỳ bản ghi Train nào bị bỏ sót hoặc kiểm định 2 lần")

    # =========================================================================
    # CỔNG 4: KIỂM TOÁN DANH MỤC THUỘC TÍNH & CHỐNG RÒ RỈ DỮ LIỆU (ANTI-LEAKAGE)
    # =========================================================================
    print("\n>>> CỔNG 4: Kiểm toán danh mục thuộc tính & Chống rò rỉ dữ liệu...")
    allowed = predictor_names(config)
    excluded = set(config["excluded_predictors"])

    log_check("Gate 4", "Allowlist gồm đúng 10 thuộc tính nghiệp vụ hợp lệ",
              len(allowed) == 10,
              f"6 định lượng + 3 phân loại + 1 boolean: {allowed}")

    overlap_excluded = set(allowed).intersection(excluded)
    log_check("Gate 4", "Tuyệt đối không chứa bất kỳ thuộc tính nào trong Excluded List",
              len(overlap_excluded) == 0,
              f"Giao giữa Allowlist và Excluded List là rỗng")

    log_check("Gate 4", "Loại trừ triệt để biến target realSum và các biến rò rỉ (price_tier, log_price_temp, dist_bin)",
              "realSum" not in allowed and "price_tier" not in allowed and "log_price_temp" not in allowed and "dist_bin" not in allowed,
              "Target leakage được ngăn chặn hoàn toàn")

    # Thử nghiệm kháng lỗi: bơm cột lạ và danh mục mới vào Pipeline M2
    pipeline_m2 = build_pipeline("M2", config)
    sample_train = train.iloc[:500]
    pipeline_m2.fit(sample_train[allowed], sample_train["realSum"])

    dirty_test_data = train.iloc[500:520].copy()
    normal_preds = pipeline_m2.predict(dirty_test_data[allowed])

    # Bơm cột rò rỉ vào DataFrame
    dirty_test_data["price_tier"] = "Luxury"
    dirty_test_data["log_price_temp"] = 999.0
    dirty_test_data["source_row"] = -1
    dirty_preds = pipeline_m2.predict(dirty_test_data)
    log_check("Gate 4", "Pipeline tự động bỏ qua cột thừa / cột rò rỉ nhờ remainder='drop'",
              np.allclose(normal_preds, dirty_preds),
              "Dự đoán không thay đổi khi DataFrame bị chèn thêm các cột ngoài Allowlist")

    # Bơm thành phố chưa từng thấy trong tập train
    unseen_city_data = dirty_test_data.copy()
    unseen_city_data["city"] = "tokyo_unseen_city"
    unseen_preds = pipeline_m2.predict(unseen_city_data)
    log_check("Gate 4", "Pipeline xử lý danh mục lạ mà không bị crash nhờ handle_unknown='ignore'",
              np.isfinite(unseen_preds).all(),
              "Danh mục lạ được mã hóa thành toàn 0 theo đúng thiết kế OneHotEncoder")

    # =========================================================================
    # CỔNG 5: KIỂM TOÁN TÍNH CÔ LẬP CỦA PIPELINE TIỀN XỬ LÝ (PIPELINE ISOLATION)
    # =========================================================================
    print("\n>>> CỔNG 5: Kiểm toán tính cô lập của Pipeline tiền xử lý...")
    fold_0_train_pos, fold_0_val_pos = cv[0]
    pipeline_fold_0 = build_pipeline("M2", config)
    pipeline_fold_0.fit(train.iloc[fold_0_train_pos][allowed], train.iloc[fold_0_train_pos]["realSum"])

    scaler_numeric = pipeline_fold_0.named_steps["preprocess"].named_transformers_["numeric"]
    scaler_means = scaler_numeric.mean_
    direct_fold_means = train.iloc[fold_0_train_pos][config["predictors"]["numeric"]].mean().to_numpy()

    log_check("Gate 5", "StandardScaler chỉ được fit trên tập train của từng fold, không rò rỉ validation/test",
              np.allclose(scaler_means, direct_fold_means),
              "Tham số chuẩn hóa trung bình mu khớp chính xác 100% với train fold 0")

    # Đánh giá thử nghiệm M0 Baseline để kiểm tra evaluate_cv
    pipeline_m0 = build_pipeline("M0", config)
    summary_m0, folds_m0 = evaluate_cv(pipeline_m0, train, cv, config, "M0", "base")
    log_check("Gate 5", "Hàm evaluate_cv đánh giá chuẩn xác 5 folds với đầy đủ MSE, RMSE, MAE, R2",
              len(folds_m0) == 5 and "cv_mse_mean" in summary_m0,
              f"M0 Baseline CV MSE Mean: {summary_m0['cv_mse_mean']:,.2f}, R2 Mean: {summary_m0['cv_r2_mean']:.4f}")

    print("\n" + "=" * 80)
    print("KẾT LUẬN: TOÀN BỘ 5 CỔNG KIỂM TOÁN T07 ĐỀU ĐẠT CHUẨN (100% PASSED)!")
    print("GIAO THỨC THỰC NGHIỆM ĐƯỢC THÀNH VIÊN A CHÍNH THỨC NGHIỆM THU!")
    print("=" * 80)

    # Xuất kết quả kiểm toán ra file JSON
    result_report = {
        "verifier": "Thành viên A (Đồ án IE313)",
        "protocol_id": config["protocol_id"],
        "status": "APPROVED",
        "n_checks": len(audit_records),
        "all_passed": all(r["status"] == "PASSED" for r in audit_records),
        "train_rows": len(train),
        "test_rows": len(test),
        "cv_folds": len(cv),
        "predictors_count": len(allowed),
        "records": audit_records
    }
    output_path = ROOT / "reports/a_t07_verification.json"
    output_path.write_text(json.dumps(result_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã lưu kết quả kiểm toán chi tiết vào: {output_path}")


if __name__ == "__main__":
    run_a_verification()
