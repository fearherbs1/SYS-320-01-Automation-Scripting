# school ssh server 192.168.6.71 port 2222 
cls
# Login to a remote ssh server
#New-SSHSession -ComputerName '184.171.154.152' -Credential (Get-Credential systest)


<#
while ($True) {
    # Add a prompt to run commands
    $the_cmd = Read-Host -Prompt "Enter A command"

    # run a command on the remote ssh server
    (Invoke-SSHCommand -index 0 $the_cmd).Output

}
#>

# download File to system
Set-SCPItem -ComputerName '184.171.154.152' -Credential (Get-Credential systest) -Path "/home/systest/hi.txt" -PathType File -Destination ./

# Put File to system
Set-SCPItem -ComputerName '184.171.154.152' -Credential (Get-Credential systest) -Path ".\hi2.txt" -Destination "/home/systest/"