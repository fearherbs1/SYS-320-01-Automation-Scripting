# get a list of running processes


# Get a list of members
#Get-Process | Get-Member

# get a list of processes, extract name id and path
#Get-Process | Select-Object ProcessName, id, Path 

# save the output to csv
# Get-Process | Select-Object ProcessName, id, Path | Export-Csv -Path "C:\Github-Repos\SYS-320-01-Automation-Scripting\Week09\class\process-export.csv"


# System Services and properties

#Get-Service | Get-Member
$outputName = "C:\Github-Repos\SYS-320-01-Automation-Scripting\Week09\class\running-services-export.csv"

# Get-Service | Select-Object Status, Name, DisplayName, BinaryPathName | Export-Csv -Path $outputName

# Get a list of running services
Get-Service | Where-Object { $_.Status -eq "Running" } | Select-Object Status, Name, DisplayName, BinaryPathName | Export-Csv -Path $outputName

# Check to see if the file exists
if (Test-Path $outputName){

    Write-Host -BackgroundColor "Green" -ForegroundColor "white" "Services File was Created"

} else{
    Write-Host -BackgroundColor "Red" -ForegroundColor "white" "Services File was NOT Created"

}
