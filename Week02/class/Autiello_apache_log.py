from Autiello_syslog_check import _syslog

# SSH authentication


def apache_events(filename, service, term):
    # call syslog_check and return the results

    is_found = _syslog(filename, service, term)

    # found list
    found = []

    # loop through the results
    for each_found in is_found:
        # split the results based on the space dilimeter
        sp_results = each_found.split(" ")

        # append the split value to the found list
        # "POST /cgi-bin/test-cgi HTTP/1.1" 404 435 "-" "-"
        found.append(sp_results[3] + " " + sp_results[0] + " " + sp_results[1])

    # Remove our duplicates and convert the list to a dict
    values = set(found)
    # print our hosts on their own separate line
    for each_value in values:
        print(each_value)
