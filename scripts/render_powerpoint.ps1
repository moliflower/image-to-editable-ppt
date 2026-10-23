param(
  [Parameter(Mandatory=$true)][string]$InputPptx,
  [Parameter(Mandatory=$true)][string]$OutputPng,
  [int]$Width=1600,
  [string]$EditProbePath
)
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $InputPptx).Path
$targetPath = [IO.Path]::GetFullPath($OutputPng)
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($targetPath)) | Out-Null
$officeApp = $null
$presentation = $null
try {
  $officeApp = New-Object -ComObject PowerPoint.Application
  $presentation = $officeApp.Presentations.Open($sourcePath, $true, $false, $false)
  if ($presentation.Slides.Count -ne 1) { throw 'Expected a one-slide figure' }
  $slide = $presentation.Slides.Item(1)
  $renderHeight = [int][Math]::Round($Width * $presentation.PageSetup.SlideHeight / $presentation.PageSetup.SlideWidth)
  $slide.Export($targetPath, 'PNG', $Width, $renderHeight)
  $objects = @()
  for ($i = 1; $i -le $slide.Shapes.Count; $i++) {
    $shape = $slide.Shapes.Item($i)
    $label = ''
    if ($shape.HasTextFrame -and $shape.TextFrame.HasText) { $label = $shape.TextFrame.TextRange.Text }
    $objects += [PSCustomObject]@{Name=$shape.Name; Type=[int]$shape.Type; Text=$label; Left=$shape.Left; Top=$shape.Top; Width=$shape.Width; Height=$shape.Height}
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($shape)
  }
  if ($EditProbePath) {
    $probe = [IO.Path]::GetFullPath($EditProbePath)
    if ($probe -eq $sourcePath) { throw 'Edit probe must use a separate file' }
    $editedText = $false
    $movedShape = $false
    $editedArrow = $false
    for ($i = 1; $i -le $slide.Shapes.Count; $i++) {
      $shape = $slide.Shapes.Item($i)
      $hasText = $shape.HasTextFrame -and $shape.TextFrame.HasText
      if (!$editedText -and $hasText) {
        $shape.TextFrame.TextRange.Text = 'EDITABILITY VERIFIED'
        $editedText = $true
      } elseif (!$movedShape -and !$hasText -and $shape.Type -ne 13) {
        $shape.Left += 2
        $movedShape = $true
      }
      if (!$editedArrow -and $shape.Line.EndArrowheadStyle -gt 1) {
        $shape.Line.ForeColor.RGB = 255
        $editedArrow = $true
      }
      [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($shape)
    }
    if (!$editedText -or !$movedShape -or !$editedArrow) { throw 'Edit probe could not modify text, geometry, and an arrow' }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($probe)) | Out-Null
    $presentation.SaveCopyAs($probe, 24)
  }
  if (!(Test-Path -LiteralPath $targetPath)) { throw 'PowerPoint did not produce the PNG' }
  $report = [PSCustomObject]@{Renderer='Microsoft PowerPoint'; ObjectCount=$objects.Count; Objects=$objects}
  $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ([IO.Path]::ChangeExtension($targetPath, '.office.json')) -Encoding UTF8
  Write-Output "PowerPoint rendered $($objects.Count) independent objects to $targetPath"
  [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($slide)
} finally {
  if ($presentation) {
    $presentation.Close()
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
  }
  if ($officeApp) {
    if ($officeApp.Presentations.Count -eq 0) { $officeApp.Quit() }
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($officeApp)
  }
}
