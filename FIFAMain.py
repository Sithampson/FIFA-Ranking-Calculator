import FIFA
import FIFAapp
from PyQt5 import QtWidgets
import sys


class Window(QtWidgets.QMainWindow, FIFAapp.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.but_pushed)

    def but_pushed(self):
        self.tableWidget.setRowCount(211)
        lisdate = FIFA.friendlywindow()
        FIFAData = FIFA.updateRankings(2019,6,14, lisdate)

        cnt = 0
        for serial in FIFAData:
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(cnt, 0, item)
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(cnt, 1, item)
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(cnt, 2, item)
            item = self.tableWidget.item(cnt, 0)
            item.setText(serial[1])
            item = self.tableWidget.item(cnt, 1)
            item.setText(serial[2])
            item = self.tableWidget.item(cnt, 2)
            item.setText(str(round(serial[3])))
            cnt += 1


app = QtWidgets.QApplication(sys.argv)
ui = Window()
ui.show()
sys.exit(app.exec_())