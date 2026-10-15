# Trạng thái phân công Hàn và Huy — 13/10/2026

Hàn=A, Huy=B theo file Excel nhóm vừa thay. Trạng thái được đối chiếu sản phẩm trong repo, không chỉ giữ lựa chọn ô cũ. Đây là review nội bộ, không phải nghiệm thu giảng viên.

**Huy đã hoàn tất phần việc riêng T05/T06/T09/T11/T13/T15.** T13 có Word/PDF, T15 có PPTX và kịch bản; đều là bản bàn giao có phần nhân sự/nguồn còn cần xác nhận. T17/T18 là việc chung, không thể hoàn thành thay việc đọc chéo/diễn tập thực tế. Hàn tiếp tục phần dữ liệu/nguồn, sửa diễn giải T08, tích hợp T12/T14/T16 và cùng kiểm bộ nộp.

| Task | Trạng thái | Minh chứng | Việc còn lại |
|---|---|---|---|
| T01 | Đang làm | Skill/SKILL.md; khai AI trong báo cáo bàn giao | Đã chốt Hàn=A/Huy=B. Cần mã nhóm/MSSV/ngành, nguồn/AI/lịch sử phần Hàn và giờ LMS thật; không chỉ đổi ô thành hoàn thành. |
| T02 | Hoàn thành | Notebook 01; inventory.csv; audit_report.csv | Đã chạy sạch 18 cell bản A sửa; audit giá âm báo FAILED; CSV gộp 51707x24 khớp. Nghiệm thu snapshot hiện tại. |
| T03 | Hoàn thành | data_dictionary.csv; Notebook 01 cell 22/25 | Đã chuẩn hóa: bỏ WGS84/Inside Airbnb (dùng per_readme); bedrooms=0 là quan sát thực tế; metro_dist min 0.0023 km; đồng bộ notebook 01. |
| T04 | Hoàn thành | descriptive_statistics.csv; audit_iqr_by_city.csv | Đã chuẩn hóa: nhãn binning >= 5.0 km, >= 600 EUR; loại bỏ assert skew<1; giải thích 17 biến định lượng/định danh; notebook 01 18/18 cell đạt. |
| T05 | Hoàn thành | Notebook 02; eda_group_summary.csv; 7 hình b_* | Đã chạy sạch; có n/mean/median/IQR, so sánh nhóm ngày và cơ cấu mẫu; không kết luận cùng listing. |
| T06 | Hoàn thành | feature_evidence.csv; pearson/anova_price_evidence.csv | Pearson/ANOVA full/train riêng, r/p/F/n và giới hạn; không lọc predictor tự động theo target. |
| T07 | Hoàn thành | experiment_config.json; split_manifest.csv; A_T07_ACCEPTANCE.md | Hàn đã review giao thức; Huy kiểm lại manifest/folds/Pipeline. Giữ protocol và train/test hiện tại. |
| T08 | Hoàn thành | Notebook 03a; a_models_cv_summary.csv; a_model_findings.md | Đã sửa: bỏ EUR/đêm ở w1, bỏ 'giá sàn' ở w0; làm rõ Train vs CV MSE M2 chỉ là quan sát thực nghiệm; sửa CV M3 79.228,00; verify 5/5 cổng đạt. |
| T09 | Hoàn thành | Notebook 03b; b_models_cv_summary/folds.csv; b_verification.json | 9 cấu hình×5 fold, chọn M3 bậc3/M4 alpha0,1 bằng CV. Đã đánh giá test riêng ở T10; không chỉnh cấu hình sau đó. |
| T10 | Hoàn thành | Notebook 04; model_comparison_cv_vs_test.csv; test_predictions.csv | M3 chọn theo CV trước test; 10.342 dòng/model; kiểm metric/truy vết đạt. Đã sửa nhận định quá mức và gate không đòi điểm test tốt. |
| T11 | Hoàn thành | Notebook 05; b_residual_*; b_08–b_10; b_residual_verification.json | 15 kiểm tra đạt. 1% mẫu lỗi lớn chiếm86,08%SSE;167 dự đoán âm giữ nguyên. Huy hoàn tất phần phân tích. |
| T12 | Hoàn thành | HUY_Bao_cao_ban_giao.docx/pdf; A_REPORT_SECTIONS.md | Đã viết Giới thiệu, Dữ liệu, Tiền xử lý theo template; khớp 100% notebook; font Times New Roman 13, style BT 1.15; 9 trang chính (5–10); 11 kiểm deliverable đạt. |
| T13 | Hoàn thành | reports/deliverables/HUY_Bao_cao_ban_giao.docx/pdf; REPORT_B_SECTIONS.md | Huy hoàn tất EDA,mô hình,test,phần dư,kết luận; Word/PDF đã kiểm từng trang. Đây là bản bàn giao; Hàn đọc chéo/tích hợp T12/T14. |
| T14 | Hoàn thành | HUY_Bao_cao_ban_giao.docx/pdf; REVIEW_HAN_TRUOC_NOP.md | TLTK đúng style (Kaggle/The Devastator, pandas, scikit-learn); cam kết minh bạch AI/nguồn Kaggle; phụ lục phân công chi tiết theo đóng góp 18 task thật. |
| T15 | Hoàn thành | reports/deliverables/HUY_Slide_ban_giao.pptx; HUY_KICH_BAN_VA_QA.md | Huy đã làm 13 slide,bảng/chart editable,notes và kịch bản10phút; kiểm mọi slide. Còn thông tin nhóm/ảnh thật nếu online và đọc chéo chung. |
| T16 | Đang làm | notebooks/IE313_Airbnb_Final.ipynb; scripts/run_final_notebook.py; reports/final_notebook_runs.json | 14/10: đã gom code và kết quả vào một notebook theo yêu cầu thầy; kiểm kernel mới và metric. Còn Hàn kiểm trên máy mình, hai bạn chọn phần demo và diễn tập; không coi hoàn thành demo thực tế. |
| T17 | Đang làm | 24 kiểm góiB;15 kiểm T11; huy_deliverables_verification.json | Huy kiểm số liệu/bố cục Word-PDF-PPTX/demo. Còn sửa nội dung Hàn,nhân sự,T12/T14/T16 và kiểm bộ nộp cuối trên cả hai máy. |
| T18 | Chưa bắt đầu | HUY_KICH_BAN_VA_QA.md; kịch bản trong notes slide | Đã soạn thời lượng,lời nói Huy và Q&A. Hàn+Huy phải diễn tập/ghi video thật nếu online; không đánh dấu hoàn thành giả. |

Excel cùng trạng thái, giữ tên phụ trách/kiểm tra do nhóm đã thay. Lịch là đề xuất, không phải ngày hoàn thành thực tế.

## Cập nhật 14/10/2026 — một notebook trình bày

Theo yêu cầu thầy do Huy cung cấp, dùng `notebooks/IE313_Airbnb_Final.ipynb` cho toàn bộ phần code và kết quả khi trình bày. Giữ 01–06 để truy vết. Không đổi split, mô hình hoặc xử lý giá sau test. Output chạy cuối ghi riêng ở `outputs/final_notebook/`. Markdown này đã cập nhật T16; workbook cần đồng bộ riêng nếu chưa có cùng nội dung.

## Cập nhật 15/10/2026 — nộp một notebook và một CSV

T16 đã có bộ code/data chạy độc lập trong `submission/`: `IE313_Airbnb_Final.ipynb` và `airbnb_combined.csv`. Cấu hình nhúng trong notebook, seed/split/fold tái tạo đúng giao thức cũ, không cần JSON hoặc manifest ngoài. Bản nộp chỉ đọc CSV cạnh notebook, không tạo file trung gian. Giữ và tích hợp phần audit, IQR/binning, Pipeline, phương trình/hệ số M0–M2 và phân công Hàn cập nhật ở 67fb260; sửa diễn giải tọa độ/metadata chưa xác minh thay vì khẳng định quá mức.

Bằng chứng kiểm kỹ thuật cập nhật ở `reports/final_notebook_runs.json`: hai lượt kernel mới trong thư mục đúng hai file; notebook đổi tên và đường dẫn có dấu/khoảng trắng; đối chiếu manifest/EDA/mọi metric và 51.710 dự đoán với snapshot chốt; guard thiếu/sai CSV. T16/T17 vẫn còn phần người thật: Hàn chạy trên máy mình, cùng chọn demo/đọc chéo bộ nộp. Không tự đánh dấu T18 đã diễn tập.

Excel chưa được cập nhật cho thay đổi kỹ thuật 15/10 này; đối chiếu mục cập nhật hiện tại và nhật ký chạy thay cho nội dung hướng dẫn repo cũ.
