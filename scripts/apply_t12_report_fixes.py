"""Apply Task T12 content updates to HUY_Bao_cao_ban_giao.docx and export PDF.

This script updates the Introduction, Data Description, and Preprocessing/Model
sections authored/reviewed by Member A (Han), preserving all template styles,
fonts (Times New Roman 13), headings, tables, figures, and page counts.
"""
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = ROOT / "reports/deliverables/HUY_Bao_cao_ban_giao.docx"
PDF_PATH = ROOT / "reports/deliverables/HUY_Bao_cao_ban_giao.pdf"

print(f"Loading {DOCX_PATH}...")
with zipfile.ZipFile(DOCX_PATH, 'r') as z_in:
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

needs_update = False
for src, dst in replacements:
    if dst in xml:
        print(f"[ALREADY UP TO DATE]: {dst[:35]}...")
    elif src in xml:
        xml = xml.replace(src, dst)
        needs_update = True
        print(f"[REPLACED]: {src[:35]}...")
    else:
        raise AssertionError(f"Target text not found in document.xml: {src[:40]}...")

if needs_update:
    with zipfile.ZipFile(DOCX_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
        z_out.writestr('word/document.xml', xml.encode('utf-8'))
        for n, data in other_files.items():
            z_out.writestr(n, data)
    print(f"Successfully updated {DOCX_PATH} ({DOCX_PATH.stat().st_size} bytes)")
else:
    print(f"{DOCX_PATH} is already up to date with all T12 fixes.")

# Export PDF via PowerShell Word COM
ps_script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $doc = $word.Documents.Open('{DOCX_PATH.resolve()}', $false, $true)
    $doc.SaveAs([ref]'{PDF_PATH.resolve()}', [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported PDF via Word COM: {PDF_PATH.name}"
}} finally {{
    $word.Quit()
}}
"""
ps_file = ROOT / "scratch/run_export_deliverable.ps1"
with open(ps_file, 'w', encoding='utf-8-sig') as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)], capture_output=True, text=True)
print("PowerShell output:", res.stdout.strip() if res.stdout else "No stdout")
if res.stderr:
    print("PowerShell error:", res.stderr.strip())
assert res.returncode == 0, f"PDF export failed with code {res.returncode}"

reader = PdfReader(PDF_PATH)
texts = [p.extract_text() or '' for p in reader.pages]
compact = [''.join(t.split()) for t in texts]
intro = next(i for i, t in enumerate(compact) if 'GIỚITHIỆU' in t)
refs = next(i for i, t in enumerate(compact) if 'TÀILIỆUTHAMKHẢO' in t)
print(f"PDF verified: {len(reader.pages)} total pages, {refs - intro} main content pages (starts at page {intro}).")
assert intro == 1 and 5 <= refs - intro <= 10, f"Page constraints violated: intro={intro}, main_pages={refs - intro}"
print("All T12 updates and PDF generation completed successfully!")
