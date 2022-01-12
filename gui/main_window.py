from PyQt5 import QtWidgets, QtGui


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.fontsize = 24

        # Set title
        self.setWindowTitle("Contact Angle System GUI")

        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())

        # Create new label
        self.my_label_entrybox = QtWidgets.QLabel('Hello World. A Longer Sentence')

        # Change font size
        self.my_label_entrybox.setFont(QtGui.QFont('Helvetica', self.fontsize))

        self.layout().addWidget(self.my_label_entrybox)

        # Create an entry box
        self.my_entry = QtWidgets.QLineEdit()
        self.my_entry.setObjectName('name_field:')
        self.my_entry.setText('')
        self.layout().addWidget(self.my_entry)

        # Create a button
        self.my_button_entrybox = QtWidgets.QPushButton('Press Me!', self)
        self.my_button_entrybox.clicked.connect(self.press_button)
        self.layout().addWidget(self.my_button_entrybox)

        # Create combo box label
        self.my_label_combobox = QtWidgets.QLabel('Pick something from the list')

        # Change fontsize
        self.my_label_combobox.setFont(QtGui.QFont('Helvetica', self.fontsize))

        self.layout().addWidget(self.my_label_combobox)

        # Create a combo box
        # to make it editable pass editable=True, and insertPolicy
        self.my_combo_box = QtWidgets.QComboBox(self)
        self.my_combo_box.setEditable(True)
        self.my_combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertAtBottom)
        # Add items to combo box
        self.my_combo_box.addItem('Entry 1', 'Here can be anything')
        self.my_combo_box.addItem('Entry 2', 1)
        self.my_combo_box.addItem('Entry 3', QtWidgets.QWidget)
        self.my_combo_box.addItem('Entry 4', "Anything goes")
        self.my_combo_box.addItem('Entry 5')
        self.my_combo_box.addItem('call this with .currentText', 'and this with .data')
        self.my_combo_box.addItem('or call the index number with .index')
        # or add multiple at once
        self.my_combo_box.addItems(['One', 'Two', 'Three'])
        self.my_combo_box.insertItem(2, "Third thing")  # index, text
        self.my_combo_box.insertItems(2, ["1", '2', '3'])  # index, list

        # Add combobox to layout
        self.layout().addWidget(self.my_combo_box)

        # create a button for the combo box
        self.my_button_combobox = QtWidgets.QPushButton('Press me for the combobox', self)
        self.my_button_combobox.clicked.connect(self.select_item)
        self.layout().addWidget(self.my_button_combobox)

        # Show the app
        self.show()

    def press_button(self):
        # Add name to label
        self.my_label_entrybox.setText(f'Hello {self.my_entry.text()}!')
        # Clear the entry box
        self.my_entry.setText("")
        return

    def select_item(self):
        # Add label
        self.my_label_combobox.setText(f'You picked {self.my_combo_box.currentText()}, '
                                       f'containing the data: {self.my_combo_box.currentData()},'
                                       f'which has the index: {self.my_combo_box.currentIndex()}')
