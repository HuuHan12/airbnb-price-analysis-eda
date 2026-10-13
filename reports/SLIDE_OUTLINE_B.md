# T15 — dàn ý slide và phần nói của B

Bản chuẩn bị nội dung ngày 12/10/2026, **chưa phải PPTX nộp cuối**. T05/T06/T09 đã có số liệu chạy. T08/T10/T11 chưa có, nên phần test/kết luận chưa điền; không lấy CV/training làm test. Tên/MSSV/mã nhóm và hệ học do nhóm điền thật.

Khung 13 slide đề xuất nằm trong các giới hạn slide mẫu: Giới thiệu 1 slide; dữ liệu 1 slide; nội dung phân tích 7 slide; kết quả/kết luận 2 slide; bìa và nhóm riêng. Mục tiêu 10 phút thuyết trình +5 phút demo. Tùy số liệu cuối có thể gộp/cắt, không kéo dài để đủ số slide.

| Slide | Nội dung | Người nói đề xuất | Bằng chứng đã có / phụ thuộc |
|---|---|---|---|
| 1 | Tên đề tài và nhóm thật, không overclaim nghiên cứu/module du lịch | A | Chờ thông tin nhóm; phương pháp hồi quy đúng phần đã làm |
| 2 | Ảnh/tên/MSSV hai thành viên; mỗi người tự giới thiệu | A+B | Online bắt buộc, mặt động đủ người trong video |
| 3 | Làm gì, cách làm và minh bạch nguồn/AI ngắn | A | Kết quả model cuối chờ T10; không ghi “hoàn toàn tự làm” |
| 4 | Data 20 file, 51.707×24, target theo README, metadata/khuyết | A | Notebook 01/02; index không listing ID |
| 5 | Quy trình thật và T07: raw target, holdout, folds, Pipeline | A | config/manifest/src, tránh đọc từng dòng code |
| 6 | Q1: lệch giá và cơ cấu loại phòng | B | b_02, bảng nhóm; mean 279,88 vs median 211,34; Shared n=366 |
| 7 | Q2: hai nhóm ngày trong city và khác cơ cấu mẫu | B | b_03 + b_07; Amsterdam median chênh 61,40, chưa ghép cùng listing |
| 8 | Q3: tương quan gộp vs trong city | B | b_05/b_06; capacity r≈0,203 gộp; Amsterdam≈0,528, Lisbon≈0,573 |
| 9 | Q4: ANOVA F/p/n và giới hạn | B | Bảng ANOVA; room F≈846,138; variance ratio≈19,69; không suy nhân quả |
| 10 | M0/M1/M2 của A, M3/M4 của B: cách so sánh | A+B | M3 degree 2/3; Ridge alpha grid; chờ kết quả T08 |
| 11 | Bảng CV chung và lý do chốt mô hình | B | T09 đã có; chờ T08 rồi chọn bằng CV MSE. Chưa tuyên bố thắng chung |
| 12 | Test metrics, residual/lỗi nhóm và case | B | Chờ T10/T11; không điền từ CV, không gọi sai số là gian lận |
| 13 | Kết quả thật và giới hạn cuối cùng | A+B | Chờ T10; không thêm hướng phát triển trong Kết luận report |

Phần B nói khoảng 4–5 phút: giá/cơ cấu → nhóm ngày → liên hệ/kiểm định có giới hạn → so sánh CV → kết quả test khi có. Cả A/B đều nói nội dung chuyên môn mình hiểu và khớp phụ lục phân công; không giao B chỉ bấm slide.

Demo 5 phút dùng notebook cuối A+B tích hợp: kiểm data/output, mở vài kết quả đúng câu hỏi, giải thích bảng mô hình/dự đoán/residual; không train grid trong demo. Online không bắt phải chung một laptop hoặc chỉ Teams; video phải thấy mặt động và phần trình bày, ảnh tĩnh không thay webcam.

Nguồn nội dung B: reports/eda_findings.md, reports/b_model_findings.md và bảng/hình Python đã chạy. Dàn ý là phần chuẩn bị; status T15 chưa “Hoàn thành” khi chưa có slide bản cuối/đối chiếu/diễn tập.
