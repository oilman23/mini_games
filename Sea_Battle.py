from copy import deepcopy
from itertools import product
from random import randint, choice
from uuid import uuid4


class ShipError(Exception):
    pass


class Ship:
    """
    _х, _y - координаты начала расположения корабля;
    _length - длина корабля (число палуб: целое значение: 1, 2, 3 или 4);
    _tp - ориентация корабля (1 - горизонтальная; 2 - вертикальная).
    _cells - статус палуб корабля (1 - палуба цела; 2 - палуба подбита).
    """
    def __init__(self, length, tp=1, x=None, y=None):
        self._id = uuid4()
        self._x = x
        self._y = y
        self._length = length
        self._tp = tp
        self._is_move = True
        self._is_alive = True
        self._cells = [1 for _ in range(length)]
        self._ship_decks = None
        self._area = set()
        self.set_start_coord(x, y)

    def set_start_coord(self, x, y):
        """Установка начальных координат, подсчет координат всех палуб
        и координат, в которых не может быть другого корабля"""
        if x is not None and y is not None:
            self._x = x
            self._y = y
            self.__calculate_ship_decks()
            self.__calculate_area()

    def __calculate_ship_decks(self):
        if self._tp == 1:
            self._ship_decks = list(
                map(lambda x: (x, self._y),
                    range(self._x, self._x + self._length))
            )
        else:
            self._ship_decks = list(
                map(lambda y: (self._x, y),
                    range(self._y, self._y + self._length))
            )

    def __calculate_area(self):
        area = set()
        for x, y in self._ship_decks:
            for dx, dy in product((-1, 0, 1), repeat=2):
                if (x + dx, y + dy) not in self._ship_decks:
                    area.add((x + dx, y + dy))
        self._area = area

    def get_start_coord(self):
        return self._x, self._y

    @property
    def cells(self):
        return self._cells

    @property
    def area(self):
        return self._area

    @property
    def ship_decks(self):
        return self._ship_decks

    def is_out_pole(self, size=10):
        if any([x not in range(size)
                or y not in range(size) for x, y in self._ship_decks]):
            return True
        return False

    def is_collide(self, ship):
        if self.ship_decks is None or ship.ship_decks is None:
            return False
        if self == ship:
            return False
        ship1 = ship.ship_decks + list(ship.area)
        ship2 = self.ship_decks
        return any(coord in ship1 for coord in ship2)

    def move(self, go):
        """Перемещение корабля в направлении его ориентации
         только если флаг _is_move = True
         (go = 1 - движение вниз / вправо на 1 клетку;
         go = -1 - движение вверх / влево на 1 клетку);
        """
        x, y = self._x, self._y
        if self._is_move:
            if self._tp == 1:
                x += go
            else:
                y += go
        self.set_start_coord(x, y)

    @property
    def is_alive(self):
        return any(x != 2 for x in self._cells)

    def __getitem__(self, item):
        self._check_key(item)
        return self._cells[item]

    def __setitem__(self, key, value):
        self._check_key(key)
        if value not in (1, 2):
            raise ValueError("Значение клетки должно быть 1 или 2")
        self._cells[key] = value

    def _check_key(self, key):
        if type(key) != int or key not in range(self._length):
            raise IndexError("Индекс должен быть целым числом в диапазоне "
                             "длины корабля")

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return hash(self) == hash(other)


class ShipDefender:
    """Класс Context Manager для безошибочного перемещения кораблей.
    Не изменяет параметры корабля, если в процессе изменения возникла ошибка"""

    def __init__(self, ship):
        self._ship = ship

    def __enter__(self):
        self._temp_ship = deepcopy(self._ship)
        return self._temp_ship

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._ship.__dict__ = self._temp_ship.__dict__
        return True


class GamePole:
    """
    _size - размер игрового поля _size x _size;
    _ships - корабли, находящиеся на поле (объекты класса Ship);
    __assort_ships - номенклатура кораблей (число кораблей заданной длинны)
    """
    COMMON_ASSORT = ((1, 4), (2, 3), (3, 2), (4, 1))

    def __init__(self, size, assort_ships=None):
        self._size = size
        self._ships = []
        self.__assort_ships = (self.COMMON_ASSORT if assort_ships is None
                               else assort_ships)

    def init(self):
        self.__create_ships()
        self.__placement_ships()

    def __create_ships(self):
        for amount, length in self.__assort_ships:
            self._ships.extend(
                [Ship(length, tp=randint(1, 2)) for _ in range(amount)])

    def __placement_ships(self):
        """Расстановка кораблей на поле, с учетом ограничений
        если за 100 попыток поставить корабль не удалось,
        сбрасываем расставленные корабли и начинаем заново"""
        try:
            placed_ships = 0
            bad_combination = False
            total_ships = len(self._ships)
            while placed_ships < total_ships and not bad_combination:
                for ship in self._ships:
                    not_placed = True
                    attempts = 0
                    while not_placed:
                        attempts += 1
                        with ShipDefender(
                                ship) as s:
                            x, y = (randint(0, self._size - 1) for _ in 'xy')
                            s.set_start_coord(x, y)
                            self.__check_ship_position(s)
                            not_placed = False
                            placed_ships += 1
                        if attempts > 100:
                            bad_combination = True
                            break
                    if bad_combination:
                        break
            if bad_combination:
                self._ships = []
                self.init()
        except RecursionError:
            print("Не удалось расставить корабли. "
                  "Измените размер поля или количество кораблей")

    def __check_ship_position(self, ship):
        if ship.is_out_pole(self._size):
            raise ShipError('корабль за пределами поля')
        if self.__check_collide(ship):
            raise ShipError('корабли соприкасаются')

    def __check_collide(self, ship):
        for other_ship in self._ships:
            if ship.is_collide(other_ship):
                return True
        return False

    @property
    def ships(self):
        return self._ships

    def move_ships(self):
        """Перемещаем все корабли, которые могут перемещаться (is_move=True),
        на 1 ячейку"""
        for ship in self._ships:
            step = choice((-1, 1))
            not_moved = True
            tries = 0
            while not_moved and tries < 2:
                with ShipDefender(ship) as s:
                    s.move(step)
                    self.__check_ship_position(s)
                    not_moved = False
                step = -step
                tries += 1

    def check_hit(self, coord):
        for ship in self._ships:
            if coord in ship.ship_decks:
                ship._is_move = False
                idx = ship.ship_decks.index(coord)
                ship._cells[idx] = 2
                if ship.is_alive:
                    return 1, ship
                else:
                    return 2, ship
        return 0, None

    def get_text_pole(self, player_step=None, hidden=False):
        """Представление поля в символьном виде.
        Возвращаем либо поле со всеми кораблями, либо только с подбитыми"""
        if hidden:
            pole = [['▓' if x == 2 else '░' for x in row] for row in
                    self.get_pole()]
        else:
            pole = [['░' if x == 0 else '▒' if x == 1 else '▓' for x in row]
                    for row in self.get_pole()]
        for x, y in player_step:
            if pole[y][x] == '░':
                pole[y][x] = "."
        return pole

    def get_pole(self):
        """Представление поля в числовом виде"""
        pole = [[0 for _ in range(self._size)] for _ in range(self._size)]
        for ship in self._ships:
            for coord, deck in zip(ship.ship_decks, ship.cells):
                col, row = coord
                pole[row][col] = deck
        return tuple(map(tuple, pole))

    def show(self):
        [print(*line) for line in self.get_pole()]


class SeaBattle:
    """
    _size - размер игрового поля _size x _size;
    _hidden - флаг, определяющий будут ли скрыты корабли PC на игровом поле;
    _game_over - флаг окончания игры;
    _human_steps, _pc_steps - поля для записи ходов, в которых уже не может
    быть кораблся противника;
    _human_turn - флаг для обозначения чей сейчас ход;
    _last_step, _first_step, _diff, _next_step - поля для логики PC;
    """
    def __init__(self, size=10, hidden=True, assort=None):
        self._size = size
        self.__game_over = False
        self._hidden = hidden
        self._human, self._pc = (GamePole(size, assort) for _ in "12")
        self._human.init(), self._pc.init()
        self._human_steps = set()
        self._pc_steps = set()
        self._human_turn = True
        self._last_step = None
        self._first_step = None
        self._diff = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        self._next_step = None

    def next_move(self):
        if self._human_turn:
            self.human_hit()
        else:
            self.pc_hit()

    def human_hit(self):
        coord = None
        while not coord:
            coord = self.__input_coord()
        self.__hit(coord)
        if not self.__is_any_alive(self._pc):
            self.__game_over = True
            print('_' * 50)
            print("\033[3;32m Поздравляем, вы победили!!! \033[0m")

    def __input_coord(self):
        try:
            print('_' * 50)
            x, y = map(int, input("Введите координаты (x, y) для выстрела "
                                  "через пробел: ").split())
            if x not in range(self._size) or y not in range(self._size):
                raise IndexError("Координата выходит за пределы поля")
            if (x, y) in self._human_steps:
                raise IndexError("В этой клетке уже не может быть корабля")
            return x, y
        except IndexError as e:
            print(e)
        except ValueError:
            print("Введите 2 числа через пробел в формате: '9 9'")

    def pc_hit(self):
        coord = self._next_step
        while not coord:
            x, y = (randint(0, self._size - 1) for _ in "xy")
            if (x, y) not in self._pc_steps:
                coord = x, y
        hit = self.__hit(coord)
        self.__pc_logic(hit, coord)

        if not self.__is_any_alive(self._human):
            self.__game_over = True
            print('_' * 50)
            print("\033[3;35m Сожалеем, победил компьютер. \033[0m")

    def __hit(self, coord):
        print('_' * 50)
        hit_text = {0: 'Промахнулся', 1: 'Ранил', 2: 'Убил'}
        hit_pole = self._pc if self._human_turn else self._human
        steps = self._human_steps if self._human_turn else self._pc_steps
        hit_result, ship = hit_pole.check_hit(coord)
        if hit_result != 0:
            steps.add(coord)
            if hit_result == 2:
                for x, y in ship.area:
                    if 0 <= x < self._size and 0 <= y < self._size:
                        steps.add((x, y))
        print(f'{"Человек" if self._human_turn else "Компьютер"} произвел '
              f'выстрел в {coord} и', hit_text.get(hit_result))
        print('_' * 50)
        hit_pole.move_ships()
        self.show_pole()
        if hit_result == 0:
            self._human_turn = not self._human_turn
        return hit_result

    def __pc_logic(self, hit, coord):
        """Логика для выстрелов компьютера: если резаультатом выстрела стало
        попадание и корабль не потоплен, то стреляем вокруг ячейки"""
        self._next_step = None
        if hit == 1:
            if not self._first_step:
                self._first_step = coord
            self._last_step = coord
            self._diff = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        elif hit == 2:
            self._last_step = None
            self._diff = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            self._first_step = None
        if self._last_step:
            while not self._next_step:
                if not self._diff:
                    self._diff = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    self._last_step = self._first_step
                diff = self._diff.pop(randint(0, len(self._diff) - 1))
                next_step = (diff[0] + self._last_step[0],
                             diff[1] + self._last_step[1])
                if next_step not in self._pc_steps and all(
                        i in range(self._size) for i in next_step):
                    self._next_step = next_step

    def show_pole(self):
        """Отображение игровых полей"""
        human_pole = self._human.get_text_pole(player_step=self._pc_steps)
        pc_pole = self._pc.get_text_pole(player_step=self._human_steps,
                                         hidden=self._hidden)
        print(f"{'Человек':^{self._size * 2 + 3}} "
              f"{'Компьютер':^{self._size * 2 + 7}}")
        print(' ', *[i for i in range(self._size)], sep=' ', end=' ' * 5)
        print(' ', *[i for i in range(self._size)], sep=' ')
        for i in range(self._size):
            print(i, *human_pole[i], end=' ' * 5)
            print(i, *pc_pole[i])

    @property
    def game_over(self):
        return self.__game_over

    @staticmethod
    def __is_any_alive(pole):
        """Проверка на наличие непотопленных кораблей на поле"""
        return any(ship.is_alive for ship in pole.ships)


if __name__ == "__main__":
    # battle = SeaBattle(10, False, ((2, 4), (3, 3), (3, 2), (4, 1)))
    battle = SeaBattle(randint(7, 10))
    battle.show_pole()
    while not battle.game_over:
        battle.next_move()
