# List the files in a directory 

# list all of the files and print the full path.
#Get-ChildItem -Recurse -Path .\Documents -Include *.docx,*.pdf*,*.txt | Select-Object FullName


Get-ChildItem -Recurse -Path .\Documents -Include *.docx,*.pdf*,*.txt | Export-Csv -Path files.csv

# import csv file
$filelist = Import-Csv -Path .\files.csv #-Header FullName


# loop throught the results
foreach ($f in $filelist){

    Get-ChildItem -Path $f.FullName

}
