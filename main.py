import sqlite3
import time

import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()
        #начальные поля
        self.record_flag = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)


        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.setWindowTitle('Мониторинг загрузки')
        self.resize(450, 300)

        self.label = QLabel('Уровень загруженности:')

        self.cpu_label = QLabel('CPU:')
        self.RAM_label = QLabel('RAM:')
        self.Disk_memory_label = QLabel('Disk:')

        self.btn = QPushButton('Начать запись')
        self.btn.clicked.connect(self.record)

        self.conn = sqlite3.connect('system_resources.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu REAL,
                    ram_free REAL,
                    ram_total REAL,
                    disk_free REAL,
                    disk_total REAL
                )
                ''')



        self.get_info()

    def get_info(self):

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.RAM_label)
        self.layout.addWidget(self.Disk_memory_label)

        self.button_layout.addWidget(self.btn)
        self.layout.addLayout(self.button_layout)


        self.setLayout(self.layout)


    def record(self):
        self.label.setText("Запись началась!")
        self.record_flag = True
        self.button_layout.removeWidget(self.btn)
        self.btn.deleteLater()
        self.btn_stop = QPushButton('Остановить')
        self.btn_stop.clicked.connect(self.save_and_stop_recording)
        self.timer_label = QLabel('Время записи: 00:00:00')

        self.button_layout.addWidget(self.btn_stop)
        self.layout.addWidget(self.timer_label)

        self.recording_start_time = time.time()
        self.timer.timeout.connect(self.update_timer)

    def update(self):
        ram = psutil.virtual_memory()
        ram_free = ram.available / (1024 ** 3)
        ram_total = ram.total / (1024 ** 3)

        disk = psutil.disk_usage('/')
        disk_free = disk.free / (1024 ** 3)
        disk_total = disk.total / (1024 ** 3)
        cpu = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.RAM_label.setText(f"Ram: {ram_free} / {ram_total}")
        self.Disk_memory_label.setText(f"Disk memory (system disk): {disk_free} / {disk_total}")

        if self.record_flag == True:
            self.cursor.execute('''
            INSERT INTO monitoring_resources(cpu,ram_free,ram_total,disk_free,disk_total)
            values (?, ?, ?, ?, ?)    
            ''',(cpu, ram_free, ram_total, disk_free, disk_total))
            self.conn.commit()


    def save_and_stop_recording(self):
        self.label.setText("Запись остановлена!")
        self.timer.timeout.disconnect(self.update_timer)


        self.button_layout.removeWidget(self.btn_stop)
        self.btn_stop.deleteLater()
        self.button_layout.removeWidget(self.timer_label)
        self.timer_label.deleteLater()

        self.btn = QPushButton('Начать запись')
        self.btn.clicked.connect(self.record)
        self.button_layout.addWidget(self.btn)

        self.record_flag = False
        self.recording_start_time = None


    def update_timer(self):
        if self.recording_start_time:
            elapsed_time = int(time.time() - self.recording_start_time)
            self.timer_label.setText(f"Время записи: 00:{elapsed_time//60:02}:{elapsed_time%60:02}")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
