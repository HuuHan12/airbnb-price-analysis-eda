# B bàn giao sau khi nhận code A — 13/10/2026

Đã pull đến ff08a22. B hoàn tất T11: Notebook 05, ba hình b_08–b_10, bảng lỗi nhóm, 10 case có khóa nguồn, kết luận thực tế. Chạy sạch kernel mới, 15 kiểm tra đạt gồm 6 đầu vào hỏng bị từ chối.

## A có thể làm tiếp ngay

1. T03/T04: sửa metadata WGS84/studio/metro làm tròn và assert skew<1/nhãn biên còn được ghi trong A_RECHECK_20261013.json. Các vấn đề này chưa được coi là hoàn thành chỉ vì T08/T10 đã xong.
2. T12: dùng Template_IE313.docx, tích hợp REPORT_B_SECTIONS.md với phần nguồn/dữ liệu/phương pháp/hệ số của A. Bảng CV/test dùng model_comparison_cv_vs_test.csv; phần dư dùng b_residual_findings.md. Chọn hình, caption và giải thích, không chép toàn bộ ghi chú kỹ thuật vào report.
3. T14: chốt thông tin nhóm thật, nguồn/AI thực tế, TLTK/phụ lục đóng góp thật. Phần B có Codex hỗ trợ; không tự khai không dùng AI hay phần trăm đóng góp.
4. T16: tích hợp notebook cuối từ 01–05. Giữ nguyên config/manifest và chọn bằng CV; demo mở kết quả, không tune lại test hay train grid khi đang trình bày.
5. Phối hợp T15/T17/T18: tạo PPTX từ dàn ý đã cập nhật, soát khớp Word/PDF/slide/code/data, diễn tập 10+5 phút và quay đủ hai người nếu online.

## B còn tham gia

B đọc chéo report, kiểm số liệu/caption, soát PPTX, tập nói/kịch bản phần mình và demo, cùng kiểm bộ nộp. T13/T15 đang làm vì thiếu bản tích hợp cuối; phần phân tích cần để A tiếp tục đã đủ.

## Các phát hiện cần nói đúng

M3 test R² 0,1912, RMSE 311,70, MAE 102,02. 1% mẫu lỗi lớn chiếm 86,08% SSE; 167 dự đoán âm được giữ nguyên. Không cắt dự đoán về 0 hoặc loại giá cao sau khi nhìn test. Đã sửa generator T10: CV MSE/baseline MSE không thay phương sai, gần metric Ridge/OLS không chứng minh định lý, thiếu listing ID nên không khẳng định mẫu độc lập theo listing. Không suy ra nhân quả, gian lận hay chất lượng dữ liệu từ residual.

## Chạy phần B mới

```text
python scripts/run_residual_notebook.py
python scripts/verify_residual_analysis.py
```

Môi trường chung requirements-b.txt. Python module không fit lại mô hình; dự đoán được kiểm theo source_file/source_row và dữ liệu holdout trước phân tích.
