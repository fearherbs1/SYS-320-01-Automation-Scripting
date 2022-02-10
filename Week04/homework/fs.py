#  File to traverse a given directory and it's subdires and reterive all the files.

import argparse
import os
import yaml


def load_files(directory):
    # check if the given argument is a directory
    if not os.path.isdir(directory):
        print(f"Invalid Directory => {directory}")
        exit()

    # list to save files
    f_list = []

    # Crawl through the provided directory
    for root, subfolders, filenames in os.walk(directory):

        for f in filenames:
            # windows
            # file_list = directory + "\\" + f

            # linux
            file_list = directory + "/" + f
            f_list.append(file_list)

    return f_list


def load_ruleset(ruleset):
    rules = []
    selected_ruleset = {}
    with open("rules.yaml", 'r') as f:
        try:
            for rule in yaml.load_all(f, Loader=yaml.SafeLoader):
                rules.append(rule)
        except yaml.YAMLError as exc:
            print(exc)

    for rule in rules:
        try:
            if rule[ruleset]:
                selected_ruleset = rule
        except KeyError:
            continue
    if selected_ruleset:
        return selected_ruleset
    else:
        print(f"Invalid Ruleset => {ruleset}")
        exit(0)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Searches a group of log files for threat indicators based on a given ruleset",
        epilog="Developed by Thomas Autiello 2022 02 10"
    )

    # directory argument
    parser.add_argument("-d", "--directory", required=True, help="Directory that you want to traverse")

    # ruleset argument
    parser.add_argument("-r", "--rules", required=True, help="Ruleset from rules.yaml that you would like to use")

    # parse the arguments
    args = parser.parse_args()

    # load the values of our arguments into their respective variables
    root_dir = args.directory
    rule_set = args.rules

    # load our files
    files = load_files(root_dir)

    # load our ruleset
    rules = load_ruleset(rule_set)

    print(rules)




