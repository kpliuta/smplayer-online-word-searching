# Smplayer Online Word Searching

Simple wrapper for smplayer that adds clickable subtitle functionality for online word searching, similar to that of PotPlayer. 

## Showcase

![2023-12-12_13-07](https://github.com/kpliuta/smplayer-online-word-searching/assets/9212935/8e07b440-2d49-453b-a133-0e54d201c791)

![2023-12-12_13-12](https://github.com/kpliuta/smplayer-online-word-searching/assets/9212935/7a5f9111-43aa-45e9-992b-5cfa90852359)

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
