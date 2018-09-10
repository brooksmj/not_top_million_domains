# not_top_million_domains
Syslog-NG configuration that reports domains not in top one million


For this scenario, you will have devices such as web proxies or DNS servers, that generate logs with domain names. It is relevant to your interests to compare domain names with the Majestic Million top one million referenced domains https://majestic.com/reports/majestic-million and notify when a domain is found in your logs that is not on the list.

This could be an indicator of an unsafe, spoofed and/or malicious domain, e.g. bankofӓmerica.com or recently registered as part of a malware campaign. Sounds good, what's the rub? 

The rub is that billion(s) of events are created daily and you would prefer to not dedicate SIEM resources to the task when much lower cost commodity resources will do the job. 

## *How does it work?*

The initial implementation of this uses VM with Ubuntu 18 with 4 cores and 8G of RAM and handles ~23k events per second before any packet loss. Given the high volume of data, instead of trying to pull the logs from the SIEM in real time, secondary syslog destinations were added to the sending devices to foward a copy of the event streams directly to the VM. 

Syslog-NG is running on the VM and uses a Python parser to load the million domain list, recieve the event, parse out the domain and make the comparison. The workflow is:
* If the domain is found on the list then the event is discarded. 
* If the domain is found on the whitelist, the the event is discarded.
* If the domain is not found on the list, it will append the phrase "Domain Not Found in Top Million" to the event and forward it onto the destination of your choice. 

None of the event data is stored on the VM.

Beyond that, there is a crontab entry to update top million list once a day.

    0 20 * * * /etc/syslog-ng/update_top_million.sh

## Requirements:
 * Syslog-NG 3.17
 * List of the top million domains
 * Something that generates syslogs with domains
 
## Setup:
* At a mininum you will need to modify the d_syslog output by either adding an IP address or changing it to a different destination.
* Change the field OFFSET setting. It's set to '21' on line 12 of the sample config. The OFFSET tells the parser which column the domain is in. I could have used regex to find it, but I didn't want the performance hit. 

Here is an example log:

```2018-09-05 18:17:35 647 10.10.10.44 ads231277.main.mydomain.com 200 TCP_NC_MISS 4412 2317 GET http http://www.yahoo.com/cbsinteractive-maxpreps/trc/3/json  www.yahoo.com 80 - /cbsinteractive-maxpreps/trc/3/json ?query=stuff http://www.yahoo.com/interactive-maxpreps/trc/3/json http://www.sample234.com/high-schools/grundy-county-yellowjackets-(coalmont,tn)/football/all_time_roster.htm ASD\funley funley - "Web Ads/Analytics" 2 www.yahoo.com application/javascript;%20charset=utf-8 "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko" OBSERVED Web%20Ads/Analytics - 10.10.83.11 80 http.proxy - - - - - - none - - application/javascript;%20charset=utf-8 10.1.202.2 United%20States - - - - - - none - none - -```

We can count fields, or use the little script in the repo called 'show_field_nums' if you want to make sure you're counting the same way the script is: 
```
$ python show_field_nums.py proxy.log
0: 2018-09-05
1: 18:17:35
2: 647
3: 10.10.10.44
4: ads231277.main.mydomain.com
5: 200
6: TCP_NC_MISS
7: 4412
8: 2317
9: GET
10: http
11: http://www.yahoo.com/cbsinteractive-maxpreps/trc/3
12: www.yahoo.com
13: 80
14: -
15: /cbsinteractive-maxpreps/trc/3/json
16: ?query=stuff
17: http://www.yahoo.com/interactive-maxpreps/trc/3/js
18: http://www.sample234.com/high-schools/grundy-count
19: ASD\funley
20: funley
21: -
22: "Web
23: Ads/Analytics"
---SNIP---
```
 
 
From this output, we can see '12' should be used as the OFFSET for this log as that is the column that has the domain name in the required format. 
 
## Notes:
 
 * This config uses syslog inputs and outputs but they could be changed to anything Syslog-NG supports.
 
 * The whitelist file has domains that should be ignored. If .gov is listed in the whitelist, all domains that end with .gov will be ignored. 
 
 * Single word domains and domains with an underscore are dropped as these are internal hosts.
