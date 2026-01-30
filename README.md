# 爬取论文元数据和摘要

**注意，本项目不会下载论文，仅获取包括摘要在内的论文元数据。**

## 支持的会议/期刊

**包含摘要的 bibtex 文件可以从 [论文元数据仓库](https://github.com/Lraxer/paper_metadata) 获取。** 如果您有包含摘要的 bibtex 或 ris 格式的文件，欢迎向这个仓库提交 PR！

本项目理论上支持 IEEE、ACM、Elsevier、Springer 出版或举办的期刊和会议论文，以及 USENIX、NDSS、IOS Press 等出版社的论文。可参考 [论文元数据收集情况表](https://rigorous-frost-052.notion.site/d5053e59458a47769fd645be500f55ff?v=c97cacf0bdc94d9b965a29f3d5f0d473)，“收录情况”一列不为空的是已经测试过可用的期刊或会议，空的是没有测试或不支持的出版社。

## 安装

### 代码设置

1. 安装 Goole Chrome 浏览器，记录 Chrome 可执行文件的路径，例如，Windows 系统下一般是 `C:/Program Files/Google/Chrome/Application/chrome.exe`。
2. 在 `settings.py` 中修改 `chrome_path`，填写 `chrome.exe` 可执行文件的路径。
3. 在 `settings.py` 中修改 `cookie_path`，创建一个目录用于保存 cookie，并填写该目录的路径。
4. （可选）修改 `req_headers`，这个字典用于 requests 库发送请求时设置请求头。

### 设置 Python 虚拟环境与安装依赖

#### 使用 uv

根据官方文档 [安装uv](https://docs.astral.sh/uv/)。

同步依赖

```bash
uv sync --locked
```

#### 手动创建虚拟环境

也可以使用 `venv` 等工具手动创建虚拟环境。

```powershell
# For Windows
cd paperinfo_crawler
python -m venv ./venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# For Linux
cd paperinfo_crawler
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## 运行

脚本分为两部分：

1. 从 [dblp](https://dblp.uni-trier.de/) 获取给定会议和年份的论文列表，或给定期刊和卷号的论文列表，得到 bibtex 格式的引用，并获取论文的 `doi.org/xxxx` 格式的 URL 链接。
2. 访问每一篇论文的链接，该链接会自动重定向到出版社的页面。脚本尝试从页面中获取摘要，合并到 bibtex 引用中，生成 `.bib` 文件。

以下是使用 `uv` 的运行示例。如果你使用自己创建的虚拟环境，将 `uv run` 替换为 `python` 即可。

```powershell
uv run ./main.py --help

# e.g.
# 会议
uv run ./main.py -n raid -y 2022 -e -d 5 -t 8
# dblp 上，部分会议一年分为多个part
# 通过 -f 参数，读取pickle文件中保存的dblp论文列表，以获取摘要
# 如果要爬取的会议/期刊不在已验证的支持范围内，用 -p 手动指定出版社
uv run ./main.py -n iccS -y 2022-2 -p springer -f ./iccS2022-2_dblp.pkl -t 6

# 期刊
uv run ./main.py -n tifs -u 16 -e -d 5 -t 8
# 可以批量下载多个卷
uv run ./main.py -n tifs -u 16-18 -e -d 5 -t 8
```

**注意爬取的速度不要太快，即 `-d` 和 `-t` 不应设置太小，以免被封禁。**

## 已知问题

### 人机验证与爬取失败

1. 首先需要保证使用的 IP 具有较高纯净度。
2. 将 Zendriver 的 `headless` 参数设置为 `False`，相比 `True` 的成功率更高。
3. 删除 `settings.py` 中，`cookie_path` 变量指定的目录下的所有文件，重新运行。

### 部分条目解析失败

由于 dblp 生成的 bibtex 格式不处理字段值中的特殊字符，例如 `@`，因此导致解析失败。本项目目前也尚未实现特殊字符转义。

### 其他问题

1. 部分带有公式的论文摘要可能无法正确爬取，公式不能正确显示。这是因为网页上的公式经过了渲染，爬到的只是渲染前的原始状态。
2. 部分论文尚未收录在 doi.org 网站上，因此无法通过该链接重定向到出版社的论文页面获取摘要。
3. pvldb 目前无法予以支持。dblp 的链接直接跳转到了 PDF 文件。而 pvldb 官网中很多论文链接是失效的。
