# chromedriver path
chromedriver_path = "D:/pycode/chromedriver-win64/chromedriver.exe"


# Interval in seconds to wait for retrying after a failed request
retry_interval = 15

# DBLP URL
dblp_url = "https://dblp.org/db/"

# User agent settings
user_agent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

# ACM header for requests
req_headers = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
}

# cookie path
cookie_path = "D:/pycode/chromedriver-user-data/"

# conference/journal -> publisher
cj_pub_dict = {
    # conference
    "sp": "ieee",
    "csfw": "ieee",
    "dsn": "ieee",
    "eurosp": "ieee",
    "trustcom": "ieee",
    "infocom": "ieee",
    "icde": "ieee",
    "icnp": "ieee",
    "iwqos": "ieee",
    "acsac": "acm",
    "ccs": "acm",
    "kdd": "acm",
    "sigir": "acm",
    "raid": "acm",
    "mobicom": "acm",
    "sigcomm": "acm",
    "conext": "acm",
    "imc": "acm",
    "asiaccs": "acm",
    "icics": "springer",
    "iccS": "springer",
    "esorics": "springer",
    "dimva": "springer",
    "uss": "usenix",
    "ndss": "ndss",
    # journal
    "jsac": "ieee",
    "tcom": "ieee",
    "tdsc": "ieee",
    "tifs": "ieee",
    "tkde": "ieee",
    "tmc": "ieee",
    "ton": "ieee",
    "twc": "ieee",
    "tissec": "acm",
    "tkdd": "acm",
    "toit": "acm",
    "cybersec": "springer",
    "vldb": "springer",
    "cn": "elsevier",
    "compsec": "elsevier",
    "istr": "elsevier",
    "iot": "elsevier",
    "jcs": "iospress",
}
# publisher -> conference/journal
pub_cj_dict = {
    "ieee": {
        "sp",
        "csfw",
        "dsn",
        "eurosp",
        "trustcom",
        "tdsc",
        "tifs",
        "tkde",
        "infocom",
        "jsac",
        "tmc",
        "ton",
        "tcom",
        "twc",
        "icde",
        "icnp",
        "iwqos",
    },
    "acm": {
        "acsac",
        "ccs",
        "mobicom",
        "kdd",
        "sigcomm",
        "sigir",
        "raid",
        "tissec",
        "tkdd",
        "toit",
        "conext",
        "imc",
        "asiaccs",
    },
    "springer": {"icics", "cybersec", "iccS", "esorics", "vldb", "dimva"},
    "usenix": {"uss"},
    "ndss": {"ndss"},
    "elsevier": {"cn", "compsec", "istr", "iot"},
    "iospress": {"jcs"},
}
