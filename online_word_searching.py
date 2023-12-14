#! /usr/bin/env python

import json
import logging
import sys
import time

from PySide6 import QtCore, QtGui, QtWidgets

BROWSER_BIN = 'google-chrome-stable'
DICT_URL = 'https://context.reverso.net/translation/spanish-english/{query}'


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Online word searching')
        self.showMaximized()
        self.setLayout(MainWidgetLayout())

        self.smplayer_process = SmplayerProcess()
        self.smplayer_process.start()
        self.layout().addWidget(self.smplayer_process.init_smplayer_widget())

        self.subtitles_text_edit = SubtitlesTextEdit()
        self.subtitles_text_edit.text_selected_signal.connect(open_web_page)
        self.layout().addWidget(self.subtitles_text_edit)

        self.subtitle_reader = SubtitlesReader(self.smplayer_process.processId())
        self.subtitle_reader.subtitles_changed_signal.connect(self.subtitles_text_edit.setText)
        self.subtitle_reader.start()


class MainWidgetLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)


class SmplayerProcess(QtCore.QProcess):
    def __init__(self):
        super().__init__()
        self.setProgram('smplayer')

    def init_smplayer_widget(self):
        ext_window_id = self.find_ext_window_id()
        ext_window = QtGui.QWindow.fromWinId(int(ext_window_id))
        return QtWidgets.QWidget.createWindowContainer(ext_window)

    def find_ext_window_id(self):
        for _ in range(10):
            ext_window_id = self.execute_xdotool()
            if ext_window_id:
                return ext_window_id
            time.sleep(0.2)
        raise Exception(f'Cannot find external window id by {self.processId()} smplayer pid')

    def execute_xdotool(self):
        return execute_command(f'xdotool search --pid {self.processId()} --onlyvisible')


class SubtitlesTextEdit(QtWidgets.QTextEdit):
    text_selected_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self.setReadOnly(True)
        self.setStyleSheet("font-size: 18pt; background-color: black;")

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.textCursor().selectedText():
            self.text_selected_signal.emit(self.textCursor().selectedText())

    def setText(self, text):
        super().setText(f'<div style="text-align: center; color: white;">{text}</div>')


class SubtitlesReader(QtCore.QTimer):
    subtitles_changed_signal = QtCore.Signal(str)

    def __init__(self, smplayer_pid):
        super().__init__()
        self.smplayer_pid = smplayer_pid

        self.ipc_server = None
        self.last_read_subtitles = None

        self.setInterval(500)
        self.timeout.connect(self.read_subtitles)

    def read_subtitles(self):
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
        Fetches mpv subprocess command line arguments using pstree command
        and initializes self.ipc_server with input-ipc-server parameter value.
        :return: True if self.ipc_server was initialized successfully of False otherwise
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
    process = QtCore.QProcess()
    process.setProgram('sh')
    process.setArguments(['-c', command])
    process.start()
    process.waitForFinished()
    output = str(process.readAllStandardOutput(), 'utf-8').strip()
    logging.debug(f'{process.program()} {process.arguments()}: {output}')
    return output


def open_web_page(query):
    process = QtCore.QProcess()
    process.setProgram(BROWSER_BIN)
    process.setArguments([DICT_URL.format(query=query)])
    process.startDetached()


def main():
    # logging.basicConfig(level=logging.DEBUG)

    app = QtWidgets.QApplication()
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
