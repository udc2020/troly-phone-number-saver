from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtUiTools import loadUiType
import sys
import json


from db import cursor, conn


#  Import Uis 
troly_ui, _ = loadUiType('./troly.ui')
add_new_number, _ = loadUiType('./new_number.ui')


# OPEN MODEL (new number or edit number )
class NewNumber(QMainWindow, add_new_number):
    def __init__(self, number=None, name=None):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.number = number
        self.name = name

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setCursor(Qt.PointingHandCursor)

        self.pushButton_2.clicked.connect(lambda: self.close())

        self.pushButton.clicked.connect(self.add_new)

    def add_new(self):

        new_number = self.lineEdit.text()
        name = self.lineEdit_2.text()
        self.pushButton.clicked.connect(lambda: _add())

        def _add():
            cursor.execute("""
                     INSERT INTO phoneData
                     (number ,name ) VALUES (?,?)
                     """, (new_number, name))

            cursor.commit()
            self.close()

    def edit_number(self, name_):
        self.pushButton.setText("Edit")
        self.label.setText("Edit Number")
        self.lineEdit.setText(self.number)
        self.lineEdit_2.setText(self.name)

        self.pushButton.clicked.connect(lambda: _edit())

        def _edit():
            new_number = self.lineEdit.text()
            new_name = self.lineEdit_2.text()

            cursor.execute("""
                            UPDATE phoneData
                            SET 
                                number = ? ,
                                name = ?
                            WHERE name = ?
                            """, (new_number, new_name, name_))

            cursor.commit()
            self.close()


class MainApp (QMainWindow, troly_ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Create Table From Data base
        self.Create_table()

        # Add New Number
        self.new_number.clicked.connect(self.new_number_model)

        # initilaze empty List
        self.data = []

        # initlaize listWidget with Data
        self.retrive_data()

        # Timer For loop Event
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()

        self.timer.timeout.connect(self.loop)

        # To Edit & Update Number
        self.listWidget_2.itemClicked.connect(
            lambda: self.onPressed(self.listWidget_2.currentItem().text()))

        # TO Remove number & Delete him
        self.listWidget_2.itemEntered.connect(
            lambda: self.doublePressed(self.listWidget_2.currentItem().text()))

    # Create Table Sql

    def Create_table(self):

        cursor.execute("""
               CREATE TABLE IF NOT EXISTS phoneData 
               (
                  id INTEGER PRIMARY KEY ,
                  number TEXT NOT NULL  ,
                  name TEXT  
               )
               """)

    # Open Model (NewNumber)
    def new_number_model(self):
        self.newNumber = NewNumber()
        self.newNumber.show()

    # to fetch & retrive data from DB
    def retrive_data(self):
        # Clearing List Widget
        self.listWidget_2.clear()

        # if we use Sreach LineEdit
        search_str = self.lineEdit.text()

        list_number = []
        list_names = []
        all_date = cursor.execute("""
                                    SELECT number , name 
                                    FROM phoneData
                                    """)
        for data in all_date.fetchall():
            list_number.append(data[0])
            list_names.append(data[1])

        # if saerch bar is empty
        if not search_str:
            self.data = list_names
        else:
            # Look we use fliter 🔥
            filtered_list = list(filter(lambda x: search_str in x, self.data))
            self.data = filtered_list

        self.listWidget_2.addItems(self.data)

    # To get Current Name & bind him with DB
    def onPressed(self, name_=None):
        data = cursor.execute("""
                       SELECT number , name 
                       FROM phoneData
                       WHERE name= ?
                       LIMIT 1
                                """, (name_,))

        number, name = data.fetchone() or ("", "")

        self.editNumber = NewNumber(number=number, name=name)
        self.editNumber.edit_number(name_)
        self.editNumber.show()

    # Remove item from list widget & DB
    def doublePressed(self, name_=None):
        cursor.execute("""
                       DELETE FROM phoneData
                       WHERE name = ?
                       """, (name_,))
        cursor.commit()

    # use json to save & modified data
    def my_number(self):

        with open("./phonejson.json", "r+") as phonejson:
            myNumber = json.load(phonejson)
            myNumber['mynumber'] = self.lineEdit_2.text()
            self.lineEdit_2.setText(myNumber['mynumber'])

            phonejson.seek(0)
            json.dump(myNumber, phonejson, indent=4)
            phonejson.truncate()

    # Loop to update UI 
    def loop(self):
        self.retrive_data()
        self.my_number()

    # Close All Window
    def closeEvent(self, event) :
        event.accept()
        self.newNumber.close()
        self.editNumber.close()
      

# Main Function 
def main():
    troly = QApplication(sys.argv)
    win = MainApp()
    win.show()
    troly.exec()


if "__main__" == __name__:
    main()
