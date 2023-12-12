# Smplayer Online Word Searching

Simple wrapper for smplayer that adds clickable subtitle functionality for online word searching, similar to that of PotPlayer. 

## Showcase

TBD

## Supported platforms

- Linux

## Required libraries

- mpv
- SMPlayer (should be configured to use mpv as a multimedia engine)
- Python 3
- PySide2
- xdotool
- socat
- pstree

## Configuration

Browser bin can be configured by editing a global variable:
```
BROWSER_BIN = 'google-chrome-stable'
```

Search engine can be configured by editing a global variable:
```
DICT_URL = 'https://context.reverso.net/translation/spanish-english/{query}'
```