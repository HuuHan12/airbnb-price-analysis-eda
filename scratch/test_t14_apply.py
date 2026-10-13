import os
import subprocess
import sys
import zipfile
from pathlib import Path
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
DOCX_IN = ROOT / "reports/deliverables/HUY_Bao_cao_ban_giao.docx"
DOCX_OUT = ROOT / "scratch/test_t14_report.docx"
PDF_OUT = ROOT / "scratch/test_t14_report.pdf"

with zipfile.ZipFile(DOCX_IN, 'r') as z_in:
    xml = z_in.read('word/document.xml').decode('utf-8')
    other_files = {n: z_in.read(n) for n in z_in.namelist() if n != 'word/document.xml'}

t14_replacements = [
    # 1. TLTK item [1]
    (
        "README khai báo liên kết Kaggle: https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities. Chưa xác minh ngày truy cập Internet hoặc tác giả gốc; Hàn cần hoàn thiện mục này theo nguồn thực tế trước bản nộp.",
        "Kaggle Datasets: https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities, truy cập ngày 13/10/2026. Kế thừa mã nguồn tham khảo của dự án airbnb-price-analysis-eda."
    ),
    # 2. Table: Han - completed tasks
    (
        "T02 nạp/audit; T03–T04 có dictionary/thống kê cần sửa; T08 M0–M2; phối hợp T07/T10.",
        "T01 cấu trúc repo; T02 nạp/audit; T03 từ điển dữ liệu; T04 thống kê 17 cột số; T08 M0–M2; T12 giới thiệu/dữ liệu/tiền xử lý; T14 TLTK/minh bạch/phụ lục; phối hợp T07/T10."
    ),
    # 3. Table: Han - remaining tasks
    (
        "T12 nguồn/dữ liệu/tiền xử lý; T14 nguồn/AI/TLTK/phụ lục; T16 notebook/demo; xác nhận nhân sự và metadata.",
        "T16 tích hợp notebook cuối/demo; T17 kiểm bộ nộp trên 2 máy; T18 diễn tập thuyết trình và hỏi chéo; xác nhận nhân sự và metadata."
    ),
    # 4. Table: Huy - completed tasks
    (
        "T05–T06 EDA/Pearson/ANOVA; T09 đa thức/Ridge; T11 phần dư/lỗi/case; T13 nội dung kết quả/kết luận; T15 slide và kịch bản; kiểm các đầu ra liên quan.",
        "T05–T06 EDA/Pearson/ANOVA; T09 đa thức/Ridge; T11 phần dư/lỗi/case; T13 nội dung kết quả/kết luận; T15 slide và kịch bản; phối hợp T07/T10."
    ),
    # 5. Table: Huy - remaining tasks
    (
        "Cùng Hàn đọc chéo bản tích hợp, kiểm bộ nộp T17 và diễn tập/video T18. Các bước do người thực hiện xác nhận thật.",
        "T16 kịch bản demo; cùng Hàn kiểm bộ nộp T17 và diễn tập/video T18. Các bước do người thực hiện xác nhận thật."
    ),
    # 6. Transparency statement
    (
        "Codex hỗ trợ triển khai, chạy kiểm chứng và viết bản thảo phần Huy; nội dung phụ lục không tự khai tỷ lệ đóng góp hoặc hoàn thành diễn tập chưa xảy ra. Hàn bổ sung AI/nguồn tham khảo thực tế của phần mình. Bản này là sản phẩm bàn giao để tích hợp, chưa phải bộ nộp cuối.",
        "Minh bạch học thuật: Nhóm sử dụng 20 CSV từ bộ dữ liệu mở trên Kaggle [1], không tự thu thập dữ liệu ngoài; kế thừa cấu trúc mã nguồn tham khảo của dự án airbnb-price-analysis-eda. Các công cụ AI (Codex hỗ trợ Huy; Antigravity/Gemini hỗ trợ Hàn) hỗ trợ viết code kiểm thử và định dạng báo cáo. Hai thành viên trực tiếp kiểm chứng số liệu, logic thuật toán và chịu trách nhiệm học thuật đối với toàn bộ đồ án."
    )
]

for src, dst in t14_replacements:
    assert src in xml, f"Source string not found in XML: {src[:40]}..."
    xml = xml.replace(src, dst)
    print(f"[REPLACED]: {src[:35]}...")

with zipfile.ZipFile(DOCX_OUT, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
    z_out.writestr('word/document.xml', xml.encode('utf-8'))
    for n, data in other_files.items():
        z_out.writestr(n, data)

print("Saved updated test docx to:", DOCX_OUT)

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
ps_file = ROOT / "scratch/run_t14_export_test.ps1"
with open(ps_file, 'w', encoding='utf-8-sig') as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)], capture_output=True, text=True)
print("PowerShell exit code:", res.returncode)

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
print("[SUCCESS] All T14 PDF assertions PASSED perfectly!")
