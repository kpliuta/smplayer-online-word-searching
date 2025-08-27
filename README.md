# SMPlayer Subtitle Searcher

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Python wrapper for SMPlayer that adds clickable subtitle functionality for online dictionary searching, similar to the feature in PotPlayer.

This application embeds an SMPlayer instance into a custom Qt window. Below the video, it displays the current subtitles in a text box. You can select any word or phrase from the subtitles to instantly look it up in an online dictionary using your web browser.

## Showcase

<img width="1920" height="1050" alt="289844264-8e07b440-2d49-453b-a133-0e54d201c791" src="https://github.com/user-attachments/assets/018059a6-f447-41f1-8b0c-0b863062fbb5" />
<img width="1920" height="1049" alt="289844294-7a5f9111-43aa-45e9-992b-5cfa90852359" src="https://github.com/user-attachments/assets/c5997268-985e-41f5-8a16-a05a38612024" />

## Requirements

This project is designed for **Linux** and has several dependencies.

### System Dependencies

You must have the following command-line tools installed and available in your system's `PATH`.

- `poetry` (https://python-poetry.org/docs/#installation)
- `mpv`
- `smplayer` (must be configured to use `mpv` as its multimedia engine)
- `xdotool`
- `socat`
- `pstree` (usually part of the `psmisc` package)

### Python Dependencies

The project uses Python ~3.13 and the dependencies are managed by Poetry.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kpliuta/smplayer-sub-search.git
    cd smplayer-sub-search
    ```

2.  **Install project dependencies using Poetry:**
    ```bash
    poetry install
    ```
    This will create a virtual environment and install `PySide6`.

## Usage

Run the application from the project's root directory using Poetry:

```bash
poetry run smplayer-sub-search
```

This will launch the application window with SMPlayer embedded. You can then open a video file using the SMPlayer controls (`File -> Open` or `Ctrl+O`). When subtitles are displayed, they will appear in the text box at the bottom.

## Configuration

To change the default web browser or the dictionary URL, you need to edit the global variables at the top of the `smplayer_sub_search.py` script.

-   **Browser:**
    Change the `BROWSER_BIN` variable to your browser's executable.
    ```python
    BROWSER_BIN = 'google-chrome-stable'
    ```

-   **Dictionary URL:**
    Change the `DICT_URL` variable. The `{query}` placeholder will be replaced with the text you select.
    ```python
    DICT_URL = 'https://context.reverso.net/translation/spanish-english/{query}'
    ```

## License

This project is licensed under the MIT License.
