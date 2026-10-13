import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('reports/deliverables/HUY_Bao_cao_ban_giao.docx') as z:
    xml = z.read('word/document.xml').decode('utf-8')

targets = [
    "Lịch sử tái sử dụng, công cụ AI phần Hàn và thông tin nguồn Internet cần Hàn xác nhận trước bản nộp cuối.",
    "Bộ dữ liệu gồm 51.707 quan sát từ 20 tệp CSV",
    "Số phòng ngủ; giá trị 0 không tự suy ra studio",
    "Khoảng cách ghi trong file; không làm tròn trước tính",
    "Hàn cần đối chiếu phương trình/hệ số với a_m2_coefficients.csv và phần phương pháp của mình khi tích hợp bản cuối."
]

for t in targets:
    if t in xml:
        print(f"[FOUND EXACT]: {t[:40]}...")
    else:
        print(f"[NOT FOUND]: {t[:40]}...")
