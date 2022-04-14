# create command line paramaters to coppy a file and place into an evidence directory

param(
    [Parameter(Mandatory = $true)]
    [int]$reportNo,

    [Parameter(Mandatory = $true)]
    [string]$filePath

)


# create a directory with a report number
$reportDir = "rpt$reportNo"

# creating a new directory
mkdir $reportDir

# copy the file into he new directory
Copy-Item $filePath $reportDir
