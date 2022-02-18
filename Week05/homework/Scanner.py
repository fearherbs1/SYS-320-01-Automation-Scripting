import argparse
import os
import textwrap
import yaml
import csv


class C:
    """
    A class that defines the ASCII control characters to color the terminal
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_files(directory):
    # check if the given argument is a directory
    if not os.path.isdir(directory):
        print(f"Invalid Directory => {directory}")
        exit()

    # list to save files
    f_list = []

    # Crawl through the provided directory
    for root, subfolders, filenames in os.walk(directory):
        # loop through every file and add the root to it.
        for f in filenames:
            # windows
            # file_list = directory + "\\" + f

            # linux
            file_list = directory + "/" + f
            f_list.append(file_list)
    return f_list


def load_ruleset(ruleset):
    # init our rules list
    rules = []
    # init our selected ruleset dict
    selected_ruleset = {}
    # open our rules.yaml file
    with open("rules.yaml", 'r') as f:
        try:
            # Load all the books within the yaml file and append them to the rules list
            for rule in yaml.load_all(f, Loader=yaml.SafeLoader):
                rules.append(rule)
        # if there is a yaml error catch it and print the error
        except yaml.YAMLError as exc:
            print(exc)

    # check if all rules are selected
    if ruleset == "all":
        selected_ruleset = rules

    # loop through all of the rules
    for rule in rules:
        # attempt to match the given ruleset to one present in the config file
        try:
            if rule[ruleset]:
                selected_ruleset = rule
        except KeyError:
            continue
    # if the ruleset is validated return it
    if selected_ruleset:
        return selected_ruleset
    # if not tell the user they entered an invalid ruleset.
    else:
        print(f"Invalid Ruleset => {ruleset}")
        exit(0)
        return None


if __name__ == "__main__":  # our main function
    # set up our arg parser
    parser = argparse.ArgumentParser(
        description="Searches a group of log files for threat indicators based on a given ruleset",
        epilog="Developed by Thomas Autiello 2022 02 17"
    )

    # directory argument
    parser.add_argument("-d", "--directory", required=True, help="Directory with your logs.")

    # ruleset argument
    parser.add_argument("-r", "--rules", required=True, help="Ruleset from rules.yaml that you would like to use. use "
                                                             "\"all\" to use all of the rules found in the rules.yaml"
                                                             " file.")

    # save to file arg
    parser.add_argument("-o", "--output", required=False, help="Output results to a file rather than the screen.")

    # parse the arguments
    args = parser.parse_args()

    # load the values of our arguments into their respective variables
    root_dir = args.directory
    rule_set = args.rules
    output_f = args.output

    # load our files
    files = load_files(root_dir)

    # load our ruleset
    rules = load_ruleset(rule_set)
    # print(rules)

    # load our rule definitions if all was not selected put the single rule set in a list
    if rule_set == "all":
        rule_def = rules
    else:
        rule_def = [rules]

    # Loop through our list of files
    for file in files:
        # open our file and convert it into a dict & force utf-8 encoding
        with open(file, 'r', encoding='utf-8') as data:
            # save our csv data to a dict
            csv_data = csv.DictReader(data)
            # loop through each dick
            for line in csv_data:
                # set our values to variables we can work with from the dict
                # index = line[""]
                arguments = line["arguments"]
                hostname = line["hostname"]
                name = line["name"]
                path = line["path"]
                pid = line["pid"]
                username = line["username"]
                # loop through all of our rules that were selected
                for rule in rule_def:
                    # get the current rule name
                    current_rule = list(rule.keys())[0]
                    # loop through all of that rules attributes
                    for rule_name, attributes in rule.items():
                        # Save all these attributes to values we can use
                        description = attributes["Description"]
                        references = attributes["References"]
                        detections = attributes["Detections"]
                        # loop through all of our detections
                        for detection in detections:
                            # Check if the detection string is within the arguments from the log
                            if detection in arguments:
                                # if the output file is specified output to it
                                if output_f:
                                    formatted_detection_f = f"===========================================" \
                                                            f"===========================\n" \
                                                            f"Detection: {current_rule}\n\n" \
                                                            f"Description: {textwrap.fill(description)}\n\n" \
                                                            f"References: {*references,}\n" \
                                                            f"  Arguments: {arguments}\n" \
                                                            f"  Hostname: {hostname}\n" \
                                                            f"  Name: {name}\n" \
                                                            f"  Path: {path}\n" \
                                                            f"  Pid: {pid}\n" \
                                                            f"  Username: {username}\n\n\n"
                                    # Open the file to save the output
                                    with open(output_f, "a+", encoding='utf-8') as f:
                                        f.write(formatted_detection_f)
                                # if no output file, use fancy colors to print to screen
                                else:
                                    # Make the string that caused the detection red.
                                    red_args = arguments.replace(detection, f"{C.FAIL}{detection}{C.WARNING}")
                                    formatted_detection = f"==================================================" \
                                                          f"====================\n" \
                                                          f"{C.FAIL}Detection: {C.WARNING}{current_rule}{C.ENDC}\n\n" \
                                                          f"{C.OKCYAN}Description: {C.WARNING}" \
                                                          f"{textwrap.fill(description)}{C.ENDC}\n\n" \
                                                          f"{C.HEADER}References: {C.WARNING}{*references,}{C.ENDC}\n" \
                                                          f"  {C.OKGREEN}Arguments: {C.WARNING}{red_args}{C.ENDC}\n" \
                                                          f"  {C.OKBLUE}Hostname: {C.WARNING}{hostname}{C.ENDC}\n" \
                                                          f"  {C.OKCYAN}Name: {C.WARNING}{name}{C.ENDC}\n" \
                                                          f"  {C.HEADER}Path: {C.WARNING}{path}{C.ENDC}\n" \
                                                          f"  {C.OKGREEN}Pid: {C.WARNING}{pid}{C.ENDC}\n" \
                                                          f"  {C.OKBLUE}Username: {C.WARNING}{username}{C.ENDC}\n\n"
                                    print(formatted_detection)
                            else:
                                pass
