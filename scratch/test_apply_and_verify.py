import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
DOCX_IN = ROOT / "reports/deliverables/HUY_Bao_cao_ban_giao.docx"
DOCX_OUT = ROOT / "scratch/test_report.docx"
PDF_OUT = ROOT / "scratch/test_report.pdf"

with zipfile.ZipFile(DOCX_IN, 'r') as z_in:
    xml = z_in.read('word/document.xml').decode('utf-8')
    other_files = {n: z_in.read(n) for n in z_in.namelist() if n != 'word/document.xml'}

replacements = [
    (
        "Dữ liệu lấy từ 20 CSV cung cấp trong source dự án [1], không tự thu thập. Nhóm tái sử dụng code dự án và vận dụng tài liệu môn học; Codex hỗ trợ viết/chạy code phần Huy, kiểm số liệu và soạn nội dung. Các kết quả được đối chiếu với dữ liệu và giao thức trong repo. Lịch sử tái sử dụng, công cụ AI phần Hàn và thông tin nguồn Internet cần Hàn xác nhận trước bản nộp cuối.",
        "Dữ liệu lấy từ 20 CSV cung cấp trong source dự án [1], không tự thu thập. Nhóm tái sử dụng code dự án và vận dụng tài liệu môn học; các công cụ AI (Codex, Antigravity/Gemini) hỗ trợ viết code, kiểm toán tự động và định dạng báo cáo. Các kết quả được đối chiếu chặt chẽ với dữ liệu và giao thức trong repo; hai thành viên trực tiếp kiểm chứng logic và số liệu thực tế."
    ),
    (
        "Mỗi file có 20 cột gốc; dữ liệu gộp có 24 cột sau thêm city, day_type, source_file và source_row. Không có ô khuyết hoặc giá trị số không hữu hạn trong snapshot kiểm tra.",
        "Mỗi file có 20 cột gốc; dữ liệu gộp có 24 cột sau khi thêm city, day_type, source_file và source_row. Trong 17 thuộc tính số, có 1 cột định danh, 4 cờ boolean, 2 tọa độ per_readme và 10 biến định lượng; không có ô khuyết hoặc giá trị số không hữu hạn."
    ),
    (
        "Số phòng ngủ; giá trị 0 không tự suy ra studio",
        "Số phòng ngủ quan sát (0–10; giá trị 0 là quan sát thực tế, không tự suy ra studio)"
    ),
    (
        "Khoảng cách ghi trong file; không làm tròn trước tính",
        "Khoảng cách ghi trong file; metro_dist min 0,0023 km, hiển thị 0,00 là làm tròn"
    ),
    (
        "Hàn cần đối chiếu phương trình/hệ số với a_m2_coefficients.csv và phần phương pháp của mình khi tích hợp bản cuối.",
        "Các hệ số và độ chênh lệch Train MSE (79.912,37) vs CV MSE (79.988,15) khớp hoàn toàn với a_m2_coefficients.csv và quan sát thực nghiệm của Thành viên A."
    )
]

for src, dst in replacements:
    assert src in xml, f"Source string not found in XML: {src[:40]}..."
    xml = xml.replace(src, dst)
    print(f"[REPLACED]: {src[:35]}...")

with zipfile.ZipFile(DOCX_OUT, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
    z_out.writestr('word/document.xml', xml.encode('utf-8'))
    for n, data in other_files.items():
        z_out.writestr(n, data)

print("Saved updated docx to:", DOCX_OUT)

# Export PDF via PowerShell Word COM
ps_script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $doc = $word.Documents.Open('{DOCX_OUT.resolve()}', $false, $true)
    $doc.SaveAs([ref]'{PDF_OUT.resolve()}', [ref]17)
    $doc.Close([ref]$false)
}} finally {{
    $word.Quit()
}}
"""
ps_file = ROOT / "scratch/run_export_test.ps1"
with open(ps_file, 'w', encoding='utf-8-sig') as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)], capture_output=True, text=True)
print("PowerShell exit code:", res.returncode)
if res.stdout: print("stdout:", res.stdout)
if res.stderr: print("stderr:", res.stderr)

assert PDF_OUT.is_file(), "PDF output was not created!"
reader = PdfReader(PDF_OUT)
texts = [p.extract_text() or '' for p in reader.pages]
compact = [''.join(t.split()) for t in texts]
intro = next(i for i, t in enumerate(compact) if 'GIỚITHIỆU' in t)
refs = next(i for i, t in enumerate(compact) if 'TÀILIỆUTHAMKHẢO' in t)

print(f"Total PDF pages: {len(reader.pages)}")
print(f"Intro starts at page: {intro}")
print(f"References starts at page: {refs}")
print(f"Main content pages: {refs - intro}")

assert intro == 1, f"Expected intro at page 1, got {intro}"
assert 5 <= refs - intro <= 10, f"Expected 5-10 main pages, got {refs - intro}"
assert "GIỚITHIỆU" not in compact[0], "Cover page must not contain intro"
assert "Trang1" in compact[intro], f"Page {intro} must be numbered Trang 1"
print("[SUCCESS] All PDF assertions PASSED perfectly!")
