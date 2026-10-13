# T13 — Nội dung báo cáo phần B để A tích hợp

Bản nội dung ngày 13/10/2026, không phải Word/PDF nộp cuối. A dùng đúng Template_IE313.docx, style BT/Heading, đưa hình vào và đánh số/caption/dẫn hình. Chưa có tên/MSSV/mã nhóm; không tự điền thông tin thật.

## Giới thiệu — đoạn kết quả đề xuất

Đồ án phân tích và dự đoán realSum của các quan sát Airbnb ở 10 thành phố châu Âu bằng thống kê mô tả, Pearson, ANOVA và các mô hình hồi quy đã học. Nhóm dùng Python để kiểm tra dữ liệu, so sánh năm mô hình trên cùng giao thức CV và đánh giá holdout. Mô hình đa thức bậc 3 được chọn bằng MSE CV, đạt RMSE 311,70, MAE 102,02 và R² 0,1912 trên 10.342 mẫu test.

Dữ liệu lấy từ 20 CSV cung cấp trong source dự án, không tự thu thập. Nhóm tái sử dụng code dự án và vận dụng tài liệu môn học; Codex đã hỗ trợ viết/chạy code B, kiểm tra số liệu và soạn nội dung báo cáo. Các kết quả được đối chiếu với dữ liệu và giao thức trong repo. A cần khai thêm công cụ AI, nguồn tham khảo và lịch sử tái sử dụng thực tế của mình trước khi chốt bản nộp.

## Nội dung EDA và kiểm định

# Phát hiện T05–T06 của B

Ngày chạy: 12/10/2026. Các bảng `full_descriptive` mô tả toàn bộ 51.707 quan sát; bảng `train_descriptive` chỉ train. Đây không phải kết quả test mô hình, không dùng bảng mô tả để tự động lọc predictor.

## Q1: giá và cơ cấu mẫu

- Mean giá 279.88, median 211.34, std 327.95, skew 21.42; đơn vị EUR/kỳ giá theo README, chưa xác minh metadata gốc. Mean cao hơn median; không dùng mean một mình để nói giá điển hình.
- Median Amsterdam 460.24, Athens 127.72. Khác mặt bằng giá theo nhóm quan sát; không kết luận city gây chênh giá hoặc dữ liệu đại diện toàn thị trường.
- Entire home/apt: n=32,648, median 248.46; Private room: n=18,693, median 166.37; Shared room: n=366, median 124.48. Shared chỉ 0.708%: đọc n từng ô trước so sánh.
- Cờ IQR và lý do giữ giá gốc dùng phần A đã review; chưa chứng minh giá cao là luxury/biệt thự. Hình B giữ đủ giá, dùng trục log có chú thích.

## Q2: hai nhóm ngày

- Chênh median gộp theo city lớn nhất về trị tuyệt đối tại amsterdam: weekdays 430.25 (n=1,103), weekends 491.65 (n=977), chênh 61.40.
- Đây là so sánh hai tập quan sát, không ghép cặp cùng phòng. Đối chiếu `eda_day_comparison_by_room.csv` và biểu đồ cơ cấu loại phòng để tách sự khác cơ cấu; không nói “cùng phòng tăng giá cuối tuần”.
- Bảng nhóm tạo đủ tổ hợp: count=0 cho tổ hợp không có mẫu, giá giữ NaN; không điền giá 0. `eda_sampling_counts.csv` lưu tỷ lệ theo city/day và n.

## Q3: Pearson

- r sức chứa–giá toàn bộ 0.203, n=51,707; r tuyến tính gộp nhỏ không phủ nhận liên hệ trong city. Xem bảng r/p/n từng city và scatter; dữ liệu tọa độ lặp làm độc lập mẫu chưa xác minh.
- Kế hoạch môn dùng ngưỡng khoảng 0,3 để tham khảo bài giá xe; không dùng ngưỡng này loại toàn bộ yếu tố Airbnb. Allowlist mô hình cố định theo ý nghĩa; các biến index/tọa độ vẫn được mô tả nhưng chưa đưa vào core do metadata/diễn giải.

## Q4: ANOVA

- ANOVA giá theo room_type toàn bộ: F=846.138, p=underflow_float64; not exact zero, min nhóm n=366; tỷ số phương sai nhóm lớn nhất/nhỏ nhất 19.69. Báo F/p đi cùng mean/median/n, không gọi p nhỏ là tác động lớn hay mọi cặp khác nhau.
- Giả định độc lập, phương sai và dạng phần dư không được đảm bảo: giá lệch phải, nhóm mất cân đối, tọa độ lặp. Đây là áp dụng kỹ thuật môn với giới hạn, không kết luận nhân quả/định giá đúng.
- p dưới độ biểu diễn float64: bảng để giá trị numeric trống với `p_underflow=True`, nhãn underflow; không khẳng định xác suất đúng bằng 0. Giữ thống kê F/r và n để đọc kết quả.

## Đầu ra và sử dụng

`eda_group_summary.csv`, `eda_sampling_counts.csv`, hai bảng chênh ngày, `pearson_price_evidence.csv`, `anova_price_evidence.csv`, `anova_group_details.csv`, `feature_evidence.csv`; 7 hình có tiền tố `b_`. Một dòng mỗi phép xét có scope/context để tránh nhầm EDA toàn bộ với kết quả trên train.

Các hình/bảng được tạo bằng Python. AI hỗ trợ code và bản thảo trong lượt này; nhóm cần kiểm tra, hiểu và khai báo công cụ thực tế khi viết đoạn minh bạch. Phần nhận xét này chỉ dùng số tính từ data, không sao chép kết quả mô hình ngoài.

## Thiết kế và kết quả phần B

# T09: đa thức và Ridge của B

Đã chạy train/CV, không đánh giá hoặc dự đoán test. So sánh cùng config, manifest và folds trong T07.

- M3: chọn degree_3 theo CV MSE trung bình 79228.00, fit lại chỉ train để lưu model.
- M4: chọn alpha_0.1 theo CV MSE trung bình 79988.15, fit lại chỉ train để lưu model.

Chưa tuyên bố mô hình thắng chung: phải nhận M0/M1/M2 của A và chốt bằng CV trước T10. Mean RMSE của folds khác sqrt(mean MSE); CSV lưu rõ từng fold và mean/std.

Allowlist cố định theo metadata trước CV; không lọc predictor theo target. Bậc 2/3 chỉ trên capacity, bedrooms, dist; các nhóm city/day/room và phần numeric còn lại dùng cùng biểu diễn nền. Ridge dùng dãy alpha đã có trong kế hoạch.

## Đánh giá năm mô hình trên cùng holdout

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


## Phân tích lỗi

# T11 — phần dư, lỗi nhóm và trường hợp sai số lớn

Mô hình M3 đã chốt ở T10 bằng CV; phân tích này chỉ mô tả holdout, không đổi biến, bậc, alpha, split hay xử lý giá dựa trên test. Đã đối chiếu toàn bộ dự đoán năm mô hình với CSV gốc qua source_file/source_row, giá thực tế, phần dư và bốn metric T10.

## Kết quả chính

Trên 10,342 dòng test, RMSE = 311.70, MAE = 102.02, R² = 0.1912. MSE giảm 19.12% so với baseline M0 trên cùng test. Kết quả thể hiện cải thiện so với dự đoán trung bình nhưng mức giải thích biến thiên còn thấp; không bảo đảm chất lượng định giá ngoài bộ dữ liệu.

Median sai số tuyệt đối = 70.92; phân vị 90% = 186.46. Trung bình actual−predicted = -0.79: số dương là dự đoán thấp hơn giá quan sát trung bình, số âm là cao hơn. Giá ở đây dùng nguyên realSum; EUR theo README, kỳ giá chưa được xác minh, không đổi sang giá/đêm.

Nhóm 1% dòng có lỗi bình phương lớn nhất chiếm 86.08% tổng SSE. Điều này mô tả độ tập trung sai số; không được loại các dòng này để báo metric đẹp hơn. Có 167 dự đoán âm; giữ nguyên để phản ánh hạn chế mô hình, không cắt về 0 sau khi nhìn test.

Trong các city quan sát ở test, athens có RMSE lớn nhất (580.44, n=1040). So sánh này chịu ảnh hưởng thang giá, phân phối và cơ cấu mẫu; không chứng minh thành phố đó có chất lượng dữ liệu kém. Bảng lỗi room_type/day_type/city×room_type luôn kèm n; nhóm ít mẫu có thể biến động lớn.

## Hình và trường hợp truy vết

Hình b_08 thể hiện tất cả các điểm test, đường residual=0 và đường actual=predicted; không cắt đuôi. Hình b_09 so sánh RMSE theo nhóm kèm số mẫu. Hình b_10 thể hiện mức tập trung SSE. Các hình là mô tả; chưa có kiểm định chính thức để khẳng định phân phối chuẩn hoặc phương sai phần dư không đổi.

Bảng b_residual_cases.csv chứa 10 dòng có sai số tuyệt đối lớn nhất kèm file/dòng nguồn, city, room, sức chứa, bedrooms, dist, actual và predicted. source_row là khóa truy vết đã tạo khi nạp CSV, không phải listing ID hay mặc định số dòng Excel. Sai số lớn không chứng minh gian lận, giá sai, nhà sang trọng hoặc cùng listing.


## KẾT LUẬN — đoạn đề xuất

Đồ án phân tích 51.707 quan sát Airbnb từ 20 tệp của 10 thành phố, mô tả phân phối giá và so sánh các nhóm bằng thống kê, Pearson và ANOVA với giới hạn giả định rõ ràng. Năm mô hình hồi quy được so sánh bằng cùng 5-fold CV trong 41.365 mẫu train; đa thức bậc 3 được chọn theo MSE CV thấp nhất. Trên holdout 10.342 mẫu, mô hình đạt RMSE 311.70, MAE 102.02, R² 0.1912, giảm MSE 19.12% so với baseline. Phân tích phần dư cho thấy sai số tập trung ở một phần nhỏ quan sát và khác nhau theo nhóm. Kết quả còn hạn chế do giá lệch mạnh, thiếu metadata về kỳ giá và listing ID, cùng khả năng lặp tọa độ giữa train/test; đây là đánh giá trên bộ dữ liệu cung cấp, không phải bằng chứng nhân quả hay xác thực ngoài mẫu thu thập.

## Kiểm tra khi tích hợp

Không đưa toàn bộ ghi chú phát triển/biên bản nghiệm thu vào báo cáo. Chọn hình có thông tin, giải thích trước/sau hình; tránh lặp bảng CV và bảng test. TLTK cần thông tin nguồn thật và ngày truy cập thật, không tự bịa hoặc đưa slide GV vào danh mục cuối. Phụ lục ghi đúng việc đã làm và AI đã hỗ trợ; không tự khai 50/50. Chưa có Word/PDF đã kiểm layout nên T13 mới hoàn tất nội dung, chưa nghiệm thu bộ nộp.
