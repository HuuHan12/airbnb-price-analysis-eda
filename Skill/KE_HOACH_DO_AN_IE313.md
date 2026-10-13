# Kế hoạch đồ án IE313 và phân công hai thành viên

Ngày lập và cập nhật: 08/10/2026, sau khi đọc thêm transcript Buổi 07 và Buổi 10. Tên/MSSV hai thành viên và mã nhóm chưa được cung cấp. Kế hoạch dùng Thành viên A/B. Buổi 10 công bố mốc cuối **15/10/2026**; lịch làm việc bên dưới là đề xuất của nhóm để kịp mốc này, chưa xác minh giờ đóng cổng hay thay đổi mới trên eLearning.

**Đề tài đề xuất: Phân tích và dự đoán giá thuê Airbnb tại 10 thành phố châu Âu bằng các mô hình hồi quy.** Tên bổ sung phương pháp theo hướng dẫn đặt tên Buổi 10; chỉ chốt sau khi đối chiếu nội dung đã làm. Giữ dữ liệu có sẵn, triển khai theo nội dung môn học, ưu tiên giải thích đúng kết quả và đáp ứng quy cách nộp. Kế hoạch này hướng đến bài làm tốt theo tài liệu đã đọc; không đặt trước điểm số hoặc chỉ số mô hình phải đạt.

## 0. Đánh giá dữ liệu hiện tại và lý do làm đồ án

### 0.1. Kết luận về mức độ phù hợp

**Bộ dữ liệu phù hợp để làm đồ án phân tích và trực quan giá, có thể thử nghiệm hồi quy theo môn học.** Dữ liệu có nhiều quan sát, cùng schema, mục tiêu số rõ và nhiều nhóm để so sánh. Điểm khó nằm ở phân phối giá, cơ cấu nhóm và cách diễn giải nguồn dữ liệu. Chưa có kết quả huấn luyện nên chưa thể kết luận dữ liệu cho dự đoán tốt hoặc mô hình nào hiệu quả.

Đánh giá này có ba mức riêng biệt: **tệp đọc được**, **giá trị vượt qua các kiểm tra đã thực hiện**, và **ý nghĩa/nguồn dữ liệu được xác minh**. Hai mức đầu đã có bằng chứng bên dưới; mức thứ ba vẫn thiếu metadata gốc ở một số biến. Không dùng chữ “data sạch hoàn toàn” để gộp cả ba mức.

### 0.2. Tình trạng tệp và tiến độ thực tế

| Hạng mục | Tình trạng hiện tại | Ý nghĩa đối với công việc tiếp theo |
|---|---|---|
| archive.zip Airbnb | Kiểm tra CRC ZIP không báo member hỏng; đọc được đủ 20 CSV, 51.707 dòng, schema thống nhất | Có thể bắt đầu phân tích từ dữ liệu hiện có; không cần tải hoặc thu thập thêm để đạt phạm vi đề xuất |
| CSV gốc | 20 cột/file, gồm Unnamed: 0; dữ liệu CSV chưa nén khoảng 10,76 MB | Vừa sức chạy trên máy demo; cần gộp có city/day_type và mã truy vết |
| Khuyết | 0 ô thiếu theo pandas; rà thêm các chuỗi rỗng, ?, ., none, null, n/a, na, nan, nat không phát hiện trường hợp nào | Báo rõ không cần điền khuyết trong bộ này; không có lý do chạy imputer chỉ để chứng minh đã học |
| Các kiểm tra giá trị cơ bản | Không có giá ≤ 0, khoảng cách âm, giá trị số NaN/±inf, sức chứa không nguyên, tọa độ vượt giới hạn địa lý toàn cầu | Chưa có bằng chứng buộc loại dòng vì các lỗi này. Kiểm tra này không xác nhận giá có đúng ngoài thực tế hay tọa độ đúng căn hộ |
| Trùng dòng | Không có dòng trùng hoàn toàn trong city/day_type khi bỏ chỉ số; có nhiều tọa độ lặp | Không deduplicate theo tọa độ một cách tự động; giữ khả năng truy vết |
| Metadata | README mô tả nguồn và biến; CSV không có tài liệu thu thập, thời điểm hoặc định nghĩa đầy đủ cho vài chỉ số | Phải khai báo mức độ biết rõ nguồn, giới hạn cách gọi biến và đơn vị |
| Code đồ án Airbnb | Hiện chỉ có README, requirements, .gitignore và archive.zip; chưa có notebooks/src/models/kết quả đồ án | README đang là định hướng. Công việc còn lại là triển khai, chạy và viết kết quả thật |
| CodeMonHoc.rar | Đã tải đủ và kiểm tra phần source/data; chứa bài thực hành Buoi1–Buoi5 | Có ví dụ kỹ thuật để tham khảo, không thay thế code phân tích Airbnb |
| Báo cáo và slide | Có template/khung GV; chưa có báo cáo kết quả hoặc slide đồ án đã hoàn thành | Bắt đầu điền phần dữ liệu/phương pháp, kết quả để sau thực nghiệm |

Các số liệu ở phần này là kiểm tra trực tiếp trên archive.zip hiện tại. Đây là kiểm kê và EDA sơ bộ để lập kế hoạch, chưa phải toàn bộ kết quả thực nghiệm cuối cùng.

### 0.3. Điểm mạnh của bộ dữ liệu

| Điểm mạnh có bằng chứng | Vì sao hữu ích cho đồ án | Cách tận dụng |
|---|---|---|
| 51.707 quan sát và 20 CSV cùng schema | Có quy mô để thống kê theo nhóm và giữ tập test; giảm công sức sửa định dạng giữa file | Gộp có nhãn nguồn, lập inventory, xây cùng một quy trình chạy lại |
| 10 thành phố × 2 nhóm ngày | Có các chiều so sánh được xác định từ tên file | Đặt Q1–Q2, vẽ groupby/pivot và biểu đồ so sánh rõ nhóm |
| Target realSum là số và có biến quy mô/vị trí/loại phòng/đánh giá | Hỗ trợ câu hỏi liên hệ với giá và các mô hình hồi quy đã học | Đặt Q3–Q5; không cần đổi sang bài toán phân loại hay thêm nhãn nhân tạo |
| Có cả biến số, phân loại và boolean | Có cơ hội vận dụng các kỹ thuật phù hợp ở Bài 2 và Bài 5 | Mã hóa room_type/city/day_type; Pearson cho biến số, ANOVA cho nhóm phù hợp |
| Không có khuyết hoặc lỗi miền cơ bản vừa kiểm tra | Có thể dành thời gian cho phân tích và đánh giá thay vì phần điền khuyết không cần thiết | Giữ nguyên raw và báo các kiểm tra đạt, tập trung vào ngoại lệ/nhóm/đánh giá |
| Có tọa độ và khoảng cách | Cho phép mô tả quan hệ vị trí–giá nếu giới hạn trong từng city | Scatter hoặc hình phân bố vị trí khi hữu ích; không bắt buộc thêm bản đồ/web app |
| Mức giá và cơ cấu nhóm khác nhau | Có vấn đề phân tích thực sự, không chỉ trình diễn lệnh vẽ | Giải thích vì sao trung bình chung và tương quan chung có thể chưa đủ |

Số lượng lớn là lợi thế cho thực nghiệm, nhưng không bảo đảm mẫu đại diện thị trường Airbnb hiện nay hoặc các quan sát độc lập.

### 0.4. Điểm yếu và ảnh hưởng cụ thể

| Điểm yếu/giới hạn | Bằng chứng hiện có | Nguy cơ nếu bỏ qua | Quyết định trong kế hoạch |
|---|---|---|---|
| Giá lệch phải và đuôi rất lớn | Median 211,34; mean 279,88; P99 khoảng 1.160,84; max 18.545,45; skewness 21,42 | Mean hoặc MSE có thể bị chi phối bởi một số giá cao; xóa toàn bộ điểm cao có thể đổi phạm vi bài toán | Báo median/IQR cùng mean/std, histogram/boxplot; xem ngoại lệ theo city, giữ test đầy đủ |
| Mất cân đối loại phòng | Shared room 366 dòng, chỉ 0,708%; Entire home/apt 63,140% | Kết quả tổng thể có thể che sai số nhóm ít mẫu; so sánh nhóm nhỏ khó ổn định | Ghi n ở từng bảng/hình, phân tích lỗi theo room_type, tránh khái quát mạnh về Shared room |
| Mất cân đối city và khác cơ cấu phòng | London 19,326% số dòng; Amsterdam 4,023%. Athens có 4.872 Entire home/apt và 397 Private room; Barcelona có 542 và 2.279 | Chênh giá giữa city có thể đồng thời phản ánh cơ cấu loại phòng; gọi city là nguyên nhân trực tiếp là vượt dữ liệu | So sánh thêm trong city/room_type; dùng city và loại phòng khi thiết kế mô hình |
| Tương quan gộp yếu nhưng không đồng nhất theo city | r(person_capacity, price) gộp ≈ 0,203; Amsterdam ≈ 0,528; Lisbon ≈ 0,573 | Loại hết biến vì ngưỡng độ lớn r > 0,3 của ví dụ giá xe sẽ bỏ các quan hệ hữu ích theo nhóm | Pearson và scatter theo city; chọn predictor có giải thích và kiểm chứng bằng CV |
| Điểm đánh giá tập trung cao | 88,04% cleanliness_rating ≥ 9; 76,86% guest_satisfaction_overall ≥ 90 | Khả năng phân biệt trong mẫu có thể hạn chế; tương quan thấp không chứng minh chất lượng không quan trọng ngoài thực tế | Xem phân phối/tần suất trước khi diễn giải hệ số; nêu phạm vi quan sát |
| Thuộc tính biểu diễn lặp | room_shared/room_private suy ra hoàn toàn từ room_type | Hệ số hồi quy có thể khó diễn giải khi đưa đồng thời toàn bộ biểu diễn lặp | Mô tả đủ trong dictionary, dùng một biểu diễn cho mô hình |
| Không có listing ID và nhiều tọa độ lặp | Index reset mỗi file; 21.582 dòng lặp city/lat/lng sau dòng đầu | Ghép nhầm phòng, xóa nhầm quan sát; train/test có thể chia các chỗ ở gần nhau sang hai phía | Không ghép cặp phòng theo index/tọa độ; nêu giới hạn split và kiểm tra thêm theo nhóm vị trí nếu đủ thời gian |
| Metadata và lịch thu thập chưa đầy đủ | Không có ngày thu thập, lịch đặt phòng, doanh thu hay định nghĩa đầy đủ chỉ số trong CSV | Dễ gọi sai giá/đêm, suy luận thời gian, nhu cầu hoặc giá trị thật | Khai báo theo README/chưa rõ; giới hạn đề tài ở phân tích mẫu và dự đoán realSum |
| Dữ liệu đã có các cột norm | attr_index_norm/rest_index_norm có sẵn nhưng công thức và phạm vi chuẩn hóa chưa có trong source | Dễ tưởng rằng mọi predictor đã được scaling phù hợp với train/test | Chọn biểu diễn có lý do, tự fit preprocessing cần thiết trong pipeline; không coi cột norm là bằng chứng chống leakage |

Các “nguy cơ” trong bảng là lý do thiết kế kiểm tra, không phải khẳng định tất cả đã xảy ra. Ví dụ, tọa độ lặp chưa chứng minh rò rỉ cùng listing; còn cần nhận diện/đánh giá phù hợp.

### 0.5. Vì sao phải phân tích dữ liệu này

**Vấn đề xuất phát từ dữ liệu:** cùng một bộ Airbnb có giá từ 34,78 đến 18.545,45, nhiều city và loại phòng với cơ cấu khác nhau. Một con số giá trung bình toàn bộ không cho biết một nhóm chỗ ở cụ thể có mức giá ra sao. Ta cần phân tích để biết giá phân bố thế nào, nhóm nào khác nhau, những biến nào có liên hệ với giá và liệu các biến có sẵn dự đoán được realSum tốt hơn mốc trung bình hay không.

**Giá trị của phần phân tích:** đưa ra kết quả có điều kiện rõ ràng, chẳng hạn trung vị của một city/loại phòng/nhóm ngày trong mẫu, thay vì một nhận xét chung “cuối tuần đắt” hoặc “gần metro đắt”. Thử nghiệm hồi quy giúp định lượng phần thông tin dự đoán mà các biến hiện có mang lại; nếu kết quả chưa tốt thì sai số và phần dư vẫn cho biết giới hạn của dữ liệu/mô hình. Không cần giả định đồ án sẽ tối ưu doanh thu hoặc có ứng dụng kinh doanh hoàn chỉnh.

**Lý do phù hợp môn học:** Bài 1 yêu cầu đặt câu hỏi theo dữ liệu; Bài 2 hướng dẫn chuẩn bị dữ liệu; Bài 3–5 yêu cầu trực quan và thăm dò; Bài 6–7 phát triển/đánh giá hồi quy. Bộ Airbnb cho phép vận dụng chuỗi này trên dữ liệu khác ví dụ giá xe, trong phạm vi nhóm tự phân tích và giải thích được.

Trong kế hoạch và khi trả lời Q&A, cần giải thích lý do chọn đề tài như trên. Riêng phần GIỚI THIỆU của **báo cáo nộp**, template ghi SV không cần trả lời “Tại sao làm đề tài này”; vì vậy giữ cấu trúc 2 đoạn theo mẫu, không thêm một phần lý do dài làm vượt ngân sách trang mục tiêu.

### 0.6. Vì sao chọn từng cách làm

| Việc cần làm | Vấn đề hoặc câu hỏi mà nó giải quyết | Vì sao chọn cách này | Căn cứ môn học và mức yêu cầu |
|---|---|---|---|
| Inventory/dictionary và kiểm tra giá trị | Tệp có đọc đủ không, mỗi dòng/cột nghĩa gì, được phép kết luận gì? | Tránh sai số mẫu, sai đơn vị, dùng index như ID và mô tả vượt metadata | Mô tả dataset **bắt buộc** trong template; kiểm tra kiểu/khuyết theo Bài 1–2 |
| Gộp kèm city/day_type | 20 file tách nhóm, dễ mất thông tin khi nối | Dùng nhãn từ tên file để phân tích so sánh và truy vết | Thiết kế của nhóm cho cấu trúc data hiện có |
| Thống kê mô tả + histogram/boxplot | Giá điển hình và độ phân tán là gì, giá cao có nhiều không? | Median/IQR bổ sung mean/std; hình cho thấy lệch/đuôi mà một số trung bình che mất | Bài 4–5; lựa chọn sát vấn đề dữ liệu |
| Groupby/pivot theo city/room_type/day_type | Chênh giá đến từ nhóm nào, so sánh đang dùng bao nhiêu mẫu? | Làm rõ cơ cấu nhóm và không nhập nhằng nhóm mẫu với cùng listing | Bài 5; trả lời Q1–Q2 |
| Pearson + scatter | Biến số liên hệ tuyến tính với giá ra sao? | r đo chiều/độ mạnh tuyến tính, scatter giúp thấy ngoại lệ và dạng cong | Bài 5; trả lời Q3. Không đủ để suy ra nhân quả hoặc loại mọi quan hệ phi tuyến |
| ANOVA loại phòng trong phạm vi hợp lý | Trung bình giữa các nhóm khác nhau không? | Bổ sung kiểm định cho so sánh boxplot, báo F/p cùng n/giả định | Bài 5; đề xuất áp dụng, **template không bắt mọi đồ án phải làm ANOVA** |
| Scaling và one-hot trong pipeline | Miền biến khác nhau, category chưa dùng trực tiếp trong hồi quy | Chuẩn bị predictor phù hợp, giữ quy trình fit/transform nhất quán | Bài 2 và Bài 6; chỉ áp dụng khi cần, không scaling target để trình bày sai đơn vị |
| Mốc mean và hồi quy đơn biến | Mô hình có hơn một dự đoán đơn giản không, một biến giải thích được gì? | Có mốc đánh giá và mô hình dễ giải thích slope/intercept | Bài 6; M0/M1 là lựa chọn thực nghiệm của nhóm |
| Hồi quy đa biến | Giá có thể liên hệ đồng thời với city, loại phòng, quy mô và vị trí | Kiểm tra thông tin bổ sung so với M1, không chỉ dựa r gộp | Bài 6; đề xuất mô hình lõi |
| Đa thức bậc thấp | Mối liên hệ có cần dạng cong không? | Thử bậc 2/3 có kiểm chứng thay vì mặc định tuyến tính hoặc bậc rất cao | Bài 6; dạng cong chưa được khẳng định trước khi xem dữ liệu/CV |
| Ridge | Độ phức tạp/hệ số liên hệ nhau có làm mô hình kém ổn định không? | Thử điều chuẩn, so với mô hình chưa điều chuẩn bằng cùng giao thức | Bài 7; không hứa Ridge thắng hoặc khẳng định đã có overfitting |
| Train/test + CV | Mô hình chỉ khớp dữ liệu đã thấy hay dự đoán được mẫu giữ lại? | Tách lựa chọn cấu hình khỏi đánh giá cuối, phát hiện chênh train/validation | Bài 7; 80/20, seed 0 và CV 5 là lựa chọn cụ thể theo ví dụ, không tỷ lệ bắt buộc |
| MSE/RMSE/MAE/R² + residual | Sai bao nhiêu, lỗi tập trung ở đâu, kết quả có hợp lý không? | MSE nhạy với sai lớn; RMSE/MAE dễ đọc trên thang giá; R² so với mốc; phần dư chỉ ra mẫu/nhóm mô hình còn sai | MSE/R² và biểu đồ theo Bài 6; RMSE/MAE được nêu trong Bài 7 |
| Report/template, minh bạch, phân công | Kết quả có đúng quy cách và truy được nguồn/đóng góp không? | Đáp ứng trực tiếp quy định nộp/chấm trong tài liệu cuối kỳ | **Bắt buộc** theo template; không thay bằng việc thêm nhiều mô hình |

**Phân biệt để tránh hiểu nhầm:** template bắt buộc mô tả dữ liệu, minh bạch, quy cách và sản phẩm nộp. Nó cho phép chọn quy trình và nhiều mô hình phù hợp. Bộ M0–M4, số hình, ANOVA, split và lịch làm việc đến 15/10 là **phương án của nhóm có căn cứ bài giảng**, không phải danh sách GV bắt buộc y nguyên. Nếu bỏ một phân tích không phù hợp dữ liệu, giải thích bằng câu hỏi/phạm vi; không thực hiện hình thức chỉ để đủ tên kỹ thuật.

### 0.7. Tiêu chí quyết định giữ phạm vi hiện tại

Giữ Airbnb làm đề tài vì đã có đủ dữ liệu và các chiều phân tích phù hợp nội dung môn học. Ưu tiên hoàn thiện EDA và đánh giá hồi quy trước RF/XGBoost/dashboard. Nếu kết quả hồi quy hạn chế, báo rõ các chỉ số và nguyên nhân có bằng chứng; không đổi target, xóa test giá cao hoặc tự thêm dữ liệu để tạo điểm số đẹp. Nếu ý nghĩa một biến chưa rõ, ghi giới hạn hoặc loại khỏi mô hình với lý do, vẫn mô tả nó trong dictionary.

## 1. Căn cứ và giới hạn đọc source

Đã đọc nội dung của 8 PDF bài giảng, Notes.txt, README.md, requirements.txt, .gitignore, hai tài liệu trong ZIP cuối kỳ và kiểm kê toàn bộ 20 CSV Airbnb. Đã đọc toàn bộ cell source của 13 notebook và các tệp Python trong bản CodeMonHoc.rar hoàn chỉnh, kiểm tra cấu trúc CSV bài thực hành và danh sách sheet của Canada.xlsx. Đã đọc thêm hai transcript DOCX Buổi 07/10; bảng dưới đây phần bổ sung ghi rõ các yêu cầu được làm rõ. Không chạy notebook cũ hoặc xem kết quả lưu trong notebook là kết quả của đồ án Airbnb.

| Nguồn | Nội dung dùng để lập kế hoạch |
|---|---|
| `02_Slides_Bai_giang/Bai01_Gioi_thieu_PTDL-Nhap_Xuat_Bo_du_lieu.pdf`, PDF tr. 3–10, 19–22 | Đặt câu hỏi phù hợp dữ liệu; hiểu từng dòng, từng cột, kiểu dữ liệu; nhập/xuất và thống kê ban đầu |
| `Bai02_Sap_xep_DL.pdf`, PDF tr. 3–23 | Kiểm tra khuyết, định dạng, chuẩn hóa, chia bin, mã hóa phân loại |
| `Bai03_Truc_quan.pdf`, PDF tr. 5–15, 29–44 | Chọn loại biểu đồ theo mục đích; truyền đạt thông điệp rõ |
| `Bai04_Cong_cu_TQ.pdf`, PDF tr. 4, 23–57, 62–67 | Quy trình trực quan; histogram, bar, box, scatter; dashboard là một công cụ được giới thiệu |
| `Bai05_PT_Tham_do.pdf`, PDF tr. 5–37 | Mean/median/mode, độ phân tán, skewness/kurtosis, ngoại lệ, Pearson, groupby/pivot, ANOVA, chọn biến |
| `Bai06_Mo_hinh.pdf`, PDF tr. 9–44 | Hồi quy đơn biến, đa biến, đa thức, Pipeline; regression/residual/distribution plot; MSE và R² |
| `Bai07_Danh_gia_MH.pdf`, PDF tr. 3–10, 17–32 | Train/test, CV, overfitting/underfitting, Ridge; Grid Search được nêu ở mục tiêu/nội dung, phần triển khai trong PDF cung cấp còn hạn chế |
| `Bai_Giang_TH_01_Python_for_DA.pdf` | Python, hàm, cấu trúc dữ liệu, pandas và NumPy |
| `05_Cuoi_ky_Do_an/Template_IE313.docx` | Quy cách báo cáo, minh bạch nguồn, sản phẩm nộp và các mức trừ điểm được ghi rõ |
| `05_Cuoi_ky_Do_an/Slides.pptx`, slide 1–9 | Khung nội dung slide, giới hạn phần trình bày, 10 phút thuyết trình và 5 phút demo |
| `airbnb-price-analysis-eda/README.md` | Định hướng Airbnb, biến mục tiêu realSum, đề xuất RF/XGBoost và hướng phát triển |
| `airbnb-price-analysis-eda/archive.zip` | Dữ liệu thực tế làm cơ sở cho phạm vi và quyết định xử lý |

Các tài liệu đã giải nén nằm trong `_review/02_Slides_Bai_giang/` và `_review/05_Cuoi_ky_Do_an/`. Số trang ở bảng trên là **trang PDF**, không phải số slide in trên trang: một số PDF chứa hai slide mỗi trang.

**Cập nhật sau khi RAR tải đủ:** `CodeMonHoc.rar` có kích thước 446.513.348 byte. Đã giải nén và kiểm tra tính toàn vẹn phần tài liệu/source/data ngoài `.venv`, `.idea`, cache: 7-Zip báo `Everything is Ok`, gồm 5 thư mục Buoi1–Buoi5 và 36 file. Nội dung đã đọc nằm tại `_review/CodeMonHoc_complete/`. Không còn giới hạn do file tải thiếu. Riêng RAR không có trọng số chấm hoặc ngày nộp; thông tin này đã được bổ sung từ transcript Buổi 10. Thư viện trong `.venv`, cache và metadata IDE không phải đề bài của nhóm.

Kế hoạch không sử dụng nguồn bên ngoài. Liên kết Kaggle trong README là thông tin nguồn được README khai báo, chưa được kiểm chứng bằng truy cập mạng.

### Đối chiếu thêm với source thực hành đã tải đủ

| Source trong CodeMonHoc.rar | Nội dung thực tế | Áp dụng vào kế hoạch |
|---|---|---|
| Buoi1 và Buoi2 | Kiểu dữ liệu, toán tử, if/for, hàm/lambda, pandas; bài kéo–búa–bao | Kiến thức lập trình nền, không thêm trò chơi vào đồ án Airbnb |
| Buoi3 và Buoi4 | Đọc giá xe, info/dtypes, xử lý khuyết, đổi kiểu, scaling và inverse transform | Củng cố T02–T04; làm theo dữ liệu thực tế, không sao chép biến của giá xe |
| Buoi5/25410199_DoanHuuHan.ipynb | replace/dropna, chia price thành bin bằng linspace/cut, get_dummies | Có căn cứ thực hành cho binning và one-hot; bin giá chỉ dùng mô tả |
| Buoi5/25410199_DoanHuuHan_P2.ipynb và …_Bai04.ipynb | Series/DataFrame plot; xử lý Canada.xlsx, line/area, tính tổng theo năm | Tham khảo cách xử lý/plot, không đưa chuỗi năm Canada vào Airbnb |
| Buoi5/25410199_DoanHuuHan_Bai07.ipynb | Thực tế chứa EDA giá xe: mode/median/mean, box/KDE, skew/kurt, corr, groupby và các hàm corr/anova/chon_so còn để `...` | Củng cố T05–T06. Tên file không phản ánh đầy đủ nội dung; ANOVA phải triển khai thật, không gọi hàm placeholder là kết quả |
| Buoi5/25410199_DoanHuuHan_Buoi06.ipynb | SLR/MLR, hệ số và predict, KDE actual/predicted, PolynomialFeatures, StandardScaler/Pipeline, MSE/R² và mốc mean | Củng cố M0–M3 và T08–T11; yêu cầu giải thích hệ số/mô hình và so sánh phân phối đã có trong source thực hành |
| Buoi5/25410199_DoanHuuHan_Bai7.ipynb | train_test_split(test_size=0.2, random_state=0), LinearRegression, R² train/test | Căn cứ trực tiếp để chọn split 80/20. Kế hoạch chốt seed 0 cho so sánh chính; seed không phải yêu cầu bắt buộc của GV |
| Buoi5/Buoi5.ipynb | 25 cell source trống | Không có nội dung phân tích để suy ra yêu cầu mới |

**Kết quả rà thêm:** không cần đổi đề tài hoặc bảng chia 18 task. Source bổ sung củng cố quy trình đã chọn. Ridge/CV/Grid Search vẫn lấy căn cứ từ bài giảng, không khẳng định đã có triển khai hoàn chỉnh trong notebook thực hành.

**Lưu ý khi tham khảo code cũ:** một số cell có biến chưa khai báo/thứ tự chưa phù hợp. Ví dụ notebook Buoi06 dùng `yhat_m2` trước cell gán nó; cell 37 khởi tạo `pf75` nhưng gọi `pf5`; Buoi2 định nghĩa lại `print`. Đây là code ghi chép/thử nghiệm, cần viết và chạy lại sạch cho Airbnb. Các bậc đa thức 10/15/16 trong notebook là thí nghiệm, không phải yêu cầu bắt buộc và không phải lý do chọn bậc cao cho đồ án. Chạy đúng thứ tự và kiểm tra train/CV/test theo T17 vẫn là điều kiện hoàn thành.

Dữ liệu thực hành bổ sung là giá điện thoại (10 × 8), giá xe thô (205 × 26), EDA_automobile và Model-Evaluation-and-Refinement (201 × 29), Model_Dataset (201 × 12), Canada.xlsx. Đây là dữ liệu minh họa khác miền; không gộp vào 51.707 quan sát Airbnb và không lấy chỉ số mô hình giá xe làm kết quả đồ án.


### Căn cứ bổ sung từ Buổi 07 và Buổi 10

Đã đọc bản transcript DOCX **Buổi 07, 27/08/2026** và **Buổi 10, 17/09/2026**, gồm phần giảng và hỏi đáp cuối buổi. Bản nhận dạng lời nói có lỗi tên thuật ngữ; các quy tắc dưới đây dựa vào đoạn có ngữ cảnh rõ hoặc được thầy nhắc lại. Chưa đối chiếu bản ghi âm/video hay thông báo hiện hành trên eLearning. Bản trích để tìm lại: `_review/buoi07_transcript.txt` và `_review/buoi10_transcript.txt`; số dòng là vị trí bản trích, không phải phút trong video.

| Nội dung được thầy nói | Áp dụng vào đồ án hai người | Căn cứ để tìm lại |
|---|---|---|
| Buổi 07: chấm kỹ thuật làm bài bản; thang đo mô hình thấp vẫn được nếu cách làm đúng | Không đặt ngưỡng R² để chạy theo; không xóa giá cao, chọn test hay đổi dữ liệu chỉ để nâng điểm. Giải thích hiệu quả thật, lỗi và giới hạn | Buổi 07, đoạn “Mình chấm là mình chấm cái kỹ thuật”, dòng 973–985 |
| Ưu tiên dữ liệu bảng phù hợp hồi quy, khoảng từ 10 cột, có biến số và phân loại; nguồn hợp pháp, có mô tả | Airbnb có 20 cột gốc, trong đó có cột index; 19 cột còn lại vẫn đủ độ phong phú. Giữ bộ hiện tại; metadata thiếu phải ghi rõ. Thầy có cho ngoại lệ dưới 10 cột nếu nội dung đủ tốt, không biến 10 thành luật tuyệt đối | Buổi 07, phần chọn dữ liệu và Q&A, dòng 860–996 và 1045–1076 |
| Pearson: với bài giá xe, chọn biến có r ngoài khoảng −0,3 đến 0,3; biến phân loại dùng ANOVA p<0,05. Biến số mang ý nghĩa phân loại có thể xét theo hai cách; không bác bỏ chỉ vì một phép xét yếu | Làm bảng bằng chứng chọn biến cho Airbnb. Không áp máy móc lọc toàn bộ theo Pearson: r toàn bộ hiện đều nhỏ hơn 0,3 nhưng trong city có biến mạnh hơn. Phân loại theo ý nghĩa, xét nhóm phù hợp; không tùy tiện biến mọi cột liên tục thành nhóm để kiếm p nhỏ | Buổi 07, phần tổng kết EDA/chọn biến và bài tập 6, dòng 600–800 |
| Đăng ký nhóm trên danh sách eLearning, gõ đúng MSSV/họ tên; chọn nhóm trống theo thứ tự, không sửa phần của nhóm khác. Có thể điền tên đề tài sau | A+B kiểm tra đăng ký và mã nhóm thật trước đặt tên file/bìa; chưa biết thông tin thì để chờ điền. Hai người phù hợp; không áp yêu cầu làm thêm thuật toán dành cho nhóm bốn người | Buổi 07, phần đăng ký nhóm, dòng 809–853 và 1071–1076; Buổi 10, Q&A nhóm bốn |
| Điểm quá trình 20%; đồ án chiếm 80%, gồm thực hành 30% và cuối kỳ 50%. Thầy review code cho điểm thực hành; báo cáo và sản phẩm là minh chứng quan trọng | Ưu tiên code dễ đọc/tái lập và báo cáo có bằng chứng ngang nhau. Hai người đều tham gia phân tích, viết và trình bày phần mình hiểu. Không suy ra công thức chấm từng task hay mức cộng cố định | Buổi 10, đầu buổi dòng 24–72 và Q&A review code dòng 1140–1142 |
| Bốn mốc: 24/09, 01/10, 08/10, **15/10/2026**. Chọn một mốc để hoàn thành; nộp lại tối đa một lần khi phiên bản sau tốt hơn rõ rệt | Với ngày lập kế hoạch 08/10, hướng tới hoàn thành và kiểm tra trước 15/10; giờ đóng cổng và thay đổi mới trên LMS chưa xác minh. Không nộp bản thiếu chỉ để lấy thưởng sớm; không nộp vét cả bốn mốc | Buổi 10, phần deadline, dòng 659–708 |
| Đoạn minh bạch phải nói cả việc dùng AI; dựa dự án mẫu phải khai báo và có phần tự làm thêm | Ghi ChatGPT/Gemini hoặc công cụ thực tế, đã hỗ trợ việc gì, phần nhóm tự thực hiện/kiểm chứng. Không khai AI là nguồn sinh số liệu; không viết “không dùng AI” khi đã dùng. Nếu tham khảo bài có sẵn, nói rõ bổ sung gì; kết quả không cải thiện thì báo thật | Buổi 10, phần Giới thiệu dòng 230–270 và Q&A dự án mẫu dòng 1030–1068 |
| Hai mục đầu giữ tên GIỚI THIỆU và MÔ TẢ BỘ DỮ LIỆU; đánh số phần, không dùng “Chương” | Giữ template. Tên đề tài diễn đạt đúng mức việc làm, có hành động/phương pháp/chủ đề; không gọi “nghiên cứu” nếu chỉ vận dụng. Giữ cột Ngành trên bìa, bỏ dòng thành viên dư và xóa mọi lời hướng dẫn của template | Buổi 10, hướng dẫn bìa/nội dung và Q&A dòng 1025–1030 |
| BT dùng Times New Roman 13, canh đều; giãn dòng 1,15. Phạm vi giá trị trong bảng cột có thể có hoặc không. Mỗi hình phải được dẫn vào, đánh số/chú thích và diễn giải | Vẫn cung cấp phạm vi quan sát vì hữu ích với data này, nhưng không gọi đó là yêu cầu cứng. Dùng hình có giá trị thông tin, không thêm logo thư viện để trang trí; quy trình mô tả việc đã làm đủ để người khác tái lập | Buổi 10, phần bảng dữ liệu/định dạng dòng 440–460; Q&A dòng 1070–1107 |
| Khuyến khích khoảng 5–10 trang nội dung chính; thầy cho tăng nếu thật sự cần, đến khoảng 20 trang là tối đa. Thời gian mục tiêu 15 phút; Q&A cho phép lỡ khoảng 20 phút | Nhóm giữ mục tiêu 8–10 trang và 10 phút nói +5 phút demo. Không tự tăng cho dài; không đánh dấu sai chỉ vì bản có nội dung thực chất 11–20 trang hoặc video hơi quá 15 phút. Không biến 20 phút thành mục tiêu mới | Buổi 10, dòng 625–638, 1108–1120 và 1210–1217 |
| Kết luận tóm tắt và đánh giá kết quả của mình, không viết hướng phát triển. Không cần liệt kê slide môn học vào TLTK; nguồn Internet có tên/link/ngày truy cập, dẫn [n] gần nội dung dùng | Bài giảng vẫn là căn cứ kỹ thuật trong kế hoạch này, nhưng không tự đưa vào TLTK cuối. Không đưa blog/wiki/mạng xã hội vào danh mục cuối; nếu được phép tham khảo ngoài thì lần về nguồn gốc. Phạm vi người dùng vẫn chỉ là source hiện có | Buổi 10, phần Kết luận và TLTK |
| Video online phải thấy thuyết trình và mặt động đủ thành viên; Teams tiện, công cụ khác cũng được. Mỗi người tự giới thiệu và có phần trình bày, không chỉ ngồi im | Slide nhóm có ảnh/tên/MSSV; webcam mặt động xuyên suốt video. Phụ lục nhiệm vụ khớp phần trình bày. Quy tắc một laptop thuộc trình bày trực tiếp, không bắt nhóm online phải ngồi chung máy | Buổi 10, phần video/online và Q&A dòng 1120–1125, 1180–1207 |
| Demo giải thích kết quả, không đọc từng dòng code; cố gắng gói toàn bộ trong một file code | Có thể tách notebook khi làm việc, nhưng A+B tích hợp một notebook cuối chạy từ đầu, đủ đọc dữ liệu → EDA → mô hình → đánh giá. Không biến việc này thành bài bắt buộc chỉ có một file trong suốt phát triển | Buổi 10, Q&A demo dòng 1130–1139 |
| Dashboard tùy khả năng, phải nộp code/file công cụ làm ra; Python là ngôn ngữ gốc cho hướng dashboard bằng thư viện Python, Power BI nộp file gốc | Đặt dashboard sau các phần lõi. Nếu dùng, lấy hình có diễn giải vào Word và nộp code hoặc PBIX tương ứng; không dựng ảnh ghép rồi nói đã xây dashboard. Không mở rộng thành web JS độc lập | Buổi 10, Q&A cuối buổi dòng 1148–1179 và 1220–1246 |

Khi lời giải thích mới làm rõ mẫu viết, áp dụng phần làm rõ ở trên và ghi nguồn; các điều khác vẫn theo template/slide. Không diễn giải phần transcript khó nghe thành mức phạt mới. Đây là tỷ trọng điểm và hướng dẫn, **chưa phải rubric chấm chi tiết**.

## 2. Những yêu cầu tác động trực tiếp đến điểm

### Báo cáo

- Dùng **đúng Template_IE313.docx**. Mẫu ghi sai template bị trừ **2 điểm**.
- Nội dung chính gồm Giới thiệu, các phần nội dung và Kết luận: **mục tiêu 5–10 trang; Buổi 10 cho phép dài hơn khi có nội dung thực chất, đến khoảng 20 trang là tối đa**, không tính bìa, tài liệu tham khảo và phụ lục.
- Giữ tiêu đề **GIỚI THIỆU**. Khoảng 10 dòng hoặc nửa trang, **2 đoạn văn**, không gạch đầu dòng. Đoạn 1 nêu đề tài, mục tiêu, cách làm và kết quả thực tế. Đoạn 2 cam kết minh bạch dữ liệu, đề tài, dự án tham khảo và **cách dùng AI thực tế** (Buổi 10).
- **MÔ TẢ BỘ DỮ LIỆU bắt buộc**, khoảng 1–2 trang; mô tả nguồn, dòng/cột, kiểu dữ liệu, phạm vi, ý nghĩa biến và khuyết. Nếu bảng dài, chuyển phần chi tiết xuống phụ lục.
- Dùng Heading 1, Heading 2 và style nội dung BT/G1/G2 theo mẫu; BT Times New Roman 13, canh đều và giãn dòng 1,15 theo Buổi 10. Đánh số phần, không ghi “Chương”; giữ hai tiêu đề đầu. Xóa lời hướng dẫn, ví dụ và placeholder khỏi bản nộp. Không thêm lời cảm ơn, tóm tắt hoặc mục lục vì mẫu rút gọn không có các phần này.
- Không đưa code vào nội dung chính. Có thể đưa xuống phụ lục nếu cần.
- Kết luận khoảng 10 dòng hoặc nửa trang; nêu mục tiêu, cách làm, kết quả nổi bật và tự đánh giá kết quả thật. **Không viết hướng phát triển** trong Kết luận (Buổi 10).
- Có tài liệu tham khảo đúng style mẫu; mẫu ghi sai style tài liệu tham khảo bị trừ **1 điểm**. Có phụ lục phân công **từng nhiệm vụ chi tiết** của mỗi thành viên.
- Mẫu ghi vi phạm các điều KHÔNG nên làm bị trừ **0,5 điểm/lần**, copy y nguyên Internet nhận **0 điểm**. Đây là các mức ghi trong mẫu, không phải rubric đầy đủ của toàn bộ đồ án.

### Slide và demo

- Slides.pptx **không bắt buộc dùng nguyên thiết kế**, cho phép tùy chỉnh và yêu cầu thiết kế hiệu ứng đẹp. Dùng hiệu ứng đơn giản để không chiếm thời gian trình bày.
- Giới thiệu: **1 slide**, viết ý ngắn; có cam kết minh bạch ngắn như báo cáo.
- Mô tả dữ liệu: **không quá 2 slide**.
- Nội dung phân tích: **không quá 10 slide**.
- Kết quả: **1–2 slide**, có hạn chế nếu chưa làm được.
- **Thuyết trình 10 phút, demo 5 phút**, sau đó Q&A. Đây là thời lượng mục tiêu; Buổi 10 Q&A cho phép hơi quá, khoảng 20 phút, nhưng vẫn khuyến khích 15 phút. Với hệ online, phần giới thiệu nhóm và video là bắt buộc: đủ mặt động thành viên xuyên suốt, mỗi người tự giới thiệu và tham gia trình bày. Teams được khuyến nghị; công cụ khác đáp ứng yêu cầu vẫn được.

### Nộp bài

- Báo cáo **Word và PDF**, slide, **code và data**, demo kết quả. Không in báo cáo.
- Tên sản phẩm bắt đầu bằng mã nhóm, ví dụ `NhomXX_Bao_cao.docx`. Thay XX bằng nhóm thực tế, không dùng nhóm mẫu trong tài liệu.
- Nộp **từng file, không nén các sản phẩm**, không dùng một link Drive để nộp toàn bộ.
- Mẫu có hai ngưỡng khác nhau cho dữ liệu đưa lên Drive: đoạn trước **60 MB**, đoạn sau **50 MB**. Airbnb hiện chỉ khoảng **10,76 MB CSV chưa nén**, nên nộp trực tiếp và không cần giải quyết mâu thuẫn này cho bộ dữ liệu hiện tại.
- Khi trình bày trực tiếp: đúng giờ, **1 laptop**, mở sẵn Word, slide và code, code chế độ sáng, chạy sẵn kết quả. Buổi 10 nói quy tắc một laptop không áp cho lớp online. Demo giải thích kết quả, không đọc từng dòng code; ưu tiên một notebook cuối tái lập toàn bộ.

## 3. Dữ liệu đã kiểm tra và các điểm cần sửa trong định hướng

### Quy mô thực tế

| Thành phố | Weekdays | Weekends | Tổng |
|---|---:|---:|---:|
| Amsterdam | 1.103 | 977 | 2.080 |
| Athens | 2.653 | 2.627 | 5.280 |
| Barcelona | 1.555 | 1.278 | 2.833 |
| Berlin | 1.284 | 1.200 | 2.484 |
| Budapest | 2.074 | 1.948 | 4.022 |
| Lisbon | 2.857 | 2.906 | 5.763 |
| London | 4.614 | 5.379 | 9.993 |
| Paris | 3.130 | 3.558 | 6.688 |
| Rome | 4.492 | 4.535 | 9.027 |
| Vienna | 1.738 | 1.799 | 3.537 |
| **Tổng** | **25.500** | **26.207** | **51.707** |

- 20 CSV có cùng **20 cột gốc**, gồm một cột chỉ số xuất file `Unnamed: 0`. Thêm `city`, `day_type` từ tên file để gộp và so sánh; không mô tả hai cột này là cột có sẵn trong CSV.
- Không phát hiện ô thiếu theo cách đọc CSV thông thường. Không có dòng trùng hoàn toàn trong từng city/day_type khi bỏ cột chỉ số. Vẫn cần rà ký hiệu thiếu và miền giá trị trong notebook chính thức.
- Cột chỉ số bắt đầu lại từ 0 ở mỗi file: **không phải ID listing dùng chung**. Dùng `source_file` + `source_row` để truy vết, không đưa các cột này vào predictor.
- Loại phòng: Entire home/apt **32.648**, Private room **18.693**, Shared room **366**. Shared room ít, phải báo kích thước nhóm khi so sánh.
- `room_shared` và `room_private` hoàn toàn suy ra được từ `room_type` trong dữ liệu hiện có. Với hồi quy, dùng một cách biểu diễn để tránh đưa thông tin lặp.
- README bỏ sót `attr_index_norm`, `rest_index_norm`; phải có trong từ điển dữ liệu. Có thể chọn một biểu diễn của mỗi cặp raw/norm sau khi xem tương quan và giải thích lý do.
- README ghi mỗi file từ 1.100 dòng; thực tế file Amsterdam weekends có **977 dòng**. Khi viết báo cáo dùng số kiểm kê thực tế.

### Các kết quả sơ bộ phục vụ thiết kế phân tích

- `realSum`: min **34,78**, median **211,34**, mean **279,88**, max **18.545,45**, std **327,95**. Giá có đuôi phải lớn: skewness khoảng **21,42**, kurtosis theo pandas khoảng **831,36**.
- Quy tắc IQR toàn bộ dữ liệu đánh dấu **3.662 dòng**; cận trên khoảng **576,11**. Đây là dấu hiệu thống kê, **không chứng minh dữ liệu sai**. Đặc biệt median Amsterdam đã khoảng **460,24**, nên một ngưỡng chung có thể loại nhiều quan sát đắt hợp lệ ở thành phố này.
- Pearson gộp toàn bộ cho các biến số với giá hiện đều có |r| < 0,3 nếu loại target và chỉ số. Vì vậy **không hứa trước dist, metro hay đánh giá là biến quan trọng**, và không áp dụng ngưỡng ví dụ ở Bài 5 một cách máy móc đến mức loại hết predictor. Cần xem theo thành phố, loại phòng và quan hệ phi tuyến.
- Có **21.582 quan sát lặp tọa độ city/lat/lng sau quan sát đầu tiên**. Trùng tọa độ không xác nhận cùng listing; không xóa tất cả và không dùng tọa độ để ghép cặp giá ngày thường/cuối tuần như đã xác minh danh tính.

### Ý nghĩa biến và giới hạn kết luận

| Nhóm | Biến | Cách sử dụng trong đồ án |
|---|---|---|
| Mục tiêu | `realSum` | Giá trong bộ dữ liệu. README khai báo EUR và tổng kỳ lưu trú 2 người/2 đêm; ghi rõ đây là mô tả theo README, cần minh chứng metadata gốc trước khi khẳng định chắc chắn hoặc quy đổi giá/đêm |
| Loại phòng | `room_type`, `room_shared`, `room_private` | Mô tả loại phòng; mô hình dùng room_type đã mã hóa, loại hai cờ lặp |
| Quy mô | `person_capacity`, `bedrooms` | Miền quan sát lần lượt 2–6 và 0–10; 0 phòng ngủ không tự động là khuyết |
| Chủ nhà | `host_is_superhost` | Biến boolean theo tên cột/README |
| Cờ khác | `multi`, `biz` | Quan sát 0/1. README có mô tả nhưng CSV không định nghĩa ngưỡng phân loại hoặc khái niệm chính xác. Không tự gán biz thành khách đi công tác hay quy mô kinh doanh đã xác minh |
| Đánh giá | `cleanliness_rating`, `guest_satisfaction_overall` | Miền quan sát 2–10 và 20–100; phân biệt miền quan sát với thang đo chính thức |
| Khoảng cách | `dist`, `metro_dist` | Khoảng cách trung tâm/metro theo README, đơn vị km theo README. Không đổi sang thời gian đi lại |
| Chỉ số khu vực | `attr_index`, `attr_index_norm`, `rest_index`, `rest_index_norm` | Phân tích dưới tên chỉ số có sẵn. Không suy ra mật độ, chất lượng nhà hàng hoặc công thức chuẩn hóa nếu chưa có định nghĩa |
| Vị trí | `lat`, `lng` | Trực quan theo từng thành phố; không diễn giải hệ số tọa độ gộp là tác động địa lý phổ quát |
| Nhãn từ file | `city`, `day_type` | Dùng để phân nhóm và mã hóa. Weekdays/weekends là hai nhóm, **không phải chuỗi thời gian** |

Không có trong CSV: ngày thu thập, listing ID, booking, doanh thu, công suất phòng, lịch sử giao dịch, nhãn gian lận hoặc nhãn giá đúng. Đồ án không kết luận về xu hướng theo năm, tối ưu doanh thu, nhu cầu đặt phòng hay “định giá ảo”. Phần dư lớn chỉ thể hiện sai lệch giữa quan sát và mô hình đang dùng.

## 4. Phạm vi và câu hỏi phân tích

Mục tiêu là vận dụng quy trình môn học để mô tả giá, xem các mối liên hệ với giá, xây dựng mô hình hồi quy và đánh giá khả năng dự đoán trên dữ liệu giữ lại. Không mở rộng thành hệ thống đặt phòng, recommendation, API, dữ liệu Việt Nam hoặc tích hợp tốt nghiệp trong kỳ này.

| Câu hỏi | Phương pháp theo môn học | Bằng chứng cần có |
|---|---|---|
| Q1. Giá phân bố thế nào, khác nhau ra sao giữa thành phố và loại phòng? | Thống kê mô tả, histogram, boxplot, groupby | Bảng count/mean/median/std/IQR; biểu đồ và nhận xét về lệch/ngoại lệ |
| Q2. Hai nhóm weekdays/weekends khác nhau thế nào trong mỗi thành phố và loại phòng? | Groupby/pivot, grouped bar và boxplot | Bảng median/mean và số mẫu theo city/day_type/room_type; giải thích khác cơ cấu mẫu |
| Q3. Các biến số có liên hệ tuyến tính với giá không? | Scatter/regression plot, Pearson r và p-value | Heatmap, bảng r/p/n cho biến được chọn; so sánh gộp và trong thành phố |
| Q4. Giá trung bình giữa các loại phòng có khác biệt có ý nghĩa thống kê không? | Boxplot, ANOVA theo Bài 5 | F, p, kích thước từng nhóm và giới hạn về giả định kiểm định |
| Q5. Hồi quy đơn biến, đa biến, đa thức và Ridge dự đoán tốt đến đâu? | Pipeline, train/test, CV, so sánh mô hình | MSE, RMSE, MAE, R², sai số train/CV/test và biểu đồ phần dư |

Q2 chỉ so sánh **nhóm mẫu**, không nói “cùng một phòng tăng giá cuối tuần”. Q3/Q4 diễn giải mối liên hệ hoặc khác biệt thống kê, không tuyên bố nguyên nhân. Với ANOVA, nêu giả định độc lập, phân phối phần dư và phương sai; nếu dữ liệu không đáp ứng thì ghi giới hạn của F/p, không dùng p nhỏ để kết luận chắc chắn. Không tạo kiểm định hoặc kết luận chỉ để lấp chỗ báo cáo.

## 5. Kế hoạch triển khai kỹ thuật

### Giai đoạn 1 — Hiểu và chuẩn bị dữ liệu

1. Đọc 20 CSV tại máy, kiểm tra đúng tên file, schema, số dòng/cột, kiểu, khuyết và miền. Giữ nguyên raw.
2. Gộp; thêm city/day_type/source_file/source_row. Tạo bảng từ điển dữ liệu có cột “đã có căn cứ/chưa rõ”. Lưu dữ liệu gộp chưa scaling để thống kê vẫn có ý nghĩa.
3. Rà tính nhất quán các cờ room_type; nhận diện thuộc tính lặp. Xuất bảng trước/sau nếu có thao tác thay đổi hoặc loại mẫu.
4. Không tạo missing giả cho đồ án. Nếu không thiếu, báo số khuyết bằng 0 và giải thích không cần điền. Minh họa phương pháp điền khuyết ở bài thực hành không phải bằng chứng đã áp dụng vào Airbnb.
5. Gắn cờ ngoại lệ IQR cả toàn bộ và trong thành phố. Phân tích đầy đủ dữ liệu trước; không xóa giá cao chỉ vì muốn tăng R².
6. Minh họa binning một biến khoảng cách hoặc giá theo Bài 2 nếu hữu ích cho biểu đồ; công bố cách đặt ngưỡng. Bin của target dùng mô tả, **không đưa vào predictor để dự đoán target**.

Đầu ra: notebook 01; inventory; dictionary; dữ liệu gộp; nhật ký xử lý và bảng ngoại lệ.

### Giai đoạn 2 — EDA và trực quan

1. Tính mean/median/mode, range, quartiles/IQR, variance/std/CV, skewness/kurtosis cho biến chính. Với mode của giá liên tục, ghi giới hạn diễn giải.
2. Trả lời Q1–Q4 bằng bảng và biểu đồ. Mỗi biểu đồ có câu hỏi, tập mẫu, nhãn/đơn vị, n và 2–4 câu nhận xét có số liệu.
3. Pearson/ANOVA dùng để giải thích và tạo tập ứng viên. Danh sách predictor dùng mô hình phải được chốt từ train, không dựa trên kết quả target trong test.
4. Chọn khoảng **8 hình EDA hữu ích** để làm việc; báo cáo chỉ giữ các hình trả lời câu hỏi rõ nhất. Không nhồi đủ mọi loại biểu đồ trong bài giảng.

Danh sách hình đề xuất: histogram giá; boxplot giá theo city; bar số mẫu theo city; grouped bar median theo day_type/city; boxplot giá theo room_type; scatter khoảng cách–giá theo một vài city; correlation heatmap; heatmap pivot giá city/room_type kèm count. Dashboard nếu có chỉ gom các hình này để demo, không thêm chức năng nghiệp vụ.

Không dùng line/area để thể hiện tiến triển theo thời gian vì dữ liệu không có ngày. Không dùng word cloud vì không có văn bản phù hợp. Khi rút trục hoặc dùng thang log cho hình, phải ghi rõ; không che đuôi phân phối.

Đầu ra: notebook 02; bảng thống kê, Pearson và ANOVA; ảnh biểu đồ; danh sách phát hiện có căn cứ.

### Bổ sung chọn biến đúng tinh thần Buổi 07

T06 phải tạo bảng `feature_evidence`: tên biến, ý nghĩa/loại, n, r và p nếu áp dụng, F/p ANOVA nếu áp dụng, phạm vi toàn bộ/theo city, quyết định và lý do. Thầy dùng Pearson ngoài [−0,3; 0,3] cho bài giá xe, ANOVA p<0,05 cho biến phân loại và nhấn mạnh không loại ngay chỉ vì một cách xét không cho thấy liên hệ. Đây là hướng dẫn vận dụng, không phải yêu cầu mọi biến Airbnb phải vượt cùng ngưỡng mới được dùng.

Với Airbnb, r toàn bộ của các biến số đang nhỏ hơn 0,3; `person_capacity` khoảng 0,203 toàn bộ nhưng khoảng 0,528 tại Amsterdam và 0,573 tại Lisbon. Vì vậy giữ phân tích theo city và phân loại thật; không kết luận “không có yếu tố liên quan” từ r gộp. Xét `room_type` và `city` bằng thống kê nhóm/ANOVA có giả định và số mẫu; các cờ boolean là phân loại, không coi số mã là thang liên tục. Bảng lựa chọn có học từ target để dùng mô hình phải được tính trong train/fold; EDA toàn bộ chỉ mô tả. Các giá trị p/F chưa tính thì để chưa chạy, không tự điền. Không dùng p nhỏ làm bằng chứng nhân quả hoặc mức tác động lớn.

### Giai đoạn 3 — Mô hình hóa theo Bài 6–7

Chọn **80% train / 20% test** vì Bài 7 có bài áp dụng test_size=0.2; dùng cùng split và seed **random_state=0** cho tất cả mô hình (trùng ví dụ thực hành trong Buoi5/Bai7). Đây là lựa chọn của nhóm từ ví dụ trong slide, không phải tỷ lệ bắt buộc của GV. Dùng **CV 5 folds trong train** để chọn mô hình/bậc/alpha. Scaler, encoder và mọi bước học từ dữ liệu đều fit trong train từng fold rồi transform validation/test.

| Mã | Mô hình | Nội dung chứng minh |
|---|---|---|
| M0 | Dự đoán bằng mean của train | Mốc so sánh gắn với đường trung bình giải thích R² ở Bài 6 |
| M1 | Linear Regression đơn biến | Một biến số có căn cứ từ train; phương trình, slope/intercept và regplot |
| M2 | Linear Regression đa biến | Predictor số và city/day_type/room_type mã hóa; so sánh với M1 |
| M3 | Polynomial Regression | Thử bậc 2 và 3 trên ít biến số đã chọn; Pipeline chuẩn hóa/PolynomialFeatures/hồi quy |
| M4 | Ridge | Điều chuẩn để kiểm tra overfitting/thuộc tính liên hệ nhau; chọn alpha bằng CV/Grid Search |

Dãy alpha đề xuất `[0.001, 0.01, 0.1, 1, 10, 100, 1000]`, có trong ví dụ Bài 7. Không triển khai polynomial bậc cao trên tất cả dummy/tọa độ chỉ để có mô hình phức tạp. Giữ tập biến đủ nhỏ để giải thích và chạy được demo.

Chọn mô hình bằng **CV MSE thấp**, xem đồng thời CV R² và chênh lệch train/validation; sau khi chốt mới đánh giá test. RMSE = căn MSE, MAE bổ sung khả năng đọc sai số trên thang giá. Không hứa mô hình nào thắng hoặc đặt ngưỡng R² tùy ý.

Do nhiều tọa độ lặp, ghi giới hạn split ngẫu nhiên: các chỗ ở gần nhau/cùng tọa độ có thể xuất hiện hai phía. Nếu còn thời gian, làm một kiểm tra bổ sung chia theo nhóm city/lat/lng để đánh giá độ nhạy; ghi rõ đây là thiết kế kiểm tra bổ sung của nhóm, tọa độ không phải listing ID. Không diễn giải test ngẫu nhiên là bằng chứng dự đoán tốt ở thành phố hoàn toàn mới.

Nếu thử xử lý ngoại lệ trong train, báo riêng thí nghiệm, ngưỡng và số mẫu bị tác động. Giữ **cùng test đầy đủ** cho so sánh chính; không cắt test theo giá rồi dùng điểm đẹp hơn như kết quả tương đương.

**Mở rộng có điều kiện:** Template cho phép nhiều mô hình phù hợp. Random Forest hoặc XGBoost trong README có thể thêm **một** mô hình sau khi M0–M4 và hồ sơ nộp đã hoàn chỉnh. Chỉ thêm nếu hai thành viên giải thích được cách train/evaluate và có thời gian. Không mặc định XGBoost là mô hình tối ưu. Không coi mô hình ngoài slide là yêu cầu phải làm để được điểm cao.

Đầu ra: notebook 03; cấu hình split/CV; bảng so sánh và cấu hình mô hình; dự đoán test cùng mã truy vết; mô hình lưu nếu cần cho demo.

### Giai đoạn 4 — Đánh giá và diễn giải

1. Bảng chính có MSE/RMSE/MAE/R² trên test, kèm train và CV ở bảng đối chiếu/phụ lục.
2. Regression plot của đơn biến; scatter actual–predicted; residual theo fitted values; đường phân phối actual/predicted. Tính phần dư đa biến bằng `actual - predicted`, vẽ trực tiếp và nêu quy ước dấu.
3. Sai số theo city/room_type/day_type có count. Chỉ chọn vài phân nhóm đáng chú ý vào báo cáo chính.
4. Kiểm tra dự đoán âm, ngoại suy và vài mẫu sai nhiều. Không sửa dự đoán âm hoặc đổi thang đo âm thầm.
5. Kết luận mô hình tốt hơn mốc trung bình đến đâu, chỗ còn sai và các nhóm ít mẫu. Phần dư lớn gọi là “mẫu dự đoán sai nhiều/cần xem thêm”, không gán gian lận hoặc giá trị thực của căn hộ.

Đầu ra: notebook 04; biểu đồ đánh giá; bảng case study có mã truy vết; phần kết quả và hạn chế.

## 6. Phân công chi tiết cho hai người

Quy ước: người phụ trách làm code, giải thích kết quả và viết phần tương ứng. Người kiểm tra chạy lại và đọc chéo. Cả hai đều làm phân tích và chuẩn bị nói, không giao một người toàn bộ code và người kia chỉ chỉnh slide.

| ID | Nhiệm vụ | Phụ trách | Kiểm tra | Phụ thuộc | Điều kiện hoàn thành | Trạng thái 13/10 | Minh chứng | Việc còn lại |
|---|---|---|---|---|---|---|---|---|
| T01 | Đọc yêu cầu cuối kỳ, chốt tên đề tài và khai báo nguồn | A+B | A+B | Không | Checklist Buổi 07/10, nhóm/hệ học/giờ LMS; xác định dự án tham khảo và hỗ trợ AI | Đang làm | Notebook 01 mục minh bạch; Skill/KE_HOACH_DO_AN_IE313.md | Đã bổ sung nguồn/AI; cần xác minh nguồn Inside Airbnb, công cụ thực tế, tên/MSSV/mã nhóm và giờ LMS. |
| T02 | Nạp 20 CSV, kiểm tra schema/số mẫu/khuyết | A | B | T01 | Notebook 01 chạy từ đầu, tổng 51.707 trước xử lý; inventory từng file | Hoàn thành | Notebook 01; inventory.csv; audit_report.csv | Đã chạy sạch 18 cell bản A sửa; audit giá âm báo FAILED; CSV gộp 51707x24 khớp. Nghiệm thu snapshot hiện tại. |
| T03 | Dictionary, metadata chưa rõ, mã truy vết, thuộc tính lặp | A | B | T02 | Bảng đủ 20 cột gốc và các cột thêm; không dùng chỉ số như listing ID | Cần sửa | data_dictionary.csv; Notebook 01 cell 22/25 | Đủ 24 biến; còn WGS84, studio, metro làm tròn và metadata suy diễn. Không chặn B/A dùng CSV đã kiểm. |
| T04 | Thống kê mô tả, IQR, so sánh trước/sau nếu xử lý | A | B | T03 | Bảng ngoại lệ toàn bộ/theo city; lý do giữ/loại có số mẫu | Cần sửa | descriptive_statistics.csv; audit_iqr_by_city.csv | Số liệu đúng, log wording đã sửa; còn assert skew<1, nhãn >=5/>5, >=600/>600, 17 numeric gồm ID/cờ. |
| T05 | EDA city/day_type/room_type, groupby/pivot | B | A | T02–T03 | Trả lời Q1–Q2 bằng bảng count/mean/median và hình | Hoàn thành | Notebook 02; eda_group_summary.csv; 7 hình b_* | Đã chạy sạch; có n/mean/median/IQR, so sánh nhóm ngày và cơ cấu mẫu; không kết luận cùng listing. |
| T06 | Pearson, scatter, ANOVA, tập ứng viên | B | A | T04–T05 | r/p/n, F/p, giả định/giới hạn, không kết luận nhân quả | Hoàn thành | feature_evidence.csv; pearson/anova_price_evidence.csv | Pearson/ANOVA full/train riêng, r/p/F/n và giới hạn; không lọc predictor tự động theo target. |
| T07 | Chốt predictor, split/CV và pipeline chung | A+B | A+B | T04–T06 | Cấu hình chung, xử lý đúng train/test, đóng băng test | Hoàn thành | experiment_config.json; split_manifest.csv; experiment.py; verify_a_t07.py; A_T07_ACCEPTANCE.md | A đã kiểm toán 5 cổng kỹ thuật (100% PASSED) và nghiệm thu chính thức; sẵn sàng làm T08. |
| T08 | M0/M1/M2, phương trình và hệ số | A | B | T07 | CV/train metrics; giải thích chọn biến, predictor không chứa target-derived bins | Hoàn thành | Notebook 03a; a_models_cv_summary.csv; fig_04; fig_05; A_T08_ACCEPTANCE.md | A đã hoàn thành 5-fold CV cho M0, M1, M2; trích xuất phương trình, hệ số; kiểm toán 5 cổng đạt 100% PASSED. |
| T09 | M3/M4, chọn bậc/alpha bằng CV | B | A | T07 | Pipeline/Grid Search, cùng fold/split, bảng chênh lệch train/CV | Hoàn thành | Notebook 03b; b_models_cv_summary/folds.csv | 9 cấu hình x5 folds; M3 bậc 3, M4 alpha 0.1 theo CV; lưu train-only, chưa đánh giá test. |
| T10 | Chốt mô hình và đánh giá test chung | A+B | A+B | T08–T09 | Bảng MSE/RMSE/MAE/R², không dùng test để tune | Hoàn thành | Notebook 04; model_comparison_cv_vs_test.csv; test_predictions.csv; fig_06; fig_07; A_B_T10_ACCEPTANCE.md | Chốt M3 chiến thắng trên CV; mở khóa đánh giá 10.342 mẫu test; kiểm toán 5 cổng đạt 100% PASSED. |
| T11 | Biểu đồ phần dư, lỗi theo nhóm và case study | B | A | T10 | Notebook 04 và các hình thực tế, không gọi giá sai là gian lận | Sẵn sàng bắt đầu | test_predictions.csv đã sẵn sàng (51.710 dòng) | B sẵn sàng vẽ biểu đồ phần dư đa biến (residual plot), lỗi theo nhóm city/room và case study. |
| T12 | Viết Giới thiệu, Dữ liệu, Tiền xử lý trong template | A | B | T03–T04, T10 | Nguồn rõ, số liệu khớp notebook, giữ heading/style mẫu | Chưa bắt đầu | Chờ report Word trong template | A có thể viết dữ liệu/phương pháp ngay; chưa có bản report phần A trong repo. |
| T13 | Viết EDA, Mô hình, Kết quả và Kết luận | B | A | T06, T08–T11 | Hình/bảng có diễn giải và hạn chế, kết quả không bịa | Đang làm | eda_findings.md; b_model_findings.md | Đã có nội dung EDA/CV thật; chờ T08/T10 cho so sánh, test và kết luận cuối. |
| T14 | TLTK, cam kết minh bạch và phụ lục phân công | A | B | T12–T13 | Đúng style; ghi dự án mẫu/source tham khảo và đóng góp thực tế | Chưa bắt đầu | Chờ TLTK/phụ lục report cuối | A chốt nguồn/AI thật, style và nhiệm vụ từng người; không ghi đóng góp giả. |
| T15 | Slide và kịch bản 10 phút | B | A | T12–T14 | Đúng giới hạn từng phần, ít chữ, số liệu đồng nhất | Đang làm | SLIDE_OUTLINE_B.md | Đã có dàn ý 13 slide/kịch bản; chưa có PPTX cuối, cần T08/T10 và thông tin nhóm. |
| T16 | Chuẩn bị demo 5 phút, hướng dẫn chạy | A | B | T10–T11 | Demo trên máy trình bày, mở sẵn output, không lệ thuộc tải mạng | Chưa bắt đầu | Chờ notebook cuối và demo | A tích hợp và chạy sẵn; B có phần trình bày chuyên môn; chưa có demo cuối. |
| T17 | Chạy lại từ đầu, kiểm báo cáo Word/PDF và từng file nộp | A+B | A+B | T14–T16 | Bộ nộp đúng tên, đủ data/code, không nén, mục tiêu 5–10 trang; notebook cuối tái lập được | Chưa bắt đầu | b_verification.json chỉ kiểm gói B | 24 kiểm tra B đạt không thay nghiệm thu bộ nộp Word/PDF/slide/code/data. |
| T18 | Diễn tập thuyết trình và hỏi chéo | A+B | A+B | T17 | Đúng 10+5 phút, cả hai trả lời được toàn bộ quy trình | Chưa bắt đầu | Chờ bộ nộp T17 | Chưa có bằng chứng diễn tập/video đủ cả hai người; mục tiêu 10+5 phút. |

Phụ lục phân công cuối cùng ghi việc **đã thực hiện**, có thể dùng ID này làm căn cứ. Không ghi đều 50% nếu thực tế khác; nếu muốn tỷ lệ đóng góp thì căn cứ log và sản phẩm.

### Cách phối hợp tránh vướng nhau

- A quản lý notebook 01, phần M0–M2 trong notebook 03, data_loader/preprocess. B quản lý notebook 02/04, phần M3–M4 và visualization/evaluate.
- Vì notebook 03 dùng chung, hai người làm nhánh/thí nghiệm riêng rồi một người tích hợp sau T07; không chỉnh đồng thời cùng cell.
- Bắt đầu thống nhất schema, tên biến, thư mục output và cách gọi hàm. EDA đọc dữ liệu gộp chưa scaling; mô hình tự fit preprocessing trong pipeline.
- Mỗi mốc bàn giao gồm code đã chạy, output và đoạn giải thích. Bản report không chờ hết code mới bắt đầu: A/B điền phần đã có bằng chứng, để trống kết quả chưa chạy.
- Người kiểm tra chạy lại sản phẩm đối phương, kiểm ngẫu nhiên vài con số từ dữ liệu gốc và hỏi tại sao chọn cách làm.

## 7. Lịch đề xuất từ 08/10 đến mốc cuối 15/10/2026

Buổi 10 nêu bốn mốc 24/09, 01/10, 08/10 và 15/10/2026. Tại ngày cập nhật, dự án chưa có notebook triển khai, nên không coi 08/10 là mốc nộp khả thi chỉ vì được thưởng sớm. Lịch nhóm dưới đây nhắm mốc **15/10**, hoàn tất bản kiểm tra ngày 14/10; kiểm tra giờ đóng cổng LMS và lịch sử đã nộp trước đó. Không mặc định được gia hạn. Giữ nguyên 18 task, gom mốc và cắt phần tùy chọn để phù hợp thời gian.

| Ngày | A | B | Bàn giao và điều kiện qua mốc |
|---|---|---|---|
| 08/10 | T01–T04: nguồn, dictionary, loader, audit | T01, T05: thống kê/phân bố, rà yêu cầu mới | Chốt phạm vi, tên đề tài dự kiến, đăng ký nhóm; data gộp khớp 51.707 dòng; chưa bịa định nghĩa thiếu |
| 09/10 | Kiểm tra T05–T06, viết nháp mô tả/phương pháp | T05–T06: nhóm, Pearson/ANOVA và bảng bằng chứng chọn biến | Khóa câu hỏi, schema và giao thức T07. Không loại hết biến chỉ vì r toàn bộ thấp |
| 10/10 | T08: M0–M2 | T09: polynomial thấp/Ridge | Các mô hình lõi chạy được, CV trong train; không chọn theo test |
| 11/10 | T10, tích hợp notebook cuối | T10–T11: metrics/phần dư/lỗi nhóm | Bảng kết quả cùng test/thang giá, mô hình chốt; báo thật kể cả R² thấp |
| 12/10 | T12, T14: report dữ liệu/phương pháp trong template | T13, T15: kết quả/kết luận/slide | Report 8–10 trang, minh bạch AI/nguồn, dẫn hình/TLTK và phụ lục việc thật |
| 13/10 | T16: demo notebook và tái lập | T15–T16: kiểm số liệu, kịch bản phần mình nói | Word/PDF/slide khớp code; demo tập trung kết quả; đủ webcam nếu online |
| 14/10 | T17–T18: chạy sạch và kiểm từng file | T17–T18: đọc chéo, diễn tập/ghi video | Chốt bộ nộp; mở Word/PDF trên cả hai máy; kiểm link ngoại lệ tải không cần đăng nhập |
| 15/10 | A+B nộp theo mốc/giờ LMS đã kiểm tra | A+B kiểm tra file và trạng thái nộp | Nộp riêng từng file; lưu bằng chứng nộp. Chỉ một lần nộp lại khi cải thiện rõ và còn được phép |

Lịch này là đề xuất, không khẳng định đã có sản phẩm hay đã nộp. Ưu tiên EDA, hồi quy đúng, báo cáo và tái lập; không dành thời gian cho RF/XGBoost, dashboard hoặc web khi phần lõi chưa xong. Nếu quá tải, giảm số cấu hình thử và hình phụ, ghi rõ phạm vi; không cắt minh bạch, mô tả dữ liệu, đánh giá đúng, video bắt buộc hoặc kiểm template.

## 8. Cấu trúc sản phẩm và báo cáo

### Cấu trúc dự kiến trong dự án

```text
airbnb-price-analysis-eda/
  data/raw/                    20 CSV nguyên bản
  data/processed/              dữ liệu gộp chưa scale; không gọi là train đã chuẩn hóa
  notebooks/
    01_data_preprocessing.ipynb
    02_exploratory_data_analysis.ipynb
    03_regression_modeling.ipynb
    04_residual_analysis.ipynb
  src/                         hàm dùng lại, chỉ tách khi có ích
  outputs/tables/              inventory, thống kê, CV, test metrics
  outputs/figures/             hình dùng cho report/slide
  models/                      model cho demo nếu cần
  submission/
    NhomXX_Do_an.ipynb          một notebook cuối tích hợp để nộp/demo
  reports/                     Word, PDF và slide cuối cùng
  README.md                    phạm vi thật và cách chạy
  requirements.txt             phiên bản đã kiểm tra trên máy demo
```

Các notebook 01–04 phục vụ phát triển; theo khuyến nghị Buổi 10, A+B tích hợp notebook cuối trong submission, chạy độc lập với data nộp kèm, không phụ thuộc notebook khác hoặc đường dẫn tuyệt đối trên máy A. src chỉ tách khi có ích; nếu notebook cuối import module thì phải nộp kèm hoặc tích hợp hàm cần thiết vào notebook cuối. **Không nén cả thư mục để nộp.**

Đây là cấu trúc **sẽ làm**. Hiện dự án Airbnb mới có README, requirements và archive dữ liệu; các notebook/src được README liệt kê chưa tồn tại. Không nói dự án đã huấn luyện hoặc đã có pipeline.

### Dàn ý nội dung chính khoảng 8–9 trang

| Phần | Ngân sách trang đề xuất | Nội dung |
|---|---:|---|
| GIỚI THIỆU | 0,5 | Hai đoạn, mục tiêu/cách làm/kết quả và minh bạch |
| MÔ TẢ BỘ DỮ LIỆU | 1–1,5 | Nguồn, 51.707 dòng, cấu trúc, biến cốt lõi và giới hạn metadata |
| PHƯƠNG PHÁP PHÂN TÍCH | 1 | Quy trình thực sự đã làm, tiền xử lý, split/CV và đánh giá |
| PHÂN TÍCH THĂM DÒ | 2 | Những phát hiện trả lời Q1–Q4, bảng/hình quan trọng |
| PHÁT TRIỂN VÀ ĐÁNH GIÁ MÔ HÌNH | 2–2,5 | M0–M4, so sánh, phần dư và lỗi theo nhóm |
| KẾT QUẢ VÀ THẢO LUẬN | 0,5–1 | Kết quả nổi bật và giới hạn, tránh lặp bảng mô hình |
| KẾT LUẬN | 0,5 | Mục tiêu, cách làm, kết quả đã chứng minh |

Có thể gộp Kết quả và Thảo luận vào phần mô hình để tránh lặp. Bìa, TLTK, dictionary đầy đủ, bảng CV chi tiết và phụ lục phân công nằm ngoài ngân sách nội dung chính. Đếm trang sau khi xuất PDF; không giảm chữ nhỏ để ép vào 10 trang.

Cam kết minh bạch phải do nhóm điền theo thực tế: bộ dữ liệu tham khảo từ nguồn được khai báo; README/repository hiện tại có phải của nhóm hay dự án mẫu; phần nào nhóm tự làm; có dùng lại đồ án môn khác không. Không tự viết “hoàn toàn tự thiết kế” khi chưa xác minh lịch sử. Nếu có tham khảo dự án mẫu, chuẩn bị code nguồn/minh chứng theo template.

### Khung slide đề xuất

1. Bìa và hai thành viên.
2. Giới thiệu mục tiêu/câu hỏi và cam kết minh bạch — 1 slide.
3–4. Dữ liệu, biến, nguồn và giới hạn — tối đa 2 slide.
5. Quy trình và tiền xử lý.
6. Phân bố/ngoại lệ của giá.
7. So sánh city/day_type/room_type.
8. Pearson và ANOVA, chọn biến.
9. Các mô hình và giao thức train/CV/test.
10. Bảng đánh giá mô hình.
11. Phần dư và lỗi theo nhóm.
12. Kết quả đạt được và hạn chế — 1 slide.
13. Q&A.

Nội dung phân tích 7 slide, nằm trong giới hạn 10. Đây là lựa chọn của nhóm, không phải số slide tổng bắt buộc. A nói mục tiêu/dữ liệu/tiền xử lý và M1–M2; B nói EDA/M3–M4/kết quả, chuyển lời gọn. Cả hai đều hiểu bảng đánh giá chung.

### Demo 5 phút

- 0:00–0:45: mở notebook, chứng minh đọc data tại máy, số file/dòng và bảng khuyết.
- 0:45–2:00: trình bày 2 biểu đồ trả lời câu hỏi quan trọng, cho xem nhóm dữ liệu dùng để vẽ.
- 2:00–3:15: nêu ngắn cách split/CV, trình bày bảng mô hình đã chạy và giải thích kết quả so sánh; không đọc từng dòng code.
- 3:15–4:30: dự đoán vài mẫu test, đối chiếu actual/predicted và biểu đồ phần dư.
- 4:30–5:00: nêu kết luận có căn cứ và hạn chế.

Chạy sẵn toàn bộ trước buổi trình bày theo yêu cầu template; không train grid lớn trong 5 phút. Có thể mở output lưu nhưng phải minh bạch thời điểm chạy, cấu hình và tái lập được.

## 9. Checklist trước khi nộp

- [x] RAR hoàn tất đã được giải nén, kiểm tra phần source/data và đọc nội dung bổ sung Buoi1–Buoi5.
- [ ] Có mã nhóm, tên/MSSV, hệ học và hạn nộp chính thức.
- [ ] Nguồn dữ liệu/dự án và việc tái sử dụng được khai báo đúng thực tế.
- [ ] Ý nghĩa realSum, multi/biz, chỉ số attr/rest không được khẳng định vượt minh chứng hiện có.
- [ ] Báo cáo dùng đúng template, mục tiêu 5–10 trang (8–10 cho nhóm); nếu tăng thì có lý do thực chất, không quá khoảng 20 theo Buổi 10; không thêm phần ngoài mẫu.
- [ ] Số mẫu/biến/khuyết khớp code; nếu loại dòng thì báo đầy đủ trước/sau.
- [ ] Không dùng Unnamed: 0 như ID toàn cục; không ghép listing theo index giữa các file.
- [ ] Không xem weekdays/weekends là chuỗi thời gian hoặc cặp phòng đã xác minh.
- [ ] Biểu đồ có câu hỏi, nhãn/đơn vị, n và giải thích bằng số liệu.
- [ ] Có Pearson/ANOVA phù hợp, có giả định/giới hạn và không suy ra nhân quả.
- [ ] Có mô hình đơn biến/đa biến/đa thức/Ridge hoặc giải thích cụ thể phần chưa thực hiện.
- [ ] Fit preprocessing trong train/fold; CV chọn cấu hình; test được giữ lại để đánh giá.
- [ ] MSE/RMSE/MAE/R² cùng test/thang đo; không xóa test outlier để làm đẹp kết quả.
- [ ] Có phần dư đa biến và thảo luận dự đoán sai; không gọi là gian lận/giá trị thực.
- [ ] Notebook chạy lại từ đầu trên máy demo, đủ dependencies; kết quả report và slide khớp lần chạy chốt.
- [ ] TLTK đúng style, dẫn [n] tại nội dung sử dụng, không tự liệt kê slide môn; có phụ lục phân công chi tiết thực tế.
- [ ] Minh bạch AI đúng việc dùng; xóa hướng dẫn template/placeholder; giữ cột Ngành trên bìa, không ghi “Chương” hoặc hướng phát triển trong Kết luận.
- [ ] Có Word/PDF/slide/code/data, tên bắt đầu bằng nhóm, nộp từng file không nén.
- [ ] Đã diễn tập mục tiêu 10 phút thuyết trình +5 phút demo; demo kết quả trong notebook cuối. Một laptop nếu trực tiếp.
- [ ] Nếu học online, có giới thiệu chính chủ, ảnh/tên/MSSV và mặt động đủ thành viên xuyên suốt video; cả hai có phần trình bày khớp phụ lục.

## 10. Những điểm phải chốt trước khi viết kết luận cuối

1. Đã có bốn mốc nộp qua Buổi 10; mốc cuối 15/10/2026. Chưa xác minh giờ đóng cổng, thông báo thay đổi mới, mã nhóm/tên/MSSV/hệ học và nhóm đã từng nộp chưa. Không tự điền các thông tin này.
2. RAR hoàn chỉnh đã được rà: không có thêm tài liệu quy định đồ án riêng trong phần source ngoài môi trường. Các notebook là bài thực hành, có cell trống hoặc chưa hoàn thiện; không xem chúng là rubric bắt buộc.
3. Metadata gốc giải thích đơn vị/kỳ giá và multi/biz/attr/rest chưa có trong CSV. Nếu giữ giới hạn chỉ dùng source hiện có, đánh dấu theo README hoặc chưa rõ; không tự lấp bằng suy đoán.
4. Lịch sử tham khảo/tái sử dụng repository phải do hai thành viên khai báo.
5. Kết quả mô hình chỉ điền sau thực nghiệm. Không lấy placeholder README hoặc dự đoán của kế hoạch làm kết quả.

Tập trung chất lượng vào từng bước có bằng chứng: câu hỏi đúng với dữ liệu, xử lý giải thích được, trực quan rõ, đánh giá tái lập và hồ sơ đúng quy cách. Đây là phần nằm trong khả năng kiểm soát của nhóm để tránh mất điểm theo tài liệu môn học.

## 11. Cập nhật thực hiện ngày 13/10/2026

Đã ghép commit A `1fd2f5a` với gói B. Lịch 08–15/10 phía trên là lịch đề xuất ban đầu, không minh chứng hoàn thành theo ngày. Trạng thái trong bảng task dựa sản phẩm repo và kiểm chạy sạch; không tự coi nghiệm thu của giảng viên.

A có thể nhận T07 và bắt đầu T08 ngay bằng `reports/HANDOFF_B_TO_A.md`: cùng config, manifest, folds và pipeline. B đã xong T05/T06/T09; T13/T15 mới bản thảo. T10/T11 chờ M0/M1/M2 của A. Audit động và wording log của A đã sửa; các mục metadata/nhãn/kiểm thử còn lại được ghi trong T03/T04. Chưa có giờ LMS, thông tin nhóm hoặc bằng chứng diễn tập/video cuối.
