$docxPath = (Resolve-Path "reports/deliverables/HUY_Bao_cao_ban_giao.docx").Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath, $false, $true) # read-only
    Write-Output "Successfully opened original docx: $($doc.Paragraphs.Count) paragraphs"
    $doc.Close([ref]$false)
} catch {
    Write-Output "Error: $_"
} finally {
    $word.Quit()
}
