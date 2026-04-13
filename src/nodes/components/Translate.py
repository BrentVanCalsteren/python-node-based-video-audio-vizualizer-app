from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QLineEdit, QPushButton, QApplication

from nodes.components.Component import Component

class Translate(Component):
    decrease_button = None
    increase_button = None
    textbox = None
    x_value = 0
    y_value = 0

    def __init__(self, node):

        self.node = node
        # Timer voor lang indrukken
        # self.timer = QTimer()
        #self.timer.timeout.connect(self.adjust_value)
        #self.increment = 0
        self.generate_widgets()

        super().__init__("Translate")
        self.init_ValsWidgts()

    def init_ValsWidgts(self):
        self.textbox.setText(str(self.x_value))
        self.increase_button.clicked.connect(self.plus_botton)


    def generate_widgets(self):

        self.textbox = QLineEdit()
        self.textbox.setMinimumSize(80, 20)
        self.textbox.setMaximumSize(80, 20)

        self.increase_button = QPushButton("+")
        self.increase_button.setMinimumSize(20, 20)
        self.increase_button.setMaximumSize(20, 20)

        self.decrease_button = QPushButton("-")
        self.decrease_button.setMinimumSize(20,20)
        self.decrease_button.setMaximumSize(20,20)

        #self.increase_button.pressed.connect(self.start_increasing)
        #self.increase_button.released.connect(self.stop_timer)


        # add widget
        self.widgets = [self.decrease_button, self.increase_button, self.textbox]


    def mousePressEvent(self, event):
        # Controleer of de klik niet binnen het tekstvak is
        if not self.textbox.geometry().contains(event.position().toPoint()):
            self.textbox.clearFocus()
            self.update_value_from_textbox()
            # Verwijder de focus van het tekstvak
        super().mousePressEvent(event)


    def plus_botton(self):
        # Controleer of de Shift-toets is ingedrukt
        self.update_value_from_textbox()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            self.x_value += 0.01  # 1/10 van de stapgrootte
        else:
            self.x_value += 0.1  # Normale stapgrootte

        # Werk de tekst bij
        self.textbox.setText(str(round(self.x_value,5)))

    def update_value_from_textbox(self):
        try:
            # Probeer de waarde in te stellen vanuit het tekstvak
            self.x_value = float(self.textbox.text())
        except Exception:
            self.textbox.setText(str(self.x_value))  # Herstel oude waarde bij ongeldige invoer