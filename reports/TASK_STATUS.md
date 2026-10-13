# Trạng thái task A/B — 13/10/2026

Nguồn: commit A `1fd2f5a`, notebook A chạy sạch 18 cell; hai notebook B, 24 kiểm tra gói B. Đây là review nhóm, không nghiệm thu giảng viên.

**A làm tiếp T08 ngay sau nhận T07.** Dùng HANDOFF_B_TO_A.md, cùng config/manifest/folds; T09 B đã có nhưng chưa dùng test.

| Task | Trạng thái | Minh chứng | Việc còn lại |
|---|---|---|---|
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
| T11 | Sẵn sàng bắt đầu | test_predictions.csv đã sẵn sàng (51.710 dòng) | B sẵn sàng vẽ biểu đồ phần dư đa biến (residual plot), lỗi theo nhóm city/room và case study. |
| T12 | Chưa bắt đầu | Chờ report Word trong template | A có thể viết dữ liệu/phương pháp ngay; chưa có bản report phần A trong repo. |
| T13 | Đang làm | eda_findings.md; b_model_findings.md | Đã có nội dung EDA/CV thật; chờ T08/T10 cho so sánh, test và kết luận cuối. |
| T14 | Chưa bắt đầu | Chờ TLTK/phụ lục report cuối | A chốt nguồn/AI thật, style và nhiệm vụ từng người; không ghi đóng góp giả. |
| T15 | Đang làm | SLIDE_OUTLINE_B.md | Đã có dàn ý 13 slide/kịch bản; chưa có PPTX cuối, cần T08/T10 và thông tin nhóm. |
| T16 | Chưa bắt đầu | Chờ notebook cuối và demo | A tích hợp và chạy sẵn; B có phần trình bày chuyên môn; chưa có demo cuối. |
| T17 | Chưa bắt đầu | b_verification.json chỉ kiểm gói B | 24 kiểm tra B đạt không thay nghiệm thu bộ nộp Word/PDF/slide/code/data. |
| T18 | Chưa bắt đầu | Chờ bộ nộp T17 | Chưa có bằng chứng diễn tập/video đủ cả hai người; mục tiêu 10+5 phút. |

Excel đồng bộ: `reports/PHAN_CONG_2_NGUOI_IE313.xlsx`. T01–T04 được đánh dấu theo review mới, không giữ “Hoàn thành” chỉ vì tracker cũ đã chọn. T07 là giao thức đã sẵn sàng để A review, không phải đang chờ B viết thêm.
