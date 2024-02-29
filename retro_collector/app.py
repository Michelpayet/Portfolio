import sys
from PyQt6 import uic
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QMainWindow, QApplication, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
                             QVBoxLayout, QLabel, QLineEdit, QPushButton)
from Items import Item


class SortItem(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sort Item")
        self.layout = QVBoxLayout(self)
        self.label = QLabel('Enter item type:', self)
        self.layout.addWidget(self.label)
        self.typeInput = QLineEdit(self)
        self.layout.addWidget(self.typeInput)
        self.okButton = QPushButton('OK', self)
        self.okButton.clicked.connect(self.accept)
        self.layout.addWidget(self.okButton)


class EditItem(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Item")
        self.item = item
        self.layout = QVBoxLayout(self)
        self.label_title = QLabel('Title:', self)
        self.layout.addWidget(self.label_title)
        self.title_input = QLineEdit(self.item.title, self)
        self.layout.addWidget(self.title_input)
        self.label_type = QLabel('Type:', self)
        self.layout.addWidget(self.label_type)
        self.type_input = QLineEdit(self.item.type, self)
        self.layout.addWidget(self.type_input)
        self.label_description = QLabel('Description:', self)
        self.layout.addWidget(self.label_description)
        self.description_input = QLineEdit(self.item.description, self)
        self.layout.addWidget(self.description_input)
        self.label_condition = QLabel('Condition:', self)
        self.layout.addWidget(self.label_condition)
        self.condition_input = QLineEdit(self.item.condition, self)
        self.layout.addWidget(self.condition_input)
        self.okButton = QPushButton('OK', self)
        self.okButton.clicked.connect(self.accept)
        self.layout.addWidget(self.okButton)


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.build_ui()
        self.error_message = ''
        self.show()

    def build_ui(self):
        self.ui.btn_add.clicked.connect(self.add_item)
        self.ui.btn_clear.clicked.connect(self.clear_form)
        self.ui.btn_delete.clicked.connect(self.delete_item)
        self.ui.btn_edit.clicked.connect(self.edit_item)
        self.ui.btn_sort.clicked.connect(self.sort_item)
        self.ui.tbl_items.setColumnCount(6)
        self.ui.tbl_items.setHorizontalHeaderLabels(('Title', 'Type', 'Description', 'Condition',
                                                     'DOM', 'Date Added'))
        self.ui.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_items()

    def is_valid_input(self) -> bool:
        is_valid = True
        if not self.ui.txt_title.text():
            is_valid = False
            self.error_message += "Title is missing. \n"

        if not self.ui.txt_type.text():
            is_valid = False
            self.error_message += "Type is missing.\n"

        if not self.ui.txt_description.text():
            is_valid = False
            self.error_message += "Description is missing. \n"

        if not self.ui.txt_condition.text():
            is_valid = False
            self.error_message += "Condition is missing. \n"

        return is_valid

    def add_item(self):
        if not self.is_valid_input():
            msg = QMessageBox()
            msg.setWindowTitle("Error in Entry")
            msg.setText(self.error_message)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            self.error_message = ""
            return

        title = self.ui.txt_title.text()
        type = self.ui.txt_type.text()
        description = self.ui.txt_description.text()
        condition = self.ui.txt_condition.text()
        dom = self.ui.cal_dom.date().toPyDate()
        dad = self.ui.cal_added.date().toPyDate()
        Item(title, type, description, condition, dom, dad)
        Item.save_to_file()
        self.clear_form()
        self.load_items()

    def clear_form(self):
        self.ui.txt_title.clear()
        self.ui.txt_type.clear()
        self.ui.txt_condition.clear()
        self.ui.txt_description.clear()
        self.ui.cal_dom.setDate(QDate.currentDate())
        self.ui.cal_added.setDate(QDate.currentDate())

    def delete_item(self):
        selected_row = self.ui.tbl_items.currentRow()

        if selected_row == -1:
            msg = QMessageBox()
            msg.setWindowTitle("No Item Selected")
            msg.setText("Please select an Item to delete.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        ask = QMessageBox()
        ask.setWindowTitle("Really Remove Item")
        ask.setText("Are you sure you want to delete this Item")
        ask.setIcon(QMessageBox.Icon.Question)
        ask.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        ask.activateWindow()
        ans = ask.exec()

        if ans == QMessageBox.StandardButton.No:
            return

        Item.ITEMS.pop(selected_row)
        Item.save_to_file()
        self.load_items()

    def load_items(self):
        for i in reversed(range(self.ui.tbl_items.rowCount())):
            self.ui.tbl_items.removeRow(i)

        Item.load_from_file()
        row = 0

        for s in Item.ITEMS:
            self.ui.tbl_items.insertRow(row)
            self.ui.tbl_items.setItem(row, 0, QTableWidgetItem(s.title))
            self.ui.tbl_items.setItem(row, 1, QTableWidgetItem(s.type))
            self.ui.tbl_items.setItem(row, 2, QTableWidgetItem(s.description))
            self.ui.tbl_items.setItem(row, 3, QTableWidgetItem(s.condition))
            self.ui.tbl_items.setItem(row, 4, QTableWidgetItem(s.dom.strftime("%d/%m/%Y")))
            self.ui.tbl_items.setItem(row, 5, QTableWidgetItem(s.dad.strftime("%d/%m/%Y")))
            row += 1

    def sort_item(self):
        sort_dialog = SortItem(self)
        if sort_dialog.exec() == QDialog.DialogCode.Accepted:
            desired_type = sort_dialog.typeInput.text().lower()
            if not desired_type:
                return

            Item.ITEMS = sorted(Item.ITEMS, key=lambda x: x.type.lower() == desired_type, reverse=True)

            Item.save_to_file()
            self.load_items()

    def edit_item(self):
        selected_row = self.ui.tbl_items.currentRow()

        if selected_row == -1:
            msg = QMessageBox()
            msg.setWindowTitle("No Item Selected")
            msg.setText("Please select an item to edit.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        selected_item = Item.ITEMS[selected_row]
        edit_dialog = EditItem(selected_item, self)

        if edit_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_item.title = edit_dialog.title_input.text()
            selected_item.type = edit_dialog.type_input.text()
            selected_item.description = edit_dialog.description_input.text()
            selected_item.condition = edit_dialog.condition_input.text()

            Item.save_to_file()
            self.load_items()


app = QApplication(sys.argv)
w = AppWindow()
sys.exit(app.exec())

