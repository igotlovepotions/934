param([string]$caso)
$dest = "resultados\$caso"
New-Item -ItemType Directory -Force $dest | Out-Null
$padroes = "ieee37_Mon_*","ieee37_MONITOR*","ieee37_Power.*","ieee37_VLN.Txt","ieee37_Losses.Txt","ieee37_Isolated.Txt","ieee37_Profile*","*_overloads.csv","*_voltages.csv"
foreach ($p in $padroes) { Move-Item $p $dest -Force -ErrorAction SilentlyContinue }
if (Test-Path ieee37) { Move-Item ieee37 $dest -Force }