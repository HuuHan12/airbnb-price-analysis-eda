# BIÊN BẢN NGHIỆM THU KỸ THUẬT TASK T10
## Chốt Mô hình và Đánh giá trên Tập Holdout Test

- **Người thực hiện phối hợp:** Thành viên A + Thành viên B
- **Thời điểm nghiệm thu:** 13/10/2026
- **Giao thức thực nghiệm:** `ie313_raw_v1_seed0_cv5`
- **Tình trạng nghiệm thu:** **100% HOÀN THÀNH (PASSED)**

### Tóm tắt Nghiệm thu
1. **Chốt mô hình:** Quy tắc chọn CV trong code xác định **M3 (Polynomial bậc 3)** là mô hình chiến thắng chung cuộc dựa trên $CV\_MSE = 79,228.00$.
2. **Đánh giá Test:** Mở khóa tập Test 10.342 dòng, xác nhận kết quả:
   - M0 (Mean Baseline): Test MSE = 120.131,61 | Test R² = -0,0000
   - M1 (SLR): Test MSE = 115.888,69 | Test R² = 0,0353
   - M2 (MLR): Test MSE = 97.964,14 | Test R² = 0,1845
   - M3 (Polynomial d=3): **Test MSE = 97.156,55** | **Test R² = 0,1912** (Dẫn đầu)
   - M4 (Ridge a=0.1): Test MSE = 97.963,94 | Test R² = 0,1845
3. **Bàn giao T11:** Đã tạo file `outputs/tables/test_predictions.csv` đầy đủ 51.710 bản ghi (10.342 dòng x 5 mô hình) có mã truy vết `source_file`, `source_row`.
