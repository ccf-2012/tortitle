import re
import os


def cut_ext(torrent_name):
    if not torrent_name:
        return ''
    tortup = os.path.splitext(torrent_name)
    torext = tortup[1].lower()
    # if re.match(r'\.[0-9a-z]{2,5}$', torext, flags=re.I):
    mvext = ['.strm', '.mkv', '.ts', '.m2ts', '.vob', '.mpg', '.mp4', '.3gp', '.mov', '.tp', '.zip', '.pdf', '.iso', '.ass', '.srt', '.7z', '.rar']
    if torext.lower() in mvext:
        return tortup[0].strip()
    else:
        return torrent_name

def delimer_to_space(input_string):
    dilimers = ['[', ']', '.', '{', '}', '_', ',', '(', ')', '「', '」']
    for dchar in dilimers:
        input_string = input_string.replace(dchar, ' ')
    return input_string

def hyphen_to_space(input_string):
    return input_string.replace('-', ' ')

def cutspan(input_string, from_index, to_index):
    if (from_index >= 0) and (len(input_string) > to_index):
        input_string = input_string[0:from_index:] + input_string[to_index::]
    return input_string

def contains_cjk(input_string):
    return re.search(r'[\u4e00-\u9fa5\u3041-\u30fc]', input_string)

def cut_aka(title_string):
    m = re.search(r'\s(/|AKA)\s', title_string, re.I)
    if m:
        title_string = title_string.split(m.group(0))[0]
    return title_string.strip()

def tryint(input_string):
    cndigit = '一二三四五六七八九十'
    if input_string and input_string[0] in cndigit and len(input_string) == 1:
        return cndigit.index(input_string[0]) + 1
    try:
        return int(input_string)
    except:
        return 0

def is_0day_name(item_string):
    # CoComelon.S03.1080p.NF.WEB-DL.DDP2.0.H.264-NPMS
    m = re.match(r'^\w+.*\b(BluRay|Blu-?ray|720p|1080[pi]|[xh].?26\d|2160p|576i|WEB-DL|DVD|WEBRip|HDTV)\b.*', item_string, flags=re.A | re.I)
    return m

class TorTitle:
    def __init__(self, name):
        self.raw_name = name  or ""
        self.title = name or ""
        self.cntitle = ''
        self.year = ''
        self.type = 'movie'
        self.season = ''
        self.episode = ''
        self.seasons = []
        self.episodes = []
        self.sub_episode = ''
        self.media_source = ''
        self.group = ''
        self.resolution = ''
        self.video = '' 
        self.audio = ''
        self.full_season = False
        self._se_pos = 0
        self._year_pos = 0
        self.failsafe_title = self.title
        self.parse()

    def parse(self):
        self.raw_name = self.title
        self.title, self.cntitle = self._handle_bracket_title(self.title)

        self.media_source, self.video, self.audio = self._parse_more(self.raw_name)
        self.resolution = self._parse_resolution(self.raw_name)
        self.type = self._check_tv_type(delimer_to_space(self.raw_name))

        self.title = self._prepare_title(self.title)

        self.group = self._parse_group(self.title)
        yearpos, self.year = self._extract_year(self.title)
        se_pos = self._extract_season_episdoe(self.title)
        self.failsafe_title = self.title
        self.title = self._cut_s_year_season(self.title, yearpos, se_pos)
        self.title = self._cut_s_keyword(self.title)

        if not self.cntitle:
            self.title, self.cntitle = self._extract_cntitle(self.title) 
        self._polish_title()


    def _parse_more(self, torrent_name):
        media_source, video, audio = '', '', ''
        if m := re.search(r"(?<=(1080p|2160p)\s)(((\w+)\s+)?WEB(-DL)?)|\bWEB(-DL)?\b|\bHDTV\b|((UHD )?(BluRay|Blu-ray))", torrent_name, re.I):
            m0 = m[0].strip()
            if re.search(r'WEB[-]?(DL)?', m0, re.I):
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

    def _parse_resolution(self, torrent_name):
        match = re.search(r'\b(4K|2160p|1080[pi]|720p|576p|480p)\b', torrent_name, re.A | re.I)
        if match:
            r = match.group(0).strip().lower()
            if r == '4k':
                r = '2160p'
            return r
        else:
            return ''
        
    def _parse_group(self, torrent_name):
        sstr = cut_ext(torrent_name)
        match = re.search(r'[@\-￡]\s?(\w+)(?!.*[@\-￡].*)$', sstr, re.I)
        if match:
            group_name = match.group(1).strip()
            return group_name

        return None
        
    def _prepare_title(self, processing_title):
        processing_title = cut_ext(processing_title)
        processing_title = re.sub(r'^[「【][^】」]*[】」]', '', processing_title, flags=re.I)
        processing_title = re.sub(r'^\w+TV-?(\d+)?([48]K)?\b', '', processing_title, flags=re.I)
        # if re.search(r"\d+x\d+", processing_title, flags=re.I):
        #     processing_title = re.sub(r'^\d{4}[\s\.]', '', processing_title, flags=re.I)
        processing_title = delimer_to_space(processing_title)
        return processing_title

    def _handle_bracket_title(self, processing_title):
        cntitle = ""
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
                if re.match(r'^'+keyword_pattern+'$', main_part, flags=re.I):
                    if keyword_idx > 0:
                        keyword_idx = keyword_idx - 1
                        processing_title = parts[keyword_idx]
                else:
                    processing_title = main_part
                if keyword_idx > 0 and contains_cjk(parts[keyword_idx-1]):
                    full_cntitle = parts[keyword_idx-1]
                    full_cntitle = re.sub(r'大陆|港台', '', full_cntitle, flags=re.I)
                    cntitle = full_cntitle.split(' ')[0].strip()
        return processing_title, cntitle

    def _extract_year(self, processing_title):
        _year_pos = 0
        year = ""
        potential_years = re.findall(r'(19\d{2}|20\d{2})(?:\d{4})?\b', processing_title)
        if potential_years:
            year = potential_years[-1]
            _year_pos = processing_title.rfind(year)
        return _year_pos, year

    def _match_season(self, processing_title, match_key=None):
        patterns = {
            's_e': r'\b(S(\d+))(E(\d+)(-Ep?(\d+))?)\b',
            'season_only': r'(?<![a-zA-Z])(S(\d+)([\-\+]S?(\d+))?)\b(?!.*\bS\d+)',
            'season_word': r'\bSeason (\d+)\b',
            'ep_only': r'\bEp?(\d+)(-E?p?(\d+))?\b',
            'cn_season': r'第([一二三四五六七八九十]|\d+)季',
            'cn_episode': r'第([一二三四五六七八九十]+|\d+)集',
            'full_season': r'[全]\w{,4}\s*[集季]'
        }
        if match_key:
            return re.search(patterns[match_key], processing_title)
        else:
            for key, pattern in patterns.items():
                match = re.search(pattern, processing_title, flags=re.IGNORECASE)
                if match:
                    return key, match
            return None, None

    def _check_tv_type(self, processing_title):
        category = 'movie'
        key, match = self._match_season(processing_title)
        if match:
            category = 'tv'
            # if self._match_season(processing_title, 'full_season'):
            #     full_season = True
        return category

    def _extract_season_episdoe(self, processing_title):
        se_pos = 0
        key, match = self._match_season(processing_title)
        if match:
            if key in ['s_e']:
                # self.season_int = int(match.group(1))
                # self.episode_int = int(match.group(2))
                self.season = match.group(1)
                self.episode = match.group(3)
                self.seasons = [int(match.group(2))]
                if match.group(6):
                    self.episodes = list(range(int(match.group(4)), int(match.group(6))+1))
                else:
                    self.episodes = [int(match.group(4))]
            elif key == 'season_only':
                # self.season_int = tryint(match.group(1))
                self.season = match.group(0)
                if match.group(4):
                    self.seasons = list(range(int(match.group(2)), int(match.group(4))+1))
                else:
                    self.seasons = [int(match.group(2))]
            elif key in ['season_word', 'cn_season']:
                # self.season_int = tryint(match.group(1))
                season_int = tryint(match.group(1))
                self.seasons = [season_int]
                self.season = 'S'+ str(season_int).zfill(2) if season_int else ''
            elif key in ['cn_episode', 'ep_only']:
                self.season = 'S01'
                self.seasons = [1]
                if match.group(3):
                    self.episodes = list(range(tryint(match.group(1)), tryint(match.group(3))+1))
                else:
                    self.episodes = [tryint(match.group(1))]

                self.episode = match.group()
            elif key == 'full_season':
                self.full_season = True

            se_pos = match.span(0)[0]
        return se_pos

    def _cut_s_year_season(self, processing_title, year_pos, se_pos):
        positions = [p for p in [year_pos, se_pos] if p > 0]
        if not positions:
            if try_match := re.search(r"(\d+x\d+|BDRip|.26[45])", processing_title, flags=re.I):
                positions = [try_match.span(0)[0]]
        if positions:
            cut_pos = min(positions)
            processing_title = processing_title[:cut_pos]
        return processing_title.strip()

    def _cut_s_keyword(self, processing_title):
        tags = [
            '2160p', '1080p', '720p', '480p', 'BluRay', r'(4K)?\s*Remux', 
            r'WEB-?(DL)?', r'(?<![a-z])4K', r'(?<=\w\s)BDMV',
        ]
        pattern = r'(' + '|'.join(tag for tag in tags) + r')\b.*$'
        processing_title = re.sub(pattern, '', processing_title, flags=re.IGNORECASE)
        return processing_title.strip()
    
    def _extract_cntitle(self, processing_title):
        cntitle = ""
        if contains_cjk(processing_title):
            cntitle = processing_title
            if m := re.search(r"([一-鿆]+[\-0-9a-zA-Z]*)[ :：]+([^一-鿆]+\b)", processing_title, flags=re.I):
                cntitle = cntitle[:m.span(1)[1]]
                processing_title = m.group(2)

            # 删去：汉字之前，有空格分隔的 ascii 字符串
            if m1 := re.match(r'^([^一-鿆]*)[\s\(\[]+[一-鿆]', cntitle, flags=re.I):
                cntitle = cntitle.replace(m1.group(1), '').strip()

            # 取汉字串中第一个空格前部分
            if cntitle:
                match = re.match(r'^([^ \-\(\[]*)', cntitle)
                if match:
                    cntitle = match.group()

        return processing_title.strip(), cntitle

    def _check_title(self):
        m1 = re.search('[a-zA-Z]', self.title)
        if len(self.title) > 2 and m1:
            return True
        else:
            return False

    def _polish_title(self):
        self.title = re.sub(r'[\._\+]', ' ', self.title)
        tags = [
            r'^Jade\b', '^TVBClassic' r'CCTV\s*\d+(HD|\+)?', r'Top\s*\d+',
            r'\b\w+版', r'全\d+集', 'BDMV',
            'COMPLETE', 'REPACK', 'PROPER', r'REMASTER\w*',
            'iNTERNAL', 'LIMITED', 'EXTENDED', 'UNRATED', 
            r"Direct.{1,5}Cut"
        ]
        pattern = r'\b(' + '|'.join(tag for tag in tags) + r')\b'
        self.title = re.sub(pattern, '', self.title, flags=re.IGNORECASE)
        self.title = self.title.strip()

        self.title = hyphen_to_space(self.title)
        self.title = cut_aka(self.title)
        self.title = re.sub(r'\s+', ' ', self.title)

        self.title = self.title if len(self.title) > 0 else self.failsafe_title
        if not self._check_title() and self.cntitle:
            self.title = self.cntitle

    def _handle_special_cases(self):
        pass

    def to_dict(self):
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
            'audio': self.audio
        }

def parse_tor_name(name):
    return TorTitle(name)

