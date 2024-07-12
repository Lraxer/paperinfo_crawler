# 爬取论文元数据和摘要

**注意，本项目不会下载论文，仅获取包括摘要在内的论文元数据。**

## 当前支持的会议/期刊

**包含摘要的 bibtex 文件可以从 [这里](https://github.com/Lraxer/paper_metadata) 获取。**

| 名称                                                                           | 类型         | 标识    | 出版社标识 | 已测试 |
| ------------------------------------------------------------------------------ | ------------ | ------- | ---------- | ------ |
| Annual ACM Conference on Computer and Communications Security (CCS)            | 会议 (CCF-A) | `ccs`   | `acm`      | ✔️     |
| IEEE Symposium on Security and Privacy (S&P)                                   | 会议 (CCF-A) | `sp`    | `ieee`     | ✔️     |
| USENIX Security Symposium (USENIX Security)                                    | 会议 (CCF-A) | `uss`   | `usenix`   | ✔️     |
| Network and Distributed System Security Symposium (NDSS)                       | 会议 (CCF-A) | `ndss`  | `ndss`     | ✔️     |
| Annual Computer Security Applications Conference (ACSAC)                       | 会议 (CCF-B) | `acsac` | `acm`      | ✔️     |
| International Symposium on Research in Attacks, Intrusions and Defenses (RAID) | 会议 (CCF-B) | `raid`  | `acm`      | ✔️     |

## 安装

为了稳定运行 selenium，建议下载 [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)，并在 `conf.py` 中修改 `chromedriver_path`。

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

## TODO

- [ ] Springer Conf
- [ ] 期刊
- [ ] UI

- [x] 命令行
- [x] 保存 dblp 检索结果到 pkl
- [x] 进度条
