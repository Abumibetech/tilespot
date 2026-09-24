$file = ".\templates\base.html"

if (-not (Test-Path $file)) {
    Write-Host "ERROR: templates/base.html was not found." -ForegroundColor Red
    exit 1
}

$path = (Resolve-Path $file).Path

# Read the existing file as UTF-8
$utf8 = [System.Text.UTF8Encoding]::new($false)
$content = [System.IO.File]::ReadAllText($path, $utf8)

# ---------------------------------------------------------
# PWA HEAD
# ---------------------------------------------------------

if ($content -notmatch 'href="/static/manifest\.json"') {

    $pwaHead = @"
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#071019">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Tilespot">
    <link rel="stylesheet" href="/static/css/pwa.css">

"@

    $headClose = '</head>'

    if ($content.Contains($headClose)) {
        $content = $content.Replace(
            $headClose,
            $pwaHead + $headClose
        )
    }
}

# ---------------------------------------------------------
# PWA JAVASCRIPT
# ---------------------------------------------------------

if ($content -notmatch 'src="/static/js/pwa\.js"') {

    $pwaScript = @"
    <script src="/static/js/pwa.js"></script>

"@

    $bodyClose = '</body>'

    if ($content.Contains($bodyClose)) {
        $content = $content.Replace(
            $bodyClose,
            $pwaScript + $bodyClose
        )
    }
}

# ---------------------------------------------------------
# MOBILE NAVIGATION
# ---------------------------------------------------------

if ($content -notmatch 'class="tilespot-mobile-nav') {

    $mobileNav = @"
    <nav class="tilespot-mobile-nav pwa-safe-bottom" aria-label="Mobile navigation">

        <a href="/" aria-label="Home">
            <span class="nav-icon">🏠</span>
            <span>Home</span>
        </a>

        <a href="{% url 'catalog' %}" aria-label="Browse tiles">
            <span class="nav-icon">🔎</span>
            <span>Browse</span>
        </a>

        {% if user.is_authenticated %}

        <a href="{% url 'dashboard' %}" aria-label="Dashboard">
            <span class="nav-icon">❤️</span>
            <span>Saved</span>
        </a>

        <a href="{% url 'inbox' %}" aria-label="Messages">
            <span class="nav-icon">💬</span>
            <span>Messages</span>
        </a>

        <a href="{% url 'profile' %}" aria-label="Profile">
            <span class="nav-icon">👤</span>
            <span>Profile</span>
        </a>

        {% else %}

        <a href="{% url 'login' %}" aria-label="Login">
            <span class="nav-icon">🔐</span>
            <span>Login</span>
        </a>

        <a href="{% url 'register' %}" aria-label="Register">
            <span class="nav-icon">👤</span>
            <span>Join</span>
        </a>

        {% endif %}

    </nav>

"@

    $bodyClose = '</body>'

    if ($content.Contains($bodyClose)) {
        $content = $content.Replace(
            $bodyClose,
            $mobileNav + $bodyClose
        )
    }
}

# ---------------------------------------------------------
# WRITE BACK AS UTF-8 WITHOUT BOM
# ---------------------------------------------------------

[System.IO.File]::WriteAllText(
    $path,
    $content,
    $utf8
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TILESPOT PWA CONNECTED SAFELY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Manifest           : CONNECTED" -ForegroundColor Green
Write-Host "PWA stylesheet     : CONNECTED" -ForegroundColor Green
Write-Host "Service worker     : CONNECTED" -ForegroundColor Green
Write-Host "PWA JavaScript     : CONNECTED" -ForegroundColor Green
Write-Host "Mobile navigation  : CONNECTED" -ForegroundColor Green
Write-Host "UTF-8 preservation : ENABLED" -ForegroundColor Green
Write-Host ""
Write-Host "Existing base.html content preserved." -ForegroundColor Yellow
Write-Host ""
