import FIFA
import FIFApp
from PyQt5 import QtWidgets
import sys


class Window(QtWidgets.QMainWindow, FIFApp.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.but_pushed)
        self.actionLatest_Fixtures.triggered.connect(self.latest_fixtures)
        self.actionCurrent_FIFA_Rankings.triggered.connect(self.FIFA_Rankings)

    def latest_fixtures(self):
        FIFA.gen_latest_results()

    def FIFA_Rankings(self):
        FIFA.getCurrentRankings()

    def but_pushed(self):
        lisdate = FIFA.friendlywindow()
        if lisdate == "Calendar":
            buttonReply = QtWidgets.QMessageBox.warning(self, 'App Error', "Please download the FIFA International Window from the Download menu.")
            return

        FIFAData = FIFA.updateRankings(lisdate)

        if FIFAData == "Latest":
            buttonReply = QtWidgets.QMessageBox.warning(self, 'App Error', "Please download latest fixtures from the Download menu.")
            return
        elif FIFAData == "Ranking":
            buttonReply = QtWidgets.QMessageBox.warning(self, 'App Error', "Please download Current FIFA Rankings from the Download menu.")
            return


        self.tableWidget.setRowCount(211)
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