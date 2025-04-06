import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QPixmap, QMouseEvent, QMovie
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
        self.setGeometry(100, 100, 720, 400)  # Увеличиваем окно для двух картинок
        self.setFixedSize(600, 500)
        # Основной вертикальный layout для интерфейса
        layout = QVBoxLayout()

        # Горизонтальный layout для размещения двух картинок рядом
        image_layout = QHBoxLayout()

        # Фотография стенда
        self.image_label = QLabel(self)
        pixmap = QPixmap("bin/images/lab_stand.jpg")  # Убедитесь, что у вас есть этот файл
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Вытяжной шкаф (вторая картинка)
        self.background_label = QLabel(self)
        background_pixmap = QPixmap("bin/images/skaf.png")  # Новая фоновая картинка
        scaled_pixmap = background_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)

        # Устанавливаем масштабированное изображение
        self.background_label.setPixmap(scaled_pixmap)
        #self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.background_label.setFixedSize(300, 300)
        self.background_label.setGeometry(20, 350, 300, 300)  # 20 пикселей слева, 150 пикселей сверху
        # Добавляем изображения в горизонтальный layout
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.background_label)

        layout.addLayout(image_layout)

        # Добавление и запуск GIF
        self.siren_label = QLabel(self)
        self.siren_movie = QMovie("bin/images/siren.gif")  # Убедитесь, что у вас есть этот файл
        self.siren_label.setMovie(self.siren_movie)
        self.siren_label.setGeometry(55, 25, 60, 50)  # Расположение GIF на экране
        self.siren_label.setScaledContents(True)
        self.siren_label.hide()  # Скрываем GIF по умолчанию

        # Включение анимации GIF
        self.siren_movie.start()  # Теперь анимация будет работать

        # Определяем область для выбора анализатора и газа
        self.selection_area = QRect(90, 120, 70, 120)  # Пример координат и размеров

        # Область тревоги (будет мигать)
        self.alarm_area = QLabel(self)
        self.alarm_area.setGeometry(40, 30, 30, 30)  # Пример координат зоны
        self.alarm_area.setStyleSheet("background-color: none; border-radius: 15px;")

        # Выбор газоанализатора
        self.gas_selector = QComboBox()
        self.gas_selector.addItems(["Анализатор A", "Анализатор B", "Анализатор C"])
        self.gas_selector.hide()
        layout.addWidget(self.gas_selector)

        # Выбор газа
        self.gas_type_selector = QComboBox()
        self.gas_type_selector.addItems(["Газ 1", "Газ 2", "Газ 3"])
        self.gas_type_selector.hide()
        layout.addWidget(self.gas_type_selector)

        # Кнопка запуска
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
        if self.selection_area.contains(event.position().toPoint()):
            self.show_selection_dialog()
        # Проверка на клик по вытяжному шкафу
        if self.background_label.geometry().contains(event.position().toPoint()):
            self.reset_gas_timer()

    def show_selection_dialog(self):
        # Показать диалог для выбора анализатора и газа
        msg = QMessageBox(self)
        msg.setWindowTitle("Выбор анализатора и газа")
        msg.setText("Выберите газоанализатор и газ:")

        # Анализатор
        analyzer_combobox = QComboBox(msg)
        analyzer_combobox.addItems(["Анализатор A", "Анализатор B", "Анализатор C"])

        # Газ
        gas_combobox = QComboBox(msg)
        gas_combobox.addItems(["Газ 1", "Газ 2", "Газ 3"])

        # Добавляем выпадающие списки в диалоговое окно
        msg.layout().addWidget(analyzer_combobox)
        msg.layout().addWidget(gas_combobox)

        # Используем стандартную кнопку OK
        ok_button = msg.addButton(QMessageBox.StandardButton.Ok)
        ok_button.setText("Выбрать")  # Устанавливаем текст кнопки
        ok_button.setMinimumSize(350, 20)
        # Подключаем обработчик нажатия
        ok_button.clicked.connect(lambda: self.set_selection(analyzer_combobox, gas_combobox))

        msg.exec()

    def set_selection(self, analyzer_combobox, gas_combobox):
        analyzer = analyzer_combobox.currentText()
        gas = gas_combobox.currentText()

        # Устанавливаем выбранный анализатор и газ
        self.selected_analyzer = analyzer
        self.selected_gas = gas

        self.start_button.show()
        print(f"Выбран: {analyzer}, Газ: {gas}")

    def start_gas_leak(self):
        if self.is_compatible(self.selected_analyzer, self.selected_gas):
            self.gas_timer.start(1000)  # Каждую секунду увеличиваем уровень загазованности
        else:
            print(f"Газ {self.selected_gas} не совместим с {self.selected_analyzer}. Уровень загазованности не увеличивается.")

    def stop_gas_leak(self):
        self.gas_timer.stop()

    def increase_gas(self):
        self.gas_level += 1
        print(f"Текущий уровень загазованности: {self.gas_level}")

        if self.gas_level > 5:  # Если достигли опасного уровня
            self.trigger_alarm()

    def is_compatible(self, analyzer, gas):
        # Проверка совместимости газоанализатора и газа
        if analyzer == "Анализатор A" and gas == "Газ 3":
            return False
        elif analyzer == "Анализатор B" and gas == "Газ 2":
            return False
        return True

    def trigger_alarm(self):
        print("⚠️ СИГНАЛ ТРЕВОГИ! ОПАСНЫЙ УРОВЕНЬ ГАЗА! ⚠️")
        #self.alarm_timer.start(500)  # Запускаем мигание
        self.alarm_sound.play()  # Включаем звук сирены
        self.siren_label.show()

    def toggle_alarm_color(self):
        if self.alarm_state:
            self.alarm_area.setStyleSheet("background-color: rgba(255, 0, 0, 100); border-radius: 15px;")
        else:
            self.alarm_area.setStyleSheet("background-color: none;")
        self.alarm_state = not self.alarm_state

    def reset_gas_timer(self):
        # Сбрасываем таймер загазованности при нажатии на вытяжной шкаф
        self.gas_timer.stop()
        self.gas_level = 0
        self.alarm_sound.stop()
        self.siren_label.hide()
        print("Таймер сброшен. Загазованность сброшена.")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabStand()
    window.show()
    sys.exit(app.exec())
