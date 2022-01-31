from Autiello_syslog_check import _syslog
import re
# SSH authentication


def proxy_events_close(filename, service, term):
    # call syslog_check and return the results

    is_found = _syslog(filename, service, term)

    # found list
    found = []

    # loop through the results
    for each_found in is_found:
        # split the results based on the space dilimeter
        # print(each_found)
        each_found = re.sub(r" \(\d+\.\d+ (?:KB|MB|GB)\)", '', each_found)
        each_found = re.sub(r" \(\d+\d+ (?:KB|MB|GB)\)", '', each_found)
        # print(each_found)
        sp_results = each_found.split(" ")

        # append the split value to the found list
        # [07.27 10:05:03] QQProtectUpd.exe - qdun-data.qq.com:443 close, 261 bytes sent, 70 bytes received, lifetime <1 sec
        found.append(sp_results[2] + " " + sp_results[4] + " " + sp_results[6] + " " + sp_results[7] + " " + sp_results[8] + sp_results[9] + " " + sp_results[10] + " " + sp_results[11])

    # Remove our duplicates and convert the list to a dict
    values = set(found)
    # print our hosts on their own separate line
    for each_value in values:
        print(each_value)
