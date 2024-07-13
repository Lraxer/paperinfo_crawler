# chromedriver path
chromedriver_path = "D:/pycode/chromedriver-win64/chromedriver.exe"

# DBLP URL
dblp_url = "https://dblp.org/db/"

# User agent settings
user_agent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# ACM header for requests
req_headers = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
}


# conference -> publisher
conf_pub_dict = {
    "sp": "ieee",
    "csfw": "ieee",
    "eurosp": "ieee",
    "acsac": "acm",
    "ccs": "acm",
    "raid": "acm",
    "icics": "springer",
    "uss": "usenix",
    "ndss": "ndss",
}
# publisher -> conference
pub_conf_dict = {
    "ieee": {"sp", "csfw", "eurosp"},
    "acm": {"acsac", "ccs", "raid"},
    "springer": {"icics"},
    "usenix": {"uss"},
    "ndss": {"ndss"},
}
