# Bàn giao B cho A — T05/T06/T07 và T09

Cập nhật **12/10/2026**, dựa dữ liệu tại commit A `e9eab7f`. **A có thể bắt đầu T08 (M0/M1/M2) sau khi kiểm và nhận giao thức dưới đây.** B không thay notebook 01, dữ liệu raw, file gộp hoặc các bảng/hình A đã làm. Các sản phẩm mới hiện ở working tree local; chưa commit/push lên GitHub, chưa nộp bài hay gửi cho A bằng công cụ liên lạc.

## 1. Trạng thái thật của task

| Task | B đã làm | A cần làm tiếp |
|---|---|---|
| T05 | Notebook 02, 5 cách grouping, count/mean/median/std/IQR, so sánh nhóm ngày theo city và loại phòng; 7 hình EDA | Chạy lại và đọc chéo; chọn hình/nhận xét phù hợp cho report |
| T06 | Pearson r/p/n gộp và trong city; ANOVA F/p và chi tiết nhóm; scope full/train riêng; bảng feature_evidence và giới hạn | Kiểm cách hiểu biến, scope và giả định; không tự lọc toàn bộ theo r/p |
| T07 | Config/manifest/folds/pipeline chung đã triển khai và kiểm tra | A review và dùng đúng giao thức; nếu muốn đổi phải đổi có phiên bản và chạy lại cả A/B |
| T09 | Đã chạy 9 cấu hình ×5 folds, chọn trong mỗi family bằng CV MSE; lưu model fit chỉ train | Dùng output B so với T08; chưa đánh giá test trước chốt mô hình |
| T13 | Có nội dung EDA và phần mô hình/CV từ kết quả thật trong `eda_findings.md` và `b_model_findings.md` | Chờ T08/T10 để hoàn tất so sánh/test/kết luận, ghép vào Word template |
| T15 | Có dàn ý 13 slide/kịch bản chia A+B trong `SLIDE_OUTLINE_B.md` | Chờ số liệu T08/T10 và thông tin nhóm để tạo/chốt slide cuối |
| T11 | Chưa làm kết quả phần dư vì chưa có T10 | Sau T10, bàn giao predictions đúng schema để B làm residual/lỗi nhóm/case |

T01 vẫn cần hai bạn chốt tên/MSSV/mã nhóm, hệ học, minh bạch nguồn/AI và giờ LMS. Các lỗi audit/diễn giải notebook 01 trong review A vẫn cần A sửa trước nghiệm thu cuối; không ngăn dùng CSV hiện tại đã được kiểm chứng.

## 2. Những file A cần mở

- `notebooks/02_exploratory_data_analysis.ipynb`: notebook EDA đã chạy sạch **6 cell code**. Hàm thực hiện trong `src/b_tasks.py`, không dựa kernel notebook 01.
- `notebooks/03b_polynomial_ridge.ipynb`: phần T09 riêng của B, đã chạy sạch **3 cell code**; không sửa chồng notebook mô hình A sẽ viết.
- `config/experiment_config.json`: target, allowlist/exclude, seed, CV, lựa chọn bậc/alpha, policy test, hash.
- `data/processed/split_manifest.csv`: **51.707 dòng**, hai mã truy vết + split + cv_fold; không chứa giá để lựa chọn split.
- `src/experiment.py`: đọc data, nạp manifest, dựng Pipeline M0–M4, đánh giá cùng CV. A dùng M0/M1/M2.
- `outputs/tables/feature_evidence.csv`: r/p/F và n có scope/context; cột `decision` là semantic candidate/mô tả, không bộ lọc học từ y.
- `outputs/tables/b_models_cv_summary.csv` và `b_models_cv_folds.csv`: điểm CV thật và train từng fold.
- `reports/eda_findings.md`, `b_model_findings.md`: nội dung có số liệu để viết report.
- `reports/b_verification.json`: **24 kiểm tra đạt**; script tái kiểm `scripts/verify_b_handoff.py`.
- `requirements-b.txt`: phiên bản môi trường đã chạy, Python 3.12. Không cần cài XGBoost/Plotly cho phần B này.

Các bảng T05/T06 khác: `eda_group_summary.csv`, `eda_sampling_counts.csv`, `eda_day_comparison_by_city.csv`, `eda_day_comparison_by_room.csv`, `eda_correlation_matrix.csv`, `pearson_price_evidence.csv`, `anova_price_evidence.csv`, `anova_group_details.csv`. Tất cả ở `outputs/tables/`. Hình B có tiền tố `b_`, không ghi đè hình A.

## 3. Giao thức A phải dùng để so với B

- Dataset 51.707×24, target **raw realSum**. Không cap, log-target, loại giá cao hoặc scale toàn bộ trước chia tập.
- Train **41.365**, test **10.342**, seed 0 và test_size 0,2. `load_protocol` đọc manifest; không chia lại một lần khác.
- **5 folds**, shuffle seed 0 trên train theo đúng fold lưu. Test có `cv_fold=-1`, không vào CV.
- Numeric: `person_capacity`, `bedrooms`, `dist`, `metro_dist`, `cleanliness_rating`, `guest_satisfaction_overall`.
- Category: `city`, `day_type`, `room_type` — OneHotEncoder drop first, handle_unknown ignore. Boolean: `host_is_superhost`.
- M1: `person_capacity` được ấn định như giả thuyết quy mô từ ý nghĩa, không được chọn bằng cách tìm biến có điểm test đẹp nhất.
- Bỏ ID/truy vết, room flags trùng biểu diễn và các cột target-derived. Core chưa dùng multi/biz/index/tọa độ do metadata/diễn giải chưa rõ; chúng vẫn được mô tả, không có nghĩa đã chứng minh vô ích.
- Allowlist cố định trước so sánh CV; bảng `full_descriptive`/`train_descriptive` phục vụ mô tả, không tự động điều chỉnh tập predictor. Vì vậy không có bộ lọc từ target đứng ngoài các folds.
- Scaler/encoder/poly fit trong Pipeline từng fold. Không tự get_dummies/scale cả data rồi chạy CV.
- Chọn mô hình theo **cv_mse_mean**, xem cùng MAE/RMSE/R² và chênh train/CV. Điểm CV dùng chọn cấu hình không thay thế test độc lập cuối.
- Hash chuẩn hóa LF/CRLF để hai máy cùng CSV không bị khác chỉ do Git đổi xuống dòng. Nếu nội dung data đổi thì module dừng và yêu cầu đối chiếu protocol.

## 4. A bắt đầu T08 bằng đoạn này

Mở notebook mô hình từ `notebooks/`, thêm root vào sys.path. Đoạn dưới **là hướng dẫn cho A**, B chưa chạy bộ CV M0–M2 hay tạo output T08 thay A.

```python
from pathlib import Path
import sys
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(ROOT))
from src.experiment import load_protocol, build_pipeline, evaluate_cv

config, train, _heldout, cv = load_protocol(ROOT)
rows, fold_tables = [], []
for model_id in ['M0', 'M1', 'M2']:
    pipeline = build_pipeline(model_id, config)
    result, fold_result = evaluate_cv(
        pipeline, train, cv, config, model_id, 'base'
    )
    rows.append(result)
    fold_tables.append(fold_result)

pd.DataFrame(rows).to_csv(
    ROOT/'outputs/tables/a_models_cv_summary.csv',
    index=False, encoding='utf-8-sig'
)
pd.concat(fold_tables, ignore_index=True).to_csv(
    ROOT/'outputs/tables/a_models_cv_folds.csv',
    index=False, encoding='utf-8-sig'
)
```

M0 là mean train. M1 không scale để slope/intercept diễn giải trực tiếp theo sức chứa; fit lại trên train sau CV để lấy phương trình. M2 dùng scaler/category trong Pipeline, nên hệ số numeric ở thang chuẩn hóa; nếu diễn giải trên đơn vị gốc, cần chuyển hệ số và intercept đúng theo scaler, không gọi nhầm là EUR/km ngay.

A bổ sung phần giải thích phương trình, chọn biểu diễn và chênh train/CV. Module dùng mảng predictor giới hạn, nên không nhận nhầm `price_tier`, `log_price_temp`, `source_row` dù dataframe trong notebook có thêm các cột đó.

## 5. Kết quả T09 đã có, chưa phải test

- Polynomial M3: **degree 3** trong tập thử 2/3, CV MSE trung bình khoảng **79.228,00**.
- Ridge M4: **alpha 0,1** trong dãy 0,001…1000, CV MSE trung bình khoảng **79.988,15**.
- Polynomial chỉ khai triển 3 numeric capacity/bedrooms/dist, các nhóm/context và numeric còn lại có trong nền chung. Dùng vòng lặp duyệt grid cấu hình + cross_validate với đúng 5 folds (tìm kiếm toàn bộ các cấu hình đã nêu).
- Từng fold có MSE, RMSE, MAE, R² train/validation. CSV summary lưu mean/std; mean(RMSE fold) khác sqrt(mean(MSE fold)).
- Hai model lưu `models/M3_B_train_only.joblib`, `models/M4_B_train_only.joblib`. Chỉ load model do nhóm tự tạo; model chưa thấy test khi fit.
- Chưa có M0–M2 của A để chọn thắng chung. Không kết luận M3 tốt hơn M2 hoặc dự đoán tốt ngoài dataset từ bảng hiện tại.

## 6. Sau T08, A trả gì để B làm tiếp

1. `a_models_cv_summary.csv`, `a_models_cv_folds.csv`, notebook/source T08 chạy từ đầu và phần giải thích hệ số.
2. A+B xem cùng CV MSE rồi ghi rõ model/cấu hình được chọn trước T10. Nếu đổi predictor/target/hyperparameter sau xem test, phải gọi đó là thí nghiệm mới và không trình bày test cũ như độc lập.
3. T10 dùng cùng test đầy đủ, thang realSum gốc; ghi model_id/protocol_id và MSE/RMSE/MAE/R². B chưa chạy hoặc tạo file kết quả T10 trong lượt này.
4. B nhận `test_predictions.csv`: `source_file`, `source_row`, `model_id`, `actual`, `predicted`, `split` (`test`), `protocol_id`. Nên có toàn bộ 10.342 test rows cho từng model đánh giá; không bỏ dòng sai lớn/dự đoán âm trước đánh giá.
5. B nối lại thông tin city/room/day bằng hai mã truy vết, tính residual=`actual-predicted`, biểu đồ fitted–residual, lỗi theo nhóm và case study. Không fit residplot đơn biến rồi nhận là phần dư MLR.

## 7. Cách chạy/kiểm nhận

Từ root repo, tạo môi trường riêng rồi cài:

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-b.txt
```

Mở notebook 02 và 03b bằng kernel của môi trường này, chạy Restart & Run All. Hoặc chạy bằng script không cần mở giao diện Jupyter:

```text
.venv\Scripts\python.exe scripts/run_b_notebooks.py
```

Sau đó:

```text
.venv\Scripts\python.exe scripts/verify_b_handoff.py
```

24 kiểm tra bao gồm: seed split khớp sklearn, mã dòng không chồng, CV validation phủ train đúng một lần, predictor không chứa target, median/Pearson/ANOVA đối chiếu, scaler chỉ fit fold train, extra ID/target-derived không làm đổi prediction, category lạ không gây crash, 9 cấu hình×5fold và phép RMSE²=MSE, model train-only đọc được, notebook không output lỗi. Kiểm category lạ có warning “encoded as all zeros” theo handle_unknown ignore, không phải dữ liệu mới đã được đánh giá.

Đã xem đủ 7 hình B, giữ đầy đủ giá ở box/scatter, ghi thang log và n. Không tự đưa slide bài giảng vào danh mục TLTK cuối; bài giảng vẫn là căn cứ phương pháp trong source nội bộ.

## 8. Thông tin anh có thể báo A

> B đã làm xong T05–T06 và gói giao thức T07, đã chạy T09 Polynomial/Ridge chỉ train/CV. Khi nhận code, bạn đọc reports/HANDOFF_B_TO_A.md, dùng src/experiment.py + config/experiment_config.json + data/processed/split_manifest.csv để làm T08 M0/M1/M2. Không chia lại split, không cap/log target hay tune theo test. Gửi lại a_models_cv_summary.csv, a_models_cv_folds.csv và notebook T08; sau đó cùng chốt mô hình trước T10. Các lỗi audit/metadata notebook 01 trong review vẫn cần sửa trước bản nộp cuối.

Task/điểm không tự coi là nghiệm thu giảng viên. Các thành viên cần hiểu và kiểm code, ghi phần đóng góp thực tế và minh bạch AI đã dùng (Codex hỗ trợ triển khai B trong lượt này). Hạn cuối thầy nêu 15/10/2026; giờ LMS và thông tin nhóm chưa có, không tự điền.
