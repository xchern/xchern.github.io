#!/usr/bin/env python2

from Tkinter import *
import tkMessageBox

from PIL import Image, ImageTk

import numpy as np

class Light():
    def __init__(self, tpl=None, size=5):
        assert size > 1, 'size should be more than one'
        if tpl: # copy construct
            self.board = np.copy(tpl.board)
            self.size = tpl.size
            self.transMat = tpl.transMat
        else: # default construct
            self.board = np.ones((size,size), dtype=np.bool) # empty
            self.size = size
            self.transMat = None
    def allOff(self):
        return np.sum(self.board) == 0
    def toggle(self,x,y):
        assert(0 <= x < self.size)
        assert(0 <= y < self.size)
        self.board[x,y] = not self.board[x,y]
        if x != 0: self.board[x-1,y] = not self.board[x-1,y]
        if y != 0: self.board[x,y-1] = not self.board[x,y-1]
        if x != self.size-1:
            self.board[x+1,y] = not self.board[x+1,y]
        if y != self.size-1:
            self.board[x,y+1] = not self.board[x,y+1]
        return self.allOff()
    def solve(self):
        if self.transMat is None:
            # transform kernel
            rowA = np.zeros((self.size,self.size), dtype=np.bool)
            rowB = np.eye(self.size, dtype=np.bool)
            for _ in range(self.size):
                row = np.zeros_like(rowA, dtype=np.bool)
                row[   0,:] = rowB[   0,:] ^ rowB[  1,:]
                row[  -1,:] = rowB[  -1,:] ^ rowB[ -2,:]
                row[1:-1,:] = rowB[1:-1,:] ^ rowB[:-2,:] ^ rowB[2:,:]
                row = row ^ rowA
                rowA, rowB = rowB, row
            self.transMat = rowB
        # propagation to end -- get last row
        def propagation(first_row):
            row = np.copy(first_row)
            click_map = []
            rowA = self.board[0]
            for line in (list(self.board[1:]) +
                        [np.zeros(self.size, dtype=np.bool)]):
                rowB = line
                click_map.append(np.copy(row))
                t = np.copy(row)
                row[1:  ] = row[1:  ] ^ t[ :-1]
                row[ :-1] = row[ :-1] ^ t[1:  ]
                rowA = rowA ^ row
                rowB = line ^ t
                row, rowA = rowA, rowB
            return row, np.array(click_map)
        row, _ = propagation(np.zeros(self.size, dtype=np.bool))
        # gaussian elimination
        transMat = np.copy(self.transMat)
        j = 0
        for i in range(0, self.size):
            if not transMat[i,j]:
                for k in range(j+1,self.size):
                    if transMat[i,k]: # try get the first non zero row
                        transMat[:,j] = transMat[:,j] ^ transMat[:,k]
                        row[j] = row[j] ^ row[k]
                        break
                # no non zero row
                if not transMat[i,j]: continue
            for k in range(j+1,self.size):
                if transMat[i,k]:
                    transMat[:,k] = transMat[:,k] ^ transMat[:,j]
                    row[k] = row[k] ^ row[j]
            j += 1
        # get solution
        line = np.zeros(self.size, dtype=np.bool)
        s_hi = self.size
        s_lo = self.size
        for j in range(self.size - 1, -1, -1):
            for i in range(self.size): # first non zero column
                if transMat[i,j]:
                    s_lo = i
                    break
            if s_lo == self.size and row[j]:
                    return None
            if (np.sum(np.logical_and(line, transMat[:,j])) % 2 != 0) != row[j]:
                line[s_lo] = not line[s_lo]
            s_hi = s_lo
        r, solution = propagation(line)
        return solution


window_size = 800
gapratio = 0.05

class LightApp(Tk):
    def __init__(self, light=Light()):
        self.light = light

        Tk.__init__(self)
        # white icon
        image=ImageTk.PhotoImage(Image.new('1', (16,16), 'white'))
        self.tk.call('wm', 'iconphoto', self._w, image)
        self.geometry("%dx%d" % (window_size, window_size))
        self.title('Light')

        # menu
        self.menu = Menu(self)
        self.menu.add_command(label="Solve", command=lambda:self.showSolution())
        self.menu.add_command(label="Harder", command=lambda:(
            self.removeButtons(),
            setattr(self, 'light', Light(size=self.light.size + 1)),
            self.addButtons()
            ))
        self.config(menu=self.menu)

        # frame
        self.frame = Frame(self)               
        self.frame.place(relwidth = 1, relheight = 1)

        # buttons
        self.addButtons()

        self.show()

    def addButtons(self):
        self.buttons = {}
        def newButton(i,j):
            btn = Button(self.frame, fg='red', command=lambda:
                            ( tkMessageBox.showinfo('Congratulations!',
                                                    'you achieved the goal')
                            , self.destroy()
                            )
                          if (self.light.toggle(i,j) , self.show())[0] else None
                        )
            return btn
        relwidth = 1. / (self.light.size + (self.light.size) * gapratio)
        relgap = gapratio * relwidth
        for i in range(self.light.size):
            for j in range(self.light.size):
                btn = newButton(i,j)
                btn.place(relx=(relgap + relwidth) * j + relgap/2.,
                          rely=(relgap + relwidth) * i + relgap/2.,
                          relwidth=relwidth, relheight=relwidth)
                self.buttons[(i,j)] = btn
        self.show()
    def removeButtons(self):
        for _, btn in self.buttons.iteritems():
            btn.destroy()
    def show(self):
        for i in range(self.light.size):
            for j in range(self.light.size):
                if self.light.board[(i,j)]:
                    self.buttons[(i,j)].config(bg='olive')
                else:
                    self.buttons[(i,j)].config(bg='gold')
    def showSolution(self):
        solution = self.light.solve()
        if solution is not None:
            for i in range(self.light.size):
                for j in range(self.light.size):
                    if solution[i,j]:
                        self.buttons[(i,j)].config(text='here', bg='red')
                    else:
                        self.buttons[(i,j)].config(text='')
        else:
            tkMessageBox.showerror('No solution!', 'you can never achieve the goal')

if __name__ == '__main__':
    app = LightApp()
    app.mainloop()
