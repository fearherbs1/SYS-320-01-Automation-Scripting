# http://rules.emergingthreats.net/blockrules/emerging-botcc.rules
# https://rules.emergingthreats.net/blockrules/compromised-ips.txt


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


# get the ip addresses dicoverd, loop throught them and replace the begining of the line wiht iptables syntax
# after the ip address, add the remaining IPTables sysntax and save the results to a file. 
# iptables -A INPUT -s 108.191.2.72 -j DROP
(Get-Content -Path ".\ips-bad.tmp") | ForEach-Object `
{$_ -replace "^", "iptables -A INPUT -s "-replace "$", " -j DROP"} | Out-File -FilePath "iptables.bash"
