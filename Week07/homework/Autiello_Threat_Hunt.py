import paramiko
from getpass import getpass
import re
import time
import os

"""
Known Info:
- account format letter.lastname with sometimes a 01 at end.
- authed useing ssh
- pseudo random file name of well known linux command but stored in a "/bin" dir to evade detection
- files are under 600k in size
- high entropy filenames lowercase letters between 6 and 17 characters
- packed using upx
- lead to admin from local priv esc vuln
- some binerys listen on a port always owned by the malicious user
- all bineries are written in go

"""
# Create the password prompt
ssh_passwd = getpass(prompt="Please Enter your SSH Password: \n\n")

# Host Information
host = "192.168.6.71"
port = 2222
username = "thomas.autiello"
password = ssh_passwd


def kraken_scan():
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
    file = "kraken"

    # upload the script
    sftp.put(file, "/home/thomas.autiello/kraken")

    # close our sftp session
    sftp.close()
    # make the file executeable:
    command_exec = "sudo chmod +x ./kraken"
    stdin, stdout, stderr = ssh.exec_command(command_exec)

    # send in our sudo password
    # stdin.write(ssh_passwd + "/n")

    # Run our hunt:
    command_hunt = "sudo ./kraken --folder /usr/bin --folder --folder /usr/sbin/ --folder /usr/local/bin --folder /sbin --folder /usr/local/sbin --folder /bin > /home/thomas.autiello/k_output.txt"

    # run our command that runs the script
    print("Running Kraken...")
    stdin, stdout, stderr = ssh.exec_command(command_hunt)
    stdin.write(ssh_passwd + "/n")

    # Wait until the command is done before exiting
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Done Running Kraken")
    else:
        print("Error", exit_status)

    # cmd_output = stdout.read()
    # print(cmd_output.decode())

    # wait for our command to finish before we grab the results:
    # time.sleep(20)

    # open a new sftp session
    sftp = ssh.open_sftp()

    # get our results from the system

    sftp.get("/home/thomas.autiello/k_output.txt", "k_output.txt")

    # close the second sftp session
    sftp.close()

    # cose the ssh connection.
    ssh.close()


def clean_output():
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    cleaned_lines = []

    with open("k_output.txt") as f:
        lines = f.readlines()
        for line in lines:
            line = ansi_escape.sub('', line)
            cleaned_lines.append(line)

    with open("k_output_cleaned.txt", "a+") as f2:
        f2.writelines(cleaned_lines)

    if os.path.exists("k_output.txt"):
        os.remove("k_output.txt")


def get_pid():

    pid_regex = re.compile(r'pid=[0-9]+')
    snap = "process=snap"

    with open("k_output_cleaned.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if snap in line:
                continue
            else:
                pid_check = pid_regex.findall(line)
                if pid_check:
                    return pid_check[0].strip("pid=")


def lsof(sus_pid):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
    except paramiko.AuthenticationException:
        print("Authentication Failed")
        exit(0)

    pid_cmd = f"sudo lsof -p {sus_pid}"
    stdin, stdout, stderr = ssh.exec_command(pid_cmd)
    cmd_output = stdout.read()
    with open("lsof_output.txt", "w") as f3:
        f3.writelines(cmd_output.decode())


def download_sus_files():
    files = []

    file_path_regex = re.compile(r'(/[^/ ]*)+/?$')
    with open("lsof_output.txt") as f:
        for line in f:
            result = file_path_regex.search(line)
            if result is not None:
                files.append(result)

    for file in files:
        print(file.group())


# kraken_scan()
#
# clean_output()
#
# pid = get_pid()
#
# lsof(pid)

download_sus_files()
