import pytest
from tortitle import TorTitle

# Test cases formatted as a list of (input_string, expected_dictionary)
TEST_CASES = [
    (
        "The.Matrix.1999.1080p.BluRay.x264-GROUP",
        {
            "title": "The Matrix", "year": "1999", "type": "movie",
            "resolution": "1080p", "media_source": "encode", "group": "GROUP"
        }
    ),
    (
        "Breaking.Bad.S01E01.720p.BluRay.x264-GROUP",
        {
            "title": "Breaking Bad", "year": "", "type": "tv", "season": "S01",
            "episode": "E01", "resolution": "720p", "media_source": "encode", "group": "GROUP"
        }
    ),
    (
        "Inception.2010.1080p.BluRay.x264-GROUP",
        {"title": "Inception", "year": "2010", "type": "movie"}
    ),
    (
        "【囧妈】Lost.in.Russia.2020.WEB-DL.1080p.H264.AAC-CMCTV",
        {
            "title": "Lost in Russia", "cntitle": "", "year": "2020",
            "resolution": "1080p", "media_source": "webdl", "group": "CMCTV"
        }
    ),
    (
        "[The.Mandalorian].S01E01.(2019).1080p.WEB-DL-GROUP",
        {
            "title": "The Mandalorian", "year": "2019", "type": "tv",
            "season": "S01", "episode": "E01"
        }
    ),
    (
        "She's Got No Name 2025 2160p WEB-DL H265 DTS5.1-CHDWEB",
        {"title": "She's Got No Name", "year": "2025", "type": "movie", "audio": "DTS5.1"}
    ),
    (
        "[大陆][绝世天医][Jue Shi Tian Yi 2025 S01 1080p WEB-DL H.264 AAC-GodDramas]",
        {
            "title": "Jue Shi Tian Yi", "cntitle": "绝世天医", "year": "2025", "type": "tv",
            "season": "S01", "episode": "", "resolution": "1080p",
            "media_source": "webdl", "group": "GodDramas"
        }
    ),
    (
        "[TV][jsum@U2][我独自升级 第二季 -起于暗影-][Ore dake Level Up na Ken Season 2: Arise from the Shadow][1080p][TV 01-13(13-25) Fin+SP][MKV/BDRip][2025年01月]",
        {"title": "Ore dake Level Up na Ken", "type": "tv"}
    ),
    (
        "[The.Movie.2023][1080p][BluRay]",
        {"title": "The Movie", "year": "2023", "resolution": "1080p", "media_source": "bluray"}
    ),
    (
        "[美剧][古战场传奇 第八季][Outlander.Blood.of.My.Blood.S01E03.School.of.the.Moon.2160p.STAN.WEB-DL.DDP5.1.HDR.H.265-NTb]",
        {
            "title": "Outlander Blood of My Blood", "cntitle": "古战场传奇", "year": "",
            "type": "tv", "season": "S01", "episode": "E03", "resolution": "2160p",
            "media_source": "webdl", "group": "NTb"
        }
    ),
    (
        "[瑞典][克拉克][Clark.S01.2160p.NF.WEB-DL.DD+5.1.H.265-playWEB]",
        {"title": "Clark", "cntitle": "克拉克", "year": ""}
    ),
    (
        "[大陆][光·渊][Justice.in.The.Dark.2023.S01.Complete.1080p.WOWOW.WEB-DL.H.264.AAC-UBWEB]",
        {
            "title": "Justice in The Dark", "cntitle": "光·渊", "year": "2023",
            "type": "tv", "season": "S01", "episode": "", "resolution": "1080p",
            "media_source": "webdl", "group": "UBWEB"
        }
    )
]

@pytest.mark.parametrize("input_string, expected_dict", TEST_CASES)
def test_title_parsing(input_string, expected_dict):
    """Tests that various torrent titles are parsed correctly."""
    tor_title = TorTitle(input_string)
    for key, value in expected_dict.items():
        assert getattr(tor_title, key) == value, f"Failed on key '{key}' for input '{input_string}'"