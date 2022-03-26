import os
import sys
import threading
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from qtwidgets import AnimatedToggle

from warp_gui.commend import Commend
from warp_gui.ui.mainwindow_ui import Ui_MainWindow


class GUI:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.mainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.commend = Commend()
        self.ui.setupUi(self.mainWindow)
        self.need_stop = False
        self.last_status = self.commend.status()
        self.connected = self.commend.is_connected()
        threading.Thread(target=self.status_thread).start()

        self.toggle_color = "#f77033"
        self.init_account()

        self.toggle = self.init_toggle(self.toggle_color)
        self.init_signals()
        self.set_icon()

    def init_account(self):
        teams = self.commend.teams()
        if teams:
            self.ui.account_type.setText('TEAMS')
            self.ui.account_type.setStyleSheet(u"color:rgb(70, 111, 221);")
            self.toggle_color = "#466fdd"

    def init_toggle(self, color):
        toggle = AnimatedToggle(
            checked_color=color,
            pulse_checked_color="#44FFB000",
        )
        if self.connected:
            toggle.setChecked(True)
        toggle.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        toggle.setMinimumSize(140, 120)
        self.ui.pushButton_start_end.close()
        self.ui.gridLayout.addWidget(toggle, 0, 1, 1, 1)
        return toggle

    def set_icon(self):
        self.mainWindow.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__) + "/../icons/logo.png"))

    def init_signals(self):
        self.toggle.clicked.connect(self.connect_button_clicked)

    def connect_button_clicked(self):
        if self.toggle.isChecked():
            self.commend.connect()
        else:
            self.commend.disconnect()

    def show(self):
        self.mainWindow.show()
        self.app.aboutToQuit.connect(self.end_program)
        sys.exit(self.app.exec_())

    def end_program(self):
        self.need_stop = True

    def status_thread(self):
        while not self.need_stop:
            status = self.commend.status()
            if status:
                self.ui.label_status_message.setText(status)

            if self.last_status != status:
                if status == 'Connected':
                    self.toggle.setChecked(True)
                    self.ui.label_status_message.setStyleSheet(u"color:rgb(123, 199, 171);")
                    self.set_sub_status_message('private')
                    self.connected = True
                elif status == 'Disconnected' or \
                        status == 'No network':
                    self.toggle.setChecked(False)
                    self.set_sub_status_message('not private')
                    self.ui.label_status_message.setStyleSheet(u"color:rgb(255, 80, 57);")
                    self.connected = False
                self.last_status = status
            time.sleep(1)

    def set_sub_status_message(self, text):
        self.ui.label_status_sub_message.setText(
            "<html><head/><body><p><span style=\" font-size:11pt; color:#ffffff;\">Your internet is </span><span "
            "style=\" font-size:11pt; font-weight:600; color:#ffffff;\">{text}</span></p></body></html>".format(
                text=text))
