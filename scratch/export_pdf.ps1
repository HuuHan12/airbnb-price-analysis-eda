$docxPath = (Resolve-Path "scratch/test_report.docx").Path
$pdfPath = [System.IO.Path]::ChangeExtension($docxPath, ".pdf")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    # 17 = wdFormatPDF
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported PDF: $pdfPath"
} finally {
    $word.Quit()
}
