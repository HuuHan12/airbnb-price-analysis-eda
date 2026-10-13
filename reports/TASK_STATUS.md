# Trạng thái task A/B — 13/10/2026

Đã pull A đến `ff08a22`. T08/T10 có sản phẩm; T11 B đã chạy kernel mới và đạt 15 kiểm tra snapshot/đầu vào hỏng. Đây là review nội bộ, không phải nghiệm thu giảng viên.

**A làm tiếp T03/T04 còn vướng và T12/T14/T16; phần phân tích B T05/T06/T09/T11 đã có.** T13/T15 đang làm vì còn tích hợp báo cáo/slide cuối và đọc chéo, không phải thiếu kết quả test của B.

| Task | Trạng thái | Minh chứng | Việc còn lại |
|---|---|---|---|
| Task | Trạng thái | Minh chứng | Việc còn lại |
| T01 | Đang làm | Notebook 01 mục minh bạch; Skill/KE_HOACH_DO_AN_IE313.md | Đã bổ sung nguồn/AI; cần xác minh nguồn Inside Airbnb, công cụ thực tế, tên/MSSV/mã nhóm và giờ LMS. |
| T02 | Hoàn thành | Notebook 01; inventory.csv; audit_report.csv | Đã chạy sạch 18 cell bản A sửa; audit giá âm báo FAILED; CSV gộp 51707x24 khớp. Nghiệm thu snapshot hiện tại. |
| T03 | Cần sửa | data_dictionary.csv; Notebook 01 cell 22/25 | Đủ 24 biến; còn WGS84, studio, metro làm tròn và metadata suy diễn. Không chặn B/A dùng CSV đã kiểm. |
| T04 | Cần sửa | descriptive_statistics.csv; audit_iqr_by_city.csv | Số liệu đúng, log wording đã sửa; còn assert skew<1, nhãn >=5/>5, >=600/>600, 17 numeric gồm ID/cờ. |
| T05 | Hoàn thành | Notebook 02; eda_group_summary.csv; 7 hình b_* | Đã chạy sạch; có n/mean/median/IQR, so sánh nhóm ngày và cơ cấu mẫu; không kết luận cùng listing. |
| T06 | Hoàn thành | feature_evidence.csv; pearson/anova_price_evidence.csv | Pearson/ANOVA full/train riêng, r/p/F/n và giới hạn; không lọc predictor tự động theo target. |
| T07 | Hoàn thành | experiment_config.json; split_manifest.csv; experiment.py; verify_a_t07.py; A_T07_ACCEPTANCE.md | A đã kiểm toán 5 cổng (100% PASSED) và nghiệm thu chính thức; sẵn sàng làm T08. |
| T08 | Hoàn thành | Notebook 03a; a_models_cv_summary.csv; a_models_cv_folds.csv; fig_04; fig_05; A_T08_ACCEPTANCE.md | A đã hoàn thành 5-fold CV cho M0, M1, M2; trích xuất phương trình, hệ số; kiểm toán 5 cổng đạt 100% PASSED. |
| T09 | Hoàn thành | Notebook 03b; b_models_cv_summary/folds.csv | 9 cấu hình x5 folds; M3 bậc 3, M4 alpha 0.1 theo CV; lưu train-only, chưa đánh giá test. |
| T10 | Hoàn thành | Notebook 04; model_comparison_cv_vs_test.csv; test_predictions.csv; fig_06; fig_07; A_B_T10_ACCEPTANCE.md | Chốt M3 chiến thắng trên CV; mở khóa đánh giá 10.342 mẫu test; kiểm toán 5 cổng đạt 100% PASSED. |
| T11 | Hoàn thành | Notebook 05; b_residual_*; b_08–b_10; b_residual_verification.json | Kernel mới 3 cell; 15 kiểm tra đạt. 1% mẫu chiếm 86,08% SSE; 167 dự đoán âm giữ nguyên. A dùng để tích hợp report/demo. |
| T12 | Chưa bắt đầu | Chờ report Word trong template | A có thể viết dữ liệu/phương pháp ngay; chưa có bản report phần A trong repo. |
| T13 | Đang làm | REPORT_B_SECTIONS.md; b_residual_findings.md; bảng CV/test thật | B hoàn tất nội dung EDA, CV, test, phần dư và kết luận. Chờ A tích hợp template Word/PDF và đọc chéo; không chờ B phân tích thêm. |
| T14 | Chưa bắt đầu | Chờ TLTK/phụ lục report cuối | A chốt nguồn/AI thật, style và nhiệm vụ từng người; không ghi đóng góp giả. |
| T15 | Đang làm | SLIDE_OUTLINE_B.md cập nhật đủ T08/T10/T11 và lời nói B | B đã cập nhật nội dung/kịch bản kết quả. Chưa có PPTX cuối; còn thông tin nhóm, tích hợp, kiểm bố cục và diễn tập. |
| T16 | Chưa bắt đầu | Notebook 01–05; NEXT_STEPS_A_20261013.md | A tích hợp notebook cuối và chạy sạch; B đã có phần dư/kịch bản demo. Chưa hoàn tất demo cả nhóm. |
| T17 | Chưa bắt đầu | b_verification.json chỉ kiểm gói B | 24 kiểm tra B đạt không thay nghiệm thu bộ nộp Word/PDF/slide/code/data. |
| T18 | Chưa bắt đầu | Chờ bộ nộp T17 | Chưa có bằng chứng diễn tập/video đủ cả hai người; mục tiêu 10+5 phút. |

Excel đồng bộ cùng trạng thái; lịch 08–15/10 là đề xuất, không phải ngày hoàn thành thực tế.
