6param(
  [switch]$ForceScan
)
$ShouldForceScan = if ($PSBoundParameters.ContainsKey('ForceScan')) { $ForceScan } else { $true } 