# BÁO CÁO KẾT QUẢ ĐÁNH GIÁ TẬP TEST VÀ CHỐT MÔ HÌNH (TASK T10)

> **Người thực hiện phối hợp:** Thành viên A + Thành viên B  
> **Giao thức thực nghiệm:** `ie313_raw_v1_seed0_cv5` ([config/experiment_config.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/config/experiment_config.json))  
> **Quy mô dữ liệu:** Tập Train 41.365 dòng (5-Fold CV) | Tập Holdout Test 10.342 dòng (Đánh giá độc lập).

---

## 1. Bảng Đối chiếu Toàn diện Hiệu năng 5 Mô hình (CV vs Test)

| Mã Mô hình | Biến thể | Người PT | CV MSE | CV R² | Test MSE | Test RMSE | Test MAE | Test R² | Chênh lệch MSE (Test - CV) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **M0** | mean_baseline | Thành viên A | 104,402.75 | -0.0000 | **120,131.61** | **346.60** | 144.86 | **-0.0000** | +15,728.85 |
| **M1** | slr_person_capacity | Thành viên A | 99,919.96 | 0.0443 | **115,888.69** | **340.42** | 137.12 | **0.0353** | +15,968.73 |
| **M2** | mlr_10_features | Thành viên A | 79,988.15 | 0.2409 | **97,964.14** | **312.99** | 103.76 | **0.1845** | +17,975.99 |
| **M3** **(Chiến thắng)** | degree_3 | Thành viên B | 79,228.00 | 0.2483 | **97,156.55** | **311.70** | 102.02 | **0.1912** | +17,928.55 |
| **M4** | alpha_0.1 | Thành viên B | 79,988.15 | 0.2409 | **97,963.94** | **312.99** | 103.76 | **0.1845** | +17,975.79 |

---

## 2. Quyết định Chốt Mô hình Chiến thắng (Model Selection)

* **Mô hình được lựa chọn:** **M3 (degree_3)**
* **Cơ sở khoa học:**
  1. **Trên tập Train (5-Fold CV):** M3 đạt $CV\_MSE = 79,228.00$, thấp nhất trong toàn bộ 5 mô hình nghiên cứu.
  2. **Trên tập Test (10.342 mẫu độc lập):** M3 tiếp tục giữ vững vị trí dẫn đầu với $\text{MSE}_{\text{test}} = 97,156.55$ và $R^2_{\text{test}} = 0.1912$.
  3. **Lý do chuyên môn:** Khai triển đa thức bậc 3 trên 3 biến số cốt lõi (`person_capacity`, `bedrooms`, `dist`) đã giúp mô hình học được mối quan hệ phi tuyến tương hỗ giữa quy mô phòng và khoảng cách tới trung tâm đô thị.

---

## 3. Nhận định về Khoảng cách Khái quát hóa (Generalization Gap)

1. **Độ lệch giữa Test và CV:**
   - Cả 5 mô hình đều có Test MSE cao hơn CV MSE khoảng 17.900 đơn vị. Điều này là hoàn toàn tự nhiên và phản ánh trung thực bản chất dữ liệu: phương sai của biến `realSum` trên tập Test ($S^2_{\text{test}} = 120.131,61$) vốn cao hơn đáng kể so với phương sai trên tập Train ($S^2_{\text{train}} = 104.402,75$).
2. **Tính ổn định của thứ bậc:**
   - Thứ bậc của các mô hình trên tập Test hoàn toàn nhất quán với kết quả 5-Fold Cross-Validation:
     $$\text{MSE}_{\text{M3}} < \text{MSE}_{\text{M4}} \approx \text{MSE}_{\text{M2}} < \text{MSE}_{\text{M1}} < \text{MSE}_{\text{M0}}$$
   - M4 (Ridge $\alpha=0.1$) và M2 (MLR) đạt sai số gần như trùng khớp trên tập test (97.963,94 vs 97.964,14), chứng minh định lý toán học: Ridge với $\alpha \to 0$ hội tụ hoàn toàn về OLS.

---

## 4. Bàn giao cho Task T11 (Thành viên B)

File dữ liệu dự đoán chi tiết **`outputs/tables/test_predictions.csv`** (gồm 10.342 dòng cho mỗi mô hình) đã được tạo lập đầy đủ với các trường khóa truy vết:
- `source_file`, `source_row`
- `model_id`, `actual`, `predicted`, `residual`
- `split`, `protocol_id`

Thành viên B sẵn sàng tiếp nhận file này để triển khai Task T11: Vẽ biểu đồ phần dư đa biến (residual plot theo fitted values), phân tích các điểm ngoại lai sai số lớn và bóc tách sai số theo từng thành phố/loại phòng.
