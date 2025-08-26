#! /usr/bin/env python
"""
A Qt-based application that embeds an SMPlayer instance to provide on-the-fly
subtitle word lookup.

This script launches a custom window, starts SMPlayer within it, and polls for
subtitle text. The subtitles are displayed in a separate text box, allowing
users to select words or phrases to search in an online dictionary.
"""

import json
import logging
import sys
import time

from PySide6 import QtCore, QtGui, QtWidgets

# --- Configuration ---
# The command to execute your web browser.
BROWSER_BIN = 'google-chrome-stable'
# The URL for the dictionary lookup. `{query}` is replaced with the selected text.
DICT_URL = 'https://context.reverso.net/translation/spanish-english/{query}'


class MainWidget(QtWidgets.QWidget):
    """The main application window that orchestrates all other components."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle('SMPlayer Subtitle Searcher')
        self.showMaximized()
        self.setLayout(MainWidgetLayout())

        # Start the SMPlayer process.
        self.smplayer_process = SmplayerProcess()
        self.smplayer_process.start()

        # Find the SMPlayer window and embed it into the layout.
        self.layout().addWidget(self.smplayer_process.init_smplayer_widget())

        # Create the text box for displaying subtitles.
        self.subtitles_text_edit = SubtitlesTextEdit()
        self.subtitles_text_edit.text_selected_signal.connect(open_web_page)
        self.layout().addWidget(self.subtitles_text_edit)

        # Start the reader that polls for new subtitles from the player.
        self.subtitle_reader = SubtitlesReader(self.smplayer_process.processId())
        self.subtitle_reader.subtitles_changed_signal.connect(self.subtitles_text_edit.setText)
        self.subtitle_reader.start()


class MainWidgetLayout(QtWidgets.QVBoxLayout):
    """A simple QVBoxLayout with zero margins for a tight fit."""
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)


class SmplayerProcess(QtCore.QProcess):
    """Manages the SMPlayer QProcess, including starting it and finding its window ID."""
    def __init__(self):
        super().__init__()
        self.setProgram('smplayer')

    def init_smplayer_widget(self):
        """
        Finds the external SMPlayer window and wraps it in a QWidget container.

        This is the core mechanism for embedding the player into the Qt application.

        Returns:
            QtWidgets.QWidget: The container widget holding the SMPlayer window.
        """
        ext_window_id = self.find_ext_window_id()
        ext_window = QtGui.QWindow.fromWinId(int(ext_window_id))
        return QtWidgets.QWidget.createWindowContainer(ext_window)

    def find_ext_window_id(self):
        """
        Finds the SMPlayer window ID by repeatedly calling `xdotool`.

        SMPlayer takes a moment to launch, so this method retries for a few
        seconds before giving up.

        Raises:
            Exception: If the window ID cannot be found after several attempts.

        Returns:
            str: The found window ID.
        """
        for _ in range(10):
            ext_window_id = self.execute_xdotool()
            if ext_window_id:
                return ext_window_id
            time.sleep(0.2)
        raise Exception(f'Cannot find external window id by {self.processId()} smplayer pid')

    def execute_xdotool(self):
        """Helper method to execute the xdotool command to find the window ID."""
        return execute_command(f'xdotool search --pid {self.processId()} --onlyvisible')


class SubtitlesTextEdit(QtWidgets.QTextEdit):
    """A custom QTextEdit to display subtitles and emit a signal when text is selected."""
    text_selected_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self.setReadOnly(True)
        self.setStyleSheet("font-size: 18pt; background-color: black;")

    def mouseReleaseEvent(self, event):
        """
        Overrides the mouse release event to detect when text has been selected.

        Args:
            event: The mouse event.
        """
        super().mouseReleaseEvent(event)
        selected_text = self.textCursor().selectedText()
        if selected_text:
            self.text_selected_signal.emit(selected_text)

    def setText(self, text):
        """
        Sets the subtitle text, wrapping it in HTML for styling.

        Args:
            text (str): The raw subtitle text.
        """
        super().setText(f'<div style="text-align: center; color: white;">{text}</div>')


class SubtitlesReader(QtCore.QTimer):
    """
    A QTimer-based class that periodically polls the running mpv instance
    (a child of SMPlayer) for subtitle changes via its IPC server.
    """
    subtitles_changed_signal = QtCore.Signal(str)

    def __init__(self, smplayer_pid):
        super().__init__()
        self.smplayer_pid = smplayer_pid

        self.ipc_server = None
        self.last_read_subtitles = None

        # Poll for subtitles every 500ms.
        self.setInterval(500)
        self.timeout.connect(self.read_subtitles)

    def read_subtitles(self):
        """Reads subtitle text from mpv's IPC server if available."""
        if self.init_ipc_server():
            output = execute_command(
                f'echo \'{{"command": ["get_property", "sub-text"] }}\' | socat - {self.ipc_server}')
            if output:
                data = json.loads(output).get("data", None)
                if data and self.last_read_subtitles != data:
                    self.last_read_subtitles = data
                    self.subtitles_changed_signal.emit(data)

    def init_ipc_server(self):
        """
        Finds the mpv IPC socket path using pstree and caches it.

        SMPlayer launches mpv as a child process. This function inspects the
        process tree to find the `--input-ipc-server` argument passed to mpv.

        Returns:
            bool: True if the IPC server path is found and set, False otherwise.
        """
        if self.ipc_server:
            return True
        output = execute_command(f'pstree -a -T {self.smplayer_pid} | grep -oP \'input-ipc-server=\\K\\S+\'')
        if output:
            self.ipc_server = output
            return True
        else:
            return False


def execute_command(command):
    """
    Executes a shell command synchronously and returns its standard output.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The stripped standard output of the command.
    """
    process = QtCore.QProcess()
    process.setProgram('sh')
    process.setArguments(['-c', command])
    process.start()
    process.waitForFinished()
    output = str(process.readAllStandardOutput(), 'utf-8').strip()
    logging.debug(f'{process.program()} {process.arguments()}: {output}')
    return output


def open_web_page(query):
    """
    Opens a new browser tab with the dictionary URL for the given query.

    Uses startDetached() to launch the browser as a separate, non-blocking process.

    Args:
        query (str): The word or phrase to search for.
    """
    process = QtCore.QProcess()
    process.setProgram(BROWSER_BIN)
    process.setArguments([DICT_URL.format(query=query)])
    process.startDetached()


def main():
    """Application entry point."""
    # logging.basicConfig(level=logging.DEBUG)

    app = QtWidgets.QApplication()
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
