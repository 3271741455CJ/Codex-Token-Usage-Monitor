param([Parameter(Mandatory=$true)][string]$Target)
$ErrorActionPreference = 'Stop'
if (-not $env:WINDOWS_CERTIFICATE_BASE64) { throw 'Signing certificate is not configured.' }
$certFile = Join-Path $env:RUNNER_TEMP 'monitor-signing.pfx'
try {
    [IO.File]::WriteAllBytes($certFile, [Convert]::FromBase64String($env:WINDOWS_CERTIFICATE_BASE64))
    $password = ConvertTo-SecureString $env:WINDOWS_CERTIFICATE_PASSWORD -AsPlainText -Force
    $cert = Get-PfxCertificate -FilePath $certFile -Password $password
    $result = Set-AuthenticodeSignature -LiteralPath $Target -Certificate $cert -HashAlgorithm SHA256 -TimestampServer 'http://timestamp.digicert.com'
    if ($result.Status -ne 'Valid') { throw 'Authenticode signature validation failed.' }
    $check = Get-AuthenticodeSignature -LiteralPath $Target
    if ($check.Status -ne 'Valid' -or -not $check.TimeStamperCertificate) { throw 'Signature or timestamp verification failed.' }
    Write-Output 'Authenticode signature and timestamp verified.'
} finally {
    if (Test-Path -LiteralPath $certFile) { Remove-Item -LiteralPath $certFile -Force }
}
