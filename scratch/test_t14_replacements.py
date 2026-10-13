import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('reports/deliverables/HUY_Bao_cao_ban_giao.docx') as z:
    xml = z.read('word/document.xml').decode('utf-8')

sources = [
    "README khai báo liên kết Kaggle: https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities. Chưa xác minh ngày truy cập Internet hoặc tác giả gốc; Hàn cần hoàn thiện mục này theo nguồn thực tế trước bản nộp.",
    "T02 nạp/audit; T03–T04 có dictionary/thống kê cần sửa; T08 M0–M2; phối hợp T07/T10.",
    "T12 nguồn/dữ liệu/tiền xử lý; T14 nguồn/AI/TLTK/phụ lục; T16 notebook/demo; xác nhận nhân sự và metadata.",
    "T05–T06 EDA/Pearson/ANOVA; T09 đa thức/Ridge; T11 phần dư/lỗi/case; T13 nội dung kết quả/kết luận; T15 slide và kịch bản; kiểm các đầu ra liên quan.",
    "Cùng Hàn đọc chéo bản tích hợp, kiểm bộ nộp T17 và diễn tập/video T18. Các bước do người thực hiện xác nhận thật.",
    "Codex hỗ trợ triển khai, chạy kiểm chứng và viết bản thảo phần Huy; nội dung phụ lục không tự khai tỷ lệ đóng góp hoặc hoàn thành diễn tập chưa xảy ra. Hàn bổ sung AI/nguồn tham khảo thực tế của phần mình. Bản này là sản phẩm bàn giao để tích hợp, chưa phải bộ nộp cuối."
]

for s in sources:
    if s in xml:
        print(f"[FOUND]: {s[:40]}...")
    else:
        print(f"[NOT FOUND]: {s[:40]}...")
