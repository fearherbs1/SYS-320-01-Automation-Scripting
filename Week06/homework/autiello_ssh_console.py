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

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
except paramiko.AuthenticationException:
    print("Authentication Failed")

# check if output file exists
if os.path.exists("output.txt"):
    # if it does ask the user if they want to delete it
    delfile = input("Output.txt already exists. Delete it? (y/n)\n\n")
    # if yes, delete it
    if delfile == "y":
        os.remove("output.txt")
        print("Old output.txt Deleted.")
    # if no, exit and keep the file
    elif delfile == "n":
        print("output file not deleted exiting...")
        exit(0)
    # if anything else, exit the program
    else:
        print("invalid answer. exiting...")
        exit(0)

# Our lists of commands to run
test_commands = ["ps -ef", "netstat -an --inet", "last -adx", "cut -d: -f1 /etc/passwd"]

list_bind_files_commands = ["cat /etc/resolv.conf", "cat /etc/motd", "cat /etc/issue", "cat /etc/passwd",
                            "cat /etc/shadow"]

system_commands = ["uname -a", "ps aux", "id", "w", "who -a"]

networking_commands = ["hostname -f", "ip addr show", "ip ro show", "ifconfig -a", "route -n"]

user_accounts_commands = ["cat /etc/passwd", "cat /etc/shadow", "cat /etc/group", "getent passwd", "getent group"]

obtain_user_info_commands = ["ls -alh /home/*/", "ls -alh /home/*/.ssh/", "cat /home/*/.ssh/authorized_keys",
                             "cat /home/*/.ssh/known_hosts", "crontab -l"]

credential_info_commands = ["ls /home/*/.ssh/id*", "ls /tmp/krb5cc_*", "ls /tmp/krb5.keytab",
                            "/home/*/.gnupg/secring.gpgs"]

gather_configs_commands = ["ls -aRl /etc/ * awk '$1 ~ /w.$/' * grep -v lrwx 2>/dev/nullte", "cat /etc/issue{,.net}",
                           "cat /etc/crontab", "cat /etc/sysctl.conf",
                           "for user in $(cut -f1 -d: /etc/passwd); do echo $user; crontab -u $user -l; done"]

determine_distro_commands = ["uname -a", "lsb_release -d", "cat /etc/os-release", "cat /etc/issue", "cat /etc/*release"]

installed_packages_commands = ["dpkg -l", "dpkg -l | grep -i “linux-image”", "dpkg --get-selections"]

package_sources_commands = ["cat /etc/apt/sources.list"]

important_files_commands = ["ls -alR | grep ^d", "find /var -type d", "ls -dl `find /var -type d`",
                            "ls -dl `find /var -type d` | grep -v root", "find /var ! -user root -type d -ls"]

# define a function that can run our commands
def run_commands(commands):

    for eachCMD in commands:
        # get the output from the command
        stdin, stdout, stderr = ssh.exec_command(eachCMD)

        # get results from stdout
        lines = stdout.readlines()
        # print(lines)

        # convert the list to a string
        output = ''.join(lines)

        # header output
        sepHeader = '' + '#### Begin ' + eachCMD + ' ####\n\n'
        sepFooter = '' + '#### End ' + eachCMD + ' ####\n\n'

        cmd_output = sepHeader + output + sepFooter
        # print(cmd_output)

        # save command output to file
        with open("output.txt", 'a') as f:
            f.write(cmd_output)
    ssh.close()

# call our function with some of the test commands.
run_commands(test_commands)
