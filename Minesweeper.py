import random


class Cell:

    def __init__(self):
        self.__is_mine = False
        self.__number = None
        self.__is_open = False

    @property
    def is_mine(self):
        return self.__is_mine

    @is_mine.setter
    def is_mine(self, value):
        if type(value) != bool:
            raise ValueError("недопустимое значение атрибута")
        self.__is_mine = value

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, value):
        if type(value) != int or value not in range(9):
            raise ValueError("недопустимое значение атрибута")
        self.__number = value

    @property
    def is_open(self):
        return self.__is_open

    @is_open.setter
    def is_open(self, value):
        if type(value) != bool:
            raise ValueError("недопустимое значение атрибута")
        self.__is_open = value

    def __bool__(self):
        return not self.__is_open


class GamePole:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, m, n, total_mines):
        self.__game_over = False
        self.M = m
        self.N = n
        self.total_mines = total_mines
        self.__pole_cells = [[Cell() for _ in range(m)] for _ in range(n)]
        self.__win = False

    def start_game(self):
        print("_" * 30)
        self.init_pole()
        self.show_pole()
        while not self.__game_over:
            try:
                print("_" * 30)
                x, y = map(int, input("Введите координаты ячейки (x, y): "
                                      ).split())
                self.open_cell(y, x)
                print("_" * 30)
                self.show_pole()
            except Exception as e:
                print(e)
        print("_" * 30)
        if self.__win:
            print("Поздравляем, вы победили!!!")
        else:
            print("Упс, вы подорвались. Попробуйте еще раз.")

    def init_pole(self):
        current_mines = 0
        while current_mines != self.total_mines:
            i, j = random.randint(0, self.N - 1), random.randint(0,
                                                                 self.M - 1)
            if not self.pole[i][j].is_mine:
                self.pole[i][j].is_mine = True
                current_mines += 1
        for i in range(self.N):
            for j in range(self.M):
                self.pole[i][j].number = self.count_mines(i, j)

    def show_pole(self):
        print(" " * 4, *range(self.M), end="\n" * 2)
        for i in range(self.N):
            print(i, end=" " * 4)
            for j in self.pole[i]:
                print(self.show_cell(j), end=" ")
            print()

    @staticmethod
    def show_cell(obj):
        if obj:
            return "*"
        if obj.is_mine:
            return "!"
        return obj.number

    def open_cell(self, x, y):
        if x < 0 or y < 0 or x > self.N or y > self.M:
            raise IndexError("Некорректные индексы i, j клетки игрового поля")
        obj = self.pole[x][y]
        if obj.is_open:
            raise IndexError("Ячейка уже открыта")
        obj.is_open = True
        if obj.number == 0:
            for a in range(max(0, x - 1), min(x + 2, self.N)):
                for b in range(max(0, y - 1), min(y + 2, self.M)):
                    if self.pole[a][b]:
                        self.open_cell(a, b)
        if obj.is_mine:
            self.__game_over = True
        elif self.count_open_cell() == self.total_mines:
            self.__game_over = True
            self.__win = True

    @property
    def pole(self):
        return self.__pole_cells

    def count_mines(self, n, m):
        count = 0
        for i in range(max(0, n - 1), min(n + 2, self.N)):
            for j in range(max(0, m - 1), min(m + 2, self.M)):
                count += self.pole[i][j].is_mine
        count -= self.pole[n][m].is_mine
        return count

    def count_open_cell(self):
        return sum([1 for line in self.pole for cell in line if cell])


if __name__ == "__main__":
    game = GamePole(11, 10, 10)
    game.start_game()
