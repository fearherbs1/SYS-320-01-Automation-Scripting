from Autiello_syslog_check import _syslog
import re
# SSH authentication


def proxy_events_open(filename, service, term):
    # call syslog_check and return the results

    is_found = _syslog(filename, service, term)

    # found list
    found = []

    # loop through the results
    for each_found in is_found:
        # split the results based on the space dilimeter
        sp_results = each_found.split(" ")

        # append the split value to the found list
        # [10.30 17:47:23] QQ.exe - cgi.qqweb.qq.com:80 open through proxy proxy.cse.cuhk.edu.hk:5070 HTTPS
        found.append(sp_results[2] + " " + sp_results[4] + " " + sp_results[5] + " " + sp_results[6] + " " + sp_results[7] + " " + sp_results[8])

    # Remove our duplicates and convert the list to a dict
    values = set(found)
    # print our hosts on their own separate line
    for each_value in values:
        print(each_value)
