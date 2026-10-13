# Review phần A và kế hoạch bàn giao của B

**Bản review lịch sử ngày 12/10.** A đã có sửa ở commit `1fd2f5a` ngày đồng bộ 13/10, gồm audit động và wording log. Trạng thái hiện hành xem [TASK_STATUS.md](TASK_STATUS.md) và [HANDOFF_B_TO_A.md](HANDOFF_B_TO_A.md); không dùng các lỗi đã sửa trong bản lịch sử này như kết luận về code hiện tại.

Ngày review: **12/10/2026**. Repo đã pull fast-forward từ `84016f3` đến **`e9eab7f`** trên `main`. Trước pull không có thay đổi local được Git báo. Phạm vi: nghiệm thu T01–T04, xác định việc B cần làm để A tiếp tục; chưa triển khai T05–T15, chưa sửa notebook của A, chưa commit/push hay nộp bài.

## 1. Kết luận để bắt đầu công việc

**B có thể bắt đầu T05–T06 bằng `data/processed/airbnb_combined.csv`.** Phần nạp/gộp dữ liệu và các bảng số liệu của A được kiểm chứng đúng trên snapshot hiện tại. Notebook 01 chạy hết **18 cell code** từ kernel sạch. Tuy nhiên, chưa nên coi T01–T04 đều nghiệm thu hoàn toàn: T01 thiếu bằng chứng thông tin nhóm/nguồn/AI; T03–T04 còn diễn giải quá mức; cơ chế báo PASS trong audit cần sửa.

Việc cần B ưu tiên để A tiếp tục mô hình là **T05 → T06 → chốt T07 cùng A**. Sau mốc này, A làm T08 (M0/M1/M2), B làm T09 (Polynomial/Ridge) song song. B không phải làm xong slide hoặc phần dư trước khi A được vào làm mô hình. Trong lúc chờ, A vẫn có thể sửa notebook 01, dựng khung report dữ liệu và chuẩn bị hàm/pipeline chung, nhưng chưa chọn cấu hình theo test.

Nguồn review: `notebooks/01_data_preprocessing.ipynb`, toàn bộ 7 CSV tại `outputs/tables/`, 3 hình tại `outputs/figures/`, `archive.zip`, 20 CSV tại `data/raw/`, file gộp, `README.md`, `requirements.txt`, và kế hoạch/skill trong `Skill/`. Hai ảnh tracker do người dùng cung cấp thể hiện T01–T04 đã được đánh dấu hoàn thành; đó là trạng thái nhóm khai báo, không thay thế nghiệm thu dưới đây.

## 2. Đã kiểm chứng những gì

Chạy lại trong bản sao riêng ngoài repo, chỉ đưa `archive.zip` và source notebook vào, xóa output/execution count trong bản sao trước chạy. Kernel thực thi đủ 18/18 cell, không có exception. Môi trường review: Python 3.12; pandas 3.0.6, NumPy 2.5.4, Matplotlib 3.11.2, Seaborn 0.13.2, nbclient 0.11.0, ipykernel 7.4.0. Đây là môi trường kiểm chứng, chưa phải phiên bản hai bạn đã chốt cho máy demo.

Các kiểm tra độc lập:

- 20 file raw có giá trị ô khớp archive. Byte có khác do LF/CRLF trong checkout Git; sau chuẩn hóa xuống dòng thì nội dung text khớp, không có bằng chứng dữ liệu bị sửa.
- File gộp khớp dữ liệu raw ghép lại về hàng/cột/thứ tự, với dung sai đọc float `1e-12`: **51.707 dòng × 24 cột**. Cột gốc và bốn cột tạo thêm được giữ đúng.
- `source_row` bằng index nguồn; với snapshot này index đúng dãy 0…n−1 ở từng file. Nó là mã truy vết trong file, không phải listing ID.
- Không khuyết; số không hữu hạn bằng 0; duplicate hoàn toàn trong cùng city/day_type khi bỏ index bằng 0; số dòng lặp city/lat/lng sau lần đầu là **21.582**.
- Dictionary đủ **24 biến**, không thiếu cột; đã phân biệt nguồn README, biến chưa rõ và biến nhóm tạo.
- Mean/median/std/IQR, bảng thống kê mô tả, số cờ IQR từng city, bảng log/capping và count bin khoảng cách khớp tính lại.
- **Cả 7 bảng CSV tái sinh từ notebook sạch đều khớp bảng A đã commit**, bỏ khác biệt kiểu lưu khi đọc CSV. Đã xem 3 hình gốc: hình đọc được; cần chỉnh một số cách gọi và chú thích theo phần 3.
- File gộp đã lưu vẫn chỉ có 24 cột, chưa log/scaling/capping. Các phép biến đổi minh họa trong notebook không ghi đè target trong file bàn giao hiện tại.

Minh chứng review ở thư mục workspace cha: `_review/audit_A_20261012/independent_audit.json`, `notebook_run.json`, `rerun_table_comparison.json`, `01_data_preprocessing.executed.ipynb`. Không dùng output lưu sẵn của A như bằng chứng duy nhất.

## 3. Nghiệm thu A theo task và các điểm phải sửa

| Task | Kết quả review | Điều kiện còn lại |
|---|---|---|
| T01 – yêu cầu/đề tài/nguồn | **Chưa đủ bằng chứng để nghiệm thu** | Source có kế hoạch/skill và link dữ liệu, nhưng chưa chứng minh mã nhóm, MSSV/tên/hệ học, đăng ký, giờ LMS, nguồn dự án/tái sử dụng và cách dùng AI thực tế đã chốt. T01 là việc chung A+B, không quy hết cho A |
| T02 – loader/schema/missing | **Đạt kỹ thuật với dữ liệu hiện tại; cần sửa độ tin cậy của audit** | Dữ liệu B dùng được. Sửa PASS tính động, không tự điền số kiểm tra bằng 0 khi chưa chạy, bổ sung kiểm hữu hạn và đọc marker phù hợp dtype string |
| T03 – dictionary/truy vết/lặp | **Có đủ sản phẩm; cần sửa diễn giải** | Giữ đủ 24 biến và mức `unclear`; bỏ khẳng định metadata chưa có căn cứ; tính miền/đếm bằng data, không ghi cứng |
| T04 – thống kê/IQR/kịch bản | **Đạt số liệu và chạy lại; cần sửa diễn giải/kiểm thử** | Giữ data gốc. Không coi log là bắt buộc hoặc skew<1 là điều kiện để task đúng; phân biệt biến định lượng với ID/cờ nhị phân; thống nhất nhãn bin và chú thích hình |

### 3.1. Ưu tiên cao: audit vẫn báo PASSED khi dữ liệu vi phạm

Căn cứ notebook: **cell 18** (đếm cell từ 0), phần tạo `audit_rows`. Các dòng có `'status': 'PASSED'` cố định; nhánh khôi phục còn gán `total_hidden_missing`, `bad_room_type`, `dup_count` bằng 0 thay vì kiểm lại. Cell 10 có tính FAILED nhưng chưa buộc kết quả này đi vào bảng audit cuối.

Đã thử **chính đoạn tạo audit_rows** trên dataframe bản sao với một `realSum=-1`: `observed_value=1`, `expected_value=0`, nhưng `status='PASSED'`. Đây là kiểm chứng lỗi logic; không sửa data thật. Dữ liệu thật hiện vẫn không có giá âm.

A cần sửa:

1. Tính status từ số vi phạm hoặc điều kiện kiểm tra, không gán nhãn đạt trước.
2. Khi chưa có biến kết quả audit, chạy kiểm tra cần thiết hoặc báo chưa chạy; không điền 0.
3. Giữ số tọa độ lặp và số cờ IQR là **thông tin mô tả/FLAG**, không đồng nhất “bằng snapshot” với chất lượng tốt hoặc độc lập mẫu.
4. Kiểm số hữu hạn với `np.isfinite` cho các cột số. Rà marker trên dtype chuỗi phù hợp; pandas 3 có thể dùng dtype `str`, nên chỉ xét `dtype == 'object'` sẽ bỏ qua cột chuỗi.
5. Tóm tắt lấy từ kết quả kiểm tra thật. Với kiểm tra đầu vào bắt buộc, dừng nếu không đạt trước khi chuyển dữ liệu cho mô hình.

Lỗi này không ngăn B đọc file hiện tại đã kiểm chứng, nhưng phải sửa trước khi dùng audit như minh chứng code đáng tin cậy.

### 3.2. Ưu tiên cao: diễn giải log/capping chưa đúng phạm vi

Căn cứ: cell 34–35 và 39, hình `fig_02_price_transform_comparison.png`. Notebook gọi Log10 “tiệm cận chuẩn”, “tối quan trọng” cho hồi quy và assert `log_skew < 1.0`.

Số skew/kurt được tính đúng, nhưng **skew nhỏ hơn không chứng minh phân phối chuẩn, target chuẩn cũng không phải điều kiện bắt buộc để chạy hồi quy tuyến tính**. Test nên kiểm công thức/giá trị hữu hạn/số mẫu, không bắt dữ liệu phải đạt một hình dạng đẹp. Diễn giải an toàn: “Log10 giảm lệch phải trong thí nghiệm mô tả này; hiệu quả dự đoán chưa kiểm chứng”.

Hai kịch bản capping hiện chỉ là khảo sát phân phối toàn bộ, chưa dùng huấn luyện; **chưa có lỗi leakage trong mô hình vì chưa có mô hình**. Không chuyển thẳng ngưỡng P99/IQR tính từ cả data vào pipeline, không cap target/test để báo điểm đẹp. Nếu nhóm thử log-target sau này, phải chốt là thí nghiệm riêng, inverse về `realSum` để đánh giá cùng thang; không so MSE log với MSE giá. Thí nghiệm log-target không phải phần bắt buộc cần thêm ngay.

### 3.3. Metadata có chỗ khẳng định vượt source

Căn cứ: cell 9/13/15/22/25/32/34/40 và `outputs/tables/data_dictionary.csv`.

| Chỗ hiện tại | Cách sửa để bám source |
|---|---|
| bedrooms=0 được xác định là studio/phòng mở | Chỉ ghi “0 được quan sát, chưa có căn cứ để coi là missing; không tự loại”. Loại phòng cụ thể chưa được xác minh |
| `metro_dist` làm tròn 0.00 nghĩa là sát ga | Min thực tế **0,002301…**, không phải 0. Ghi số đủ chính xác hoặc `<0,01 km theo đơn vị README`; không suy ra ở sát ga từ làm tròn |
| lat/lng ghi WGS84 và `confirmed` | Source hiện có không xác minh hệ quy chiếu WGS84. Tách giá trị/toạ độ quan sát được khỏi chuẩn tọa độ chưa rõ |
| weekday/weekend là “hai đợt lấy mẫu độc lập” | Ghi hai nhóm theo tên file, chưa biết độc lập thống kê hoặc cùng listing hay không. Đây là giới hạn cần nhắc cả khi ANOVA và split |
| tọa độ lặp do chung tòa/cùng chỗ nghỉ hai ngày | Đây chỉ là giả thuyết. Kết quả biết chắc là 21.582 dòng lặp tọa độ; không dùng để xác nhận listing |
| giá cao phản ánh luxury/biệt thự/vị trí đắc địa | Data không có nhãn xác nhận luxury/biệt thự. Giữ vì chưa chứng minh sai, không vì đã chứng minh “cao cấp” |
| `_norm` khẳng định chuẩn hóa thang 100 | Ghi miền quan sát tới 100, công thức/chia theo city/file chưa rõ. Không coi đó là bằng chứng quá trình chuẩn hóa đã tránh leakage |

Giữ nhãn `per_readme` cho giá/kỳ/đơn vị; không lấy README làm metadata gốc đã xác minh. Giá là giá quan sát trong dataset, không gọi giá trị thật, tối ưu hoặc giao dịch thực tế.

### 3.4. Bảng/nhãn cần chỉnh trước report

- Cell 22 `get_observed_range` ghi cứng nhiều min/max/mean/%, cell 18/28/39 cũng có tóm tắt cứng. Các số hiện khớp snapshot, nhưng dễ lệch khi data thay đổi. A nên tính trực tiếp và giữ snapshot riêng để đối chiếu.
- Cell 31 dùng tất cả cột numeric: **17 cột gồm `Unnamed: 0`, `source_row`, `multi`, `biz`**. Không gọi tất cả là 17 yếu tố định lượng dự báo; ID chỉ truy vết, cờ nhị phân dùng count/tỷ lệ. CV của kinh/vĩ độ không phù hợp để giải thích độ phân tán có ý nghĩa theo tỉ lệ. Phần mô tả nói có mode nhưng bảng chưa tính mode: sửa lời mô tả hoặc tính cho biến phù hợp, không cần thêm hàng loạt thống kê hình thức.
- Cell 33/35 hardcode fence `576.11`; dùng fence tính từ quantile chưa làm tròn, chỉ làm tròn khi hiển thị. Biểu thức `overall_overall` là dấu vết biến không có trong notebook; trên clean run nhánh fallback vẫn chạy đúng, nên không gọi đó là lỗi làm notebook hiện tại crash. Nên bỏ nhánh thừa và dùng biến fence chung.
- Cell 37 dùng `right=False`, nên bin cuối là **`dist >=5`** và **`price >=600`**, không phải `>5` / `>600`. Ghi rõ các khoảng nửa kín. “Trung tâm/vành đai/luxury” là nhãn nhóm tự đặt, không phân vùng hoặc hạng phòng đã được nguồn chứng nhận.
- Trên hình, dùng “số quan sát/niêm yết”, tránh “số căn hộ” cho cả Private/Shared room, và không xem count là số listing độc nhất.
- Hình giá cắt trục 1.500 đã ghi rõ, tốt; nên ghi thêm **258 quan sát có giá >1.500 không hiện trong histogram giới hạn**. Boxplot log `showfliers=False` cần chú thích ẩn điểm ngoại lệ chỉ trên hình, không xóa dữ liệu.
- Cell 40 còn link `file:///p:/...` theo máy A; đổi link tương đối để B/máy thầy mở được. README vẫn có mục tiêu module du lịch/RF/XGBoost/“định giá ảo” và số dòng xấp xỉ cũ; không bê các tuyên bố này vào báo cáo môn.

### 3.5. Cột phát sinh trong RAM dễ làm B nhầm khi tích hợp

Cell 33/37 thêm `log_price_temp`, `dist_bin`, `price_tier` vào `df_combined` trong RAM. CSV đã lưu trước đó vẫn 24 cột nên **file B nhận hiện không rò rỉ target**. Tuy nhiên, notebook cuối chạy nối A rồi B có thể nhận dataframe 27 cột. Không chọn predictor tự động bằng “tất cả cột numeric”. B nên đọc CSV sạch riêng hoặc tạo dataframe copy; pipeline dùng **allowlist predictor rõ ràng**. `log_price_temp` và `price_tier` tính từ giá phải loại khỏi X; cột bin khoảng cách chỉ dùng nếu nhóm thật sự chọn và giải thích.

## 4. B cần làm gì trước để A tiếp tục

### Bước 1 — T05: EDA trả lời Q1–Q2

Input: file gộp 24 cột và dictionary. Không cần làm lại loader hay toàn bộ IQR của A. Có thể dùng lại hình A sau chỉnh chú thích, nhưng phải thêm phân tích nhóm còn thiếu.

Làm trong `notebooks/02_exploratory_data_analysis.ipynb` (chưa tồn tại tại thời điểm review):

1. Đọc data độc lập, assert đủ 51.707 dòng/24 cột, giữ nhóm và truy vết; không scale/cap/loại giá cao.
2. Bảng theo **city**, **room_type**, **city × day_type**, **city × room_type × day_type**: `n`, mean, median, std, Q1/Q3 hoặc IQR. Tổ hợp không có mẫu giữ là thiếu/không áp dụng, không biến thành giá 0.
3. Cơ cấu mẫu theo loại phòng/ngày/thành phố. Shared room chỉ 366 quan sát toàn bộ; nhóm nhỏ hoặc trống cần ghi rõ.
4. Biểu đồ ưu tiên: số mẫu city; giá theo room_type; median weekdays/weekends trong city; heatmap/pivot city×room_type đi cùng n. Hình có trục/đơn vị theo README, thang log/cắt trục nếu dùng và nhận xét 2–4 câu có số.
5. So sánh Q2 theo city và loại phòng, không suy “cùng phòng tăng cuối tuần” hoặc “cuối tuần gây tăng giá”.

Bàn giao đề xuất: `eda_group_summary.csv`, `eda_sampling_counts.csv`, `eda_findings.md` cùng hình dùng trong report. Đây là tên sản phẩm cần tạo, chưa phải file đã có.

**A nhận được gì:** bảng để kiểm Q1–Q2, chọn phát hiện đưa vào report và biết lệch cơ cấu mẫu; A có thể viết phần dữ liệu bằng các bảng T02–T04 sẵn có ngay khi B đang làm bước này.

### Bước 2 — T06: bằng chứng liên hệ và danh sách ứng viên

1. Phân loại theo ý nghĩa: numeric thật, category/boolean, ID, target, cột target-derived. Không dùng ID làm biến số phân tích giá.
2. Pearson với `realSum`: r, p, n và scatter cho biến số phù hợp; xem gộp và theo city. Không loại hết chỉ vì `|r|<0,3` ở mẫu gộp; không diễn giải tương quan thành nhân quả.
3. ANOVA giá theo `room_type` và các nhóm cần thiết: F/p, n từng nhóm, mean/median/boxplot; ghi giả định và giới hạn do lệch phải/phương sai/mẫu nhỏ/tọa độ lặp. p nhỏ không cho biết tác động lớn hay tất cả cặp nhóm khác nhau.
4. Tạo `feature_evidence.csv`: tên biến, loại, phạm vi mẫu, n, phép xét, r/p hoặc F/p, giả định/giới hạn, quyết định **ứng viên** và lý do. Chưa tính không điền p=0; p quá nhỏ có thể dùng ký pháp khoa học và nói giới hạn hiển thị.
5. Các bảng mô tả toàn bộ chỉ để giải thích dataset. Để chọn biến **có học từ y** phục vụ mô hình, tính trong train; nếu chọn biến tự động nằm trong kết quả CV thì selector phải được fit trong từng fold. Không dùng bảng toàn bộ để chọn predictor rồi nói test/CV độc lập.

**A nhận được gì:** ứng viên cho M1/M2, lý do chọn/không chọn, biểu diễn category và lưu ý tập biến. Đây mới là phần bàn giao kỹ thuật mở đường T08.

### Bước 3 — T07 chung: chốt giao thức trước khi A/B huấn luyện

Không cần đợi làm tất cả hình report mới chốt. Có thể chuẩn bị split cố định sớm ngay khi vào T06 để bảng lựa chọn predictor dùng đúng train; sau đó A+B chốt T07 từ bằng chứng phù hợp.

| Quyết định cần A+B thống nhất | Đề xuất theo kế hoạch hiện có | Điều kiện để A dùng tiếp |
|---|---|---|
| Dữ liệu chính | CSV gộp 51.707×24, raw target `realSum`, giữ tất cả mẫu | Ghi phiên bản/hash dữ liệu; không ngầm dùng bản cap/log hoặc df có cột phát sinh |
| Mã dòng | `(source_file, source_row)` | Duy nhất, giữ trong manifest/predictions; không coi là listing ID hoặc dùng trong X |
| Holdout | 80% train, 20% test, `random_state=0` | Xuất một manifest chia mẫu chung. sklearn sẽ cho **41.365 train / 10.342 test** với n=51.707 và test_size=0.2; đây là số kỳ vọng cần kiểm khi tạo, chưa phải split đã chạy |
| CV | 5 folds chỉ trong train | Chốt cùng cấu hình fold cho A/B; nếu dùng shuffle thì chốt seed và indices chung, không để mỗi notebook tạo khác nhau |
| Số / category / boolean | Allowlist từng nhóm | Không infer tất cả numeric. Category `city`, `day_type`, `room_type`; cờ `host_is_superhost` dùng một biểu diễn được chốt |
| Tập numeric lõi | Ứng viên dễ giải thích: capacity, bedrooms, dist, metro_dist, cleanliness, satisfaction | Tên cột thật tương ứng; chốt dựa ý nghĩa và protocol hợp lệ. Đây là gợi ý ứng viên, không danh sách cuối đã nghiệm thu |
| Các index/tọa độ | Cân nhắc riêng, khai rõ metadata và giới hạn | Raw/norm chọn một biểu diễn mỗi cặp; không khẳng định `_norm` đã tránh leakage. Không thêm biến chỉ để nâng điểm |
| Loại khỏi predictor | realSum; Unnamed: 0; source_file/source_row; room flags khi có room_type; log_price_temp/price_tier | Không có target hay proxy trực tiếp của target trong X. Các cột metadata chưa rõ phải có quyết định dùng/không dùng rõ |
| Preprocessing | Encoder/scaler trong pipeline fit train/fold | Không scale toàn bộ trước CV; với hồi quy có intercept, thống nhất encoding category tránh dummy trùng hoàn hảo |
| Cách chốt mô hình | CV MSE, xem thêm R²/chênh train–CV | Không dùng test chọn bậc/alpha/mô hình. Test để T10 sau khi chốt |
| So sánh | Cùng dữ liệu/split/folds/thang giá | T08/T09 output cùng schema; không so điểm log với điểm giá |

Bàn giao đề xuất **một gói thống nhất**, không chỉ nhắn “EDA xong”:

- Notebook 02 chạy từ đầu và bảng/hình T05–T06 có nhận xét.
- `feature_evidence.csv`: phân biệt EDA toàn bộ và bằng chứng dùng lựa chọn trên train.
- `experiment_config.json`: target, predictor allowlist theo nhóm, exclude, split seed/tỷ lệ, CV, thang target và metric chọn mô hình.
- `split_manifest.csv`: `source_file`, `source_row`, `split` (train/test); nếu lưu folds, mỗi train row có fold validation cố định. Không cần đưa giá target vào config/manifest.
- `HANDOFF_B_TO_A.md`: đường dẫn input, những gì đã chạy, schema, quyết định đã chốt/chưa chốt, cách chạy và đoạn A cần kiểm tra.

Tên file trên là **đề xuất của nhóm**, không yêu cầu nguyên văn của thầy; chưa tạo chúng trong lượt review này. A kiểm tra và chạy lại gói này trước khi nhận T08. Có thể dùng cấu trúc gọn hơn miễn đủ cùng thông tin.

## 5. Sau khi bàn giao, A/B làm song song thế nào

| Thứ tự | A | B | Điều kiện qua mốc |
|---|---|---|---|
| Ngay 12/10 | Sửa audit/diễn giải notebook 01; chuẩn bị khung report dữ liệu/phương pháp | T05, T06 và chốt T07 cùng A | Dữ liệu không đổi ngầm; gói input/biến/split/CV dùng chung |
| Sau T07, mục tiêu 13/10 | T08: mean baseline, SLR/MLR, hệ số, train/CV | T09: Polynomial bậc thấp và Ridge, bậc/alpha qua CV | Hai bảng CV cùng schema/folds/thang giá; test chưa dùng tune |
| Sau T08–T09 | T10 chung; notebook cuối; phần report A | T10 chung; T11 residual, lỗi theo city/room/day, case có truy vết | Chốt mô hình trước, test một giao thức; residual = actual−predicted |
| Mục tiêu 14/10 | T12/T14, demo T16, tích hợp và kiểm T17 | T13/T15, đối chiếu số liệu/video và kiểm T17 | Word/PDF/slide/code/data đồng nhất; minh bạch AI; đủ video nếu online |
| 14–15/10 | T18 chung, sửa lỗi và nộp đúng giờ LMS | T18 chung, kiểm phần mình nói và bộ nộp | Hoàn thành thật trước nộp; không tự giả định gia hạn |

Ngày **15/10/2026** là mốc cuối thầy nói trong Buổi 10; giờ đóng cổng và thay đổi LMS chưa xác minh. Lịch trên là kế hoạch phục hồi từ ngày review, không khẳng định các mốc cũ đã hoàn thành. Không thêm dashboard/RF/XGBoost khi phần lõi và hồ sơ còn thiếu; giảm số hình/cấu hình phụ nếu thiếu thời gian, giữ đánh giá và minh bạch đúng.

## 6. Toàn bộ trách nhiệm B cần theo dõi

| Loại trách nhiệm | Task của B |
|---|---|
| B phụ trách chính | **T05, T06, T09, T11, T13, T15** |
| B cùng A quyết định/thực hiện | **T01, T07, T10, T17, T18** |
| B kiểm tra đầu ra của A | **T02, T03, T04, T08, T12, T14, T16** |

T13/T15 có thể dựng dàn ý trong lúc chờ mô hình, nhưng không điền metric hoặc kết luận chưa chạy. T11 cần output T10; T09 cần T07; T15 bản cuối cần nội dung T12–T14 đã đối chiếu. B cần tham gia demo/phần nói của mình theo T16/T18, không chỉ làm slide im lặng.

Đầu ra T08/T09 nên thống nhất: `model_id`, cấu hình, tên tập biến, protocol/split ID, train metric, CV MSE/RMSE/MAE/R² và độ biến thiên phù hợp. Test metric/predictions để mốc T10; các file prediction cuối phải có mã dòng, actual, predicted và split. B dùng chúng cho residual/case study, không fit `residplot` đơn biến rồi gán đó là phần dư của MLR.

## 7. Checklist nhận bàn giao ngắn

- [x] Pull thành công và ghi commit review.
- [x] Đã đọc toàn bộ cell source, kiểm 7 bảng, xem 3 hình.
- [x] Đã chạy sạch 18/18 cell trên bản sao; 7 bảng tái sinh khớp bản commit.
- [x] File gộp đủ 51.707×24, không bị cap/log/scaling; B có thể bắt đầu EDA.
- [ ] A sửa PASS/audit, metadata quá mức và wording log/bin/hình trước nghiệm thu cuối.
- [ ] A+B cung cấp/chốt minh bạch T01, thông tin nhóm và giờ LMS.
- [ ] B hoàn thành T05–T06 với bảng/hình/nhận xét thực tế.
- [ ] A+B khóa T07 và cùng split/folds/predictor; sau đó A T08 / B T09.
- [ ] T10–T18 hoàn tất, mọi số liệu khớp lần chạy chốt và hồ sơ đúng mẫu.

Không chuyển các checkbox còn trống thành “Hoàn thành” chỉ vì báo cáo review hoặc notebook 01 đã chạy được. Nghiệm thu số liệu hiện tại và sửa chất lượng diễn giải là hai việc riêng cần hoàn tất.
