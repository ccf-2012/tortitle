# TorTitle

A title parser for torrent filenames.

This library helps parse torrent filenames to extract structured information like title, year, season, episode, etc.

## Installation

```bash
pip install tortitle
```

## Usage

```python
from tortitle import TorTitle


result = TorTitle("The.Mandalorian.S01E01.1080p.WEB-DL.DDP5.1.H.264-NTb.mkv")
print(result.to_dict())
```
