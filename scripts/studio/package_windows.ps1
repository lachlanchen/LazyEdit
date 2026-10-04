# Exact MSIX identity must come from Partner Center for a Store submission.
param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..\.."),
    [Parameter(Mandatory=$true)][string]$IdentityFile,
    [string]$Version = "1.0.0.0",
    [string]$SdkBin = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64",
    [string]$CertificateThumbprint,
    [switch]$TestPackage
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$identity = Get-Content $IdentityFile -Raw | ConvertFrom-Json
if ($identity.name -notmatch '^[A-Za-z0-9.-]{3,50}$' -or -not $identity.publisher.StartsWith("CN=") -or -not $identity.publisherDisplayName) { throw "Invalid package identity" }
if ($Version -notmatch '^\d+\.\d+\.\d+\.0$') { throw "Store version must have four numeric components ending in zero" }
if (-not $TestPackage -and $identity.source -ne "partner-center") { throw "Store packages require the actual reserved Partner Center identity" }
$suffix = if ($TestPackage) { "-qa" } else { "" }
$output = Join-Path $Root ("temp\desktop\LazyEditStudio-windows-x64-" + $Version + $suffix + ".msix")
$receipt = $output + ".json"
$partial = $output + ".partial.msix"
$partialReceipt = $receipt + ".partial"
if ((Test-Path $output) -or (Test-Path $receipt)) { throw "Preserve an existing candidate; use a new version or reconcile it" }
if ((Test-Path $partial) -or (Test-Path $partialReceipt)) { throw "Reconcile an interrupted packaging operation before continuing" }
$payload = Join-Path $Root "temp\desktop\windows-x64"
if (-not (Test-Path "$payload\LazyEditStudio.exe")) { throw "Build the native Windows candidate first" }
$stage = Join-Path $Root "temp\desktop\msix-staging"
if (Test-Path $stage) { throw "Reconcile existing packaging staging before continuing" }
$exe = Join-Path $stage "LazyEditStudio.exe"
try {
    Copy-Item $payload $stage -Recurse
    New-Item -ItemType Directory -Force "$stage\Assets" | Out-Null
    Copy-Item "$Root\mobile\windows\msix\Assets\*.png" "$stage\Assets"
    $manifest = Get-Content "$Root\mobile\windows\msix\AppxManifest.xml.template" -Raw
    foreach ($pair in @{NAME=$identity.name; PUBLISHER=$identity.publisher; PUBLISHER_DISPLAY_NAME=$identity.publisherDisplayName; VERSION=$Version}.GetEnumerator()) {
        $manifest = $manifest.Replace("@" + $pair.Key + "@", [Security.SecurityElement]::Escape([string]$pair.Value))
    }
    [IO.File]::WriteAllText("$stage\AppxManifest.xml", $manifest, [Text.UTF8Encoding]::new($false))
    if ($CertificateThumbprint) {
        if ($CertificateThumbprint -notmatch '^[A-Fa-f0-9]{40}$') { throw "Invalid certificate thumbprint" }
        $certificate = Get-Item ("Cert:\CurrentUser\My\" + $CertificateThumbprint)
        if (-not $certificate.HasPrivateKey -or $certificate.Subject -ne $identity.publisher -or $certificate.NotAfter -lt (Get-Date)) { throw "Certificate identity, key or expiry mismatch" }
        if (-not ($certificate.EnhancedKeyUsageList.ObjectId -contains "1.3.6.1.5.5.7.3.3")) { throw "A code-signing certificate is required" }
        # Only the app's launcher is signed; Microsoft/.NET DLLs are preserved.
        & "$SdkBin\signtool.exe" sign /fd SHA256 /sha1 $CertificateThumbprint $exe
        if ($LASTEXITCODE -ne 0) { throw "Launcher signing failed" }
    }
    & "$SdkBin\makeappx.exe" pack /d $stage /p $partial
    if ($LASTEXITCODE -ne 0) { throw "MSIX schema/package validation failed" }
    if ($CertificateThumbprint) {
        & "$SdkBin\signtool.exe" sign /fd SHA256 /sha1 $CertificateThumbprint $partial
        if ($LASTEXITCODE -ne 0) { throw "MSIX signing failed" }
    }
    $record = [pscustomobject]@{version=$Version; identity=$identity; testPackage=[bool]$TestPackage;
        msixSha256=(Get-FileHash $partial -Algorithm SHA256).Hash.ToLowerInvariant();
        executableSha256=(Get-FileHash $exe -Algorithm SHA256).Hash.ToLowerInvariant();
        certificateThumbprint=$CertificateThumbprint; publicCaTrustClaimed=$false;
        createdAt=(Get-Date).ToUniversalTime().ToString("o")}
    $record | ConvertTo-Json -Depth 5 | Set-Content $partialReceipt -Encoding UTF8
    # A failed pack/sign must never leave a final release candidate behind.
    Move-Item $partial $output
    Move-Item $partialReceipt $receipt
    $record | ConvertTo-Json -Depth 5
} finally {
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
    if (Test-Path $partial) { Remove-Item $partial }
    if (Test-Path $partialReceipt) { Remove-Item $partialReceipt }
}
