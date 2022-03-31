# send an email using powershell


$toSend = @('thomas.autiello@mymail.champlain.edu', 'thomas@mymail.champlain.edu', 'tom@mymail.champlain.edu')


# message body 
$msg = "hello"

while($true){
    foreach ($email in $toSend){
        # send the email
        Write-Host "Send-MailMessage -From 'thomas.autiello@mymail.champlain.edu' -to $email -Subject 'Tisk Tisk' -Body $msg -SmtpServer x.x.x.x"

        Start-Sleep 1
    }
}