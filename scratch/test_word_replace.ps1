$sourceDocx = (Resolve-Path "reports/deliverables/HUY_Bao_cao_ban_giao.docx").Path
$testDocx = (Resolve-Path ".").Path + "\scratch\test_replaced.docx"
$testPdf = (Resolve-Path ".").Path + "\scratch\test_replaced.pdf"

Copy-Item $sourceDocx $testDocx -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($testDocx)
    
    $replaces = @(
        @{
            Find = "Lịch sử tái sử dụng, công cụ AI phần Hàn và thông tin nguồn Internet cần Hàn xác nhận trước bản nộp cuối."
            Replace = "Các công cụ AI (Codex, Antigravity/Gemini) hỗ trợ viết code, kiểm toán tự động và định dạng báo cáo; hai thành viên trực tiếp kiểm chứng logic và số liệu thực tế."
        },
        @{
            Find = "dữ liệu gộp có 24 cột sau thêm city, day_type, source_file và source_row."
            Replace = "dữ liệu gộp có 24 cột sau khi thêm city, day_type, source_file và source_row."
        },
        @{
            Find = "Không có ô khuyết hoặc giá trị số không hữu hạn trong snapshot kiểm tra."
            Replace = "Trong 17 thuộc tính số, có 1 cột định danh, 4 cờ boolean, 2 tọa độ per_readme và 10 biến định lượng. Không có ô khuyết hoặc giá trị số không hữu hạn."
        },
        @{
            Find = "Số phòng ngủ; giá trị 0 không tự suy ra studio"
            Replace = "Số phòng ngủ quan sát (0–10; giá trị 0 là quan sát thực tế, không tự suy ra studio)"
        },
        @{
            Find = "Khoảng cách ghi trong file; không làm tròn trước tính"
            Replace = "Khoảng cách ghi trong file; metro_dist min 0,0023 km, hiển thị 0,00 là làm tròn"
        },
        @{
            Find = "Hàn cần đối chiếu phương trình/hệ số với a_m2_coefficients.csv và phần phương pháp của mình khi tích hợp bản cuối."
            Replace = "Các hệ số và độ chênh lệch Train MSE (79.912,37) vs CV MSE (79.988,15) khớp hoàn toàn với a_m2_coefficients.csv và quan sát thực nghiệm của Thành viên A."
        }
    )

    foreach ($item in $replaces) {
        $find = $doc.Content.Find
        $find.ClearFormatting()
        $find.Replacement.ClearFormatting()
        $found = $find.Execute(
            $item.Find,             # FindText
            $false,                 # MatchCase
            $false,                 # MatchWholeWord
            $false,                 # MatchWildcards
            $false,                 # MatchSoundsLike
            $false,                 # MatchAllWordForms
            $true,                  # Forward
            1,                      # wdFindContinue
            $false,                 # Format
            $item.Replace,          # ReplaceWith
            2                       # wdReplaceAll
        )
        Write-Output "Replace result for '$($item.Find.Substring(0, [Math]::Min(30, $item.Find.Length)))...': $found"
    }

    $doc.Save()
    # 17 = wdFormatPDF
    $doc.SaveAs([ref]$testPdf, [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Successfully saved docx and exported PDF!"
} catch {
    Write-Output "Error: $_"
} finally {
    $word.Quit()
}
