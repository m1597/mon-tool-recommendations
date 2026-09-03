$ErrorActionPreference = 'Stop'

$documents = @(
    @{
        Path = Join-Path $PSScriptRoot '..\README.md'
        Tools = @(
            'OBS Studio', 'Bandicam', 'Geek Uninstaller', 'Clash Verge Rev',
            'DeskBox', 'Escrcpy', 'Everything', 'Neat Download Manager',
            'Internet Download Manager', 'foobar2000', 'Honeyview', 'PotPlayer',
            'PowerToys', 'qBittorrent', 'Typora', 'WizTree',
            '福昕 PDF 阅读器', 'Arctime', '火绒安全软件', 'Spotify',
            'SakuraFrp 启动器', 'Kazumi', 'Lossless Scaling', 'DeepSeek Harness'
        )
        Labels = @('功能', '优点', '官网')
        LanguageLink = '[English](README.en.md)'
    },
    @{
        Path = Join-Path $PSScriptRoot '..\README.en.md'
        Tools = @(
            'OBS Studio', 'Bandicam', 'Geek Uninstaller', 'Clash Verge Rev',
            'DeskBox', 'Escrcpy', 'Everything', 'Neat Download Manager',
            'Internet Download Manager', 'foobar2000', 'Honeyview', 'PotPlayer',
            'PowerToys', 'qBittorrent', 'Typora', 'WizTree',
            'Foxit PDF Reader', 'Arctime', 'Huorong Internet Security', 'Spotify',
            'SakuraFrp Launcher', 'Kazumi', 'Lossless Scaling', 'DeepSeek Harness'
        )
        Labels = @('Features', 'Advantages', 'Website')
        LanguageLink = '[简体中文](README.md)'
    }
)

foreach ($document in $documents) {
    $content = Get-Content -LiteralPath $document.Path -Raw -Encoding UTF8
    $name = Split-Path $document.Path -Leaf

    $missingTools = @($document.Tools | Where-Object { $content -notmatch [regex]::Escape($_) })
    if ($missingTools.Count -gt 0) {
        throw "$name 缺少工具：$($missingTools -join ', ')"
    }

    $categoryCount = ([regex]::Matches($content, '(?m)^## (?!目录|关于本清单|Contents|About This List).+$')).Count
    if ($categoryCount -ne 4) {
        throw "$name 应包含 4 个工具分类，实际为 $categoryCount 个。"
    }

    $toolHeadingCount = ([regex]::Matches($content, '(?m)^### .+$')).Count
    if ($toolHeadingCount -ne $document.Tools.Count) {
        throw "$name 应包含 $($document.Tools.Count) 个工具条目，实际为 $toolHeadingCount 个。"
    }

    foreach ($label in $document.Labels) {
        $count = ([regex]::Matches($content, "(?m)^- \*\*$label[:：]\*\*")).Count
        if ($count -ne $document.Tools.Count) {
            throw "$name 的每个工具都应包含字段 $label，实际找到 $count 项。"
        }
    }

    if (-not $content.Contains($document.LanguageLink)) {
        throw "$name 缺少语言切换链接。"
    }

    $links = [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')
    foreach ($link in $links) {
        $target = $link.Groups[1].Value
        if ($target -notmatch '^(https://|#|README\.md$|README\.en\.md$)') {
            throw "$name 中发现无效链接：$target"
        }
    }

    Write-Host "$name 检查通过：$($document.Tools.Count) 个工具、$categoryCount 个分类、$($links.Count) 个有效链接。"
}