# T12 — Nội dung báo cáo phần A (Đoàn Hữu Hàn) để tích hợp

Bản nội dung ngày 13/10/2026. Soạn thảo chuẩn quy cách môn học IE313 theo `Template_IE313.docx` (Font Times New Roman 13, canh đều, giãn dòng 1.15 multiple, Heading 1/2 rõ ràng, không dùng chữ "Chương"). Số liệu khớp 100% với các bảng biểu và kết quả chạy sạch của `notebooks/01_data_preprocessing.ipynb` và `notebooks/03a_linear_regression_models.ipynb`.

---

## 1. GIỚI THIỆU

Đồ án phân tích khám phá và xây dựng mô hình dự đoán giá niêm yết `realSum` của 51.707 quan sát chỗ nghỉ Airbnb tại 10 thành phố châu Âu bằng các kỹ thuật thống kê mô tả, kiểm định tương quan Pearson, phân tích phương sai ANOVA một nhân tố và các mô hình hồi quy tuyến tính trong chương trình môn học. Toàn bộ quy trình từ tiền xử lý, kiểm toán chất lượng dữ liệu, phân chia tập dữ liệu đến đánh giá mô hình được thực hiện bằng Python với quy trình chống rò rỉ thông tin chặt chẽ. Năm mô hình hồi quy (M0 Baseline, M1 Hồi quy đơn biến, M2 Hồi quy đa biến OLS, M3 Hồi quy đa thức bậc 3, M4 Hồi quy Ridge) được so sánh công bằng trên cùng giao thức 5-Fold Cross-Validation. Mô hình M3 (Đa thức bậc 3 trên 3 biến số cốt lõi) được lựa chọn với sai số kiểm định chéo trung bình thấp nhất ($MSE_{CV} = 79.228,00$), đạt $RMSE = 311,70$, $MAE = 102,02$ và $R^2 = 0,1912$ khi đánh giá trên tập kiểm tra độc lập 10.342 mẫu (giảm 19,12% MSE so với mô hình baseline).

Bộ dữ liệu nghiên cứu gồm 20 tệp CSV được cung cấp sẵn từ dự án tham khảo trên kho mở Kaggle ("Airbnb Prices in European Cities" của tác giả The Devastator [1]), nhóm hoàn toàn không tự thu thập dữ liệu ngoài. Nhóm đã kế thừa cấu trúc mã nguồn ban đầu của dự án và chuẩn hóa lại toàn bộ quy trình tiền xử lý, giao thức thực nghiệm theo sát yêu cầu học thuật của môn học IE313. Trong quá trình thực hiện, nhóm có sử dụng các công cụ trí tuệ nhân tạo (Codex, Antigravity/Gemini) để hỗ trợ rà soát cú pháp, viết các đoạn mã kiểm thử tự động (verification scripts) và hỗ trợ định dạng bảng biểu báo cáo. Hai thành viên nhóm trực tiếp kiểm chứng toàn bộ logic thuật toán, tái lập số liệu độc lập trên máy cá nhân và chịu trách nhiệm học thuật về các diễn giải và kết luận trong đồ án.

---

## 2. MÔ TẢ BỘ DỮ LIỆU

Bộ dữ liệu nghiên cứu được hợp nhất từ 20 tệp CSV tương ứng với 10 thành phố du lịch lớn tại châu Âu (Amsterdam, Athens, Barcelona, Berlin, Budapest, Lisbon, London, Paris, Rome, Vienna), mỗi thành phố được phân tách thành hai nhóm thời gian lưu trú trong tuần (`weekdays`) và cuối tuần (`weekends`). Mỗi tệp nguồn ban đầu gồm 20 cột thuộc tính; sau khi nạp và bổ sung các trường thông tin quản trị (`city`, `day_type`, `source_file`, `source_row`), bộ dữ liệu tổng hợp đạt quy mô chính xác 51.707 dòng quan sát và 24 thuộc tính. Kiểm toán chất lượng dữ liệu xác nhận 100% các ô dữ liệu không bị khuyết tật (`NaN`/`null`) và không chứa giá trị số vô hạn. Trong 17 thuộc tính có kiểu dữ liệu số, có 1 cột định danh kỹ thuật ban đầu (`Unnamed: 0`), 4 cột dạng cờ boolean nhị phân (`room_shared`, `room_private`, `host_is_superhost`, `multi`), 2 cột tọa độ địa lý (`lat`, `lng` ghi nhận theo `per_readme`), và 10 biến định lượng thực tế. Biến mục tiêu `realSum` được giữ nguyên giá trị gốc trong dữ liệu; đơn vị EUR được ghi nhận theo tài liệu README của bộ dữ liệu nguồn, kỳ lưu trú chưa có metadata xác minh nên giữ nguyên `realSum`, không tự ý quy đổi thành giá mỗi đêm.

### Bảng 1. Các biến mục tiêu, dự báo cốt lõi và khóa truy vết

| Biến cốt lõi | Kiểu dữ liệu | Ý nghĩa và vai trò dùng trong đồ án |
|---|---|---|
| `realSum` | Số thực | Biến giá mục tiêu dự đoán, giữ nguyên thang đo gốc của dữ liệu |
| `person_capacity` | Số nguyên | Sức chứa tối đa của chỗ nghỉ (từ 2 đến 6 khách) |
| `bedrooms` | Số nguyên | Số lượng phòng ngủ quan sát (từ 0 đến 10; giá trị 0 là quan sát thực tế trong dữ liệu, không tự suy ra studio) |
| `dist` | Số thực | Khoảng cách từ chỗ nghỉ tới trung tâm thành phố tính bằng km |
| `metro_dist` | Số thực | Khoảng cách tới trạm metro gần nhất tính bằng km (giá trị 0,00 là làm tròn hiển thị 2 chữ số thập phân, min thực tế là 0,0023 km) |
| `cleanliness_rating` | Số thực | Điểm đánh giá mức độ sạch sẽ quan sát (từ 2 đến 10) |
| `guest_satisfaction_overall` | Số thực | Điểm đánh giá mức độ hài lòng tổng thể của khách hàng (từ 20 đến 100) |
| `city` | Phân loại | Tên thành phố nơi chỗ nghỉ tọa lạc (10 giá trị danh mục) |
| `day_type` | Phân loại | Nhóm ngày lưu trú xác định từ tên tệp (`weekdays` hoặc `weekends`) |
| `room_type` | Phân loại | Loại hình phòng (`Entire home/apt`, `Private room`, `Shared room`) |
| `host_is_superhost` | Boolean | Cờ chỉ báo chủ nhà đạt chuẩn Superhost (True/False) |
| `source_file`, `source_row` | Khóa truy vết | Cặp khóa kỹ thuật định danh nguồn gốc dòng dữ liệu ban đầu; không phải mã listing ID gốc của Airbnb |

---

## 3. THIẾT KẾ THỰC NGHIỆM VÀ TIỀN XỬ LÝ

### 3.1. Phạm vi và tiền xử lý dữ liệu

Nghiên cứu tuân thủ nghiêm ngặt nguyên tắc chỉ sử dụng bộ dữ liệu được cung cấp và các phương pháp trong phạm vi môn học, không tự ý bổ sung dữ liệu ngoại sinh, không sử dụng các thuật toán cây quyết định phức tạp hay mở rộng ngoài phạm vi bài toán hồi quy. Để bảo đảm tính trung thực của bài toán dự báo giá thực tế, biến mục tiêu `realSum` được giữ nguyên thang đo ban đầu trong suốt quá trình huấn luyện và kiểm định mô hình; không áp dụng biến đổi log lên biến mục tiêu để dự báo rồi tự ý mũ hóa ngược lại khi đánh giá. Toàn bộ các quan sát có giá trị cao trong tập dữ liệu đều được giữ nguyên vẹn; không áp dụng bất kỳ hình thức cắt tỉa ngoại lệ (clipping) nào trên tập kiểm tra độc lập. Phương pháp hàng rào khoảng tứ phân vị (IQR) theo từng thành phố được sử dụng như một công cụ phân tích khám phá cấu trúc phân phối, không dùng làm căn cứ để loại bỏ dữ liệu hoặc quy chụp là gian lận. Do thiếu thông tin về mã định danh chỗ nghỉ (`listing_id`) và mốc thời gian thu thập cụ thể, nghiên cứu không thể xác nhận tính độc lập tuyệt đối giữa các quan sát (khả năng lặp lại cùng một chỗ nghỉ qua các tuần).

### 3.2. Chia dữ liệu và quy trình chống rò rỉ

Thực nghiệm áp dụng giao thức phân chia dữ liệu thống nhất `ie313_raw_v1_seed0_cv5` được cấu hình chi tiết tại `config/experiment_config.json` và lưu vết tại `split_manifest.csv`. Dữ liệu được phân chia ngẫu nhiên với `seed = 0` thành hai tập độc lập: Tập Huấn luyện (Train) gồm 41.365 dòng (chiếm 80,00%) và Tập Kiểm tra độc lập (Holdout Test) gồm 10.342 dòng (chiếm 20,00%). Tập Test được đóng băng hoàn toàn (`cv_fold = -1`), tuyệt đối không được tiếp cận trong quá trình tiền xử lý, huấn luyện hay lựa chọn mô hình. Trên tập Huấn luyện, quy trình kiểm định chéo 5 phần (5-Fold Cross-Validation, KFold shuffle với `seed = 0`) được thiết lập: mỗi fold gồm 33.092 dòng huấn luyện và 8.273 dòng kiểm định; 5 tập kiểm định này phủ kín và tách biệt hoàn toàn 41.365 dòng tập Train.

Toàn bộ các bước tiền xử lý biến số được đóng gói hoàn toàn bên trong `Pipeline` của thư viện Scikit-learn:
- Biến định lượng: Được chuẩn hóa bằng `StandardScaler`, trong đó tham số trung bình $\mu$ và độ lệch chuẩn $\sigma$ chỉ được tính toán (fit) trên tập huấn luyện của từng fold, loại bỏ hoàn toàn nguy cơ rò rỉ dữ liệu sang tập kiểm định và tập test.
- Biến phân loại: Được mã hóa bằng `OneHotEncoder(drop='first', handle_unknown='ignore')`, chọn nhóm cơ sở mặc định để tránh đa cộng tuyến và thiết lập xử lý an toàn cho các danh mục mới nếu xuất hiện.
- Cơ chế bảo vệ thuộc tính: Sử dụng tham số `remainder='drop'` trong bộ chuyển đổi cột `ColumnTransformer` để chỉ cho phép đúng 10 thuộc tính nghiệp vụ hợp lệ trong danh mục cho phép (Allowlist), loại bỏ triệt để các trường dữ liệu rò rỉ từ biến mục tiêu (như `price_tier`, `dist_bin`).

### Bảng 2. Danh mục các thuộc tính trong Allowlist thực nghiệm

| Nhóm thuộc tính | Danh sách thuộc tính được đưa vào mô hình | Phương pháp tiền xử lý trong Pipeline |
|---|---|---|
| Định lượng (6 biến) | `person_capacity`, `bedrooms`, `dist`, `metro_dist`, `cleanliness_rating`, `guest_satisfaction_overall` | `StandardScaler` (fit trên train của từng fold) |
| Phân loại (3 biến) | `city`, `day_type`, `room_type` | `OneHotEncoder(drop='first', handle_unknown='ignore')` |
| Boolean (1 biến) | `host_is_superhost` | `StandardScaler(with_mean=False)` giữ nguyên dạng nhị phân |

### 3.3. Chỉ số đánh giá và quy tắc lựa chọn mô hình

Hiệu năng của các mô hình được đo lường thông qua 4 chỉ số thống kê tiêu chuẩn: Sai số bình phương trung bình ($MSE$), Căn bậc hai sai số bình phương trung bình ($RMSE$), Sai số tuyệt đối trung bình ($MAE$), và Hệ số xác định ($R^2$). Trong đó, $RMSE_{CV}$ được tính bằng trung bình các giá trị $RMSE$ của từng fold, không đồng nhất với $\sqrt{MSE_{CV}}$ do tính chất của bất đẳng thức Jensen. Tiêu chí duy nhất để lựa chọn mô hình chiến thắng giữa các cấu hình thử nghiệm là giá trị $MSE_{CV}$ trung bình thấp nhất qua 5 fold kiểm định chéo trên tập Train. Tập Test chỉ được giải phóng một lần duy nhất tại bước kiểm tra cuối cùng để đánh giá khách quan năng lực tổng quát hóa, tuyệt đối không dùng kết quả trên tập Test để quay ngược lại tinh chỉnh siêu tham số hay lựa chọn biến.

---

## 4. DIỄN GIẢI CÁC MÔ HÌNH TUYẾN TÍNH CỦA THÀNH VIÊN A (M0, M1, M2)

- **Mô hình M0 (Baseline - Giá trị trung bình):** Dự đoán giá cố định bằng giá trị trung bình của tập huấn luyện trong từng fold ($\hat{y} = \bar{y}_{train}$). Kết quả đạt $MSE_{CV} = 104.402,75$, $R^2_{CV} = -0,0000$, đóng vai trò mốc tham chiếu cơ sở để so sánh mức độ cải thiện của các mô hình tiếp theo.
- **Mô hình M1 (Hồi quy tuyến tính đơn biến):** Sử dụng duy nhất thuộc tính sức chứa `person_capacity` ở thang đo gốc. Phương trình hồi quy khớp trên toàn bộ tập Train:
  $$\widehat{\text{realSum}} = 117,21 + 51,52 \times \text{person\_capacity}$$
  Hệ số góc $w_1 = 51,52$ phản ánh rằng khi sức chứa tăng thêm 1 người thì giá dự đoán tăng trung bình $51,52$ đơn vị `realSum` (theo dữ liệu cung cấp, không suy diễn thành EUR/đêm hay quan hệ nhân quả). Hệ số chặn $w_0 = 117,21$ chỉ là giá trị kỳ vọng về mặt toán học khi sức chứa bằng 0 (điểm nằm ngoài miền dữ liệu quan sát, không được hiểu là chi phí cố định tối thiểu hay giá sàn). Mô hình đạt $MSE_{CV} = 99.919,96$, $R^2_{CV} = 0,0443$.
- **Mô hình M2 (Hồi quy tuyến tính đa biến OLS):** Kết hợp toàn bộ 10 thuộc tính trong Allowlist. Các biến định lượng được chuẩn hóa nên hệ số phản ánh mức thay đổi giá dự đoán khi biến số tăng thêm 1 độ lệch chuẩn trên tập train nếu cố định các biến còn lại. Các hệ số phân loại phản ánh mức chênh lệch giá dự đoán so với nhóm tham chiếu (Athens đối với thành phố, Weekdays đối với nhóm ngày, Entire home/apt đối với loại phòng). Mô hình đạt $MSE_{CV} = 79.988,15$, $R^2_{CV} = 0,2409$. Độ chênh lệch giữa Train MSE ($79.912,37$) và CV MSE ($79.988,15$) chỉ là $75,78$ đơn vị ($0,095\%$), là một quan sát thực nghiệm nội bộ cho thấy mô hình không bị quá khớp nghiêm trọng trên tập huấn luyện của bộ dữ liệu này.
