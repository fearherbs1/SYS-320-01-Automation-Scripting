<# Storyline: dropper for our spambot that will 
save to a dir and then execute it
#>

$writesbBot = @'

# send an email using powershell
$toSend = @('thomas.autiello@mymail.champlain.edu', 'thomas@mymail.champlain.edu', 'tom@mymail.champlain.edu')

# message body 
$msg = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse vel finibus orci. Donec condimentum, lorem sed cursus porta, nulla lacus porta leo, vel tempus elit ipsum vel est. Nam ac nisi cursus, finibus massa sit amet, elementum lacus. Cras erat elit, condimentum id nibh ut, facilisis congue augue. Sed ligula erat, mollis eget purus in, consequat porttitor tortor. Vestibulum in lorem eget eros elementum lacinia. Nulla sit amet finibus nisl. "

while($true){
    foreach ($email in $toSend){
        # send the email
        Write-Host "Send-MailMessage -From 'thomas.autiello@mymail.champlain.edu' -to $email -Subject 'Tisk Tisk' -Body $msg -SmtpServer x.x.x.x"

        Start-Sleep 1
    }
}
'@

# Directory to write
$sbDir = 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week10\class\'


# Create a random number to add to the file.
$sbRand = Get-Random -Minimum 1000 -Maximum 1999

# create the file and location to save the bot

$file = $sbDir + $sbRand + "winevent.ps1"
# write to file
$writesbBot | Out-File -FilePath $file

#execute the posershell wcript 
Invoke-Expression $file