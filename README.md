# 爬取论文元数据和摘要

**注意，本项目不会下载论文，仅获取包括摘要在内的论文元数据。**

## 当前确认支持的会议/期刊

**包含摘要的 bibtex 文件可以从 [这里](https://github.com/Lraxer/paper_metadata) 获取。**

| 名称                                                                           | 类型         | 标识      | 出版社标识 | 已测试 |
| ------------------------------------------------------------------------------ | ------------ | --------- | ---------- | ------ |
| Annual ACM Conference on Computer and Communications Security (CCS)            | 会议 (CCF-A) | `ccs`     | `acm`      | ✔️     |
| IEEE Symposium on Security and Privacy (S&P)                                   | 会议 (CCF-A) | `sp`      | `ieee`     | ✔️     |
| USENIX Security Symposium (USENIX Security)                                    | 会议 (CCF-A) | `uss`     | `usenix`   | ✔️     |
| Network and Distributed System Security Symposium (NDSS)                       | 会议 (CCF-A) | `ndss`    | `ndss`     | ✔️     |
| ACM SIGCOMM Conference (SIGCOMM)                                               | 会议 (CCF-A) | `sigcomm` | `acm`      | ✔️     |
| IEEE Conference on Computer Communications (INFOCOM)                           | 会议 (CCF-A) | `infocom` | `ieee`     | ✔️     |
| IEEE Transactions on Dependable and Secure Computing (TDSC)                    | 期刊 (CCF-A) | `tdsc`    | `ieee`     | ✔️     |
| IEEE Transactions on Information Forensics and Security (TIFS)                 | 期刊 (CCF-A) | `tifs`    | `ieee`     | ✔️     |
| IEEE Journal of Selected Areas in Communications (JSAC)                        | 期刊 (CCF-A) | `jsac`    | `ieee`     | ✔️     |
| IEEE Transactions on Mobile Computing (TMC)                                    | 期刊 (CCF-A) | `tmc`     | `ieee`     | ✔️     |
| IEEE/ACM Transactions on Networking (TON)                                      | 期刊 (CCF-A) | `ton`     | `ieee`     | ✔️     |
| Annual Computer Security Applications Conference (ACSAC)                       | 会议 (CCF-B) | `acsac`   | `acm`      | ✔️     |
| IEEE Computer Security Foundations Workshop (CSFW)                             | 会议 (CCF-B) | `csfw`    | `ieee`     | ✔️     |
| International Symposium on Research in Attacks, Intrusions and Defenses (RAID) | 会议 (CCF-B) | `raid`    | `acm`      | ✔️     |
| IEEE International Conference on Network Protocols (ICNP)                      | 会议 (CCF-B) | `icnp`    | `ieee`     | ✔️     |
| IEEE/ACM International Workshop on Quality of Service (IWQoS)                  | 会议 (CCF-B) | `iwqos`   | `ieee`     | ✔️     |
| Conference on Emerging Network Experiment and Technology (CoNEXT)              | 会议 (CCF-B) | `conext`  | `acm`      | ✔️     |
| ACM/SIGCOMM Internet Measurement Conference (IMC)                              | 会议 (CCF-B) | `imc`     | `acm`      | ✔️     |
| Computer Networks (CN)                                                         | 期刊 (CCF-B) | `cn`      | `elsevier` | ✔️     |
| IEEE Transactions on Communications (TCOM)                                     | 期刊 (CCF-B) | `tcom`    | `ieee`     | ✔️     |
| Computers & Security                                                           | 期刊 (CCF-B) | `compsec` | `elsevier` | ✔️     |
| ACM Transactions on Privacy and Security (TOPS)                                | 期刊 (CCF-B) | `tissec`  | `acm`      | ✔️     |
| IEEE Transactions on Wireless Communications (TWC)                             | 期刊 (CCF-B) | `twc`     | `ieee`     | ✔️     |
| ACM Transactions on Internet Technology (TOIT)                                 | 期刊 (CCF-B) | `toit`    | `acm`      | ✔️     |
| IEEE European Symposium on Security and Privacy (EuroS&P)                      | 会议 (CCF-C) | `eurosp`  | `ieee`     | ✔️     |
| International Conference on Information and Communication Security (ICICS)     | 会议 (CCF-C) | `icics`   | `springer` | ✔️     |
| Journal of Information Security and Applications (JISA)                        | 期刊 (CCF-C) | `istr`    | `elsevier` | ✔️     |
| Internet of Things (IOT)                                                       | 期刊 (CCF-C) | `iot`     | `elsevier` | ✔️     |

## 安装

为了稳定运行 selenium，建议下载 [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)，并在 `settings.py` 中修改 `chromedriver_path`。

```powershell
# For Windows
cd paperinfo_crawler
python -m venv ./venv
.\venv\Scripts\activate
pip install -r requirements-no-version.txt
```

```bash
# For Linux
cd paperinfo_crawler
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements-no-version.txt
```

## 运行

```powershell
cd src
python ./main.py --help

# e.g.
python ./main.py -n raid -y 2022
```

## 测试平台

### OS

- [x] Windows
- [ ] Linux
- [ ] MacOS

### Python

- Python 3.9.7

## 已知问题

1. 部分带有公式的论文摘要可能无法正确爬取。
2. 对于 Elsevier 旗下的期刊，爬取不稳定。

## TODO

- [ ] UI

---

- [x] 命令行
- [x] 保存 dblp 检索结果到 pkl
- [x] 进度条
- [x] Springer Conf
- [x] 期刊
- [x] Elseiver journals
- [x] 优化 IEEE 爬取代码
- [x] 爬取 JCS
