# BIÊN BẢN NGHIỆM THU KỸ THUẬT TASK T08
## Mô hình Hồi quy Tuyến tính Nền tảng (M0, M1, M2)

- **Người thực hiện:** Thành viên A
- **Người phối hợp nghiệm thu:** Thành viên B (Quang Huy)
- **Thời điểm nghiệm thu:** 13/10/2026
- **Căn cứ tài liệu:** [SKILL.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/Skill/SKILL.md), [KE_HOACH_DO_AN_IE313.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/Skill/KE_HOACH_DO_AN_IE313.md), [A_T07_ACCEPTANCE.md](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/reports/A_T07_ACCEPTANCE.md)
- **Mã định danh giao thức:** `ie313_raw_v1_seed0_cv5`

---

### 1. Kết quả Kiểm toán qua 5 Cổng Kỹ thuật (5 Verification Gates)

Script kiểm toán độc lập [scripts/verify_a_t08.py](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/scripts/verify_a_t08.py) đã thực thi toàn diện và đạt chuẩn 100%:

| Cổng kiểm toán | Tiêu chí kỹ thuật | Kết quả định lượng | Trạng thái |
|---|---|---|:---:|
| **Cổng 1: Tệp tin Sản phẩm** | Đầy đủ 2 bảng CSV kết quả, bảng hệ số, 2 biểu đồ PNG, 3 mô hình `.joblib`, config JSON, findings MD, notebook runs JSON | Khớp 100% (12/12 files tồn tại và có kích thước > 0 bytes) | **PASSED** |
| **Cổng 2: Bảo vệ Tập Test** | Không rò rỉ tập Holdout Test (10.342 dòng), chỉ chạy trên 41.365 dòng tập Train, không có cột `test_` nào trong bảng | Tập test cô lập hoàn toàn; số mẫu fold: Train 33.092, Valid 8.273 | **PASSED** |
| **Cổng 3: Đẳng thức Toán học** | Đẳng thức $\text{RMSE}^2 = \text{MSE}$ trên 15 folds; tuân thủ quy tắc $\text{mean}(\text{RMSE}) \neq \sqrt{\text{mean}(\text{MSE})}$ | Sai số tối đa $\le 4.37 \times 10^{-11}$; đúng quy tắc thống kê Bài 7 | **PASSED** |
| **Cổng 4: Thứ bậc Tiến bộ & Quá khớp** | Thứ bậc tiến bộ: $MSE_{\text{M2}} < MSE_{\text{M1}} < MSE_{\text{M0}}$ và $R^2_{\text{M2}} > R^2_{\text{M1}} > R^2_{\text{M0}} \ge 0$; không overfitting | $MSE$: $79.988 < 99.920 < 104.403$; $R^2$: $0.2409 > 0.0443 > 0.0000$; khoảng cách Train vs Valid M2 chỉ 0.095% | **PASSED** |
| **Cổng 5: Tính Tái lập Notebook** | Notebook `03a_linear_regression_models.ipynb` chạy từ đầu đến cuối không lỗi, lưu đủ kết quả | 100% 6/6 code cells chạy thành công trong 4.2 giây, 0 lỗi | **PASSED** |

Minh chứng chi tiết dạng JSON được lưu trữ tại [reports/a_t08_verification.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/reports/a_t08_verification.json).

---

### 2. Tóm tắt Chỉ số Hiệu năng Nghiệm thu

* **Mô hình M0 (Baseline Trung bình):**
  - $CV\_MSE = 104.402,75 \pm 18.916,77$
  - $CV\_RMSE = 322,09 \pm 31,48$ EUR
  - $CV\_R^2 = -0,0000 \pm 0,0497$
* **Mô hình M1 (Hồi quy Đơn biến `person_capacity`):**
  - Phương trình hồi quy: $\widehat{\text{realSum}} = 117,21 + 51,52 \times \text{person\_capacity}$
  - $CV\_MSE = 99.919,96 \pm 18.672,83$
  - $CV\_RMSE = 314,99 \pm 31,81$ EUR
  - $CV\_R^2 = 0,0443 \pm 0,0485$ (cải thiện 4.29% MSE so với M0)
* **Mô hình M2 (Hồi quy Đa biến 10 biến Allowlist):**
  - $CV\_MSE = 79.988,15 \pm 18.800,24$
  - $CV\_RMSE = 281,17 \pm 34,14$ EUR
  - $CV\_R^2 = 0,2409 \pm 0,0508$ (cải thiện 23.38% MSE so với M0)
  - Train MSE: $79.912,37$ (chênh lệch Validation vs Train chỉ 75.78 đơn vị, không overfitting)

---

### 3. Quyết định Nghiệm thu & Chuyển giao

1. **CHẤP THUẬN NGHIỆM THU 100%** Task T08 do Thành viên A phụ trách.
2. Cập nhật trạng thái chính thức của **Task T08** trong hệ thống theo dõi dự án sang: **HOÀN THÀNH (COMPLETED)**.
3. **Sẵn sàng bước vào Task T10 (So chiếu chốt mô hình và Đánh giá trên tập Holdout Test chung):**
   - Đối chiếu nhánh A (M0, M1, M2) với nhánh B (M3 Polynomial bậc 3 $CV\_MSE \approx 79.228$ và M4 Ridge $\alpha=0.1$ $CV\_MSE \approx 79.988$).
   - Thống nhất chọn mô hình chiến thắng trước khi mở khóa tập Test 10.342 dòng.
