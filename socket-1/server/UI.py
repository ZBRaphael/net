# __author__ = 'ayew'
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QFormLayout,
                             QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QRadioButton,
                             QTextEdit, QVBoxLayout, QWidget)

import time as t
import datetime
import server

class login(QWidget):
    def __init__(self):
        super(login, self).__init__()
        self.initUi()

    def initUi(self):
        self.setWindowTitle("AFL-PTFuzzer")
        layout = QGridLayout()
        self.setGeometry(600, 600, 400, 400)

        timeLabel = QLabel("时间限制")
        self.timeLineEdit = QLineEdit()
        self.timeLineEdit.setPlaceholderText("50ms-1000ms")
        memoryLabel = QLabel("内存限制")
        self.memoryLineEdit = QLineEdit()
        self.memoryLineEdit.setPlaceholderText("50MB none=unlimited")
        # mainLabel = QLabel("主模糊器")
        self.cbLineEdit = QLineEdit("master")
        layout.setSpacing(10)
        inputpathButton = QPushButton("选择种子文件夹")
        self.inputpath = QLineEdit("")
        self.inputpath.setReadOnly(True)
        outputpathButton = QPushButton("选择输出文件夹")
        self.outputpath = QLineEdit()
        self.outputpath.setReadOnly(True)
        exepathButton = QPushButton("选择被测程序")
        self.exepath = QLineEdit()
        self.exepath.setReadOnly(True)
        self.radioButton = QRadioButton("被测程序参数")
        self.diyLineEdit = QLineEdit("")
        self.cb = QComboBox()  # 创建一个 Qcombo  box实例
        self.cb.addItems(["master", "slaver1", "slaver2",
                          "slaver3", "slaver4", "slaver5"])
        self.cb.currentIndexChanged.connect(self.selectionchange)
        # layout.addWidget(self.cb)
        layout.addWidget(exepathButton, 1, 0)
        layout.addWidget(self.exepath, 1, 1)
        layout.addWidget(inputpathButton, 2, 0)
        layout.addWidget(self.inputpath, 2, 1)
        layout.addWidget(outputpathButton, 3, 0)
        layout.addWidget(self.outputpath, 3, 1)
        layout.addWidget(timeLabel, 4, 0)
        layout.addWidget(self.timeLineEdit, 4, 1)
        layout.addWidget(memoryLabel, 5, 0)
        layout.addWidget(self.memoryLineEdit, 5, 1)
        layout.addWidget(self.cb, 6, 0)
        layout.addWidget(self.cbLineEdit, 6, 1)
        # layout.addWidget(slaveLabel, 6, 0)
        # layout.addWidget(self.slaveLineEdit, 6, 1)
        layout.addWidget(self.radioButton, 7, 0)
        layout.addWidget(self.diyLineEdit, 7, 1)
        layout.setColumnStretch(1, 10)
        save_Btn = QPushButton('运行')
        cancle_Btn = QPushButton('退出')
        cancle_Btn.clicked.connect(self.close)
        save_Btn.clicked.connect(self.runProgram)
        inputpathButton.clicked.connect(self.openinputFile)
        outputpathButton.clicked.connect(self.openoutputFile)
        exepathButton.clicked.connect(self.openexeFile)
        layout.addWidget(save_Btn)
        layout.addWidget(cancle_Btn)
        self.setLayout(layout)

    def selectionchange(self, i):
        self.cbLineEdit.setText(self.cb.currentText())  # 将当前选项 文字设置子lab 标签上

        # print("Items in the list are :")

    def runProgram(self):
        diy = ''
        if self.radioButton.isChecked():
            diy = self.diyLineEdit.text()
            # print(diy)
        seeddir = self.inputpath.text()  # 获取文本框内容
        seeddir = os.path.abspath(seeddir)
        outdir = self.outputpath.text()
        outdir = os.path.abspath(outdir)
        progname = self.exepath.text()
        progname = os.path.abspath(progname)
        timelimit = self.timeLineEdit.text()
        progInput = self.cbLineEdit.text()
        memorylimit = self.memoryLineEdit.text()

        prog_info = {}
        prog_info["seeddir"] = seeddir
        prog_info["outdir"] = outdir
        prog_info["progname"] = progname
        prog_info["progInput"] = progInput
        prog_info["timelimit"] = timelimit
        prog_info["memorylimit"] = memorylimit

        server.startServers(progInfo=prog_info)
        
        #开启socket
        # if cb == "master":
        #     command = 'python ptfuzzer.py '+'\"'+'-i:'+intext+' -o:'+outtext+' -t:'+time+' -M:'+cb+' -m:'+memory+'\" '+'\"'+test+" "+diy+'\"'
        # else:
        #     command = 'python ptfuzzer.py '+'\"'+'-i:'+intext+' -o:'+outtext+' -t:'+time+' -S:'+cb+' -m:'+memory+'\" '+'\"'+test+" "+diy+'\"'
        # # os.system("python3 receiver.py")
        # os.system("python3 sender.py -C "+"\'"+command+"\'")
        # # print(command)
        # file_list = os.listdir(intext)
        # starttime = t.process_time()
        # for f in file_list:
        #     os.system("python3 sender.py -F "+ intext +'/'+ f)

        # endtime = t.process_time()
        # print (endtime - starttime)
    def openinputFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(self, "选取种子文件夹")
        self.inputpath.setText(str(get_directory_path))

    def openoutputFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(self, "选取输出文件夹")
        self.outputpath.setText(str(get_directory_path))

    def openexeFile(self):
        get_filename_path, ok = QFileDialog.getOpenFileName(self,
                                                            "选取单个文件",
                                                            ".",
                                                            "All Files (*);;Text Files (*.txt)")
        if ok:
            self.exepath.setText(str(get_filename_path))

    def close(self):
        reply = QMessageBox.question(self, '退出',
                                     "确认退出?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QCoreApplication.quit()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, '退出',
                                     "确认退出?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginUI = login()
    loginUI.show()
    sys.exit(app.exec_())
