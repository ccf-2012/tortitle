"""
This module provides the TorTitle class for parsing torrent names.
"""

import re
import os
from typing import List, Tuple, Dict, Any, Optional, Match

def cut_ext(torrent_name: str) -> str:
    """Removes the file extension from a torrent name."""
    if not torrent_name:
        return ''
    tortup = os.path.splitext(torrent_name)
    torext = tortup[1].lower()
    mvext = ['.strm', '.mkv', '.ts', '.m2ts', '.vob', '.mpg', '.mp4', '.3gp', '.mov', '.tp', '.zip', '.pdf', '.iso', '.ass', '.srt', '.7z', '.rar']
    if torext.lower() in mvext:
        return tortup[0].strip()
    else:
        return torrent_name

def delimer_to_space(input_string: str) -> str:
    """Replaces various delimiters in a string with spaces."""
    # add Chinese parentheses and full-width brackets to delimiters so they won't remain
    delimiters = ['[', ']', '.', '{', '}', '_', ',', '(', ')', '「', '」', '（', '）', '【', '】']
    for dchar in delimiters:
        input_string = input_string.replace(dchar, ' ')
    return input_string

def hyphen_to_space(input_string: str) -> str:
    """Replaces hyphens in a string with spaces."""
    return input_string.replace('-', ' ')

def contains_cjk(input_string: str) -> Optional[Match[str]]:
    """Checks if a string contains CJK characters."""
    return re.search(r'[\u4e00-\u9fa5\u3041-\u30fc]', input_string)

def cut_aka(title_string: str) -> str:
    """Cuts the 'AKA' part from a title string."""
    m = re.search(r'\s(/|AKA)\s', title_string, re.I)
    if m:
        title_string = title_string.split(m.group(0))[0]
    return title_string.strip()

def try_int(input_string: str) -> int:
    """Tries to convert a string to an integer, handling Chinese numerals."""
    cndigit = '一二三四五六七八九十'
    if input_string and input_string[0] in cndigit and len(input_string) == 1:
        return cndigit.index(input_string[0]) + 1
    try:
        return int(input_string)
    except (ValueError, TypeError):
        return 0

class TorTitle:
    """
    Parses a torrent name to extract details like title, year, season, episode, etc.
    """
    def __init__(self, name: str):
        self.raw_name: str = name or ""
        self.title: str = name or ""
        self.cntitle: str = ''
        self.year: str = ''
        self.type: str = 'movie'
        self.season: str = ''
        self.episode: str = ''
        self.seasons: List[int] = []
        self.episodes: List[int] = []
        self.media_source: str = ''
        self.group: str = ''
        self.resolution: str = ''
        self.video: str = ''
        self.audio: str = ''
        self.full_season: bool = False
        self.failsafe_title: str = self.title
        self.parse()

    def parse(self) -> None:
        """
        The main parsing logic to extract information from the torrent name.
        """
        self.raw_name = self.title.strip()

        # Remove trailing file size tags like （3.22G）, (7.43GB), [3.22G]
        cleaned_name = re.sub(r'[\(（\[]\s*\d+(?:\.\d+)?\s*[GgMm][Bb]?\s*[\)）\]]\s*$', '', self.title).strip()
        if cleaned_name:
            self.title = cleaned_name
            self.raw_name = cleaned_name

        self.resolution = self._parse_resolution(self.raw_name)
        self.media_source, self.video, self.audio = self._parse_media_info(self.raw_name)
        if not self.resolution and not self.video:
            self.type, match = self._check_non_media_type(self.raw_name)
            if match:
                return

        self._check_movie_tv_type(delimer_to_space(self.raw_name))

        self.title, self.cntitle = self._handle_bracket_title(self.title)
        self.title = self._prepare_title(self.title)

        if not self.group:
            self.group = self._parse_group(self.title)

        year_pos, year_val = self._extract_year(self.title)
        if not self.year:
            _, raw_year = self._extract_year(self.raw_name)
            self.year = year_val or raw_year

        se_pos = self._extract_season_episode(self.title)
        if not self.season and not self.episode:
            self._extract_season_episode(self.raw_name)

        self.failsafe_title = self.title
        self.title = self._cut_year_season(self.title, year_pos, se_pos)
        self.title = self._cut_keywords(self.title)

        if not self.cntitle:
            self.title, self.cntitle = self._extract_cn_title(self.title)
        self._polish_title()

    def _parse_media_info(self, torrent_name: str) -> Tuple[str, str, str]:
        """Parses media source, video and audio info from the torrent name."""
        media_source, video, audio = '', '', ''
        if m := re.search(r"(?<=(1080p|2160p)\s)(((\w+)\s+)?WEB(-DL|-rip)?)|\bWEB(-DL|-rip)?\b|\bHDTV\b|((UHD )?(BluRay|Blu-ray))", torrent_name, re.I):
            m0 = m[0].strip()
            if re.search(r'WEB[-]?(DL|rip)?', m0, re.I):
                media_source = 'webdl'
            elif re.search(r'BLURAY|BLU-RAY', m0, re.I):
                if re.search(r'x26[45]', torrent_name, re.I):
                    media_source = 'encode'
                elif re.search(r'remux', torrent_name, re.I):
                    media_source = 'remux'
                else:
                    media_source = 'bluray'
            else:
                media_source = m0
        if m := re.search(r"AVC|HEVC(\s(DV|HDR))?|H\.?26[456](\s(HDR|DV))?|x26[45]\s?(10bit)?(HDR)?|DoVi (HDR(10)?)? (HEVC)?", torrent_name, re.I):
            video = m[0].strip()
        if m := re.search(r"DTS-HD MA \d.\d|LPCM\s?\d.\d|TrueHD\s?\d\.\d( Atmos)?|DDP[\s\.]*\d\.\d( Atmos)?|(AAC|FLAC)(\s*\d\.\d)?( Atmos)?|DTS(\s?\d\.\d)?|DD\+? \d\.\d", torrent_name, re.I):
            audio = m[0].strip()
        return media_source, video, audio

    def _parse_resolution(self, torrent_name: str) -> str:
        """Parses the resolution from the torrent name."""
        match = re.search(r'\b(4K|2160p|1080[pi]|720p|576p|480p)\b', torrent_name, re.A | re.I)
        if match:
            r = match.group(0).strip().lower()
            if r == '4k':
                r = '2160p'
            return r
        if match := re.search(r'\b(3840[xX]2160|1920[xX]1080|1280[xX]720)\b', torrent_name, re.I):
            res_map = {'3840x2160': '2160p', '1920x1080': '1080p', '1280x720': '720p'}
            return res_map.get(match.group(0).lower(), '')
        return ''

    def _parse_group(self, torrent_name: str) -> Optional[str]:
        """Parses the release group from the torrent name."""
        sstr = cut_ext(torrent_name)
        match = re.search(r'[@\-￡]\s?(\w+)(?!.*[@\-￡].*)$', sstr, re.I)
        return match.group(1).strip() if match else ''

    def _prepare_title(self, processing_title: str) -> str:
        """Prepares the title for further parsing."""
        processing_title = cut_ext(processing_title)
        processing_title = re.sub(r'^[「【][^】」]*[】」]', '', processing_title, flags=re.I).strip()
        processing_title = re.sub(r'^\w+TV-?(\d+)?([48]K)?\b', '', processing_title, flags=re.I).strip()
        processing_title = delimer_to_space(processing_title)
        return processing_title

    def _handle_bracket_title(self, processing_title: str) -> Tuple[str, str]:
        """Handles titles enclosed in brackets."""
        cn_title = ""
        if processing_title.startswith('[') and ']' in processing_title:
            brackets = re.findall(r'\[([^\]]+)\]', processing_title)

            # Strip leading group bracket if it ends with 字幕组/Fansub/etc.
            if brackets and re.search(r'字幕组|Fansub|Sub$|Studio$|Team$|Raws$', brackets[0], re.I):
                if not self.group:
                    self.group = brackets[0]
                processing_title = processing_title.replace(f'[{brackets[0]}]', '', 1).strip()
                brackets = brackets[1:]

            non_bracket_text = re.sub(r'\[[^\]]+\]', '', processing_title).strip()

            if (len(brackets) >= 2 and len(non_bracket_text) < 50) or (len(brackets) >= 1 and len(non_bracket_text) < 5):
                countries = r'瑞典|加拿大|美国|爱尔兰|日本|韩国|南韩|法国|英国|德国|意大利|西班牙|俄罗斯|印度|泰国|澳大利亚|新西兰|瑞士|挪威|荷兰|波兰|丹麦|芬兰|捷克|比利时|巴西|阿根廷|墨西哥|南非|埃及|土耳其|希腊|匈牙利|奥地利|罗马尼亚|保加利亚|新加坡|马来西亚|印尼|越南|菲律宾|中国|大陆|香港|台湾|港台|欧美|中东'
                country_pattern = r'^(?:(?:' + countries + r')(?:/(?:' + countries + r'))*)$'
                category_pattern = r'^(?:[国日美韩泰英台陆](?:剧|漫)|国产(?:动漫|剧|影)?|国漫|日漫|美剧|日剧|韩剧|泰剧|英剧|台剧|陆剧|大陆|港台|欧美|纪录片?|动画|电影|电视剧|国创|动态漫画|TV|MOVIES?|ANIME|官方|首发|独占|招募|漫画)$'
                spec_pattern = r'^(?:1080[pi]?|2160p|4K|720p|576p|480p|\d{3,4}[xX]\d{3,4}|AVC|HEVC|x26[45]|H\.?26[45]|10bit|8bit|HDR(?:10)?|DV|Dolby Vision|WEB-?DL|WEB-?rip|BDRip|BluRay|HDTV|UHD|MKV(?:/BDRip)?|MP4|AAC|FLAC|DTS|DDP|AC3|TrueHD|MP3|GB|BIG5|CHS|CHT|TC|SC|INT|国语中字|中文字幕|双语|简繁|中字|简中|繁中|简体|繁体|硬字|国语硬字|简日双语|简日|外挂字幕|内嵌中字|内封字幕|双语字幕|国语|粤语|Fin(?:\+SP)?|SP|Complete|REPACK|PROPER|附OPED)$'
                ep_pattern = r'^(?:[全共]\s*\d+\s*[集期话]|\d+\s*集全|S\d+(?:E\d+)?|Season\s*\d+|第\d+季|第?\d+(?:-\d+)?[集期话]|\d{1,3}\s*-\s*\d{1,3}.*|TV\s*\d{1,3}.*)$'
                year_pattern = r'^(?:19|20)\d{2}$'
                group_pattern = r'^(?:[A-Za-z0-9_\-]+-(?:Team|Raws|Studio|Sub|Fansub|Rip|Group)|\w+字幕组|\w+Fansub|\w+Sub)$'

                cjk_candidates = []
                non_cjk_candidates = []

                if non_bracket_text:
                    cleaned_nb = re.sub(r'^\d{2,4}年\d{1,2}月[新]?番[，,\s]*', '', non_bracket_text).strip()
                    cleaned_nb = re.sub(r'^[「【\[](?:[国日美韩]漫|国产(?:动漫|剧)?|动漫|动画|纪录片?|电影|TV|\w+字幕组|\w+Fansub)[】」\]]\s*', '', cleaned_nb, flags=re.I).strip()
                    if contains_cjk(cleaned_nb):
                        cjk_candidates.append(cleaned_nb)
                    elif cleaned_nb:
                        non_cjk_candidates.append(cleaned_nb)

                for idx, part in enumerate(brackets):
                    part_str = part.strip()
                    if not part_str:
                        continue

                    if re.match(year_pattern, part_str):
                        if not self.year:
                            self.year = part_str
                        continue

                    if re.match(ep_pattern, part_str, re.I):
                        if re.search(r'[全共]\s*\d+\s*[集期话]|\d+\s*集全', part_str):
                            self.full_season = True
                            self.type = 'tv'
                        continue

                    if re.match(spec_pattern, part_str, re.I) or re.match(category_pattern, part_str, re.I) or re.match(country_pattern, part_str, re.I):
                        continue

                    if (idx == 0 or '@' in part_str) and (re.match(group_pattern, part_str, re.I) or part_str.endswith('-Team') or part_str.endswith('-Raws') or part_str.endswith('字幕组') or '@' in part_str):
                        if not self.group:
                            self.group = part_str
                        continue

                    if contains_cjk(part_str):
                        cjk_candidates.append(part_str)
                    else:
                        non_cjk_candidates.append(part_str)

                cjk_filtered = []
                for c in cjk_candidates:
                    if re.match(category_pattern, c, re.I) or re.match(country_pattern, c, re.I):
                        continue
                    clean_c = re.sub(r'^\d{2,4}年\d{1,2}月[新]?番[，,\s]*', '', c).strip()
                    clean_c = re.sub(r'\s*第[一二三四五六七八九十\d]+[季集].*', '', clean_c).strip()
                    clean_c = re.sub(r'\s*S\d+.*', '', clean_c, flags=re.I).strip()
                    clean_c = re.sub(r'(?:1080[pi]?|2160p|4K|720p|576p|480p|\d{3,4}[xX]\d{3,4}|国语中字|中文字幕|双语|简繁|中字|简中|繁中|简体|繁体|硬字|国语硬字|国语|粤语|日语中字|日语).*$', '', clean_c).strip()
                    if clean_c:
                        cjk_filtered.append(clean_c)

                if cjk_filtered:
                    cn_title = cjk_filtered[0]

                non_cjk_title_candidates = [n for n in non_cjk_candidates if not ('@' in n or n.lower() in ['mp4', 'mkv', 'avi', 'ts', 'iso', 'strm', 'flac', 'zip', '7z', 'rar'] or re.match(r'^[a-zA-Z0-9_\-]+-(?:Team|Raws|Studio|Sub|Fansub|Rip|Group)$', n, re.I) or re.match(spec_pattern, n, re.I))]
                if non_cjk_title_candidates:
                    non_cjk_title_candidates.sort(key=lambda x: len(x.split()), reverse=True)
                    processing_title = non_cjk_title_candidates[0]
                elif cjk_filtered:
                    processing_title = cjk_filtered[0]

                return processing_title, cn_title

        if processing_title.startswith('[') and processing_title.endswith(']'):
            parts = [part.strip() for part in processing_title[1:-1].split('][') if part.strip()]
            keyword_pattern = r'1080p|2160p|4K|Web-?DL|720p|H\.?26[45]|x26[45]|全.{1,4}集'
            
            main_part = ''
            keyword_idx = -1
            for idx, part in enumerate(parts):
                if re.search(keyword_pattern, part, re.I):
                    keyword_idx = idx
                    main_part = part
                    break
            
            if main_part:
                if re.match(r'^' + keyword_pattern + '$', main_part, flags=re.I):
                    if keyword_idx > 0:
                        keyword_idx = keyword_idx - 1
                        processing_title = parts[keyword_idx]
                else:
                    processing_title = main_part
                if keyword_idx > 0 and contains_cjk(parts[keyword_idx-1]):
                    full_cn_title = parts[keyword_idx-1]
                    full_cn_title = re.sub(r'大陆|港台', '', full_cn_title, flags=re.I)
                    cn_title = full_cn_title.split(' ')[0].strip()
        return processing_title, cn_title

    def _extract_year(self, processing_title: str) -> Tuple[int, str]:
        """Extracts the year from the title."""
        _year_pos = 0
        year = ""
        potential_years = re.findall(r'\b(?<!\d{4}-)(19\d{2}|20\d{2})(?:\d{4})?\b', processing_title)
        if potential_years:
            year = potential_years[-1]
            _year_pos = processing_title.rfind(year)
        return _year_pos, year

    patterns = {
        's_e': r'\b(S(\d+))\s*(E(\d+)(-Ep?(\d+))?)\b',
        'season_only': r'(?<![a-zA-Z])(S(\d+)([\-\+]S?(\d+))?)\b(?!.*\bS\d+)',
        'season_word': r'\bSeason (\d+)\b',
        'ep_only': r'\bEp?(\d+)(-E?p?(\d+))?\b',
        'ep_range': r'(?<!\d)(0[1-9]|[1-9]\d)\s*-\s*(0[1-9]|[1-9]\d{1,2})(?:\s*(?:Fin|END|Complete|\+SP|v2|OVA|SP))*\b',
        'cn_season': r'第([一二三四五六七八九十]|\d+)季',
        'cn_episode': r'第([一二三四五六七八九十]+|\d+)集',
        'full_season': r'[全]\w{,4}\s*[集季]|\d+\s*集全|\d{4}\s*(S\d+\s*)?complete'
    }
    def _match_season(self, processing_title: str, match_key: Optional[str] = None) -> Any:
        """Matches season and episode patterns."""
        if match_key:
            return re.search(self.patterns[match_key], processing_title)
        
        for key, pattern in self.patterns.items():
            match = re.search(pattern, processing_title, flags=re.IGNORECASE)
            if match:
                return key, match
        return None, None

    def _check_movie_tv_type(self, processing_title: str) -> str:
        """Checks if the title is a TV show."""
        key, match = self._match_season(processing_title)
        self.type = 'tv' if match else 'movie'
        if self.type == 'tv':
            if key == 'full_season':
                self.full_season = True
            if re.search(r'complete', processing_title[match.span(0)[1]:], flags=re.I):
                self.full_season = True
        return self.type

    def _extract_season_episode(self, processing_title: str) -> int:
        """Extracts season and episode numbers."""
        se_pos = 0
        key, match = self._match_season(processing_title)
        if match:
            if key in ['s_e']:
                self.season = match.group(1)
                self.episode = match.group(3)
                self.seasons = [int(match.group(2))]
                if match.group(6):
                    self.episodes = list(range(int(match.group(4)), int(match.group(6)) + 1))
                    self.episode = match.group(3)
                else:
                    self.episodes = [int(match.group(4))]
            elif key == 'season_only':
                self.season = match.group(0)
                if match.group(4):
                    self.seasons = list(range(int(match.group(2)), int(match.group(4)) + 1))
                else:
                    self.seasons = [int(match.group(2))]
            elif key in ['season_word', 'cn_season']:
                season_int = try_int(match.group(1))
                self.seasons = [season_int]
                self.season = 'S' + str(season_int).zfill(2) if season_int else ''
            elif key in ['cn_episode', 'ep_only']:
                self.season = 'S01'
                self.seasons = [1]
                if match.re.groups >= 3 and match.group(3):
                    self.episodes = list(range(try_int(match.group(1)), try_int(match.group(3)) + 1))
                    self.episode = match.group(0)
                else:
                    self.episodes = [try_int(match.group(1))]
                    self.episode = match.group(0)
            elif key == 'ep_range':
                start_ep = int(match.group(1))
                end_ep = int(match.group(2))
                if start_ep < end_ep and end_ep <= 300:
                    self.season = 'S01'
                    self.seasons = [1]
                    self.episodes = list(range(start_ep, end_ep + 1))
                    self.episode = f"E{start_ep:02d}-E{end_ep:02d}"
            elif key == 'full_season':
                self.full_season = True
    
            self.full_season = self.full_season or (self.season and not self.episode)
            se_pos = match.span(0)[0]
        return se_pos


    def _check_non_media_type(self, processing_title: str) -> str:
        """Checks if the title is a music or others."""
        patterns_ebook = [
            r'(pdf|epub|mobi|txt|chm|azw3|eBook-\w{4,8}|mobi|doc|docx).?$',
            r'(上下册|全.{1,4}册|精装版|修订版|第\d版|共\d本|文集|新修版|PDF版|课本|课件|出版社)',
        ]
        patterns_music = [
            # r'(\b\d+ ?CD|(\[|\()\s*(16|24)\b|\-(44\.1|88.2|48|192)|24Bit|44\s*\]|FLAC.*(16|24|48|CUE|WEB|Album)|WAV.*CUE|CD.*FLAC|(\[|\()\s*FLAC)', 
            r'(\b\d+ ?CD\b|\-(44\.1|88\.2)|24Bit|FLAC.*(16|24|48|CUE|WEB|Album)|WAV.*CUE|CD.*FLAC|(\[|\()\s*FLAC)', 
            r'(\bVarious Artists|\bMQA\b|整轨|\b分轨|\b分軌|\b无损|\bLPCD|\bSACD|\bMP3|XRCD\d{1,3})',
            r'(\b|_)(FLAC.{0,3}|DSF.{0,3}|DSD(\d{1,3})?)$',
            r'\bVolume.*[\(\[]\d+[\)\]]$',
            r'\w+Music$', r'HDSCD$', r'Hi-?Res'
        ]
        pattern_game = [
            r'\b(PC|PS4|PS5|Switch|WiiU|XBOXONE|XBOX360|XBOXSeriesX|PSVita|PS3|PS2|PSP|3DS|DS)\b',
            r'\b(\w*Game|GOG|DINOByTES|RAZOR|TiNYiSO|RUNE|VACE|P2P|5play|\w*Know|KaOs|TENOKE|FitGirl)$'
        ]
        patterns_other = [
            r'(zip|7z|rar).?$',
        ]
        for pattern in patterns_ebook:
            match = re.search(pattern, processing_title, flags=re.IGNORECASE)
            if match:
                return 'ebook', match
        for pattern in patterns_music:
            match = re.search(pattern, processing_title, flags=re.IGNORECASE)
            if match:
                return 'music', match
        for pattern in pattern_game:
            match = re.search(pattern, processing_title, flags=re.IGNORECASE)
            if match:
                return 'game', match
        for pattern in patterns_other:
            match = re.search(pattern, processing_title, flags=re.IGNORECASE)
            if match:
                return 'other', match
        return '', None

    def _cut_year_season(self, processing_title: str, year_pos: int, se_pos: int) -> str:
        """Cuts the year and season part from the title."""
        positions = [p for p in [year_pos, se_pos] if p > 0]
        if not positions:
            if try_match := re.search(r"(\d+x\d+|BDRip|.26[45])", processing_title, flags=re.I):
                positions = [try_match.span(0)[0]]
        if positions:
            cut_pos = min(positions)
            processing_title = processing_title[:cut_pos]
            # remove trailing noise including ASCII and CJK parentheses/brackets and common separators
            processing_title = re.sub(r'[\s\._\-\(\)\（\）\[\]\{\}]+$', '', processing_title)
        return processing_title.strip()

    def _cut_keywords(self, processing_title: str) -> str:
        """Cuts keywords like resolution, source, etc. from the title."""
        tags = [
            '2160p', '1080p', '720p', '480p', 'BluRay', r'(4K)?\s*Remux',
            r'WEB-?(DL)?', r'(?<![a-z])4K', r'(?<=\w\s)BDMV',
        ]
        pattern = r'(' + '|'.join(tag for tag in tags) + r')\b.*$'
        processing_title = re.sub(pattern, '', processing_title, flags=re.IGNORECASE)
        return processing_title.strip()

    def _extract_cn_title(self, processing_title: str) -> Tuple[str, str]:
        """Extracts the Chinese title from the string."""
        cn_title = ""
        if contains_cjk(processing_title):
            cn_title = processing_title
            # Strip category bracket prefix like 【日漫】
            cn_title = re.sub(r'^[「【\[](?:[国日美韩]漫|国产(?:动漫|剧)?|日漫|国漫|美剧|动漫|动画|纪录片?|电影|TV|\w+字幕组|\w+Fansub)[】」\]]\s*', '', cn_title, flags=re.I).strip()
            cn_title = re.sub(r'^\d{2,4}年\d{1,2}月[新]?番[，,\s]*', '', cn_title).strip()

            if m := re.search(r"([一-鿆]+[\-0-9a-zA-Z]*)[ :：]+([^一-鿆]+\b)", cn_title, flags=re.I):
                cn_title = cn_title[:m.span(1)[1]]
                processing_title = m.group(2)

            if m1 := re.match(r'^([^一-鿆]*)[\s\(\[]+[一-鿆]', cn_title, flags=re.I):
                cn_title = cn_title.replace(m1.group(1), '').strip()

            if cn_title:
                match = re.match(r'^([^ \-\(\[]*)', cn_title)
                if match:
                    cn_title = match.group()

            # Clean attached specs like 1080p简中, 日语中字720p, 国语硬字
            cn_title = re.sub(r'(?:1080[pi]?|2160p|4K|720p|576p|480p|\d{3,4}[xX]\d{3,4}|国语中字|中文字幕|双语|简繁|中字|简中|繁中|简体|繁体|硬字|国语硬字|国语|粤语|日语中字|日语).*$', '', cn_title).strip()

        return processing_title.strip(), cn_title

    def _has_english_chars(self, text: str) -> bool:
        """Checks if the title contains meaningful English title words."""
        cleaned = re.sub(r'\b(1080[pi]?|2160p|4K|720p|576p|480p|\d{3,4}[xX]\d{3,4}|AVC|HEVC|x26[45]|H\.?26[45]|10bit|8bit|HDR|DV|WEB-?DL|WEB-?rip|BDRip|MP4|MKV)\b', '', text, flags=re.I)
        return bool(re.search('[a-zA-Z]{2,}', cleaned))

    def _polish_title(self) -> None:
        """Polishes the final title by removing noise."""
        self.title = re.sub(r'[\._\+]', ' ', self.title)
        tags = [
            r'^Jade\b', r'^(KBS|SBS)\d*\b', r'^TVBClassic', r'CCTV\s*\d+(HD|\+)?', r'Top\s*\d+',
            r'\b\w+版', r'[全共]\d+集', 'BDMV',
            'COMPLETE', 'REPACK', 'PROPER', r'REMASTER\w*',
            'iNTERNAL', 'LIMITED', 'EXTENDED', 'UNRATED',
            r"Direct.{1,5}Cut"
        ]
        pattern = r'\b(' + '|'.join(tag for tag in tags) + r')\b'
        self.title = re.sub(pattern, '', self.title, flags=re.IGNORECASE)
        self.title = self.title.strip()

        self.title = hyphen_to_space(self.title)
        self.title = cut_aka(self.title)
        self.title = re.sub(r'\s+', ' ', self.title).strip()

        if len(self.title) < 1 or self.title.lower() in ['mp4', 'mkv', 'avi', 'ts', 'iso', 'flac', 'zip', '7z', 'rar', 'strm']: 
            self.title = self.failsafe_title.strip()

        if not self._has_english_chars(self.title) and self.cntitle:
            self.title = self.cntitle

        if not self._has_english_chars(self.title):
            self.title = re.sub(r'(?:1080[pi]?|2160p|4K|720p|576p|480p|\d{3,4}[xX]\d{3,4}|国语中字|中文字幕|双语|简繁|中字|简中|繁中|简体|繁体|硬字|国语硬字|国语|粤语|日语中字|日语).*$', '', self.title).strip()

    def to_dict(self) -> Dict[str, Any]:
        """Returns the parsed data as a dictionary."""
        return {
            'title': self.title,
            'cntitle': self.cntitle,
            'year': self.year,
            'type': self.type,
            'season': self.season,
            'episode': self.episode,
            'seasons': self.seasons,
            'episodes': self.episodes,
            'media_source': self.media_source,
            'group': self.group,
            'resolution': self.resolution,
            'video': self.video,
            'audio': self.audio,
            'full_season': self.full_season,
        }

def parse_tor_name(name: str) -> TorTitle:
    """
    Parses a torrent name and returns a TorTitle object.
    This is a convenience function.
    """
    return TorTitle(name)
