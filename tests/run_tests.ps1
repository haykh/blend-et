param(
    [string]$Blender = $env:BLENDER_BIN,
    [ValidateSet("all", "volume", "fieldlines", "pointcloud", "annotations", "latex")]
    [string]$Feature = "all",
    [switch]$KeepArtifacts
)

$Arguments = @("$PSScriptRoot/run_tests.py", "--feature", $Feature)
if ($Blender) { $Arguments += @("--blender", $Blender) }
if ($KeepArtifacts) { $Arguments += "--keep-artifacts" }
python @Arguments
exit $LASTEXITCODE
