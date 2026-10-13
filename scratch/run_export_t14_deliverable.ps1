
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open('P:\CITD\HK3\Phân tích và trực quan dữ liệu\Đồ án môn học\Source\reports\deliverables\HUY_Bao_cao_ban_giao.docx', $false, $true)
    $doc.SaveAs([ref]'P:\CITD\HK3\Phân tích và trực quan dữ liệu\Đồ án môn học\Source\reports\deliverables\HUY_Bao_cao_ban_giao.pdf', [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported PDF via Word COM: HUY_Bao_cao_ban_giao.pdf"
} finally {
    $word.Quit()
}
