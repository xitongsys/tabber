import sys
from PySide6 import QtCore, QtWidgets, QtGui
import PySide6.QtGui
import wmctrl

CMD_LIST = [
    ("xterm", "xterm"),
    ("rdp01", "xfreerdp /u:zxt /p:t /v:127.0.0.1 /port:33891 -wallpaper +clipboard +compression /bpp:24 /dynamic-resolution"),
]


class TabberSettingWidget(QtWidgets.QWidget):
    def __init__(self, tabwidget):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.tabwidget = tabwidget
        self.tab_type = 'tabber'

        # ToolBar
        self.tool_bar = QtWidgets.QToolBar()

        self.tool_bar_name_label = QtWidgets.QLabel("name:")
        self.tool_bar_name_edit = QtWidgets.QLineEdit()
        self.tool_bar_cmd_label = QtWidgets.QLabel("   cmd:")
        self.tool_bar_cmd_edit = QtWidgets.QLineEdit()
        self.tool_bar_run_btn = QtWidgets.QPushButton("run")
        self.tool_bar.addWidget(self.tool_bar_name_label)
        self.tool_bar.addWidget(self.tool_bar_name_edit)
        self.tool_bar.addWidget(self.tool_bar_cmd_label)
        self.tool_bar.addWidget(self.tool_bar_cmd_edit)
        self.tool_bar.addWidget(self.tool_bar_run_btn)

        self.tool_bar_name_edit.setMaximumWidth(100)
        self.tool_bar_run_btn.clicked.connect(self.tool_bar_conn_btn_click)
        self.layout.addWidget(self.tool_bar)
        ########

        # Table cmd List
        self.table_cmds = QtWidgets.QTableWidget()
        self.table_cmds.setRowCount(len(CMD_LIST))
        self.table_cmds.setColumnCount(2)
        self.table_cmds.setHorizontalHeaderLabels(["name", "cmd"])
        header = self.table_cmds.horizontalHeader()       
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table_cmds.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        for i, (name,cmd) in enumerate(CMD_LIST):
            item_name = QtWidgets.QTableWidgetItem(name)
            item_cmd = QtWidgets.QTableWidgetItem(cmd)

            self.table_cmds.setItem(i, 0, item_name)
            self.table_cmds.setItem(i, 1, item_cmd)

        self.table_cmds.cellDoubleClicked.connect(self.table_cmds_cell_double_click)

        self.layout.addWidget(self.table_cmds)
        ########


        # All Win ToolBar
        self.tool_bar_all_wins = QtWidgets.QToolBar()

        self.tool_bar_all_wins_name_label = QtWidgets.QLabel("All Windows   ")
        self.tool_bar_all_wins_fresh_btn = QtWidgets.QPushButton("fresh")
        self.tool_bar_all_wins.addWidget(self.tool_bar_all_wins_name_label)
        self.tool_bar_all_wins.addWidget(self.tool_bar_all_wins_fresh_btn)
        
        self.tool_bar_all_wins_fresh_btn.clicked.connect(self.tool_bar_fresh_btn_click)
        self.layout.addWidget(self.tool_bar_all_wins)
        ########

        # All Wins List
        self.table_all_wins = QtWidgets.QTableWidget()
        self.table_all_wins.setColumnCount(3)
        self.table_all_wins.setHorizontalHeaderLabels(["pid", "wid", "name"])
        header = self.table_all_wins.horizontalHeader()       
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table_all_wins.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.tool_bar_fresh_btn_click()
        self.table_all_wins.cellDoubleClicked.connect(self.table_all_wins_cell_double_click)

        self.layout.addWidget(self.table_all_wins)
        ########

        self.setLayout(self.layout)

    @QtCore.Slot()
    def tool_bar_fresh_btn_click(self):
        ws = wmctrl.Window.list()
        self.table_all_wins.setRowCount(len(ws))
        for i, w in enumerate(ws):
            item_name = QtWidgets.QTableWidgetItem(w.wm_name)
            item_wid = QtWidgets.QTableWidgetItem(w.id)
            item_pid = QtWidgets.QTableWidgetItem(str(w.pid))

            self.table_all_wins.setItem(i, 0, item_pid)
            self.table_all_wins.setItem(i, 1, item_wid)
            self.table_all_wins.setItem(i, 2, item_name)

    @QtCore.Slot()
    def table_cmds_cell_double_click(self, row, col):
        name = self.table_cmds.item(row,0).text()
        cmd = self.table_cmds.item(row,1).text()

        self.tool_bar_name_edit.setText(name)
        self.tool_bar_cmd_edit.setText(cmd)
        self.tool_bar_conn_btn_click()

    @QtCore.Slot()
    def table_all_wins_cell_double_click(self, row, col):
        pid = int(self.table_all_wins.item(row,0).text())
        wid = int(self.table_all_wins.item(row,1).text(),16)
        name = self.table_all_wins.item(row,2).text()
        self.tabwidget.new_tab(pid,wid,name)
        self.tool_bar_fresh_btn_click()

    
    @QtCore.Slot()
    def tool_bar_conn_btn_click(self):
        #wid = int(self.tool_bar_edit.text(), 16)
        #self.tabwidget.new_tab(0, wid)

        name = self.tool_bar_name_edit.text()
        cmd = self.tool_bar_cmd_edit.text().split()

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
        self.tabwidget.new_tab(pid, wid, name, proc)     

    def tabber_close(self):
        pass


class TabberWinWidget(QtWidgets.QWidget):
    def __init__(self, pid:int, wid:int, name:str, proc=None):
        super().__init__()
        self.tab_type = 'win'

        self.pid = pid
        self.wid = wid
        self.name = name
        self.proc = proc
        self.win = QtGui.QWindow.fromWinId(wid)
        self.old_flags = self.win.flags()

        self.layout = QtWidgets.QVBoxLayout()
        
        self.win_container = self.createWindowContainer(self.win, self)
        self.layout.addWidget(self.win_container)

    def resizeEvent(self, event) -> None:
        win = QtGui.QWindow.fromWinId(self.wid)
        win.resize(self.size())
        return super().resizeEvent(event)
    
    def tabber_close(self):
        win = QtGui.QWindow.fromWinId(self.wid)
        win.setParent(QtGui.QWindow.fromWinId(0))
        win.setFlags(self.old_flags)
        self.win_container.close()
        if self.proc:
            self.proc.terminate()


class TabberTabWidget(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setMovable(True)

        self.setting_tab = TabberSettingWidget(self)

        self.addTab(self.setting_tab, "MAIN")       

        self.tabCloseRequested.connect(self.close_tab)
    

    def new_tab(self, pid:int, wid:int, name:str, proc=None):
        wintab = TabberWinWidget(pid, wid, name, proc)
        win = QtGui.QWindow.fromWinId(wid)
        self.addTab(wintab, name)


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