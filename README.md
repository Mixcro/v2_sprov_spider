# v2_sprov_spider
盖子上的盖子，给sprov_ui又套了一层。

## TODO
1. add comments for the code;
2. add log file;
3. add config file;
4. add std output;

## first run
```
wget https://raw.githubusercontent.com/Mixcro/v2_sprov_spider/master/spider.py
chmod +x spider.py
```

## use as script
```
USAGE: ./spider.py [cmd] [target]
    [cmd]: reset, check
    [target]: all, [user port]
EXAMPLE:
    ./spider.py reset all      # reset all user traffic
    ./spider.py check all      # check all user traffic and auto ban overload user
    ./spider.py reset 59603    # reset user's traffic whois port is 59603
  ```
    
## add to crontab
```
0 */6 * * * *  root  /root/spider.py check all  # check user traffic every 6 hours
0 0 1 * * *    root  /root/spider.py reset all  # reset all user traffic at every month's first day
```
