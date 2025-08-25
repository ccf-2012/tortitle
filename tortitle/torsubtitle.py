"""
This module provides a class to parse movie and series information from raw subtitle names.
"""
import re

# Dictionary to map Chinese numerals to integers
CHINESE_NUMERALS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
}

def chinese_to_arabic(s: str) -> int | None:
    """Converts a Chinese numeral string to an integer."""
    return CHINESE_NUMERALS.get(s)

def contains_cjk(str):
    return re.search(r'[\u4e00-\u9fa5\u3041-\u30fc]', str)

def split_by_language_boundary(text: str) -> list[str]:
    """
    Splits a string by spaces, but keeps English phrases together.

    The function uses a regular expression to find two types of patterns:
    1. A sequence of English words/numbers that can be separated by spaces,
       colons, dots, or hyphens.
    2. Any other sequence of non-space characters.

    Args:
        text: The input string to split.

    Returns:
        A list of strings, split according to the rules.
    """
    # 正则表达式：匹配一个英文词组（允许内部有空格和部分标点）且后面不跟中文，或者匹配一个非空格的词
    pattern = r"[a-zA-Z0-9]+(?:[\s.:-]+[a-zA-Z0-9]+)*(?![一-鿆])|[^\s丨|/]+"
    
    return re.findall(pattern, text)


class TorSubtitle:
    """
    Parses a raw subtitle string to extract title, season, and episode information.
    """
    def __init__(self, raw_name: str):
        """
        Initializes the TorSubtitle object and parses the raw name.

        Args:
            raw_name: The raw string from the subtitle file name or torrent title.
        """
        self.raw_name = raw_name
        self.extitle = ""
        self.season = ""
        self.episode = ""
        self.total_episodes = ""

        self._parse()

    def _parse_season(self, name: str):
        """Parses season information."""
        # Pattern for "第三季", "Season 4"
        season_pattern = r'(?:第([一二三四五六七八九十]+|[0-9]+)季|Season\s*([0-9]+))'
        match = re.search(season_pattern, name, re.IGNORECASE)
        if match:
            season_str = match.group(1) or match.group(2)
            if season_str.isdigit():
                self.season = int(season_str)
            else:
                self.season = chinese_to_arabic(season_str)

    def _parse_episode(self, name: str):
        """Parses episode information."""
        # Pattern for "第01集", "第1-2集", "第1-10集", "全10集"
        episode_pattern = r'(?:第([0-9]+(?:-[0-9]+)?)集|全([0-9]+)集)'
        match = re.search(episode_pattern, name)
        if match:
            episode_str = ""
            if match.group(1):  # "第1-2集" or "第1集"
                episode_str = match.group(1)
            elif match.group(2):  # "全10集"
                self.total_episodes = int(match.group(2))
                # episode_str = f"1-{self.total_episodes}"

            if '-' in episode_str:
                parts = episode_str.split('-')
                start = parts[0].zfill(2)
                end = parts[1].zfill(2)
                self.episode = f"E{start}-E{end}"
            elif episode_str:
                self.episode = f"E{episode_str.zfill(2)}"


    def _parse_extitle(self, name: str):
        """Parses the main title (extitle)."""
        self.extitle = ""
        processed_name = name.strip()
        # [] 【 】都展开，对中文标题来说，标以这样方括号的，有可能是主要信息
        # processed_name = re.sub(r"\[|\]|【|】", " ", processed_name).strip()
        # processed_name = re.sub(r"【|】", " ", processed_name).strip()
        # 包含这些的，直接跳过
        if m := re.search(r"0day破解|\bFLAC\b|无损\b", processed_name, flags=re.I):
            return
        # 这些开头的，直接不处理
        if m := re.search(r"^((全|第).{1,4}[季|集]|[简中].*?字幕|导演|主演\b|无损\b)", processed_name, flags=re.I):
            self.extitle = ''
            return

        # 开头的一些可能字词，先删掉：...新番，官方国语中字，国漫，国家，xxx剧，xxx台/卫视，综艺，带上分隔符一起删
        processed_name = re.sub(r"\d+\s*年\s*\d+\s*月\s*\w*番[\:：\s/\|]?", "", processed_name)
        processed_name = re.sub(r"^[\:：]", "",  processed_name)
        # 开头的官方国语中字 跟:：
        processed_name = re.sub(r"^(?:官方\s*|首发\s*|禁转\s*|独占\s*|限转\s*|国语\s*|中字\s*|国漫\s*|国创\s*|特效\s*|DIY\s*)+\b", "", processed_name, flags=re.I).strip()
        # 开头是国家、XYZTV、卫视，带上分隔符一起删
        processed_name = re.sub(r"\b(日本|瑞典|挪威|大陆|香港|港台|\w剧|(墨西哥|新加坡)剧)[\]\:：\s/\|]", "", processed_name)
        processed_name = re.sub(r"^(?:\(?新\)?|\w+TV|Jade|TVB\w*|点播|翡翠台|\w*卫视|电影|韩综)+\b", "", processed_name)

        # 干扰字词，可能在开头，或前2格
        processed_name = re.sub(r"\b(连载\w*|\w*国漫|短剧)\b", "", processed_name)
        processed_name = re.sub(r"\b([全第]\w{,4}\s*集|第\d+集|S\d+|(\d+-\d+集)|第.{1,4}[季|集]|纪录|专辑|综艺|动画|剧场版)\b", "", processed_name)
        processed_name = re.sub(r"1080p|2160p|720p|4K\b|IMax\b|杜比视界|中\w双语", "", processed_name)
        processed_name = processed_name.strip()

        # 中文相关的忽略模式
        chinese_ignore = [
            "中字", r"\b导演", r"\b\w语\b", r"\b\w国\b", r"点播\b", r"\w+字幕",
            r"\b纪录", "简繁", r"国创\b", "翡翠台", r"\w*卫视", r"中\w+频道",
            r"类[别型][:：]", r"\b无损\b", r"原盘\b", r"\b台湾\b",
        ]
        # 纯英文的忽略模式
        english_ignore = [
            r"PTP Gold.*?corn", r"\bDIY\b", "Checked by "
        ]

        # 合并所有模式并编译正则表达式
        ignore_list = chinese_ignore + english_ignore
        ignore_patterns = re.compile("|".join(ignore_list), re.IGNORECASE)
        eng_pattern = re.compile("|".join(english_ignore), re.IGNORECASE)

        # 方括号内有特征词，则整个方括号不要了
        bracket_blocks = re.findall(r'【[^】]*】|\[[^\]]*\]', processed_name)
        for block in bracket_blocks:
            if ignore_patterns.search(block):
                processed_name = processed_name.replace(block, "", 1)

        # 以 特殊标点符 或 中英文段落 分 segments
        if re.search(r'[【】\[\]丨|/]', processed_name):
            segments = re.split(r'[【】\[\]丨|/]', processed_name)
        else:
            segments = split_by_language_boundary(processed_name)
        # clear empty segments
        segments = [p for p in segments if p.strip()]
        candidate_list = []
        # 3 段之内要见到 title，否则不要了
        for segment in segments[:3]:
            # 这一segment以此开头，就没戏了
            if re.match(r"^类型|导演|主演", segment.strip() ):
                # 保留英文标题
                if candidate_list:
                    self.extitle = candidate_list[0].strip()
                return 
            if contains_cjk(segment):
                # 所有分隔化为空格，再将空格合并
                segment = re.sub(r"[丨|/\(\)）（]", " ", segment)
                segment = re.sub(r"\s+", " ", segment).strip()
                sub_parts = segment.split(' ')
                for spart in sub_parts[:3]:
                    if m := ignore_patterns.search(spart):
                        continue
                    candidate_list.append(spart)
                    if not contains_cjk(spart):
                        continue
                    self.extitle = spart
                    return
            else:
                # 一段[丨|/]分隔的仅包括英文的，
                if not eng_pattern.search(segment):
                    candidate_list.append(segment)

        # 保留英文标题
        if candidate_list:
            self.extitle = candidate_list[0].strip()
        return 


    def _parse(self):
        """
        Runs the parsing logic for season, episode, and title.
        """
        self._parse_season(self.raw_name)
        self._parse_episode(self.raw_name)
        self._parse_extitle(self.raw_name)

    def to_dict(self):
        """Returns the parsed data as a dictionary."""
        return {
            "extitle": self.extitle,
            "season": self.season,
            "episode": self.episode,
            "total_episodes": self.total_episodes,
        }

# For backward compatibility, we can keep a function that uses the class.
def parse_subtitle(name: str) -> str:
    """
    Parses a raw subtitle string to extract the movie/series title.
    This is a wrapper for the TorSubtitle class for backward compatibility.
    """
    return TorSubtitle(name).extitle
