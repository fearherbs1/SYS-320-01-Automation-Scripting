import paramiko
from getpass import getpass
import os

# Create the password prompt
thePass = getpass(prompt="Please Enter your SSH Password: \n\n")

# Host Information
host = "184.171.154.66"
port = 22
username = "systest"
password = thePass

# attempt to get our ssh connection, exit on bad password
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
except paramiko.AuthenticationException:
    print("Authentication Failed")
    exit(0)


# Send our python script to the server:
sftp = ssh.open_sftp()

# The name of the script to upload
file = "fs.py"

# upload the script
sftp.put(file, "/usr/bin/fs.py")

# close our sftp session
sftp.close()

# set up our command:
command = "sudo -s python3 ./usr/bin/fs.py -d '/usr/bin' > /usr/bin/fs-output.body"

# run our command that runs the script
stdin, stdout, stderr = ssh.exec_command(command)

# open a new sftp session
sftp = ssh.open_sftp()

# get our results from the system
sftp.get("/usr/bin/fs-output.body", "fs-output.body")

# close the second sftp session
sftp.close()

# cose the ssh connection.
ssh.close()
