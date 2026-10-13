# BÁO CÁO KẾT QUẢ ĐÁNH GIÁ TẬP TEST VÀ CHỐT MÔ HÌNH (TASK T10)

> **Người thực hiện phối hợp:** Thành viên A + Thành viên B  
> **Giao thức thực nghiệm:** `ie313_raw_v1_seed0_cv5` (`config/experiment_config.json`)
> **Quy mô dữ liệu:** Tập Train 41.365 dòng (5-Fold CV) | Tập Holdout Test 10.342 dòng (tách khỏi train; chưa xác minh độc lập theo listing).

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
  2. **Trên tập Test (10.342 dòng holdout, không dùng để chọn mô hình):** M3 tiếp tục giữ vững vị trí dẫn đầu với $\text{MSE}_{\text{test}} = 97,156.55$ và $R^2_{\text{test}} = 0.1912$.
  3. **Lý do chuyên môn:** Khai triển đa thức bậc 3 trên 3 biến số cốt lõi (`person_capacity`, `bedrooms`, `dist`) cho phép biểu diễn các hạng phi tuyến và tương tác. MSE CV thấp hơn trong thí nghiệm này; chưa chứng minh quan hệ thực tế là phi tuyến hoặc có tính nhân quả.

---

## 3. Nhận định về Khoảng cách Khái quát hóa (Generalization Gap)

1. **Độ lệch giữa Test và CV:**
   - Trong snapshot này, Test MSE cao hơn CV MSE khoảng 15.729–17.976. Đây là chênh lệch quan sát, chưa đủ để kết luận nguyên nhân hay mức ổn định ngoài bộ dữ liệu. MSE baseline M0 không phải phương sai mẫu train/test: M0 dự đoán trung bình train, còn CV MSE là trung bình lỗi của các fold. Không thay hai đại lượng này cho phương sai.
2. **Tính ổn định của thứ bậc:**
   - Thứ bậc của các mô hình trên tập Test hoàn toàn nhất quán với kết quả 5-Fold Cross-Validation:
     $$\text{MSE}_{\text{M3}} < \text{MSE}_{\text{M4}} \approx \text{MSE}_{\text{M2}} < \text{MSE}_{\text{M1}} < \text{MSE}_{\text{M0}}$$
   - M4 (Ridge $\alpha=0.1$) và M2 (MLR) đạt sai số gần như trùng khớp trên tập test (97.963,94 vs 97.964,14), cho thấy hai mô hình có metric gần nhau trong cấu hình này. Một kết quả thực nghiệm với alpha=0.1 không chứng minh định lý hội tụ và không cho thấy hệ số hoặc dự đoán trùng hoàn toàn.

---

## 4. Bàn giao cho Task T11 (Thành viên B)

File dữ liệu dự đoán chi tiết **`outputs/tables/test_predictions.csv`** (gồm 10.342 dòng cho mỗi mô hình) đã được tạo lập đầy đủ với các trường khóa truy vết:
- `source_file`, `source_row`
- `model_id`, `actual`, `predicted`, `residual`
- `split`, `protocol_id`

Thành viên B sẵn sàng tiếp nhận file này để triển khai Task T11: Vẽ biểu đồ phần dư đa biến (residual plot theo fitted values), phân tích các điểm ngoại lai sai số lớn và bóc tách sai số theo từng thành phố/loại phòng.
