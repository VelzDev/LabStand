import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QPixmap, QMouseEvent, QPalette, QColor
import pygame  # Импортируем pygame для работы с аудио

class LabStand(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        # Инициализация Pygame для работы с аудио
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound("bin/images/siren.mp3")  # Убедитесь, что у вас есть этот файл в нужной папке

    def initUI(self):
        self.setWindowTitle("Цифровой двойник лабораторного стенда")
        self.setGeometry(100, 100, 360, 400)
        
        layout = QVBoxLayout()
        
        # Фотография стенда
        self.image_label = QLabel(self)
        pixmap = QPixmap("bin/images/lab_stand.jpg")  # Убедитесь, что у вас есть этот файл
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.image_label)
        
        # Определяем область, где можно кликнуть для выбора анализатора (например, ящик)
        self.analyzer_area = QRect(260, 260, 50, 50)  # Пример координат и размеров
        
        # Область тревоги (будет мигать)
        self.alarm_area = QLabel(self)
        self.alarm_area.setGeometry(40, 30, 30, 30)  # Пример координат зоны
        self.alarm_area.setStyleSheet("background-color: none; border-radius: 15px;")
        
        # Выбор газоанализатора (скрытый до клика)
        self.gas_selector = QComboBox()
        self.gas_selector.addItems(["Анализатор A", "Анализатор B", "Анализатор C"])
        self.gas_selector.hide()
        layout.addWidget(self.gas_selector)
        
        # Кнопка запуска (скрытая до выбора анализатора)
        self.start_button = QPushButton("Запустить проверку")
        self.start_button.pressed.connect(self.start_gas_leak)
        self.start_button.released.connect(self.stop_gas_leak)
        self.start_button.hide()
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)
        
        # Таймер для загазованности
        self.gas_timer = QTimer()
        self.gas_timer.timeout.connect(self.increase_gas)
        self.gas_level = 0  # Начальный уровень загазованности
        
        # Таймер для мигания
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.toggle_alarm_color)
        self.alarm_state = False

    def mousePressEvent(self, event: QMouseEvent):
        if self.analyzer_area.contains(event.position().toPoint()):
            self.show_gas_selector()
        
    def show_gas_selector(self):
        msg = QMessageBox()
        msg.setWindowTitle("Выбор анализатора")
        msg.setText("Выберите газоанализатор:")
        msg.addButton("Анализатор A", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Анализатор B", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Анализатор C", QMessageBox.ButtonRole.AcceptRole)
        msg.buttonClicked.connect(self.set_analyzer)
        msg.exec()
        
    def set_analyzer(self, button):
        self.gas_selector.setCurrentText(button.text())
        self.start_button.show()
        print(f"Выбран: {button.text()}")
        
    def start_gas_leak(self):
        self.gas_timer.start(1000)  # Каждую секунду увеличиваем уровень загазованности
        
    def stop_gas_leak(self):
        self.gas_timer.stop()
        
    def increase_gas(self):
        self.gas_level += 1
        print(f"Текущий уровень загазованности: {self.gas_level}")
        
        if self.gas_level > 5:  # Если достигли опасного уровня
            self.trigger_alarm()
        
    def trigger_alarm(self):
        print("⚠️ СИГНАЛ ТРЕВОГИ! ОПАСНЫЙ УРОВЕНЬ ГАЗА! ⚠️")
        self.alarm_timer.start(500)  # Запускаем мигание
        self.alarm_sound.play()  # Включаем звук сирены
        
    def toggle_alarm_color(self):
        if self.alarm_state:
            self.alarm_area.setStyleSheet("background-color: rgba(255, 0, 0, 100); border-radius: 15px;")
        else:
            self.alarm_area.setStyleSheet("background-color: none;")
        self.alarm_state = not self.alarm_state
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabStand()
    window.show()
    sys.exit(app.exec())