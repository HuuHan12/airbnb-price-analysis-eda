$docxPath = (Resolve-Path "reports/deliverables/HUY_Bao_cao_ban_giao.docx").Path
$pdfPath = (Resolve-Path ".").Path + "\scratch\original_test.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docxPath, $false, $true)
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported original PDF: $pdfPath"
} catch {
    Write-Output "Error: $_"
} finally {
    $word.Quit()
}
