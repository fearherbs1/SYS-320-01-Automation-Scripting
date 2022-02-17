import argparse
import os
import yaml
import re
import csv
import pandas

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
    # intit our rules list
    rules = []
    # init our selected ruleset dict
    selected_ruleset = {}
    # open our rules.yaml file
    with open("rules.yaml", 'r') as f:
        try:
            # uoad all of the books within the yaml file and append them to the rules list
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
    parser.add_argument("-r", "--rules", required=True, help="Ruleset from rules.yaml that you would like to use. use \"all\" to use all of the rules found in the rules.yaml file.")

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

    #print(rule_def)


    # create an empty list to store our output if it is going to be saved to a file
    file_output_list = []

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
                    # loop through all of that rules attributes
                    for rule_name, attributes in rule.items():
                        # Save all these attributes to values we can use
                        description = attributes["Description"]
                        references = attributes["References"]
                        detections = attributes["Detections"]
                        for detection in detections:
                            if detection in arguments:
                                print(path)











    #         for csv in log_lines:
    #             # loop through all of our rules
    #             for rule, definition in rule_def.items():
    #                 # search the file for out match
    #                 if re.search(definition, log_line):
    #                     # if output file is defined, save the match to our output list
    #                     if output_f:
    #                         match = f"Rule: {rule} Has been matched in Ruleset: {rule_set} Within File: {file}\n" \
    #                                 f"Matched Log Entry:{log_line}\n\n"
    #                         file_output_list.append(match)
    #                     # if no output is defined print the results to the console with color coding
    #                     else:
    #                         log_line = re.sub(definition, f"{C.FAIL}{definition}{C.ENDC}", log_line)
    #                         print(f"{C.WARNING}Rule: {C.FAIL}{rule}{C.WARNING} Has been matched in Ruleset: {C.WARNING}"
    #                               f"{rule_set} {C.WARNING} Within File: {C.OKCYAN}{file}{C.ENDC}\n"
    #                               f"{C.OKBLUE}Matched Log Entry:{C.ENDC} {log_line}\n\n")
    #
    # # if an ouput file is provided and matches exist
    # if output_f and match:
    #     # open our output file
    #     with open(output_f, "w+") as f:
    #         # loop through our list and write all of our matches
    #         for match in file_output_list:
    #             f.write(match)
