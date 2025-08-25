# TorTitle

一个用于从种⼦标题中解析电影、剧集信息的 Python 库，支持主标题和副标题的提取。

## 安装

```bash
pip install tortitle
```

## 使用方法

### 解析主标题

`TorTitle` 类用于解析种⼦标题，并提取主要信息，例如标题、年份、季数、集数、分辨率等。

```python
from tortitle import TorTitle
torrent_name = "The.Mandalorian.S01E01.1080p.WEB-DL.DDP5.1.H.264-NTb"
title = TorTitle(torrent_name)

print(f"标题: {title.title}")
print(f"中文标题: {title.cntitle}")
print(f"年份: {title.year}")
print(f"季: {title.season}")
print(f"集: {title.episode}")
print(f"分辨率: {title.resolution}")
print(f"片源: {title.media_source}")
print(f"制作组: {title.group}")
```

### 解析副标题

`TorSubtitle` 类用于从 PT 站的种⼦标题中提取副标题信息。

```python
from tortitle import TorSubtitle
torrent_name = "[SubSub] The Queen's Gambit S01E01 Queen's Gambit.ass"
subtitle = TorSubtitle(torrent_name)

print(f"副标题: {subtitle.extitle}")
print(f"季: {subtitle.season}")
print(f"集: {subtitle.episode}")
```

## 贡献

欢迎提交 Pull Request。对于重大更改，请先开一个 issue 进行讨论。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/)