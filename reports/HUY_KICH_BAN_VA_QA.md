# Kịch bản và chuẩn bị hỏi đáp Huy

Phần chuẩn bị T15/T18, dùng cùng HUY_Slide_ban_giao.pptx. Các mốc là thời lượng đề xuất, chưa phải bằng chứng đã diễn tập. Mỗi người nói nội dung chuyên môn mình hiểu; cả hai cần tự giới thiệu thật. Nếu online, bổ sung ảnh/tên/MSSV thật và webcam động đủ hai người trong video.

| Slide | Người nói | Thời lượng đề xuất |
|---|---|---|
| 1. Đề tài | Hàn | 20 giây |
| 2. Thành viên | Hàn + Huy | 30 giây |
| 3. Mục tiêu/minh bạch | Hàn | 35 giây |
| 4. Dữ liệu | Hàn | 45 giây |
| 5. Giao thức | Hàn | 45 giây |
| 6. Phân phối giá | Huy | 50 giây |
| 7. Nhóm ngày | Huy | 50 giây |
| 8. Pearson | Huy | 45 giây |
| 9. ANOVA | Huy | 40 giây |
| 10. Các mô hình | Hàn + Huy | 55 giây |
| 11. Chọn bằng CV | Huy | 50 giây |
| 12. Test/phần dư | Huy | 60 giây |
| 13. Kết luận | Hàn + Huy | 45 giây |

Tổng dự kiến 570 giây = 9 phút 30 giây, còn khoảng 30 giây cho chuyển slide. Demo sau đó 5 phút. Nhóm phải bấm giờ khi diễn tập; đọc văn bản dài không chứng minh sẽ đúng thời lượng.

## Lời nói phần Huy

**Slide 6.** “Giá có trung bình 279,88 nhưng trung vị chỉ 211,34; skewness 21,42 cho thấy lệch phải mạnh. Vì vậy chúng em báo thêm median, IQR và số mẫu thay vì dùng một giá trung bình làm mức điển hình. Hình dùng trục log để nhìn đủ các điểm, còn mô hình giữ nguyên realSum. Shared room chỉ có 366 mẫu, chiếm 0,708%, nên các so sánh tiếp theo phải đọc số mẫu từng nhóm.”

**Slide 7.** “Ở Amsterdam, median weekdays là 430,25 trên 1.103 mẫu và weekends là 491,65 trên 977 mẫu, chênh 61,40. Hai file không có listing ID để ghép cùng phòng, nên đây là khác biệt giữa hai tập quan sát. Chúng em còn đối chiếu cơ cấu loại phòng theo ngày và không kết luận cùng phòng tăng giá vào cuối tuần.”

**Slide 8.** “Pearson sức chứa–giá gộp khoảng 0,203, nhưng trong Amsterdam là 0,528 và Lisbon 0,573. r gộp nhỏ không đủ để bỏ sức chứa hoặc tất cả biến khác. Chúng em giữ tập biến lõi theo ý nghĩa và mức rõ ràng của metadata; Pearson chỉ là bằng chứng mô tả tuyến tính, không chứng minh nhân quả.”

**Slide 9.** “ANOVA theo loại phòng cho F khoảng 846,138 và nhóm nhỏ nhất có 366 mẫu. p nằm dưới mức biểu diễn float64, chúng em không ghi p chính xác bằng 0. Tỷ số phương sai nhóm khoảng 19,69, giá lệch và nhóm mất cân đối, nên giả định kiểm định không được đảm bảo. Chúng em báo F/p/n và giới hạn, không suy p nhỏ thành tác động lớn hay mọi cặp nhóm khác nhau.”

**Slide 10, sau Hàn nói M0–M2.** “Phần em là M3 và M4. M3 khai triển đa thức trên sức chứa, bedrooms và dist, rồi ghép các biến còn lại và context; thử bậc 2 và 3. M4 dùng Ridge và thử bảy giá trị alpha đã ghi trong config. Tất cả dùng đúng manifest, fold và preprocessing trong Pipeline để so sánh cùng điều kiện.”

**Slide 11.** “M3 bậc 3 có MSE trung bình validation thấp nhất, 79.228,00, nên được chọn trước khi đánh giá test. M4 chọn alpha 0,1 trong họ Ridge. RMSE CV là trung bình RMSE từng fold, không phải căn MSE CV trung bình. Chênh M3 với M2 còn nhỏ; chúng em chưa có kiểm định để khẳng định ưu thế ổn định ngoài bộ dữ liệu.”

**Slide 12.** “Trên 10.342 mẫu test nguyên giá, M3 đạt RMSE 311,70, MAE 102,02 và R² 0,1912. MSE giảm 19,12% so baseline cùng test, nhưng mức giải thích còn thấp. Một phần trăm mẫu lỗi lớn chiếm 86,08% tổng SSE; có 167 dự đoán âm. Chúng em giữ tất cả khi báo metric, không loại giá cao hoặc cắt dự đoán sau khi nhìn test. Demo sẽ mở phần dư và một case có khóa truy vết.”

**Slide 13, phần Huy.** “Phân tích đã mô tả phân phối giá, quan hệ trong nhóm và so sánh mô hình trên cùng giao thức. Giới hạn chính là thiếu kỳ giá/listing ID, giá lệch mạnh và dự đoán âm. Đây là kết quả trên dữ liệu cung cấp; chúng em không xem là bằng chứng nhân quả hoặc xác thực định giá ngoài mẫu.”

## Demo 5 phút

| Mốc | Thao tác và điều cần giải thích |
|---|---|
| 0:00–0:45 | Hàn mở notebook cuối, kiểm đường dẫn/data/protocol. Huy có notebook 06 bàn giao để tích hợp. |
| 0:45–1:45 | Huy mở bảng CV/test: cách chọn M3 bằng CV, bốn metric test, hai vai trò khác nhau. |
| 1:45–3:00 | Huy mở bảng lỗi room/day kèm n và hình phần dư; giải thích actual−predicted, 167 dự đoán âm, tập trung SSE. |
| 3:00–4:15 | Mở case đầu, kiểm source_file/source_row và actual trong dữ liệu gộp. Không gọi là giá sai/gian lận. |
| 4:15–5:00 | Hàn/Huy chỉ kết quả, giới hạn và hướng dẫn chạy; không đọc từng dòng code hoặc chạy grid dài. |

Chạy sẵn notebook và mở output trên máy trình bày. Hàn vẫn phụ trách T16 tích hợp notebook cuối. Notebook 06 chỉ đọc kết quả đã chốt và kiểm truy vết, không fit lại mô hình; đã có log chạy kernel mới trong huy_demo_run.json.

## Câu hỏi có thể gặp

| Câu hỏi | Cách trả lời dựa trên sản phẩm thật |
|---|---|
| Vì sao phải phân tích trước khi mô hình? | Phát hiện giá lệch, nhóm nhỏ/mất cân đối, khác mặt bằng city và metadata thiếu; nhờ đó chọn thống kê/hình phù hợp và giới hạn diễn giải. EDA không dùng để tự động chọn predictor theo target test. |
| Vì sao không bỏ giá cao? | Chưa có bằng chứng giá sai. Giao thức giữ raw target và mọi mẫu; bỏ sau nhìn test sẽ làm sai ý nghĩa đánh giá hiện tại. IQR chỉ là cờ thăm dò. |
| Vì sao Pearson nhỏ vẫn giữ sức chứa? | r gộp 0,203 khác r trong city; tập biến cố định theo ý nghĩa, không lấy ngưỡng 0,3 của ví dụ giá xe làm điều kiện tuyệt đối. |
| ANOVA p=0 có đúng không? | Không. Phần mềm underflow dưới mức biểu diễn; báo trạng thái này cùng F/n/giới hạn phương sai và độc lập. |
| Vì sao M3 bậc 3? | Thử bậc 2/3 bằng cùng CV trong train; bậc 3 thấp nhất. Không thử lại bậc theo kết quả test. |
| Vì sao Ridge gần OLS? | Trong cấu hình alpha0,1 và dữ liệu này metric gần nhau. Không dùng một thí nghiệm để chứng minh định lý hoặc tuyên bố hệ số/dự đoán trùng hoàn toàn. |
| R² thấp có làm bài sai? | Kết quả thấp phản ánh giới hạn trên dữ liệu/giao thức này. Báo thật và giải thích; không có ngưỡng R² bắt buộc hay bảo đảm điểm đã đọc từ hướng dẫn thầy. |
| Vì sao RMSE cao hơn MAE nhiều? | Bình phương nhấn mạnh lỗi lớn; 1% mẫu lỗi bình phương lớn chiếm86,08%SSE. Đây là mô tả đã tính, không kết luận ngoại lai sai. |
| Dự đoán âm xử lý thế nào? | Báo 167 trường hợp và giữ nguyên khi tính metric; mô hình chưa ràng buộc dương. Không cắt về0 sau xem test để cải thiện kết quả. |
| Test có thực sự độc lập theo listing? | Chưa xác minh: thiếu ID, tọa độ có thể lặp. Train/test tách theo dòng, không khẳng định tổng quát hóa sang listing mới hoặc thành phố mới. |
| Giá là mỗi đêm hay hai đêm? | README khai báo EUR và kỳ lưu trú, nhưng metadata gốc chưa được xác minh. Kết quả giữ realSum, không chuyển sang giá/đêm. |
| AI đã làm gì? | Codex hỗ trợ code, chạy kiểm chứng và bản thảo phần Huy. Nhóm cần tự kiểm tra/hiểu khi trình bày; Hàn khai thêm công cụ và nguồn phần mình thật. |

Không học thuộc để trả lời vượt kết quả. Khi thiếu metadata, nói rõ chưa xác minh. T18 chỉ hoàn thành sau diễn tập/ghi hình thực tế, không phải sau có kịch bản.
