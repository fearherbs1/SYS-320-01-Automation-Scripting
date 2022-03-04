import paramiko
from getpass import getpass
import re
import os
from stat import S_ISDIR, S_ISREG

# print some cool art
print(
    '''
  _______ _                    _____ _         _        _    _             _            
 |__   __| |                  / ____| |       | |      | |  | |           | |           
    | |  | |__  _   _  __ _  | (___ | |_ _   _| | ___  | |__| |_   _ _ __ | |_ ___ _ __ 
    | |  | '_ \| | | |/ _` |  \___ \| __| | | | |/ _ \ |  __  | | | | '_ \| __/ _ \ '__|
    | |  | | | | |_| | (_| |  ____) | |_| |_| | |  __/ | |  | | |_| | | | | ||  __/ |   
    |_|  |_| |_|\__,_|\__, | |_____/ \__|\__, |_|\___| |_|  |_|\__,_|_| |_|\__\___|_| v1.0
                       __/ |              __/ | A Detector for APT 'ThugStyle' Activity
                      |___/              |___/ 
    Made by Thomas Autiello Jr 3/3/2021 
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
    # regex to remove ascii color codes from our output
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # list for our final lines
    cleaned_lines = []

    # open the output file clean the lines with regex and then append them to cleaned lines
    with open("k_output.txt") as f:
        lines = f.readlines()
        for line in lines:
            line = ansi_escape.sub('', line)
            cleaned_lines.append(line)

    # write the cleaned lines to a new file
    with open("k_output_cleaned.txt", "a+") as f2:
        f2.writelines(cleaned_lines)

    # Delete the old file
    if os.path.exists("k_output.txt"):
        os.remove("k_output.txt")


def get_pid():
    # regex match for the pid
    pid_regex = re.compile(r'pid=[0-9]+')
    # we don't want any snap in here
    snap = "process=snap"

    # open our cleaned file and use our pid regex to search for the suspicous pid
    with open("k_output_cleaned.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        # check all the lines
        for line in lines:
            # ignore snap
            if snap in line:
                continue
            # check for pid and if found return it
            else:
                pid_check = pid_regex.findall(line)
                if pid_check:
                    return pid_check[0].strip("pid=")


def lsof(sus_pid):
    # try to connnect back to our host fail if wrong password
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
    except paramiko.AuthenticationException:
        print("Authentication Failed")
        exit(0)

    # command to get our process associated files
    pid_cmd = f"sudo lsof -p {sus_pid}"

    # run the command
    stdin, stdout, stderr = ssh.exec_command(pid_cmd)
    cmd_output = stdout.read()

    # save the output of this command to a file
    with open("lsof_output.txt", "w") as f3:
        f3.writelines(cmd_output.decode())


def download_sus_files():
    # make some lists to save our found files
    files_match = []
    files = []

    # regex to match linux file paths
    file_path_regex = re.compile(r'(/[^/ ]*)+/?$')

    # look through our output and save all the regex match objects to a list
    with open("lsof_output.txt") as f:
        for line in f:
            result = file_path_regex.search(line)
            if result is not None:
                files_match.append(result)

    # grab the exact match from our match objects and append it to a list
    for file_obj in files_match:
        files.append(file_obj.group().strip())

    # regex to remove /dev/null
    remove_devnull = re.compile(r'/dev/null')

    # remove /dev/null entries from our list as that is not a valid file
    files_filtered_dev_null = [i for i in files if not remove_devnull.match(i)]

    # remove "/" from our list if it exists we do not want to donload the whole filesystem
    final_files = [i for i in files_filtered_dev_null if i != "/"]

    # try and connect back to our host, fail on bad password
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
    except paramiko.AuthenticationException:
        print("Authentication Failed")
        exit(0)

    # open sftp connection to that host
    sftp = ssh.open_sftp()

    # get the current dir
    current_dir = os.getcwd()

    print(f"Attempting to grab malicious files associated with the pid: {pid}...\n")

    # looping though our file list grab every file and save it to sus_files fail on io error
    for file in final_files:

        # get our results from the system
        try:
            sftp.get(file, f"{current_dir}\\sus_files\\{file.replace('/', '#')}")
            print(f"File: {file} Transferred.")

        except IOError:
            print(f"Error transferring file {file}, Is it even a real file?")

    # close sftp connection
    sftp.close()

    print("\nAll Files Grabbed and downloaded to the 'sus_files' directory. Note: '/'s have been replaced with '#'s.")


def search_for_other_activity():

    print("Attempting to search for more activity....\n")
    # try and connect back to our host, fail on bad password
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
    except paramiko.AuthenticationException:
        print("Authentication Failed")
        exit(0)

    # copy the files in question to our home dir and change the owner of them so we can download them
    ssh.exec_command("sudo cp /etc/passwd /home/thomas.autiello/passwd")
    ssh.exec_command("sudo cp /var/log/auth.log /home/thomas.autiello/auth.log")
    ssh.exec_command("sudo chown thomas.autiello /home/thomas.autiello/passwd")
    ssh.exec_command("sudo chown thomas.autiello /home/thomas.autiello/auth.log")

    # open sftp
    sftp = ssh.open_sftp()

    # get our files in question and save them to other-activity
    sftp.get("/home/thomas.autiello/passwd", f"other-activity\\#etc#passwd")
    sftp.get("/home/thomas.autiello/auth.log", f"other-activity\\#var#log#auth.log")

    # close our sftp conenction
    sftp.close()

    # command to get our process data
    get_processes = "ps -aux"
    # execute the command and read the output
    stdin, stdout, stderr = ssh.exec_command(get_processes)
    get_processes_output = stdout.read()

    # save the output to a file
    with open("other-activity\\ps_output.txt", "w") as f4:
        f4.writelines(get_processes_output.decode())

    # our regex patterns for matching thug life activity in the files
    thug_regex_log = re.compile(r'( [A-Za-z])\.([A-Za-z]+[0-1]+)|( [A-Za-z])\.([A-Za-z]+)')
    thug_regex = re.compile(r'([A-Za-z])\.([A-Za-z]+[0-1]+)|([A-Za-z])\.([A-Za-z]+)')

    # search through the log file:
    log_file_matches = []

    # open the log file and search through it
    with open("other-activity\\#var#log#auth.log") as f:
        for line in f:
            result = thug_regex_log.search(line)
            if result is not None:
                log_file_matches.append(line)

        # once all matches are found print them to the screen and save them to results.txt
        with open("other-activity\\results.txt", "a+") as f2:
            print("----------------------/VAR/LOG/AUTH.LOG FILE MATCHES----------------------\n")
            f2.write("----------------------/VAR/LOG/AUTH.LOG FILE MATCHES----------------------\n")
            for line in log_file_matches:
                f2.write(line)
                print(line)

    # search through the etc passwd file:
    passwd_file_matches = []

    # open the /etc/passwd file and search through it
    with open("other-activity\\#etc#passwd") as f:
        for line in f:
            result = thug_regex.search(line)
            if result is not None:
                passwd_file_matches.append(line)

        # once all matches are found print them to the screen and save them to results.txt
        with open("other-activity\\results.txt", "a+") as f2:
            print("----------------------/ETC/PASSWD FILE MATCHES----------------------\n")
            f2.write("----------------------/ETC/PASSWD FILE MATCHES----------------------\n")
            for line in passwd_file_matches:
                f2.write(line)
                print(line)

    # search through the etc passwd file:
    ps_matches = []

    # open the ps output file and search through it
    with open("other-activity\\ps_output.txt") as f:
        for line in f:
            result = thug_regex.search(line)
            if result is not None and "thomas.autiello" not in line and "oddjobd" not in line:
                ps_matches.append(line)

        # once all matches are found print them to the screen and save them to results.txt
        with open("other-activity\\results.txt", "a+") as f2:
            print("----------------------RUNNING PROCESS MATCHES----------------------\n")
            f2.write("----------------------RUNNING PROCESS MATCHES----------------------\n")
            for line in ps_matches:
                f2.write(line)
                print(line)

    print("Note: This other activity is also saved to /other-activity/results.txt")


def get_home_dir():
    # ask the user if they want to grab contents of a home dir
    sus_user_prompt = input("Is there a user you would like to download the home directory of? (y/n)")

    # if yes ask them for what user
    if sus_user_prompt == "y":
        # ask them what user
        sus_user = input("Ok, enter the username:\n")

        # Function to recursively download all files in a given dir
        # https://stackoverflow.com/questions/6674862/recursive-directory-download-with-paramiko
        def sftp_get_recursive(path, dest, sftp):
            item_list = sftp.listdir_attr(path)
            dest = str(dest)
            if not os.path.isdir(dest):
                os.makedirs(dest, exist_ok=True)
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    sftp_get_recursive(path + "/" + item.filename, dest + "/" + item.filename, sftp)
                else:
                    sftp.get(path + "/" + item.filename, dest + "/" + item.filename)

        # connect back to our host
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # run the function on the given home dir and save all the files to our output folder
        sftp_get_recursive(f"/home/{sus_user}", "home-dir-output", sftp)
        print(f"Home Dir of {sus_user} Downloaded!")

        # close the client connection.
        sftp.close()

    # if not exit the program
    else:
        print("Ok, Goodbye.")
        exit(0)


if __name__ == '__main__':
    # call kracken function
    kraken_scan()

    # call function to clean our output
    clean_output()

    # get our pid and save it
    pid = get_pid()

    # if the pid exists run the lsof function
    if pid:
        print(f"Suspicious pid: {pid} Found!\n")
        lsof(pid)
    else:
        print("No Suspicious Pid Found!\n")

    # call downloading the suspicious files
    download_sus_files()

    # call the funcion that searches for other activity
    search_for_other_activity()

    # call the function that can grab the home dir if the user wants
    get_home_dir()
