# TorTitle

一个用于从种⼦标题中解析电影、剧集、音乐等信息的 Python 库，支持主标题和副标题的提取。

## 安装

```bash
pip install tortitle
```

## 使用方法

### 解析主标题 (TorTitle)

`TorTitle` 用于解析种⼦标题，并提取主要信息，例如标题、年份、季数、集数、分辨率等。

#### 基础用法

```python
from tortitle import TorTitle

# 电视剧示例
torrent_name = "The.Mandalorian.S01E01.1080p.WEB-DL.DDP5.1.H.264-NTC"
title = TorTitle(torrent_name)

print(f"标题: {title.title}")           # The Mandalorian
print(f"中文标题: {title.cntitle}")     # (为空)
print(f"类型: {title.type}")            # tv
print(f"季: {title.season}")            # S01
print(f"集: {title.episode}")           # E01
print(f"分辨率: {title.resolution}")    # 1080p
print(f"片源: {title.media_source}")    # webdl
print(f"音频: {title.audio}")           # DDP5.1
print(f"制作组: {title.group}")         # NTC
```

#### 支持的类型 (type 字段)

- `movie` - 电影
- `tv` - 电视剧
- `music` - 音乐
- `ebook` - 电子书
- `other` - 其他

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `title` | 英文或主标题 | `The Mandalorian` |
| `cntitle` | 中文标题 | `曼达洛人` |
| `year` | 发行年份 | `2019` |
| `type` | 内容类型 | `tv` 或 `movie` |
| `season` | 季号(格式化) | `S01` |
| `episode` | 集号(格式化) | `E01` 或 `E01-E05` |
| `seasons` | 季号列表 | `[1]` 或 `[1, 2, 3]` |
| `episodes` | 集号列表 | `[1]` 或 `[1, 2, 3, 4, 5]` |
| `resolution` | 分辨率 | `1080p`, `2160p`, `720p` |
| `media_source` | 片源类型 | `webdl`, `bluray`, `remux`, `encode` |
| `video` | 视频编码 | `H.264`, `HEVC`, `x265` |
| `audio` | 音频信息 | `DDP5.1`, `TrueHD`, `DTS-HD MA` |
| `group` | 制作组/发布组 | `NTC`, `CMCC` |
| `full_season` | 是否为完整季 | `True` 或 `False` |

#### 范围格式支持

季和集支持范围格式：
```python
title = TorTitle("[The.Mandalorian].S01E01-E05.(2019).1080p.WEB-DL-GROUP")
print(title.season)    # S01
print(title.episode)   # E01-E05
print(title.episodes)  # [1, 2, 3, 4, 5]
```

#### 中文标题支持

```python
title = TorTitle("[曼达洛人].The.Mandalorian.S01E01.2019.1080p.WEB-DL-NTb")
print(title.title)     # The Mandalorian
print(title.cntitle)   # 曼达洛人
```

#### 多种输出格式

```python
torrent_name = "[美国][金钱世界][All.the.Money.in.the.World.2017.1080p.BluRay.x264.DTS.5.1-CMCC]"
title = TorTitle(torrent_name)

# 方式1：逐个访问属性
print(title.title)     # All the Money in the World
print(title.year)      # 2017

# 方式2：获取完整字典
result = title.to_dict()
print(result)
# 输出：
# {
#   'title': 'All the Money in the World',
#   'cntitle': '金钱世界',
#   'year': '2017',
#   'type': 'movie',
#   'season': '',
#   'episode': '',
#   'seasons': [],
#   'episodes': [],
#   'media_source': 'bluray',
#   'video': 'x264',
#   'audio': 'DTS5.1',
#   'group': 'CMCC',
#   'resolution': '1080p',
#   'full_season': False
# }
```

#### 更多示例

```python
# 电影示例
t1 = TorTitle("Inception.2010.1080p.BluRay.x264-GROUP")
print(t1.type)  # movie
print(t1.year)  # 2010

# 多集电视剧
t2 = TorTitle("Breaking.Bad.S01E01-E10.720p.BluRay.x264-GROUP")
print(t2.season)   # S01
print(t2.episodes) # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 完整季
t3 = TorTitle("Game.of.Thrones.Season.1.Complete.1080p.BluRay.x264")
print(t3.full_season)  # True

# 音乐
t4 = TorTitle("Artist - Album (2023) [SACD]")
print(t4.type)  # music

# 电子书
t5 = TorTitle("MyBook.epub")
print(t5.type)  # ebook
```

### 解析副标题 (TorSubtitle)

`TorSubtitle` 用于从 PT 站的种⼦副标题中提取`可能是标题`的信息(这里叫 `extitle`)，以及 season, episode 等。

#### 基础用法

```python
from tortitle import TorSubtitle

torrent_name = "舌尖上的中国 第一季 | 全7集 | 导演: 陈晓卿 | 主演: 李立宏 国语/中字 4K高码版"
subtitle = TorSubtitle(torrent_name)

print(f"标题: {subtitle.extitle}")      # 舌尖上的中国
print(f"季: {subtitle.season}")         # 1
print(f"集: {subtitle.episode}")        # (为空，因为是全季)
print(f"全季: {subtitle.full_season}")  # True
```

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `extitle` | 提取的标题 | `舌尖上的中国` |
| `season` | 季号(整数) | `1` 或 `4` |
| `episode` | 集号(格式化) | `E07` 或 `E07-E10` |
| `total_episodes` | 总集数 | `7` |
| `full_season` | 是否为完整季 | `True` 或 `False` |

#### 详细示例

```python
# 单季单集
sub1 = TorSubtitle("盾之勇者成名录 第四季 | 第07集 | 1080p | 类型: 动画")
print(sub1.extitle)      # 盾之勇者成名录
print(sub1.season)       # 4
print(sub1.episode)      # E07

# 多集范围
sub2 = TorSubtitle("锦月如歌 | 第32-36集 | 4K 杜比视界")
print(sub2.extitle)      # 锦月如歌
print(sub2.episode)      # E32-E36

# 全季
sub3 = TorSubtitle("暗蚀 Andhera 全8集 | 类型: 剧情")
print(sub3.extitle)      # 暗蚀
print(sub3.full_season)  # True
print(sub3.total_episodes)  # 8

# 中英混合
sub4 = TorSubtitle("夜樱家的大作战 | 全27集 | 4K 高码 | 导演: 凑未来")
print(sub4.extitle)      # 夜樱家的大作战
print(sub4.total_episodes)  # 27

# 带 / 分隔的标题(提取第一个)
sub5 = TorSubtitle("坏蛋联盟2 / 大坏蛋2 / 坏家伙2 | 类别：喜剧 动作 动画")
print(sub5.extitle)      # 坏蛋联盟2
```

#### 多种输出格式

```python
torrent_name = "盾之勇者成名录 / The Rising of the Shield Hero Season 4 第四季 | 第07集 | 1080p | 类型: 动画"
subtitle = TorSubtitle(torrent_name)

# 方式1：逐个访问属性
print(subtitle.extitle)     # 盾之勇者成名录
print(subtitle.season)      # 4

# 方式2：获取完整字典
result = subtitle.to_dict()
print(result)
# 输出：
# {
#   "extitle": "盾之勇者成名录",
#   "season": 4,
#   "episode": "E07",
#   "total_episodes": 0,
#   "full_season": False
# }
```

#### 便利函数

```python
# 快速提取标题，不需要其他字段时
from tortitle import parse_subtitle

title = parse_subtitle("夏目友人帐 第七季 | 全12集+OVA | 中日双语字幕")
print(title)  # 夏目友人帐
```

## Contribution

欢迎提交 Pull Request

## License

[MIT](https://choosealicense.com/licenses/mit/)