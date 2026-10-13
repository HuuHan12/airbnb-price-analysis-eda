# Huy đọc chéo phần Hàn trước tích hợp cuối

Snapshot sau d2e0299, kiểm ngày 13/10/2026. Nguồn chỉ từ repo và tài liệu môn; đây là review nội bộ, không phải nghiệm thu giảng viên. Code T08/T10 đã có số liệu chạy; các lỗi dưới nằm ở metadata hoặc cách diễn giải, cần sửa cả generator lẫn output/notebook để chạy lại không sinh lỗi cũ.

| Task | Vị trí | Cần sửa và lý do |
|---|---|---|
| T01/T03 | Notebook 01; data_dictionary.csv | Không xác nhận Inside Airbnb/WGS84 nếu chưa có nguồn gốc; bedrooms=0 là giá trị quan sát, không tự gọi studio; metro_dist nhỏ làm tròn0 không phải bằng0. |
| T04 | Notebook 01; descriptive_statistics.csv; A_RECHECK_20261013.json | Rà assert skew<1, nhãn >5/>600 nhưng đếm>=, số biến numeric gồm ID/cờ. Không gọi tất cả numeric là thuộc tính dự báo liên tục. |
| T08 | src/a_tasks.py; reports/a_model_findings.md; Notebook03a | Bỏ đơn vị EUR/đêm khỏi hệ số M1 vì kỳ giá chưa xác minh. Hệ số góc theo đơn vị realSum và một đơn vị sức chứa. |
| T08 | src/a_tasks.py, đoạn hệ số chặn M1 | Sức chứa0 ngoài miền quan sát; hệ số chặn không phải chi phí cố định tối thiểu hoặc giá sàn. |
| T08 | src/a_tasks.py, nhận xét train/CV | Chênh train/CV nhỏ không chứng minh không overfit hoặc tổng quát hóa cao. Báo quan sát có giới hạn, CV không chứng minh xác thực bên ngoài. |
| T08 | src/a_tasks.py, hệ số M2 | Hệ số city dummy không gọi là chuẩn hóa như biến số; hệ số dist/city không chứng minh quy luật hay nhân quả. Numeric scaler có đơn vị theo1SD, hệ số gốc phải quy đổi đúng. |
| T08 | src/a_tasks.py, bàn giao M3 | CV MSE M3 là79.228,00, không phải79.227,00; lấy số từ bảng. M3−M2 chênh≈760,15. |
| T12/T14 | Word bàn giao | Nội dung phần Huy đã có. Hàn review/hoàn thiện nguồn,data dictionary,phương pháp/TLTK/AI và nhân sự. Dùng đúng template; xóa các câu chờ xác nhận ở bản cuối sau đã xác nhận thật. |
| T16/T17 | Notebook cuối / bộ nộp | Tích hợp notebook01–05 và phần demo06 nếu dùng; chạy sạch. Các log kiểm B không thay kiểm toàn bộ bộ nộp cuối. |

Trong Word bàn giao, các nhận định M1/M2 đã được viết theo cách có giới hạn. Hàn có thể dùng phần diễn giải đó sau đối chiếu số liệu của mình. Không cần đổi mô hình hoặc tune lại test để sửa lỗi diễn giải.

T03/T04 và T08 diễn giải được để “Cần sửa” dù Excel thay vào đã chọn hoàn thành: sản phẩm hiện tại còn các vấn đề trên. Số liệu T08/T10 hợp lệ không đồng nghĩa mọi nội dung báo cáo đã đúng.
