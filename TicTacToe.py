import random


class Cell:

    def __init__(self):
        self.value = 0

    def __bool__(self):
        return not self.value

    def __setattr__(self, key, value):
        if value != 0 and self.value != 0:
            raise ValueError('клетка уже занята')
        super().__setattr__(key, value)


class TicTacToe:
    FREE_CELL = 0  # свободная клетка
    HUMAN_X = 1  # крестик (игрок - человек)
    COMPUTER_O = 2  # нолик (игрок - компьютер)

    def __init__(self, human_turn=True):
        self.pole = [[Cell() for _ in range(3)] for _ in range(3)]
        self.human_turn = human_turn

    def start_game(self):
        while self:
            try:
                self.next_step()
                self.show()
            except (ValueError, IndexError) as e:
                print("_" * 30)
                print(e)
        print("_" * 30)
        if self.is_human_win:
            print("Поздравляем, вы выиграли!!!")
        if self.is_computer_win:
            print("К сожалению вы проиграли, попробуйте еще раз")
        if self.is_draw:
            print("Игра закончена. Ничья.")

    def next_step(self):
        if self.human_turn:
            self.human_go()
        else:
            self.computer_go()
        self.human_turn = not self.human_turn

    def human_go(self):
        print("_" * 30)
        column, row = map(int, input("Введите координаты клетки: ").split())
        self[row, column] = self.HUMAN_X

    def computer_go(self):
        row, column = self.find_empty_cell()
        self[row, column] = self.COMPUTER_O

    def find_empty_cell(self):
        row = random.randint(0, 2)
        column = random.randint(0, 2)
        while not self.pole[row][column]:
            row = random.randint(0, 2)
            column = random.randint(0, 2)
        return row, column

    def __getitem__(self, item):
        row, column = item
        self._check_index(row, column)
        return self.pole[row][column].value

    def __setitem__(self, key, value):
        row, column = key
        self._check_index(row, column)
        self.pole[row][column].value = value

    @staticmethod
    def _check_index(row, column):
        if abs(row) not in range(3) or abs(column) not in range(3):
            raise IndexError('некорректно указанные индексы')

    def show(self):
        print("_" * 30)
        dict_char = {self.FREE_CELL: '.', self.HUMAN_X: 'X',
                     self.COMPUTER_O: 'O'}
        for row in self.pole:
            for cell in row:
                print(dict_char[cell.value], end=' ')
            print()

    def check_win(self, value):
        for row in self.pole:
            if all(cell.value == value for cell in row):
                return True
        for i in range(3):
            if all(cell.value == value for cell
                   in (row[i] for row in self.pole)):
                return True
        if (all(self[i, i] == value for i in range(3))
                or all(self[i, -1 - i] == value for i in range(3))):
            return True
        return False

    @property
    def is_human_win(self):
        return self.check_win(self.HUMAN_X)

    @property
    def is_computer_win(self):
        return self.check_win(self.COMPUTER_O)

    @property
    def is_draw(self):
        return (not self.is_human_win and not self.is_computer_win
                and not bool(self))

    def __bool__(self):
        return (not self.is_human_win and not self.is_computer_win
                and any([cell.value == self.FREE_CELL for rows in self.pole
                         for cell in rows]))


if __name__ == "__main__":
    game = TicTacToe()
    # game = TicTacToe(False)
    game.show()
    game.start_game()
