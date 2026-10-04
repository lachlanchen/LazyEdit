# Test deployment uses the existing interactive console, not SSH's service token.
param(
    [Parameter(Mandatory=$true)][string]$Package,
    [Parameter(Mandatory=$true)][string]$ExpectedSha256,
    [string]$PackageName = "LazyingArt.LazyEditStudio.QA",
    [switch]$ConsoleStep,
    [switch]$Remove
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
if ($PackageName -notmatch '^LazyingArt\.LazyEditStudio\.QA$') { throw "This helper handles only the dedicated test package" }
if ($ExpectedSha256 -notmatch '^[A-Fa-f0-9]{64}$' -or (Get-FileHash $Package -Algorithm SHA256).Hash -ne $ExpectedSha256) { throw "Test package digest mismatch" }
$result = "$env:LOCALAPPDATA\LazyEditStudio\msix-install.json"
if ($ConsoleStep) {
    try {
        if ($Remove) {
            Get-AppxPackage -Name $PackageName | Remove-AppxPackage
            $data = [pscustomobject]@{removed=$true;packageName=$PackageName}
        } else {
            Add-AppxPackage -Path $Package
            $p = Get-AppxPackage -Name $PackageName
            if (-not $p) { throw "Test package registration missing" }
            $exe = Join-Path $p.InstallLocation "LazyEditStudio.exe"
            $signature = Get-AuthenticodeSignature $exe
            if ($signature.Status -ne "Valid") { throw "Installed launcher signature is not valid" }
            $data = [pscustomobject]@{host=$env:COMPUTERNAME;installed=$true;packageName=$p.Name;
                packageFullName=$p.PackageFullName;packageFamilyName=$p.PackageFamilyName;
                installLocation=$p.InstallLocation;signatureStatus=[string]$signature.Status;
                signer=$signature.SignerCertificate.Subject;certificateThumbprint=$signature.SignerCertificate.Thumbprint;
                executableSha256=(Get-FileHash $exe -Algorithm SHA256).Hash.ToLowerInvariant()}
        }
        $data | ConvertTo-Json -Compress | Set-Content $result -Encoding UTF8
        exit 0
    } catch {
        [pscustomobject]@{failed=$true;message=$_.Exception.Message} | ConvertTo-Json -Compress | Set-Content $result -Encoding UTF8
        exit 1
    }
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
if ((Get-CimInstance Win32_ComputerSystem).UserName -ne $identity) { throw "Use the existing console user's SSH account" }
$name = "LazyEditStudioPackageQA"
if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) { throw "An existing package test task must be reconciled" }
New-Item -ItemType Directory -Force (Split-Path $result) | Out-Null
if (Test-Path $result) { Remove-Item $result }
$arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $PSCommandPath + '" -ConsoleStep -Package "' + $Package + '" -ExpectedSha256 ' + $ExpectedSha256
if ($Remove) { $arguments += ' -Remove' }
$action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $arguments
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings | Out-Null
try {
    $start = (Get-Date).AddSeconds(-2) # Task Scheduler records whole seconds.
    Start-ScheduledTask -TaskName $name
    $deadline = (Get-Date).AddSeconds(120)
    do {
        Start-Sleep -Seconds 2
        $state = (Get-ScheduledTask -TaskName $name).State
        $info = Get-ScheduledTaskInfo -TaskName $name
        if ($info.LastRunTime -ge $start -and $state -notin @("Running", "Queued") -and (Test-Path $result)) { break }
    } while ((Get-Date) -lt $deadline)
    if ($info.LastRunTime -lt $start -or $state -in @("Running", "Queued") -or -not (Test-Path $result)) { throw "Interactive package deployment timed out" }
    if ($info.LastTaskResult -ne 0) { throw (Get-Content $result -Raw) }
    Get-Content $result -Raw
} finally {
    if ((Get-ScheduledTask -TaskName $name).State -in @("Running", "Queued")) { Stop-ScheduledTask -TaskName $name }
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
}
