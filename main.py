import random
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QMainWindow, \
    QTableWidgetItem, QTableWidget, QTextEdit, QStackedWidget
from PyQt5.QtMultimedia import QSound
import sys
from PyQt5 import uic
import sqlite3

# просто набор цветов
COLORS = ['#ffd700', 'green', 'yellow', 'orange', 'blue', 'violet', 'brown', 'red', 'coral', 'Magenta', '0f93ff']

# библиотечка с координатами (очень нужная!!!!!!)
COORDS = {
    1: 'А',
    2: 'Б',
    3: 'В',
    4: 'Г',
    5: 'Д',
    6: 'Е',
    7: 'Ж',
    8: 'З',
    9: 'И',
    10: 'К'
}

MAKE_MOVE = 0
MOVE = (1, 2)
WHERE = 'Up'

NOTES = {
    'warning': QSound("sounds/warning.wav"),
    'background': QSound("background.wav"),
    'hit': QSound("sounds_hit.wav"),
    'miss': QSound("sounds_miss.wav"),
    'main': QSound("main_sound.wav"),
    'win': QSound("sounds/win.wav")
}


class Ships:
    def __init__(self):
        self.field = [[0 for i in range(10)] for j in range(10)]
        self.letters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")
        self.ships_rules = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        self.shipy = []
        self.ships_rules.reverse()

    def __eq__(self, other):
        self.field = other

    def check_up(self, x, y, w, h):
        width = w
        height = h
        if x + height - 1 >= 10 or \
                y + width - 1 >= 10:
            return False
        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= 10 or p_y < 0 or p_y >= 10:
                    continue
                if self.field[p_x][p_y] != 0:
                    return False
        return True

    def put_boats(self):
        for i in self.ships_rules:
            x, y = random.choice([i for i in range(9)]), random.choice([i for i in range(9)])
            while not self.check_up(x, y, i, 1) and not self.check_up(x, y, 1, i):
                x, y = random.choice([i for i in range(9)]), random.choice([i for i in range(9)])
            if self.check_up(x, y, i, 1):
                for _ in range(i):
                    self.field[x][y + _] = 1
                    self.shipy.append([x, y, i, 1])
            else:
                for _ in range(i):
                    self.field[x + _][y] = 1
                    self.shipy.append([x, y, 1, i])
        return self.field

    def mark_destroyed_ship(self, ship):
        y, x = ship[0], ship[1]
        width, height = ship[2], ship[3]
        summa = 0
        for p_x in range(x, x + width):
            for p_y in range(y, y + height):
                summa += self.field[p_y][p_x] == 2
        print(summa, width + height - 1)
        if summa == width + height - 1:
            for p_x in range(x - 1, width + x + 1):
                for p_y in range(y - 1, y + height + 1):
                    if p_x < 0 or p_x >= 10 or p_y < 0 or p_y >= 10:
                        continue
                    self.field[p_y][p_x] = -1
            for p_x in range(x, x + width):
                for p_y in range(y, y + height):
                    self.field[p_y][p_x] = 2
        else:
            return 0
        return self.field


USER = Ships()
COMPUTER = Ships()
COMPUTER_SHIPS = 0
USER_SHIPS = 0


def set_start_pos_ships():
    global USER, USER_SHIPS, COMUTER_SHIPS, COMPUTER
    COMPUTER = Ships()
    COMUTER_SHIPS = COMPUTER.put_boats()
    USER = Ships()
    USER_SHIPS = USER.field


def correct_coords(x, y):
    if 1000 < x < 1600 and 300 < y < 900:
        return True
    return False


# считаем координаты по формулке
def calculate_coords(x, y):
    if correct_coords(x, y):
        x = (x - 1000) // 60 + 1
        y = (y - 300) // 60 + 1
        return COORDS[y] + str(x)
    else:
        return 'NONE'


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.query = 'SELECT * FROM game'
        self.gamy = False
        self.count_game = 1
        set_start_pos_ships()
        self.connection = sqlite3.connect('new_base1.2.sqlite')
        self.cur = self.connection.cursor()
        uic.loadUi('UI2.ui', self)
        self.initUI()
        self.sound('background')

    def initUI(self):
        # self.pushButton = QPushButton(self)
        #self.pushButton.clicked.connect(self.select_data)
        # По умолчанию будем выводить все данные из таблицы films
        #self.textEdit = QTextEdit(self)
        self.setGeometry(0, 0, 2400, 1400)
        self.setWindowTitle('Координаты')
        # При нажатии на любую клетку противника появится здесь ее координата
        #self.coords = QLabel(self)
        self.coords.setText("Координаты: None, None")
        self.coords.move(30, 30)
        # расставляем циферки
        self.new_coords = QLabel(self)
        self.new_coords.setText(' 1    2    3    4    5    6    7    8   9   10')
        self.new_coords.setGeometry(300, 250, 900, 30)
        self.new_coords1 = QLabel(self)
        self.new_coords1.setText(' 1    2    3    4    5    6    7    8   9   10')
        self.new_coords1.setGeometry(1000, 250, 650, 30)
        # расставляем буковки
        c = 1
        for j in range(300, 900, 60):
            self.new_coordsy = QLabel(self)
            self.new_coordsy.setText(COORDS[c])
            self.new_coordsy.setGeometry(950 - 5, j + 5, 30, 30)
            c += 1
        self.setStyleSheet(f"background-color: #87cefa")
        #self.button_OK = QPushButton('Переставить корабли', self)
        self.button_OK.setText('Поставить корабли')
        self.button_OK.move(300, 1000)
        self.button_OK.setStyleSheet("background-color: {}".format(COLORS[0]))
        self.button_OK.clicked.connect(self.reset_ship_pos)
       # self.button_start = QPushButton('Start Game', self)
        self.button_start.move(600, 1000)
        self.button_start.setStyleSheet("background-color: {}".format(COLORS[0]))
        self.button_start.clicked.connect(self.game)
        #self.btn_new_game = QPushButton('New Game', self)
        self.btn_new_game.setStyleSheet("background-color: {}".format(COLORS[0]))
        self.btn_new_game.clicked.connect(self.start_new_game)
        self.btn_new_game.move(900, 1000)
        self.select_data()

    def sound(self, filename):
        NOTES[filename].play()

    def not_sound(self):
        NOTES['background'].stop()

    def select_data(self):
        # Получим результат запроса,
        # который ввели в текстовое поле
        res = self.cur.execute(self.query).fetchall()
        # print(res)
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        self.connection.close()

    def reset_ship_pos(self):
        global USER_SHIPS, USER
        if self.gamy:
            return
        USER = Ships()
        USER.put_boats()
        USER_SHIPS = USER.field
        self.update()

    def start_new_game(self):
        global USER, COMPUTER
        self.gamy = False
        self.sound('main')
        self.sound('background')
        print('PKY')
        b = 0
        print(USER.field)
        for i in USER.field:
            b += i.count(2)
        print(b)
        c = 0
        for i in COMPUTER.field:
            c += i.count(2)
        print(c)
        a = f'INSERT INTO game(id, play1, play2) VALUES({self.count_game}, {b}, {c})'
        print(self.count_game)
        self.count_game += 1
        print(self.count_game)
        self.cur.execute(a)
        print(self.cur.execute('SELECT * FROM game').fetchall())
        print('docky')
        self.select_data()
        set_start_pos_ships()
        self.update()

    def mousePressEvent(self, event):
        global COMUTER_SHIPS, COMPUTER
        self.x = event.x()
        self.y = event.y()
        # здесь мы пишем куда нажимали
        s = calculate_coords(event.x(), event.y())
        self.coords.setText(f"Координаты: {s}")
        if self.gamy:
            if s != 'NONE':
                x = (self.x - 1000) // 60
                y = (self.y - 300) // 60
                print('ыстрел пользователя', x, y)
                if COMUTER_SHIPS[y][x] == 0:
                    self.sound('miss')
                    self.sound('background')
                    COMUTER_SHIPS[y][x] = -1
                    print("Мимо")
                    a = self.make_move()
                    while a:
                        if a == -1:
                            self.not_sound()
                            self.sound('main')
                            self.sound('background')
                            self.start_new_game()
                            break
                        if a == -2:
                            self.not_sound()
                            self.sound('main')
                            self.sound('background')
                            self.start_new_game()
                            break
                        self.sound('hit')
                        self.update()
                        a = self.make_move()
                elif COMUTER_SHIPS[y][x] == 1:
                    COMUTER_SHIPS[y][x] = 2
                    self.sound('hit')
                    for i in COMPUTER.shipy:
                        if (i[0] <= y <= i[0] + i[3] and i[1] <= x <= i[1] + i[2]) or i[0: 2] == [y, x]:
                            if COMPUTER.mark_destroyed_ship(i):
                                COMPUTER.mark_destroyed_ship(i)
                                COMUTER_SHIPS = COMPUTER.field
                else:
                    pass

            else:
                pass
            self.update()

    def mouseMoveEvent(self, event):
        self.setMouseTracking(True)
        self.x = event.x()
        self.y = event.y()
        # здесь мы пишем куда нажимали
        s = calculate_coords(event.x(), event.y())
        self.coords.setText(f"Координаты: {s}")

    # обработка рисовалки поля

    def paintEvent(self, event):
        print('paint')
        qp = QPainter()
        qp.begin(self)
        self.draw_field(qp)
        qp.end()

    def make_move(self):
        global USER_SHIPS, MAKE_MOVE, MOVE, WHERE, USER, COMPUTER
        s = 0
        for i in COMPUTER.field:
            s += i.count(1)
        e = 0
        for i in USER.field:
            e += i.count(1)
        if s == 0:
            return -1
        if e == 0:
            return -2
        if MAKE_MOVE == 0:
            x = random.choice([i for i in range(10)])
            y = random.choice([i for i in range(10)])
            while USER_SHIPS[y][x] != 0 and USER_SHIPS[y][x] != 1:
                x = random.choice([i for i in range(10)])
                y = random.choice([i for i in range(10)])
            if USER_SHIPS[y][x] == 0:
                USER_SHIPS[y][x] = -1
                return 0
            else:
                USER_SHIPS[y][x] = 2
                MOVE = (y, x)
                MAKE_MOVE = 1
                return 1
        else:
            Kil = False
            x = MOVE[1]
            y = MOVE[0]
            if x >= 10:
                x -= 1
            elif x < 0:
                x += 1
            elif y >= 10:
                y -= 1
            elif y < 0:
                y += 1
            self.chsck_Kill(x, y)
            if WHERE == 'Up':
                if USER_SHIPS[y - 1][x] == 1 or USER_SHIPS[y - 1][x] == 2:
                    while USER_SHIPS[y - 1][x] == 1 or USER_SHIPS[y - 1][x] == 2:
                        y -= 1
                        USER_SHIPS[y][x] = 2
                        for i in USER.shipy:
                            if (i[0] <= y <= i[0] + i[3] and i[1] <= x <= i[1] + i[2]) or i[0: 2] == [y, x]:
                                if USER.mark_destroyed_ship(i):
                                    USER.mark_destroyed_ship(i)
                                    USER_SHIPS = USER.field
                                    Kil = True
                                    break
                        if Kil:
                            break
                    if Kil:
                        MAKE_MOVE = 0
                        return 1
                    else:
                        MOVE = (y + 1, x)
                        WHERE = 'Down'
                        return 0
                else:
                    MOVE = (y, x)
                    WHERE = 'West'
                    USER_SHIPS[y - 1][x] = -1
            elif WHERE == 'Down':
                if USER_SHIPS[y + 1][x] == 1 or USER_SHIPS[y + 1][x] == 2:
                    while USER_SHIPS[y + 1][x] == 1 or USER_SHIPS[y + 1][x] == 2:
                        y += 1
                        USER_SHIPS[y][x] = 2
                        for i in USER.shipy:
                            if (i[0] <= y <= i[0] + i[3] and i[1] <= x <= i[1] + i[2]) or i[0: 2] == [y, x]:
                                if USER.mark_destroyed_ship(i):
                                    USER.mark_destroyed_ship(i)
                                    USER_SHIPS = USER.field
                                    Kil = True
                                    break
                        if Kil:
                            break
                    if Kil:
                        MAKE_MOVE = 0
                        return 1
                    else:
                        MOVE = (y - 1, x)
                        WHERE = 'Up'
                        return 0
                else:
                    USER_SHIPS[y + 1][x] = -1
                    MOVE = (y, x)
                    WHERE = 'East'
            elif WHERE == 'West':
                if USER_SHIPS[y][x - 1] == 1 or USER_SHIPS[y][x - 1] == 2:
                    while USER_SHIPS[y][x - 1] == 1 or USER_SHIPS[y][x - 1] == 2:
                        x -= 1
                        USER_SHIPS[y][x] = 2
                        for i in USER.shipy:
                            if (i[0] <= y <= i[0] + i[3] and i[1] <= x <= i[1] + i[2]) or i[0: 2] == [y, x]:
                                if USER.mark_destroyed_ship(i):
                                    USER.mark_destroyed_ship(i)
                                    USER_SHIPS = USER.field
                                    Kil = True
                                    break
                        if Kil:
                            break
                    if Kil:
                        MAKE_MOVE = 0
                        return 1
                    else:
                        MOVE = (y, x + 1)
                        WHERE = 'East'
                        return 0
                else:
                    MOVE = (y, x)
                    WHERE = 'Down'
                    USER_SHIPS[y][x - 1] = -1
            elif WHERE == 'East':
                if USER_SHIPS[y][x + 1] == 1 or USER_SHIPS[y][x + 1] == 2:
                    while USER_SHIPS[y][x + 1] == 1 or USER_SHIPS[y][x + 1] == 2:
                        x += 1
                        USER_SHIPS[y][x] = 2
                        for i in USER.shipy:
                            if (i[0] <= y <= i[0] + i[3] and i[1] <= x <= i[1] + i[2]) or i[0: 2] == [y, x]:
                                if USER.mark_destroyed_ship(i):
                                    USER.mark_destroyed_ship(i)
                                    USER_SHIPS = USER.field
                                    Kil = True
                                    break
                        if Kil:
                            break
                    if Kil:
                        MAKE_MOVE = 0
                        return 1
                    else:
                        MOVE = (y, x - 1)
                        WHERE = 'West'
                        return 0
                else:
                    WHERE = 'Up'
                    USER_SHIPS[y][x + 1] = -1
                    MOVE = (y, x)
            self.chsck_Kill(y, x)
            return 0

    def chsck_Kill(self, x, y):
        global USER_SHIPS, USER, MAKE_MOVE
        for i in USER.shipy:
            if (i[0] <= x <= i[0] + i[3] and i[1] <= y <= i[1] + i[2]) or i[0: 2] == [y, x]:
                if USER.mark_destroyed_ship(i):
                    USER.mark_destroyed_ship(i)
                    USER_SHIPS = USER.field
                    MAKE_MOVE = 0
                    return 1
        return 0

    # рисовалка поля
    def draw_field(self, qp):
        for i in range(300, 900, 60):
            for j in range(300, 900, 60):
                if USER_SHIPS[(j - 300) // 60][(i - 300) // 60] == 1:
                    qp.setBrush(QColor('coral'))
                    qp.drawRect(i, j, 60, 60)
                elif USER_SHIPS[(j - 300) // 60][(i - 300) // 60] == 2:
                    qp.setBrush(QColor(COLORS[7]))
                    qp.drawRect(i, j, 60, 60)
                elif USER_SHIPS[(j - 300) // 60][(i - 300) // 60] == -1:
                    qp.setBrush(QColor('#cfcfcf'))
                    qp.drawRect(i, j, 60, 60)
                else:
                    qp.setBrush(QColor('#f7f7f7'))
                    qp.drawRect(i, j, 60, 60)

        for i in range(1000, 1600, 60):
            for j in range(300, 900, 60):
                if COMUTER_SHIPS[(j - 300) // 60][(i - 1000) // 60] == 2:
                    qp.setBrush(QColor(COLORS[7]))
                    qp.drawRect(i, j, 60, 60)
                elif COMUTER_SHIPS[(j - 300) // 60][(i - 1000) // 60] == -1:
                    qp.setBrush(QColor('#cfcfcf'))
                    qp.drawRect(i, j, 60, 60)
                else:
                    qp.setBrush(QColor('#f7f7f7'))
                    qp.drawRect(i, j, 60, 60)

    def game(self):
        global USER_SHIPS
        if sum(sum(i) for i in USER_SHIPS) != 0:
            self.not_sound()
            self.sound('main')
            self.sound('background')
            self.gamy = True
        return 0


class StartMenuMain(QMainWindow):
    """Стартовое меню, где можно переключаться между окнами, а также выйти из игры"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 2400, 1400)
        self.setWindowTitle('')
        self.setStyleSheet("background-color: ##87cefa;")
        self.load_mp3("background")  # Загружаю звук
        self.startButton = QPushButton('Start Game', self)
        self.startButton.setStyleSheet("background-color: {}".format(COLORS[0]))
        self.startButton.move(300, 1000)
        self.startButton.resize(200, 50)
        self.setStyleSheet(f"background-color: #87cefa;")
        self.startButton.clicked.connect(self.to_start)

    def load_mp3(self, filename):  # Загрузка WAV-файла
        NOTES[filename].play()

    def to_start(self):  # Переходит в меню начала игры
        self.load_mp3("main")
        self.load_mp3("background")
        print(1)
        windows.setCurrentIndex(1)


if __name__ == '__main__':  # Дописать
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 13pt;}")
    settings_window = Example()
    startmenu_window = StartMenuMain()

    windows = QStackedWidget()
    windows.addWidget(startmenu_window)  # 1
    windows.addWidget(settings_window)
    windows.show()
    sys.exit(app.exec())
    # 2


#if __name__ == '__main__':
    #app.setStyleSheet("QLabel{font-size: 13pt;}")
    #window = Example()
    #window.show()
    #sys.exit(app.exec())
