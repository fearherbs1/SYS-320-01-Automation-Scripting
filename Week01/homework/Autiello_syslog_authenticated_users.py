from Autiello_syslog_check import _syslog

# Authenticated ssh users


def authenticated_ssh_users(filename, search_terms):
    # call syslog_check and return the results

    is_found = _syslog(filename, search_terms)

    # found list
    found = []

    # loop through the results
    for each_found in is_found:
        # split the results based on the space dilimeter
        sp_results = each_found.split(" ")

        # append the split value to the found list
        found.append(sp_results[5])

    # Remove our duplicates and convert the list to a dict
    returned_values = set(found)
    # print our hosts on their own separate line
    for each_value in returned_values:
        print(each_value)
