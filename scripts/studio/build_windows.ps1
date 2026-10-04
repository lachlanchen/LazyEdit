# Run on Windows with the shared .NET 10 SDK, not a separate SDK per project.
param([string]$Root = (Resolve-Path "$PSScriptRoot\..\.."), [string]$DotNet = "dotnet")
$ErrorActionPreference = "Stop"
$project = Join-Path $Root "mobile\windows\LazyEditStudio.csproj"
$output = Join-Path $Root "temp\desktop\windows-x64"
& $DotNet publish $project -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -p:DebugType=None -o $output
if ($LASTEXITCODE -ne 0) { throw "Windows publish failed" }
$test = Start-Process -FilePath (Join-Path $output "LazyEditStudio.exe") -ArgumentList "--contract-test" -Wait -PassThru
if ($test.ExitCode -ne 0) { throw "Windows contract test failed" }
$archive = Join-Path $Root "temp\desktop\LazyEditStudio-windows-x64-1.0.0.zip"
Compress-Archive -Path "$output\*" -DestinationPath $archive -Force
Get-FileHash $archive -Algorithm SHA256 | Select-Object Algorithm,Hash
Write-Output "Prepared native Windows package. No Microsoft Store submission or code-signing claim."
