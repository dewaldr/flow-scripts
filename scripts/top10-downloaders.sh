#!/bin/dash

# Report the top 10 internet downloaders: yesterday, today and month

<<<<<<< Updated upstream
SOURCE_GLOB='/var/flows/edenrouter/*/*/*/ft-v05.*'
=======
SOURCE_GLOB='/var/flows/max/*/*/*/ft-v05.*'
>>>>>>> Stashed changes
HOSTNAME=$(hostname -f)
REPORTTIME=$(/bin/date '+%Y-%m-%d %H:%M:%S')
YESTERDAY=$(/bin/date '+%Y-%m-%d' -d "yesterday")
TODAY=$(/bin/date '+%Y-%m-%d')
THISMONTH=$(/bin/date '+%Y-%m')
FIRSTOFMTH="$THISMONTH-01"
HEADER1="IP Address\t\tHostname\t\t\t\t\tMBytes"
HEADER2="==============\t\t=======================================\t\t======"

AWK_SCRIPT='
    {
        if (($2 ~ /^192\.168\.11\..+/) && ($1 !~ /^192\.168\.11\..+/) && ($1 !~ /^192\.168\.1\..+/)) {
            ip_arr[$2]+=$4;
       }
    } 
    END { 
        PROCINFO["sorted_in"] = "@val_num_desc"; 
        for(ip in ip_arr) {
            host_str=ip" ---"; 
            "getent hosts " ip | getline host_str; 
            split(host_str, host_arr, " "); 
            printf "%-16s\t%-40s\t%dM\n", ip, host_arr[2], (ip_arr[ip]/(1048576))
        }
    }'

echo "\t---=(Top 10 downloaders: yesterday [$YESTERDAY])=---\n"
echo "$HEADER1"
echo "$HEADER2"
/usr/bin/flow-cat -t "$YESTERDAY" -T "$TODAY" $SOURCE_GLOB \
    | /usr/bin/flow-stat -f10 -S3 \
    | /usr/bin/awk "$AWK_SCRIPT" \
    | /usr/bin/head -10

echo "\n\n\t---=(Top 10 downloaders: today [$TODAY])=---\n"
echo "$HEADER1"
echo "$HEADER2"
/usr/bin/flow-cat -t "$TODAY 00:00:00" -T "$TODAY 23:59:59" $SOURCE_GLOB \
    | /usr/bin/flow-stat -f10 -S3 \
    | /usr/bin/awk "$AWK_SCRIPT" \
    | /usr/bin/head -10

echo "\n\n\t---=(Top 10 downloaders: month [$THISMONTH])=---\n"
echo "$HEADER1"
echo "$HEADER2"
/usr/bin/flow-cat -t "$FIRSTOFMTH 00:00:00" -T "$TODAY 23:59:59" $SOURCE_GLOB \
    | /usr/bin/flow-stat -f10 -S3 \
    | /usr/bin/awk "$AWK_SCRIPT" \
    | /usr/bin/head -10

echo "\nReported on $HOSTNAME at $REPORTTIME"
