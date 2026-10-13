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
