# Create an interface to search through syslog files
import re
import sys
import yaml

# open the yaml file

try:
    with open('Autiello_search_terms.yaml') as yf:
        keywords = yaml.safe_load(yf)

except EnvironmentError as e:
    print(e.strerror)


def _syslog(filename, service, term):

    # queries the yaml file for term or directive
    # retrieve the strings to search on

    terms = keywords[service][term]

    # split the values based on a comma
    list_of_keywords = terms.split(",")

    # Open a file
    with open(filename) as f:
        # read file and save it into a variable
        contents = f.readlines()

    # list to store our results
    results = []

    # Loop through the list of lines returned, each element is a line from the small smallSyslog file
    for line in contents:
        # loops through all of our keywords
        for eachKeyword in list_of_keywords:
            # if the 'line' contains the keyword, then print it out
            # if eachKeyword in line:
            # searches and returns results using a regex search
            x = re.findall(r''+eachKeyword+'', line)

            for found in x:
                # append the returned keywords to the results list
                results.append(found)

    # check to see if there are results
    if len(results) == 0:
        print("No Results")
        sys.exit(1)

    # sort the list
    results = sorted(results)

    return results
    # print(x)
