# Huy bàn giao cho Hàn

Ngày 13/10/2026. File phân công mới xác nhận Hàn=A/Huy=B; cập nhật giữ nguyên cột người phụ trách/người kiểm tra của nhóm.

## Sản phẩm Huy đã có

| Nhiệm vụ riêng | Sản phẩm và bằng chứng |
|---|---|
| T05/T06 | Notebook02, bảng EDA/Pearson/ANOVA và7hình; kiểm góiB24mục đạt. |
| T09 | Notebook03b,9cấu hình×5fold, M3degree3/M4alpha0,1 theoCV; mô hình train-only. |
| T11 | Notebook05, phần dư/lỗi nhóm/10case/3hình;15kiểm tra đạt, giữ mọi mẫu test. |
| T13 | reports/deliverables/HUY_Bao_cao_ban_giao.docx và PDF: nội dung EDA,mô hình,test,phần dư,kết luận đầy đủ.9trang nội dung chính,12trang tổng dự kiến sau xuất Word; số thực tế ghi trong huy_deliverables_verification.json. |
| T15 | reports/deliverables/HUY_Slide_ban_giao.pptx:13slide,8bảng editable,1chart editable có workbook nhúng, notes; kịch bản9phút30giây vàQ&A. |

Huy còn bàn giao Notebook06 demo kết quả đã chạy sạch3cell, chỉ đọc và kiểm truy vết, không fit/tune lại. Đây là phần chuẩn bị cho T16 của Hàn, không tự đánh dấu đã demo/diễn tập.

## Hàn làm nốt theo thứ tự

1. Đọc REVIEW_HAN_TRUOC_NOP.md, sửa T03/T04/T08 metadata và diễn giải trong generator/output/notebook. Không đổi giao thức hoặc nhìn test để tune.
2. T12: mở Word bàn giao từ template, review và hoàn thiện phần nguồn/dữ liệu/tiền xử lý/phương pháp của Hàn. Nội dung phân tích Huy đã hoàn tất; không chờ Huy có thêm test/residual.
3. T14: xác nhận tên đầy đủ,MSSV,ngành,mã nhóm/hệ học; nguồn/AI/lịch sử dùng dự án thực tế. Hoàn thiện TLTK đúng style và ngày truy cập thật; không bịa tác giả/ngày hoặc tự ghi50/50.
4. T16: tích hợp notebook cuối và hướng dẫn chạy, mở sẵn output. Có thể dùng Notebook06 làm phần demo kết quả; không train grid khi đang thuyết trình.
5. T17: cùng Huy kiểm Word/PDF/PPTX/code/data cuối trên hai máy, cập nhật thông tin nhóm ở slide1/2, thêm ảnh thật nếu online, xóa ghi chú chờ xác nhận khỏi bản nộp sau xác nhận xong.
6. T18: cùng Huy diễn tập10+5phút, hỏi chéo và ghi video đủ mặt động nếuonline. Kịch bản đã có; không coi việc có kịch bản là diễn tập thật.

## Phạm vi hoàn thành

“Hoàn thành” T13/T15 nghĩa là Huy đã giao đủ sản phẩm phần mình. T12/T14/T16 và các việc chung chưa hoàn thành; Word/PDF/PPTX hiện là bản bàn giao có metadata/nguồn cần xác nhận, chưa phải file nộp. Tên file cuối phải bắt đầu bằng mã nhóm thật do Hàn chốt. Không nộp ZIP thay từngfile hoặc dùng linkDrive cho toàn bộ sản phẩm.

Huy sẽ cùng đọc chéo và trình bày phần mình; không chuyển diễn tập của Huy sang cho Hàn làm thay. Chỉ người thật có thể xác nhận phần diễn tập/video.

## Chạy và kiểm phần Huy

```text
python scripts/verify_b_handoff.py --checked-on 2026-10-13
python scripts/verify_residual_analysis.py
python scripts/run_huy_demo.py
python scripts/verify_huy_deliverables.py
```

Môi trường khoa học dùng requirements-b.txt. Script kiểm báo cáo/slide dùng Python stdlib và pypdf (requirements-artifact-review.txt); không cần python-docx để chạy kiểm. Chạy lại toàn bộ để nộp thuộc T17, không thay bằng log cũ.

## Cập nhật 14/10 — trình bày toàn dự án bằng một notebook

Dùng `notebooks/IE313_Airbnb_Final.ipynb` thay việc mở nhiều notebook khi trình bày. Notebook chứa code dữ liệu/audit/dictionary/IQR/binning, EDA/Pearson/ANOVA, Pipeline và CV M0–M4, test, phần dư/case và kết luận; không import src hoặc cần chạy 01–06 trước. Không thay mô hình hay giao thức đã chốt. Output cuối ghi riêng để bảo toàn các sản phẩm trước.

Hàn pull bản này, mở notebook, kiểm `Restart Kernel and Run All` trên máy mình (hoặc `python scripts/run_final_notebook.py`), rồi cùng Huy chọn bảng/hình để demo và hỏi chéo code. Nhật ký kernel mới ở `reports/final_notebook_runs.json`; README đã đổi sang nội dung thực tế của đồ án. Các thông tin trạng thái trước 14/10 ở trên là lịch sử bàn giao; đối chiếu `TASK_STATUS.md` hiện tại cho phần Hàn đã sửa. Chưa xác nhận thay hai bạn việc diễn tập, metadata nhân sự hoặc giờ nộp LMS.

## Cập nhật 15/10 — bộ code/data đúng hai file

Phần hướng dẫn này thay hướng dẫn chạy trong repo ở các bản bàn giao trước. Nộp riêng hai file trong `submission/`: `IE313_Airbnb_Final.ipynb` và `airbnb_combined.csv`. Không chọn file `split_manifest.csv` hoặc config JSON để thêm vào bộ này. Cấu hình và tái tạo split/fold nằm trong notebook; không yêu cầu src, raw, model hay output ngoài. Notebook không ghi file trung gian. Dùng `reports/final_notebook_runs.json` để đọc bằng chứng kiểm mới; đây là nhật ký nội bộ, không phải file thứ ba cần nộp.

Hàn chỉ cần tải/copy đúng hai file vào một thư mục và Restart Kernel and Run All trong thư mục đó, với môi trường có thư viện ghi đầu notebook. Bản notebooks/ cũng có CSV đặt cạnh. Hai bạn vẫn cần kiểm máy Hàn, metadata nhóm, bộ báo cáo/slide/video và nộp trực tiếp từng sản phẩm; không coi kiểm tự động là diễn tập thực tế.
