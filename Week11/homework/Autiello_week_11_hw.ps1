# array of websites containing the threat intel
$drop_urls = @('https://rules.emergingthreats.net/blockrules/emerging-botcc.rules', 'https://rules.emergingthreats.net/blockrules/compromised-ips.txt')

# loop throught the urls for the rules list
foreach ($u in $drop_urls){

    # extract thr filename
    $temp = $u.Split("/")
    
    # the last element in the array plucked off is the filename
    $file_name = $temp[-1]

    if (Test-Path $file_name){
    # Download the rules list
        continue
    } else {
        Invoke-WebRequest -Uri $u -OutFile $file_name
    } # close if statement
} # close loop

# array contining the filenames
$input_paths = @('.\compromised-ips.txt','.\emerging-botcc.rules')

# 108.231.32.4
# extract the Ip addresses
$regex_drop = '\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'


# append the ip addresses to the tempory IP list
Select-String -Path $input_paths -Pattern $regex_drop | ForEach-Object {$_.Matches} | `
ForEach-Object {$_.Value} | Sort-Object | Get-Unique | Out-File -FilePath "ips-bad.tmp"

# Ask the user what system they want to write the rules for and take their input
$os_selection = Read-Host -Prompt "Ip download complete, Please enter windows or iptables"


# check what the user selected
if ($os_selection -eq "windows"){
    # netsh advfirewall firewall add rule name="BLOCK MALICIOUS IP (script)" dir=in action=block remoteip=10.10.10.10

    # Set up our ip list in windows firewall format and save it to a windows bat file
    (Get-Content -Path ".\ips-bad.tmp") | ForEach-Object `
    {"netsh advfirewall firewall add rule name=`"BLOCK MALICIOUS IP $_`" dir=in action=block remoteip=$_"} | Out-File -FilePath "windows.bat"

}
elseif ($os_selection -eq "iptables"){
    # Set up our ip list in iptables format and save to iptables.bash
    (Get-Content -Path ".\ips-bad.tmp") | ForEach-Object `
    {$_ -replace "^", "iptables -A INPUT -s "-replace "$", " -j DROP"} | Out-File -FilePath "iptables.bash"

    # Put File to our linux system
    Set-SCPItem -ComputerName '184.171.154.152' -Credential (Get-Credential systest) -Path ".\iptables.bash" -Destination "/home/systest/"
}