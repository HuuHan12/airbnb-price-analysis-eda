
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open('P:\CITD\HK3\Phân tích và trực quan dữ liệu\Đồ án môn học\Source\scratch\test_t14_report.docx', $false, $true)
    $doc.SaveAs([ref]'P:\CITD\HK3\Phân tích và trực quan dữ liệu\Đồ án môn học\Source\scratch\test_t14_report.pdf', [ref]17)
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
