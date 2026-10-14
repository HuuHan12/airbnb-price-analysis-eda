# IE313 — Phân tích giá Airbnb tại 10 thành phố châu Âu

## Notebook trình bày đồ án

Mở **[notebooks/IE313_Airbnb_Final.ipynb](notebooks/IE313_Airbnb_Final.ipynb)** và chọn **Restart Kernel and Run All**. Theo yêu cầu thầy do nhóm cập nhật ngày 14/10/2026, toàn bộ dự án được trình bày trong một notebook này.

Notebook gồm kiểm kê/nạp dữ liệu, dictionary, audit/IQR, thống kê và EDA, Pearson/ANOVA, giao thức train/CV/test, M0–M4, hệ số hồi quy, đánh giá holdout, phần dư/lỗi nhóm/case truy nguồn và kết luận. Code xử lý nằm trực tiếp trong file, không cần chạy notebook khác hoặc import `src`. Các notebook 01–06 là tài liệu phát triển để truy vết.

### Chạy trên máy mới

Từ thư mục repo, tạo môi trường Python phù hợp với các phiên bản đã kiểm trong `requirements-b.txt` (môi trường nhóm đang dùng Python 3.12). Cài thư viện và mở notebook bằng Jupyter/VS Code:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-b.txt
```

Cần giữ `data/raw/` (20 CSV), `data/processed/airbnb_combined.csv`, `data/processed/split_manifest.csv` và `config/experiment_config.json` trong repo. Notebook nạp lại CSV gốc và đối chiếu dữ liệu gộp/hash/split; không phụ thuộc model đã lưu hay output cũ để tính kết quả. Nếu bảng T10 cũ có sẵn, nó được dùng thêm để kiểm tái lập metric ở cell cuối.

Để chạy và kiểm tự động từ kernel mới:

```powershell
python scripts/run_final_notebook.py
```

Script lưu output vào notebook và `outputs/final_notebook/`; nhật ký ở `reports/final_notebook_runs.json`. File script `build_final_notebook.py` dùng khi cần xây lại nội dung notebook từ code/metadata đã review, không cần chạy trước mỗi lần demo.

### Nội dung và giới hạn

- Dữ liệu: 51.707 quan sát, 20 cột gốc, thêm bốn cột city/day/file/dòng để nhóm và truy vết. Nguồn README ghi Kaggle/The Devastator. Giá dùng nguyên `realSum`, EUR theo README; kỳ giá chưa được metadata gốc xác minh, không quy đổi giá/đêm.
- Phân tích: n/mean/median/IQR và cơ cấu nhóm; hai nhóm ngày không được coi là cùng listing. Pearson/ANOVA mô tả liên hệ kèm giả định và giới hạn, không kết luận nhân quả.
- Mô hình: M0 trung bình, M1 tuyến tính sức chứa, M2 tuyến tính đa biến, M3 đa thức bậc 2/3 trên ba biến, M4 Ridge. Không có Random Forest/XGBoost trong phần môn học hiện tại.
- Giao thức `ie313_raw_v1_seed0_cv5`: 41.365 train, 10.342 test; 5-fold CV trong train; preprocessing trong Pipeline; chọn cấu hình bằng CV MSE. Target và ngoại lệ giữ nguyên, không chỉnh theo test.
- M3 bậc 3 được chọn bằng CV: test RMSE 311,70; MAE 102,02; R² 0,1912. Đây là kết quả trên bộ dữ liệu cung cấp; sai số lớn không chứng minh gian lận hay định giá sai.

## Phân công và sản phẩm

Hàn (A) chủ trì dữ liệu/audit và M0–M2; Huy (B) chủ trì EDA/Pearson/ANOVA, M3–M4, phần dư và bản thảo kết quả/slide. Cả hai cùng giao thức, test, notebook cuối và kiểm bộ nộp. Xem `reports/TASK_STATUS.md`, `reports/HANDOFF_HUY_TO_HAN.md` và `reports/PHAN_CONG_2_NGUOI_IE313.xlsx` để đối chiếu việc thực tế; workbook có thể cần đồng bộ với cập nhật markdown mới.

Quy tắc theo source môn: `Skill/SKILL.md`. Word/PDF/PPTX nằm trong `reports/deliverables/`. Yêu cầu một notebook trình bày không thay thế các file báo cáo/slide/data phải nộp riêng. Thông tin nhóm/MSSV/giờ LMS, kiểm trên máy Hàn và diễn tập thực tế vẫn phải do nhóm xác nhận.
