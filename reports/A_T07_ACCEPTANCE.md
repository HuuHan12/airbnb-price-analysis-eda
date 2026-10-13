# BIÊN BẢN NGHIỆM THU KỸ THUẬT TASK T07
## Giao thức Thực nghiệm Chung (Shared Experiment Protocol)

- **Người thực hiện nghiệm thu:** Thành viên A
- **Người bàn giao kỹ thuật:** Thành viên B (Quang Huy)
- **Thời điểm nghiệm thu:** 13/10/2026
- **Căn cứ tài liệu:** [SKILL.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/Skill/SKILL.md), [KE_HOACH_DO_AN_IE313.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/Skill/KE_HOACH_DO_AN_IE313.md), [HANDOFF_B_TO_A.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/reports/HANDOFF_B_TO_A.md)
- **Mã định danh giao thức:** `ie313_raw_v1_seed0_cv5`

---

### 1. Kết quả kiểm toán qua 5 Cổng kỹ thuật (Verification Gates)

Thành viên A đã xây dựng script kiểm toán độc lập [verify_a_t07.py](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/scripts/verify_a_t07.py) và thực thi toàn diện trên dữ liệu thực tế:

| Cổng kiểm toán | Tiêu chí kỹ thuật | Kết quả quan sát | Trạng thái |
|---|---|---|:---:|
| **Cổng 1: Tính toàn vẹn dữ liệu gốc** | Quy mô $51.707 \times 24$, hash SHA-256 bất biến, `realSum` thang đo EUR gốc không khuyết | Khớp 100% hash `089643810f...`, min 34.78 EUR, max 18.545.45 EUR | **PASSED** |
| **Cổng 2: Holdout Split 80/20 & Đóng băng Test** | Train 41.365 (80%), Test 10.342 (20%), ngẫu nhiên `seed=0`, tập Test gán `cv_fold = -1` | Khớp 100% `train_test_split`, Test không tham gia vào bất kỳ fold nào | **PASSED** |
| **Cổng 3: Cấu trúc 5-Fold Cross-Validation** | 5 validation folds phủ kín 41.365 dòng train đúng 1 lần, các fold rời rạc | $\bigcup \text{ValidFold} = \text{Train}$; không trùng lặp giữa Train/Valid trong fold | **PASSED** |
| **Cổng 4: Danh mục Allowlist & Chống Leakage** | 10 biến mô hình (6 định lượng, 3 phân loại, 1 boolean); loại trừ ID, tọa độ, biến target-derived | Bơm thử cột lạ và danh mục mới `tokyo_unseen_city` $\rightarrow$ Pipeline kháng lỗi, không crash | **PASSED** |
| **Cổng 5: Tính cô lập Pipeline tiền xử lý** | `StandardScaler` và `OneHotEncoder` chỉ fit trên fold train; metric chọn mô hình `cv_mse_mean` | $\mu_{\text{scaler}}$ khớp tuyệt đối với train fold 0; M0 Baseline $CV\_MSE \approx 104.402,75$ | **PASSED** |

Minh chứng chi tiết dạng JSON được lưu trữ tại [reports/a_t07_verification.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/reports/a_t07_verification.json).

---

### 2. Quyết định nghiệm thu

1. **CHẤP THUẬN NGHIỆM THU 100%** gói giao thức thực nghiệm T07 do Thành viên B chuyển giao.
2. Xác nhận tập dữ liệu phân chia trong [split_manifest.csv](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/data/processed/split_manifest.csv) và cấu hình trong [experiment_config.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/config/experiment_config.json) là chuẩn mực chung duy nhất cho cả Giai đoạn 3 (Mô hình hóa) và Giai đoạn 4 (Đánh giá).
3. Chuyển trạng thái chính thức của **Task T07** trong hệ thống theo dõi dự án sang: **HOÀN THÀNH (COMPLETED)**.

---

### 3. Kế hoạch bước tiếp theo (Next Action)

Thành viên A chính thức bắt tay vào thực hiện **Task T08 (Mô hình M0, M1, M2)**:
- Xây dựng notebook huấn luyện: `notebooks/03a_linear_regression_models.ipynb`.
- Khai thác trực tiếp các hàm `load_protocol()`, `build_pipeline()`, `evaluate_cv()` từ `src/experiment.py`.
- Xuất 2 bảng báo cáo kết quả CV chuẩn:
  - `outputs/tables/a_models_cv_summary.csv`
  - `outputs/tables/a_models_cv_folds.csv`
- Bàn giao kết quả để cùng Thành viên B đối chiếu với M3, M4 trước khi bước vào Task T10 (Đánh giá Test chung).
