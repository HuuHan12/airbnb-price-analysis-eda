try {
    $word = New-Object -ComObject Word.Application
    Write-Output "Word COM is available: $($word.Version)"
    $word.Quit()
} catch {
    Write-Output "Word COM error: $_"
}
