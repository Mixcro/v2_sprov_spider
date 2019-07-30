# v2_sprov_spider
盖子上的盖子，给sprov_ui又套了一层。

## TODO
1. add comments for the code;

## First run
```
wget https://raw.githubusercontent.com/Mixcro/v2_sprov_spider/master/spider.py
wget https://raw.githubusercontent.com/Mixcro/v2_sprov_spider/master/config.json  # change this file for your config
chmod +x spider.py
```

## Use as script
```
USAGE: ./spider.py [cmd] [target]
    [cmd]: reset, check
    [target]: all, [user port]
EXAMPLE:
    ./spider.py reset all      # reset all user traffic
    ./spider.py check all      # check all user traffic and auto ban overload user
    ./spider.py reset 59603    # reset user's traffic whois port is 59603
  ```

## Demonstration
![img](https://raw.githubusercontent.com/Mixcro/v2_sprov_spider/master/nothing/stdo.gif)

## Add to crontab
```
0 */6 * * * *  root  /root/spider.py check all  # check user traffic every 6 hours
0 0 1 * * *    root  /root/spider.py reset all  # reset all user traffic at every month's first day
```

## Config file
```
{
	"server": {
		"server_url": "server_url",
		"user": "user",
		"password": "passwd"
	},
	"traffic_limit": {
		"default_limit": 68719476736,  # 默认单用户月总流量限制，单位是byte
		"accounts": {
			"59603": 0,  # 此处可以单独设置使用某端口的用户流量限制
			"10086": 1024  # 0代表不限速
		}
	}
}
```
