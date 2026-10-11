# Draws the Arabic words of the doors as white-on-black PNG masks.
# Blender text objects do not join Arabic letters, so the words are drawn here with GDI+, which shapes Arabic correctly.
# Run from the project folder:  powershell -ExecutionPolicy Bypass -File tools\make_text_masks.ps1
# Input: blender\texts.json   Output: blender\text\<file>.png
# Each picture holds the name plate on the left (title_width x height) and a square numeral plate on the right.
param([string]$Project = (Split-Path -Parent $PSScriptRoot))

Add-Type -AssemblyName System.Drawing
$spec = Get-Content -Raw -Encoding utf8 (Join-Path $Project 'blender\texts.json') | ConvertFrom-Json
$outDir = Join-Path $Project 'blender\text'
New-Item -ItemType Directory -Force $outDir | Out-Null

# first installed font from the list
$installed = (New-Object System.Drawing.Text.InstalledFontCollection).Families | ForEach-Object { $_.Name }
$familyName = $spec.font | Where-Object { $installed -contains $_ } | Select-Object -First 1
if (-not $familyName) { throw 'None of the fonts in texts.json is installed.' }
$family = New-Object System.Drawing.FontFamily($familyName)
$bold = [int][System.Drawing.FontStyle]::Bold

$format = New-Object System.Drawing.StringFormat
$format.FormatFlags = [System.Drawing.StringFormatFlags]::DirectionRightToLeft -bor [System.Drawing.StringFormatFlags]::NoWrap
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

# Draws one word as large as fits inside the box, as a filled and stroked outline so the letters are heavy enough to read
# from far away. Returns the letter height in pixels.
function Draw-Word($g, [string]$text, [single]$x, [single]$y, [single]$w, [single]$h, [double]$fillW, [double]$fillH) {
    $size = [double]$h
    while ($true) {
        $path = New-Object System.Drawing.Drawing2D.GraphicsPath
        $box = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
        $path.AddString($text, $family, $bold, [single]$size, $box, $format)
        $b = $path.GetBounds()
        if ((($b.Width -le $w * $fillW) -and ($b.Height -le $h * $fillH)) -or $size -le 12) { break }
        $path.Dispose()
        $size = $size * 0.95
    }
    # centre the letters themselves, not their line box
    $m = New-Object System.Drawing.Drawing2D.Matrix
    $m.Translate([single](($x + $w / 2) - ($b.X + $b.Width / 2)), [single](($y + $h / 2) - ($b.Y + $b.Height / 2)))
    $path.Transform($m)
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, [single]($size * 0.045))
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $g.FillPath([System.Drawing.Brushes]::White, $path)
    $g.DrawPath($pen, $path)
    $pen.Dispose(); $path.Dispose(); $m.Dispose()
    return $size
}

$h = [int]$spec.height
foreach ($item in $spec.items) {
    $tw = [int]$item.title_width
    $bmp = New-Object System.Drawing.Bitmap(($tw + $h), $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::Black)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias

    # a thin line round each plate, like the rim of an enamel sign
    $rim = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 9)
    $inset = 22
    $g.DrawRectangle($rim, $inset, $inset, $tw - 2 * $inset, $h - 2 * $inset)
    $g.DrawEllipse($rim, $tw + $inset, $inset, $h - 2 * $inset, $h - 2 * $inset)
    $rim.Dispose()

    $s1 = Draw-Word $g $item.title 0 0 $tw $h 0.8 0.62
    $s2 = Draw-Word $g $item.number $tw 0 $h $h 0.5 0.55
    $bmp.Save((Join-Path $outDir ($item.file + '.png')), [System.Drawing.Imaging.ImageFormat]::Png)
    "{0}  {1}x{2}  font={3}  title={4:N0}px  number={5:N0}px" -f $item.file, ($tw + $h), $h, $familyName, $s1, $s2
    $g.Dispose(); $bmp.Dispose()
}
