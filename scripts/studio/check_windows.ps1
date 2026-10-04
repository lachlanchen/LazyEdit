# Live native qualification in the existing Windows console. No publication.
param(
    [Parameter(Mandatory=$true)][string]$Executable,
    [Parameter(Mandatory=$true)][string]$ExpectedSha256,
    [Parameter(Mandatory=$true)][string]$ReviewerCredentials,
    [string]$ResultDirectory = "$env:LOCALAPPDATA\LazyEditStudio"
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
if ([IO.Path]::GetFullPath($ReviewerCredentials) -ne [IO.Path]::GetFullPath("$env:LOCALAPPDATA\LazyEditStudio\reviewer-qa.json")) {
    throw "Copy reviewer input to the designated temporary reviewer-qa.json; never pass the source account file"
}
$taskName = "LazyEditStudioDesktopQA"
$created = $false
$start = (Get-Date).AddSeconds(-2) # Task Scheduler records whole seconds.
$resultDirectories = @($ResultDirectory)
$package = Get-AppxPackage -Name LazyingArt.LazyEditStudio.QA -ErrorAction SilentlyContinue
if ($package -and [IO.Path]::GetDirectoryName($Executable) -eq $package.InstallLocation) {
    # Packaged full-trust apps may redirect LocalAppData into their own cache.
    $resultDirectories += "$env:LOCALAPPDATA\Packages\$($package.PackageFamilyName)\LocalCache\Local\LazyEditStudio"
}
try {
    if ((Get-FileHash $Executable -Algorithm SHA256).Hash -ne $ExpectedSha256) { throw "Candidate executable digest mismatch" }
    if ((Get-Content $ReviewerCredentials -Raw | ConvertFrom-Json).username -eq "lachlanchen") { throw "Use an isolated reviewer, never the owner" }
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) { throw "An existing QA task must be reconciled first" }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $console = (Get-CimInstance Win32_ComputerSystem).UserName
    if ($console -ne $identity) { throw "Qualification needs this user's existing interactive console" }
    & icacls.exe $ReviewerCredentials /inheritance:r /grant:r ($identity + ":F") "SYSTEM:F" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not protect temporary credentials" }
    $action = New-ScheduledTaskAction -Execute $Executable -Argument ('--workspace-check "' + $ReviewerCredentials + '"')
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
    Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings | Out-Null
    $created = $true
    foreach ($directory in $resultDirectories) {
        $previous = Join-Path $directory "workspace-check.txt"
        if (Test-Path $previous) { Remove-Item $previous }
    }
    Start-ScheduledTask -TaskName $taskName
    $deadline = (Get-Date).AddSeconds(120)
    do {
        Start-Sleep -Seconds 2
        $info = Get-ScheduledTaskInfo -TaskName $taskName
        $state = (Get-ScheduledTask -TaskName $taskName).State
        if ($info.LastRunTime -ge $start -and $state -ne "Running" -and $state -ne "Queued") { break }
    } while ((Get-Date) -lt $deadline)
    if ($info.LastRunTime -lt $start -or $state -eq "Running" -or $state -eq "Queued") { throw "Native qualification timed out" }
    $results = @($resultDirectories | ForEach-Object { Join-Path $_ "workspace-check.txt" } | Where-Object { Test-Path $_ })
    if ($info.LastTaskResult -ne 0 -or $results.Count -ne 1) { throw "Native qualification failed; inspect the private result" }
    $result = $results[0]
    $text = Get-Content $result -Raw
    if (-not $text.StartsWith("PASS:")) { throw "Native qualification did not pass" }
    Write-Output $text
    [pscustomobject]@{host=$env:COMPUTERNAME; executableSha256=$ExpectedSha256; passed=$true; socialPostsCreated=$false; qualifiedAt=(Get-Date).ToUniversalTime().ToString("o")} | ConvertTo-Json -Compress
} finally {
    if ($created) {
        if ((Get-ScheduledTask -TaskName $taskName).State -in @("Running", "Queued")) { Stop-ScheduledTask -TaskName $taskName }
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    # This input is explicitly temporary; never delete the source account file.
    if (Test-Path $ReviewerCredentials) { Remove-Item $ReviewerCredentials }
}
