# 爬取论文元数据和摘要

**注意，本项目不会下载论文，仅获取包括摘要在内的论文元数据。**

## 支持的会议/期刊

**包含摘要的 bibtex 文件可以从 [这里](https://github.com/Lraxer/paper_metadata) 获取。**

理论上支持 IEEE、ACM、Elsevier、Springer 出版或举办的期刊和会议，以及 USENIX、NDSS、IOS Press 出版社。可参考 [论文元数据收集情况表](https://rigorous-frost-052.notion.site/d5053e59458a47769fd645be500f55ff?v=c97cacf0bdc94d9b965a29f3d5f0d473)，“收录情况”一列不为空的是已经测试过可用的期刊或会议，空的是没有测试或不支持的出版社。

## 安装

### 下载 chromedriver

为了稳定运行 selenium，请下载合适版本的 [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) 并解压缩。

1. 打开 Goole Chrome 浏览器，查看浏览器的版本号；
2. 下载和浏览器版本对应的 [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)，解压缩到一个目录；
3. 在 `settings.py` 中修改 `chromedriver_path`，填写 `chromedriver` 可执行文件的路径。

**注意，chromedriver 的版本必须与你的系统的 chrome 浏览器版本一致（或者大版本一致）。** 当出现类似下面的错误时，下载新版本的 chromedriver。

```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version [xxx]
Current browser version [yyy] with binary path [...]
```

### 设置 Python 虚拟环境与安装依赖

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

脚本分为两部分：

1. 从 [dblp](https://dblp.org/) 获取给定会议和年份的论文列表，或给定期刊和卷号的论文列表，得到 bibtex 格式的引用，并获取论文的 `doi.org/xxxx` 格式的 URL 链接。
2. 访问每一篇论文的链接，该链接会自动重定向到出版社的页面。脚本尝试从页面中获取摘要，合并到 bibtex 引用中，生成 `.bib` 文件。

```powershell
cd src
python ./main.py --help

# e.g.
# 会议
python ./main.py -n raid -y 2022 -e -d 5 -t 8
# dblp 上，部分会议一年分为多个part
# 通过 -f 参数，读取pickle文件中保存的dblp论文列表，以获取摘要
# 如果要爬取的会议/期刊不在已验证的支持范围内，用 -p 手动指定出版社
python .\main.py -n iccS -y 2022-2 -p springer -f ./iccS2022-2_dblp.pkl -t 6

# 期刊
python ./main.py -n tifs -u 16 -e -d 5 -t 8
# 可以批量下载多个卷
python ./main.py -n tifs -u 16-18 -e -d 5 -t 8
```

## 测试环境

由于设备有限，当前只在 Windows 11 系统下，Python 3.9.7 环境运行过脚本。该脚本理论上不受系统限制。

## 已知问题

1. 部分带有公式的论文摘要可能无法正确爬取，公式不能正确显示。这是因为网页上的公式是经过渲染后的，爬到的只是渲染前的原始状态。
2. 部分论文尚未收录在 doi.org 网站上，因此无法通过该链接重定向到出版社的论文页面获取摘要。

## TODO

- [x] 命令行
- [x] 保存 dblp 检索结果到 pkl
- [x] 进度条
- [x] Springer Conf
- [x] 期刊
- [x] Elseiver journals
- [x] 优化 IEEE 爬取代码
- [x] 爬取 JCS
