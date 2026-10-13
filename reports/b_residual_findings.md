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

## Đoạn kết luận dùng cho T13

Đồ án phân tích 51.707 quan sát Airbnb từ 20 tệp của 10 thành phố, mô tả phân phối giá và so sánh các nhóm bằng thống kê, Pearson và ANOVA với giới hạn giả định rõ ràng. Năm mô hình hồi quy được so sánh bằng cùng 5-fold CV trong 41.365 mẫu train; đa thức bậc 3 được chọn theo MSE CV thấp nhất. Trên holdout 10.342 mẫu, mô hình đạt RMSE 311.70, MAE 102.02, R² 0.1912, giảm MSE 19.12% so với baseline. Phân tích phần dư cho thấy sai số tập trung ở một phần nhỏ quan sát và khác nhau theo nhóm. Kết quả còn hạn chế do giá lệch mạnh, thiếu metadata về kỳ giá và listing ID, cùng khả năng lặp tọa độ giữa train/test; đây là đánh giá trên bộ dữ liệu cung cấp, không phải bằng chứng nhân quả hay xác thực ngoài mẫu thu thập.
