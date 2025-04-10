import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QLineEdit
from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QPixmap, QMouseEvent, QMovie
import pygame  # Импортируем pygame для работы с аудио

class LabStand(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_analyzer = "СИГМА-03М"  # Устанавливаем значение по умолчанию для анализатора
        self.selected_gas = "Метан"  # Устанавливаем значение по умолчанию для газа
        self.gas_fill_speed = 0  # Скорость утечки газа в м³/с
        self.gas_volume = 0  # Объем газа в м³

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
        self.gas_selector.addItems(["Сенсон-СВ-5022", "СИГМА-03М", "ЭКОЛАБ ПЛЮС"])
        self.gas_selector.hide()
        layout.addWidget(self.gas_selector)

        # Выбор газа
        self.gas_type_selector = QComboBox()
        self.gas_type_selector.addItems(["Метан", "Аммиак", "Угарный газ", "Хлор", "Сероводород"])
        self.gas_type_selector.hide()
        layout.addWidget(self.gas_type_selector)

        # Поле для ввода скорости заполнения газа
        self.gas_fill_speed_input = QLineEdit(self)
        self.gas_fill_speed_input.setPlaceholderText("Скорость заполнения (м³/с)")
        self.gas_fill_speed_input.textChanged.connect(self.update_gas_fill_speed)  # Подключаем обработчик
        layout.addWidget(self.gas_fill_speed_input)

        # Картинка газоанализатора
        self.analyzer_image_label = QLabel(self)
        self.analyzer_image_label.setGeometry(410, 160, 100, 100)  # Позиция картинки газоанализатора
        self.update_analyzer_image()

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

    def update_gas_fill_speed(self):
        # Обновление скорости заполнения газа, если введено значение
        try:
            self.gas_fill_speed = float(self.gas_fill_speed_input.text())
        except ValueError:
            self.gas_fill_speed = 0  # Если введено некорректное значение, обнуляем скорость

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
        analyzer_combobox.addItems(["Сенсон-СВ-5022", "СИГМА-03М", "ЭКОЛАБ ПЛЮС"])

        # Газ
        gas_combobox = QComboBox(msg)
        gas_combobox.addItems(["Метан", "Аммиак", "Угарный газ", "Хлор", "Сероводород"])

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
        self.update_analyzer_image()

    def update_analyzer_image(self):
        # Обновление картинки газоанализатора в зависимости от выбора
        analyzer_images = {
            "Сенсон-СВ-5022": "bin/images/senson.png",
            "СИГМА-03М": "bin/images/sigma.png",
            "ЭКОЛАБ ПЛЮС": "bin/images/ekolab.png"
        }
        analyzer_image = analyzer_images.get(self.selected_analyzer, "bin/images/default.png")
        
        # Масштабируем картинку с сохранением пропорций
        pixmap = QPixmap(analyzer_image)
        scaled_pixmap = pixmap.scaled(self.analyzer_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Устанавливаем масштабированное изображение
        self.analyzer_image_label.setPixmap(scaled_pixmap)

    def start_gas_leak(self):
        if self.is_compatible(self.selected_analyzer, self.selected_gas):
            self.gas_timer.start(1000)  # Каждую секунду увеличиваем объем газа
        else:
            print(f"Газ {self.selected_gas} не совместим с {self.selected_analyzer}. Уровень загазованности не увеличивается.")

    def stop_gas_leak(self):
        self.gas_timer.stop()

    def increase_gas(self):
        # Увеличиваем объем газа на основе скорости утечки (м³/с)
        self.gas_volume += self.gas_fill_speed
        print(f"Текущий объем газа: {self.gas_volume:.3f} м³")

        # ПДК газов в миллиграммах
        pdk_values_mg = {
            "Метан": 7000,  # ПДК в мг/м³
            "Аммиак": 20,
            "Угарный газ": 20,
            "Хлор": 1,
            "Сероводород": 10
        }

        # Плотности газов при стандартных условиях (кг/м³)
        densities = {
            "Метан": 0.717,  # плотность метана (кг/м³)
            "Аммиак": 0.73,
            "Угарный газ": 1.25,
            "Хлор": 3.2,
            "Сероводород": 1.36
        }

        # Преобразуем объем газа в массу (кг)
        gas_mass_kg = self.gas_volume * densities.get(self.selected_gas, 0)  # масса газа в кг
        gas_mg = gas_mass_kg * 1000  # Переводим массу газа в мг

        print(f"Концентрация газа: {gas_mg:.2f} мг")

        if gas_mg > pdk_values_mg.get(self.selected_gas, float('inf')):  # Если масса газа превышает ПДК
            self.trigger_alarm()


    def is_compatible(self, analyzer, gas):
        # Проверка совместимости газоанализатора и газа
        if analyzer == "Сенсон-СВ-5022" and gas != "Аммиак":
            return False
        return True

    def trigger_alarm(self):
        print("⚠️ СИГНАЛ ТРЕВОГИ! ОПАСНЫЙ УРОВЕНЬ ГАЗА! ⚠️")
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
        self.gas_volume = 0  # Сброс объема газа
        self.alarm_sound.stop()
        self.siren_label.hide()
        print("Таймер сброшен. Объем газа сброшен.")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabStand()
    window.show()
    sys.exit(app.exec())
