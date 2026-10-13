import os
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2] / "Source"
DOCX_ORIG = ROOT / "reports/deliverables/HUY_Bao_cao_ban_giao.docx"
DOCX_TEMP = ROOT / "scratch/test_report.docx"
PDF_TEMP = ROOT / "scratch/test_report.pdf"

shutil.copy2(DOCX_ORIG, DOCX_TEMP)

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ET.register_namespace('w', NS['w'])

with zipfile.ZipFile(DOCX_TEMP, 'r') as z:
    xml_content = z.read('word/document.xml')
    other_files = {name: z.read(name) for name in z.namelist() if name != 'word/document.xml'}

root = ET.fromstring(xml_content)
body = root.find('w:body', NS)

def set_para_text(p, text):
    pPr = p.find('w:pPr', NS)
    p.clear()
    if pPr is not None:
        p.append(pPr)
    r = ET.SubElement(p, '{%s}r' % NS['w'])
    t = ET.SubElement(r, '{%s}t' % NS['w'])
    t.text = text

def set_cell_text(tc, text):
    tcPr = tc.find('w:tcPr', NS)
    p = tc.find('w:p', NS)
    pPr = p.find('w:pPr', NS) if p is not None else None
    tc.clear()
    if tcPr is not None:
        tc.append(tcPr)
    new_p = ET.SubElement(tc, '{%s}p' % NS['w'])
    if pPr is not None:
        new_p.append(pPr)
    r = ET.SubElement(new_p, '{%s}r' % NS['w'])
    t = ET.SubElement(r, '{%s}t' % NS['w'])
    t.text = text

# Update P017 (Intro paragraph 2)
p017_text = (
    "Dữ liệu lấy từ 20 CSV cung cấp trong source dự án [1], không tự thu thập. Nhóm tái sử dụng code "
    "dự án và vận dụng tài liệu môn học; các công cụ AI (Codex, Antigravity/Gemini) hỗ trợ viết/chạy code, "
    "kiểm số liệu tự động và định dạng báo cáo. Các kết quả được đối chiếu chặt chẽ với dữ liệu và "
    "giao thức trong repo; hai thành viên trực tiếp kiểm chứng logic và số liệu thực tế."
)
set_para_text(body[17], p017_text)

# Update P019 (Dataset description)
p019_text = (
    "Bộ dữ liệu gồm 51.707 quan sát từ 20 tệp CSV, tương ứng 10 thành phố và hai nhóm weekdays/weekends. "
    "Mỗi file có 20 cột gốc; dữ liệu gộp có 24 cột sau khi thêm city, day_type, source_file và source_row. "
    "Trong 17 thuộc tính số, có 1 cột định danh kỹ thuật, 4 cột boolean, 2 cột tọa độ per_readme và 10 biến định lượng. "
    "Không có ô khuyết hoặc giá trị số không hữu hạn. Giá dùng nguyên realSum; EUR được khai báo ở README, "
    "kỳ lưu trú chưa xác minh nên không đổi thành giá mỗi đêm."
)
set_para_text(body[19], p019_text)

# Update Table 1 (ELEM 20)
tbl020 = body[20]
rows = tbl020.findall('.//w:tr', NS)
# Row 3: bedrooms
set_cell_text(rows[3].findall('w:tc', NS)[2], "Số phòng ngủ quan sát (0–10; giá trị 0 là quan sát thực tế, không tự suy ra studio)")
# Row 4: dist; metro_dist
set_cell_text(rows[4].findall('w:tc', NS)[2], "Khoảng cách ghi trong file; metro_dist min 0,0023 km, hiển thị 0,00 là làm tròn")

# Update P066 (M2 Model findings)
p066_text = (
    "M2 chuẩn hóa biến số; hệ số biến số phản ánh thay đổi theo một độ lệch chuẩn train nếu giữ các biến khác cố định. "
    "Hệ số one-hot là chênh so với nhóm tham chiếu, không phải hệ số chuẩn hóa theo độ lệch chuẩn của city. "
    "Các hệ số và độ chênh lệch Train MSE (79.912,37) vs CV MSE (79.988,15) khớp hoàn toàn với "
    "a_m2_coefficients.csv và quan sát thực nghiệm của Thành viên A."
)
set_para_text(body[66], p066_text)

# Save updated docx
with zipfile.ZipFile(DOCX_TEMP, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
    z_out.writestr('word/document.xml', ET.tostring(root, encoding='utf-8', xml_declaration=True))
    for name, content in other_files.items():
        z_out.writestr(name, content)

print("Saved updated docx to:", DOCX_TEMP)
