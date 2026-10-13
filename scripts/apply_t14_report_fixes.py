"""Apply Task T14 content updates to HUY_Bao_cao_ban_giao.docx and export PDF.

This script updates:
1. TÀI LIỆU THAM KHẢO: Full citation of Kaggle The Devastator dataset, access date 13/10/2026,
   and reference source repo airbnb-price-analysis-eda.
2. PHỤ LỤC PHÂN CÔNG NHIỆM VỤ: Detailed completed tasks based on actual 18-task contribution
   for both Member A (Han) and Member B (Huy).
3. CAM KẾT MINH BẠCH: Academic integrity statement declaring Kaggle source, reference code,
   and transparent AI tool usage (Codex for Huy, Antigravity/Gemini for Han).

Designed to be completely idempotent (safe to run multiple times).
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
    ),
    # 7. Cover subtitle
    (
        "Bản bàn giao phần Huy để Hàn tích hợp và đọc chéo",
        "Báo cáo đồ án môn học — Tích hợp kết quả Đoàn Hữu Hàn (A) và Nguyễn Quang Huy (B)"
    ),
    (
        "Thông tin nhóm và nguồn tham khảo còn cần xác nhận",
        "Đã tích hợp hoàn thiện Giới thiệu, Dữ liệu, Tiền xử lý, Mô hình và Phụ lục"
    ),
    # 8. Cover team name
    (
        "Nhóm Hàn – Huy; mã nhóm chưa cung cấp",
        "Nhóm thực hiện: Đoàn Hữu Hàn (Thành viên A) – Nguyễn Quang Huy (Thành viên B)"
    )
]

needs_update = False
for src, dst in t14_replacements:
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
    print(f"{DOCX_PATH} is already up to date with all T14 fixes.")

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
ps_file = ROOT / "scratch/run_export_t14_deliverable.ps1"
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
print("All T14 updates and PDF generation completed successfully!")
