$ErrorActionPreference = 'Stop'

$readmePath = Join-Path $PSScriptRoot '..\README.md'
$content = Get-Content -LiteralPath $readmePath -Raw -Encoding UTF8

$expectedTools = @(
    'OBS Studio', 'Bandicam', 'Geek Uninstaller', 'Clash Verge Rev',
    'DeskBox', 'Escrcpy', 'Everything', 'Neat Download Manager',
    'Internet Download Manager', 'foobar2000', 'Honeyview', 'PotPlayer',
    'PowerToys', 'qBittorrent', 'Typora', 'WizTree',
    '福昕 PDF 阅读器', 'Arctime', '火绒安全软件', 'Spotify',
    'SakuraFrp 启动器', 'Kazumi', 'Lossless Scaling', 'DeepSeek Harness'
)

$missingTools = @($expectedTools | Where-Object { $content -notmatch [regex]::Escape($_) })
if ($missingTools.Count -gt 0) {
    throw "README 中缺少工具：$($missingTools -join ', ')"
}

$categoryCount = ([regex]::Matches($content, '(?m)^## (?!目录|关于本清单).+$')).Count
if ($categoryCount -ne 4) {
    throw "应包含 4 个工具分类，实际为 $categoryCount 个。"
}

$toolHeadingCount = ([regex]::Matches($content, '(?m)^### .+$')).Count
if ($toolHeadingCount -ne $expectedTools.Count) {
    throw "应包含 $($expectedTools.Count) 个工具条目，实际为 $toolHeadingCount 个。"
}

foreach ($label in @('功能', '优点', '官网')) {
    $count = ([regex]::Matches($content, "(?m)^- \*\*$label：\*\*")).Count
    if ($count -ne $expectedTools.Count) {
        throw "每个工具都应包含字段 $label，实际找到 $count 项。"
    }
}

$links = [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')
foreach ($link in $links) {
    $url = $link.Groups[1].Value
    if ($url -notmatch '^(https://|#)') {
        throw "发现无效链接：$url"
    }
}

Write-Host "README 检查通过：$($expectedTools.Count) 个工具、$categoryCount 个分类、$($links.Count) 个有效链接。"