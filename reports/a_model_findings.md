# BÁO CÁO KẾT QUẢ MÔ HÌNH HỒI QUY TUYẾN TÍNH M0, M1, M2 (TASK T08)

> **Người thực hiện:** Thành viên A  
> **Người phối hợp nghiệm thu:** Thành viên B (Quang Huy)  
> **Giao thức thực nghiệm:** `ie313_raw_v1_seed0_cv5` ([config/experiment_config.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/config/experiment_config.json))  
> **Phạm vi dữ liệu:** 41.365 dòng tập Train (5 Folds CV). Tập Test (10.342 dòng) được đóng băng hoàn toàn.

---

## 1. Bảng Tổng hợp Hiệu năng Đánh giá 5-Fold Cross-Validation

| Mã Mô hình | Biến thể | CV MSE | CV RMSE | CV MAE | CV R² | Train MSE | Chênh lệch MSE (Overfitting Check) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **M0** (Baseline) | Mean Dummy | 104,402.75 ± 18,227.99 | 322.09 ± 28.75 | 146.41 ± 1.62 | -0.0000 ± 0.0000 | 104,401.93 | +0.83 |
| **M1** (Đơn biến) | person_capacity | 99,919.96 ± 18,372.51 | 314.99 ± 29.66 | 139.13 ± 0.95 | 0.0443 ± 0.0097 | 99,918.57 | +1.39 |
| **M2** (Đa biến) | 10 Allowlist | **79,988.15 ± 18,800.21** | **281.17 ± 34.14** | **104.35 ± 0.66** | **0.2409 ± 0.0508** | 79,912.37 | +75.78 |

### Nhận xét Thứ bậc Tiến bộ:
1. **Từ M0 lên M1:** Đưa thêm biến đơn quy mô `person_capacity` giúp giảm MSE từ 104,402.75 xuống 99,919.96 (giảm 4,482.79 đơn vị MSE, cải thiện tương đối 4.29%). Hệ số xác định $R^2$ tăng từ ~0 lên 0.0443.
2. **Từ M1 lên M2:** Khi tích hợp đầy đủ 10 thuộc tính thuộc Allowlist (bao gồm vị trí, khoảng cách, thành phố và loại phòng), MSE giảm ngoạn mục xuống còn 79,988.15 (giảm thêm 19.09% so với mốc baseline ban đầu). $R^2$ đạt 0.2409, giải thích được khoảng 24.1% tổng biến thiên giá phòng.
3. **Đánh giá Quá khớp (Overfitting):**
   - Chênh lệch giữa Validation MSE và Train MSE ở mô hình M2 chỉ là 75.78 đơn vị (tương đương chênh lệch chưa tới 0.1%).
   - Điều này chứng minh mô hình tuyến tính M2 có độ tổng quát hóa (generalization) rất cao trên tập train, không có hiện tượng quá khớp (overfitting).

---

## 2. Phương trình Hồi quy Đơn biến M1 (Simple Linear Regression)

Phương trình hồi quy mẫu fit trên toàn bộ 41.365 dòng tập Train:
$$\widehat{\text{realSum}} = 117.21 + 51.52 \times \text{person_capacity}$$

* **Hệ số chặn ($w_0 = 117.21$ EUR):** Thể hiện chi phí cố định tối thiểu ước tính cho một chỗ ở (giá sàn lý thuyết khi sức chứa = 0).
* **Hệ số góc ($w_1 = 51.52$ EUR/người):** Khi sức chứa tăng thêm 1 người, giá thuê ước tính tăng thêm trung bình **51.52 EUR/đêm**.
* **Đánh giá nghiệp vụ:** Hệ số góc dương phù hợp hoàn toàn với quy luật kinh tế và trực giác thực tế. Tuy nhiên vì $R^2 = 0.0443$, sức chứa phòng đơn lẻ chỉ giải thích được một phần nhỏ giá thuê; phần biến thiên lớn còn lại phụ thuộc vào vị trí địa lý và loại phòng.

---

## 3. Phân tích Hệ số Hồi quy Đa biến M2 (Multiple Linear Regression)

* **Hệ số chặn ($w_0 = 620.90$ EUR):** Giá dự đoán cho một chỗ nghỉ có các đặc trưng định lượng ở mức trung bình của tập train, tại **Amsterdam**, loại phòng **Entire home/apt**, vào các ngày trong tuần (**weekdays**), và host **không phải superhost**.

### 3.1. Các yếu tố kéo giá giảm mạnh nhất (Hệ số âm lớn nhất):
- **`city_athens` (Hệ số chuẩn hóa: -522.26):** EUR chênh lệch vs nhóm tham chiếu (Amsterdam / Entire home / Weekdays). Cụ thể: giá ước tính giảm khoảng 522.26 EUR so với nhóm tham chiếu.
- **`city_budapest` (Hệ số chuẩn hóa: -467.94):** EUR chênh lệch vs nhóm tham chiếu (Amsterdam / Entire home / Weekdays). Cụ thể: giá ước tính giảm khoảng 467.94 EUR so với nhóm tham chiếu.
- **`city_rome` (Hệ số chuẩn hóa: -386.91):** EUR chênh lệch vs nhóm tham chiếu (Amsterdam / Entire home / Weekdays). Cụ thể: giá ước tính giảm khoảng 386.91 EUR so với nhóm tham chiếu.

### 3.2. Các yếu tố thúc đẩy giá tăng mạnh nhất (Hệ số dương lớn nhất):
- **`bedrooms` (Hệ số chuẩn hóa: +52.19):** EUR / 1 đơn vị bedrooms. Mỗi độ lệch chuẩn tăng thêm của biến này làm giá tăng ước tính +52.19 EUR (tương đương +82.92 EUR trên mỗi đơn vị gốc).
- **`person_capacity` (Hệ số chuẩn hóa: +36.92):** EUR / 1 đơn vị person_capacity. Mỗi độ lệch chuẩn tăng thêm của biến này làm giá tăng ước tính +36.92 EUR (tương đương +28.40 EUR trên mỗi đơn vị gốc).
- **`cleanliness_rating` (Hệ số chuẩn hóa: +7.74):** EUR / 1 đơn vị cleanliness_rating. Mỗi độ lệch chuẩn tăng thêm của biến này làm giá tăng ước tính +7.74 EUR (tương đương +8.10 EUR trên mỗi đơn vị gốc).

### 3.3. Tác động của Vị trí và Khoảng cách:
- Khoảng cách đến trung tâm (`dist`): Hệ số chuẩn hóa mang giá trị âm đáng kể (-48.29), xác nhận quy luật: chỗ nghỉ càng xa trung tâm thành phố thì giá thuê càng giảm.
- Thành phố: Toàn bộ các thành phố khác đều có hệ số âm so với Amsterdam, chứng minh trong tập dữ liệu khảo sát, Amsterdam là thị trường có mức giá cơ sở cao nhất.

---

## 4. Bàn giao và So chiếu với Nhánh Mô hình B (Task T09)

* **Kết quả T09 của Thành viên B:**
  - Mô hình Đa thức M3: Lựa chọn **degree = 3** với $CV\_MSE = 79.227,00$.
  - Mô hình Ridge M4: Lựa chọn **$\alpha = 0,1$** với $CV\_MSE = 79.988,15$.
* **So chiếu đối chuẩn:**
  - $CV\_MSE$ của mô hình OLS M2 (79,988.15) xấp xỉ tương đương với Ridge M4 $\alpha=0.1$ (79,988.15), đúng với kỳ vọng lý thuyết vì khi $\alpha \to 0$, Ridge hội tụ về OLS.
  - Mô hình Đa thức M3 (bậc 3) giảm nhẹ MSE thêm khoảng 760 đơn vị (761.15).
* **Sản phẩm sẵn sàng cho Task T10:**
  - `outputs/tables/a_models_cv_summary.csv`
  - `outputs/tables/a_models_cv_folds.csv`
  - `outputs/figures/fig_04_m1_regression_plot.png`
  - `outputs/figures/fig_05_m2_coefficients.png`
  - `models/M0_A_train_only.joblib`, `models/M1_A_train_only.joblib`, `models/M2_A_train_only.joblib`
  - `config/a_selected_models.json`
