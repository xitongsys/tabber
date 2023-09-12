import sys
from PySide6 import QtCore, QtWidgets, QtGui
import PySide6.QtGui
import wmctrl


class TabberSettingWidget(QtWidgets.QWidget):
    def __init__(self, tabwidget):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.tabwidget = tabwidget
        self.tab_type = 'setting'

        # ToolBar
        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar_edit = QtWidgets.QLineEdit()
        self.tool_bar_conn_btn = QtWidgets.QPushButton("connect")
        self.tool_bar.addWidget(self.tool_bar_edit)
        self.tool_bar.addWidget(self.tool_bar_conn_btn)

        self.tool_bar_conn_btn.clicked.connect(self.tool_bar_conn_btn_click)
        self.layout.addWidget(self.tool_bar)
        ########

        self.setLayout(self.layout)

    
    @QtCore.Slot()
    def tool_bar_conn_btn_click(self):
        #wid = int(self.tool_bar_edit.text(), 16)
        #self.tabwidget.new_tab(0, wid)

        cmd = self.tool_bar_edit.text().split()

        proc = QtCore.QProcess()
        proc.start(cmd[0], cmd[1:])
        proc.waitForStarted(1000)
        pid = proc.processId()

        import time
        wins = []
        for _ in range(5):               
            wins = list(filter(lambda w: w.pid == pid, wmctrl.Window.list()))
            if len(wins) == 0:
                time.sleep(1)

        if len(wins) == 0:
            return
            
        wid = int(wins[0].id, 16)

        print(wid, pid)

        self.tabwidget.new_tab(pid, wid, proc)     



    def tabber_close(self):
        pass


class TabberWinWidget(QtWidgets.QWidget):
    def __init__(self, pid:int, wid:int, proc=None):
        super().__init__()
        self.tab_type = 'win'

        self.pid = pid
        self.wid = wid
        self.proc = proc
        self.win = QtGui.QWindow.fromWinId(wid)

        self.layout = QtWidgets.QVBoxLayout()
        
        self.win_container = self.createWindowContainer(self.win, self)
        self.layout.addWidget(self.win_container)

    def resizeEvent(self, event) -> None:
        win = QtGui.QWindow.fromWinId(self.wid)
        win.resize(self.size())
        return super().resizeEvent(event)
    
    def tabber_close(self):
        win = QtGui.QWindow.fromWinId(self.wid)
        win.close()
        if self.proc:
            self.proc.terminate()


class TabberTabWidget(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setMovable(True)

        self.setting_tab = TabberSettingWidget(self)

        self.addTab(self.setting_tab, "setting")       

        self.tabCloseRequested.connect(self.close_tab)
    

    def new_tab(self, pid:int, wid:int, proc=None):
        wintab = TabberWinWidget(pid, wid, proc)
        win = QtGui.QWindow.fromWinId(wid)
        self.addTab(wintab, win.title())


    @QtCore.Slot()
    def close_tab(self, idx):
        widget = self.widget(idx)
        if widget.tab_type == 'win':
            widget.tabber_close()
            self.removeTab(idx)
        
    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("tabber")
        self.tab_widget = TabberTabWidget()
        self.setCentralWidget(self.tab_widget)
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())