import paramiko
from getpass import getpass
import re
import os


# print some cool art
print(
    '''
  _____       _   _                   _______ _                    _     _    _             _            
 |  __ \     | | | |                 |__   __| |                  | |   | |  | |           | |           
 | |__) |   _| |_| |__   ___  _ __      | |  | |__  _ __ ___  __ _| |_  | |__| |_   _ _ __ | |_ ___ _ __ 
 |  ___/ | | | __| '_ \ / _ \| '_ \     | |  | '_ \| '__/ _ \/ _` | __| |  __  | | | | '_ \| __/ _ \ '__|
 | |   | |_| | |_| | | | (_) | | | |    | |  | | | | | |  __/ (_| | |_  | |  | | |_| | | | | ||  __/ |   
 |_|    \__, |\__|_| |_|\___/|_| |_|    |_|  |_| |_|_|  \___|\__,_|\__| |_|  |_|\__,_|_| |_|\__\___|_|   
         __/ | Version 1.0  by Thomas Autiello Jr                                                                                    
        |___/ 
    ''')

# Host Information
host = "192.168.6.71"
port = 2222
username = "thomas.autiello"
print(f"Loaded Host Information:\n host: {host}\n port: {port} \n username: {username}\n ")


# Create the password prompt
ssh_passwd = getpass(prompt="Please Enter your SSH Password: \n\n")
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

    # Run our hunt:
    command_hunt = "sudo ./kraken --folder /usr/bin --folder --folder /usr/sbin/ --folder /usr/local/bin --folder " \
                   "/sbin --folder /usr/local/sbin --folder /bin > /home/thomas.autiello/k_output.txt "

    # run our command that runs the script
    print("Running Kraken...\n")
    stdin, stdout, stderr = ssh.exec_command(command_hunt)
    stdin.write(ssh_passwd + "/n")

    # Wait until the command is done before exiting
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Done Running Kraken... \n")
    else:
        print("Error", exit_status)


    # open a new sftp session
    sftp = ssh.open_sftp()

    # get our results from the system

    sftp.get("/home/thomas.autiello/k_output.txt", "k_output.txt")

    # close the second sftp session
    sftp.close()

    # cose the ssh connection.
    ssh.close()


def clean_output():
    print("Cleaning Kraken output...\n")
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
    files_match = []
    files = []

    file_path_regex = re.compile(r'(/[^/ ]*)+/?$')
    with open("lsof_output.txt") as f:
        for line in f:
            result = file_path_regex.search(line)
            if result is not None:
                files_match.append(result)

    for file_obj in files_match:
        files.append(file_obj.group().strip())

    remove_devnull = re.compile(r'/dev/null')
    files_filtered_dev_null = [i for i in files if not remove_devnull.match(i)]

    final_files = [i for i in files_filtered_dev_null if i != "/"]

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
    except paramiko.AuthenticationException:
        print("Authentication Failed")
        exit(0)

    sftp = ssh.open_sftp()

    current_dir = os.getcwd()

    print(f"Attempting to grab malicious files associated with the pid: {pid}...\n")

    for file in final_files:

        # get our results from the system
        try:
            sftp.get(file, f"{current_dir}\\sus_files\\{file.replace('/', '#')}")
            print(f"File: {file} Transferred.")

        except IOError:
            print(f"Error transferring file {file}, Is it even a real file?")

    sftp.close()

    print("\nAll Files Grabbed and downloaded to the 'sus_files' directory. Note: '/'s have been replaced with '#'s.")


if __name__ == '__main__':

    kraken_scan()

    clean_output()

    pid = get_pid()

    if pid:
        print(f"Suspicious pid: {pid} Found!\n")
        lsof(pid)
    else:
        print("No Suspicious Pid Found!\n")

    download_sus_files()
