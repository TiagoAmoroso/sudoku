import pygame
import sudokuSolver
from sudokuSolver import valid, solve
pygame.font.init()
import time



levelBoard = [
    [7,8,0,4,0,0,1,2,0],
    [6,0,0,0,7,5,0,0,9],
    [0,0,0,6,0,1,0,7,8],
    [0,0,7,0,4,0,2,6,0],
    [0,0,1,0,5,0,9,3,0],
    [9,0,4,0,6,0,0,0,5],
    [0,7,0,3,0,0,0,1,2],
    [1,2,0,0,0,7,4,0,0],
    [0,4,9,2,0,6,0,0,7]
]


class grid:

    def __init__(self, board, width, height, debug=False):
        self.startBoard = board #The empty, beginning board
        self.width = width #The pixel width of the displayed screen
        self.height = height #The pixel height of the displayed screen
        self.rows = len(board) #The number of rows on the board
        self.columns = len(board[0]) #The number of columns on the board
        self.board = board.copy() #The current board
        self.selected = None #The current selected cell
        self.cells = [[cell(self.board[i][j], i, j, width, height) for j in range(self.columns)] for i in range(self.rows)] #A list of the cells on the board
        #Extrapolate and tinker with list comprehension above until I fully understand it
        self.debug = debug

    def update_board(self):
        self.board = [[self.cells[i][j].value for j in range(self.columns)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cells[row][col].value == 0:
            if self.debug:
                print('cell is empty and is available for a number to be placed')
            self.cells[row][col].set_value(val)
            self.update_board()

    
            if valid(self.board, val, (row,col)):
                if self.debug:
                    print('The value entered is valid on the current board') 
                if solve(self.board): #Checks if the cell is valid in the board and also if it can lead to a fully complete solution
                    if self.debug:
                        print('With this new entry, the full board can still come to a complete solution')
                    return True
                else:
                    self.cells[row][col].set_value(0) 
                    self.cells[row][col].set_corner_value(0)
                    self.update_board()
                    return False
            else:
                    self.cells[row][col].set_value(0) 
                    self.cells[row][col].set_corner_value(0)
                    self.update_board()
                    return False
        else:
            if self.debug:
                print('This cell has already been set to a correct value, so the cell cannot be altered')

    def select(self, row, col):
        # Reset all cells to not selected
        for i in range(self.rows):
            for j in range(self.columns):
                self.cells[i][j].selected = False

        #Select specified cell
        self.cells[row][col].selected = True
        self.selected = (row, col)
        
    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height: #Checks if mouse [pos]ition is within the screen parameters
            gap = self.width / self.rows
            x = pos[0] // gap #Uses integer divisionn to find the cell that the mouse is within
            y = pos[1] // gap #Uses integer division to find the cell that the mouse is within
            return (int(y),int(x))
        else:
            return None

    def draw(self, window):
        # Draw Grid Lines
        gap = self.width / self.rows
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(window, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(window, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cells
        for i in range(self.rows):
            for j in range(self.columns):
                self.cells[i][j].draw(window)

    def clear(self):
        row, col = self.selected
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_corner_value(0)

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cells[i][j].value == 0: #If any cell on the board is not filled, the board is not finished
                    return False
        return True

class cell:

    def __init__(self, value, row, column, width, height, dimensions = 9):
        self.value = value #The value of the cell
        self.cornerValue = 0 #The corner value of the cell
        self.row = row #The row of the cell
        self.column = column #The column of the cell
        self.width = width #The pixel width of the displayed screen
        self.height = height #The pixel height of the displayed screen 
        self.dimensions = dimensions #The dimensions of the board (The amount of row/columns on each side)
        self.selected = False

    def set_value(self, newValue):
        self.value = newValue

    def set_corner_value(self, newValue):
        self.cornerValue = newValue

    def draw(self, window):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / self.dimensions
        x = gap * self.column
        y = gap * self.row

        #Drawing the cell's values
        if self.cornerValue != 0 and self.value == 0:
            text = fnt.render(str(self.cornerValue), 1, (128,128,128))
            window.blit(text, (x+5, y+5)) #Need to make these additions more relative to the cell
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            window.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2))) #Maths to centralise the number in the cell

        #Drawing the 'cell selected' box around the selected cell
        if self.selected:
            pygame.draw.rect(window, (255,0,0), (x,y, gap ,gap), 3)




def redraw_window(win, board, strikes, timeElapsed):
    win.fill((255,255,255))
    fnt = pygame.font.SysFont("comicsans", 40)
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw time
    text = fnt.render('Time Elapsed: ' + timeElapsed, 1, (0, 0, 0))
    win.blit(text, (270, 560))
    # Draw grid and board
    board.draw(win)


def main():
    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku")
    board = grid(levelBoard, 540, 540)
    key = None
    running = True
    strikes = 0
    startTime = time.time()
    while running:
        currentTime = time.time()
        timeElapsed = currentTime - startTime
        timeElapsed = round(timeElapsed, 0)
        timeElapsed = str(timeElapsed).replace('.0', '')
        #print(timeElapsed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cells[i][j].cornerValue != 0:
                        if board.place(board.cells[i][j].cornerValue):
                            print("Success in placing the value")
                        else:
                            print("Failed to place the value")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over - You completed the puzzle!")
                            running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None: #If the user has pressed a key button and has a cell selected, we set that to the corner value
            row, col = board.selected
            board.cells[row][col].set_corner_value(key)

        redraw_window(win, board, strikes, timeElapsed)
        pygame.display.update()


main()
pygame.quit()