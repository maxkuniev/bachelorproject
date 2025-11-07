import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
import pandas as pd
from tkinter import PhotoImage
from PIL import Image, ImageTk
from collections import defaultdict
import numpy as np
import re
from matrixviewer2 import MatrixViewer2
from backendcalculation_df import matrixchoose
from itertools import zip_longest

class BackEnd:
    def __init__(self, main_window, toplevel_window, data, matrixdata, columndata, rowdata):
        print(len(data))
        self.data_new = data[1:]
        self.data_rec = data[0]


        self.data_recal = []

        self.main = main_window
        self.toplevel = toplevel_window

        self.toplevel.destroy()
        self.main.destroy()

        self.new_root = tk.Tk()
        self.new_root.title("СППР")

        self.new_root.resizable(False, False)

        style = ttk.Style()

        style.theme_use("classic")

        style.configure("TNotebook.Tab",
                        font=("Arial", 16),
                        padding=[10, 5],
                        borderwidth=2,
                        relief="raised",
                        background="lightgray"
                        )

        style.map("TNotebook.Tab",
                  background=[("selected", "#f0f6d0")],
                  expand=[("selected", [0, 0, 0, 0])]
                  )

        notebook = ttk.Notebook(self.new_root)
        notebook.pack(expand=True)
        notebook.pack(anchor='n', pady=20, padx=30)

        self.entry_widgets = []

        self.file_paths = [
            "C:/Users/maks/Desktop/Диплом/Tables/_01_оцінки_промислові_викиди.xlsx",
            "C:/Users/maks/Desktop/Диплом/Tables/_03_оцінки_стічні_води.xlsx",
            "C:/Users/maks/Desktop/Диплом/Tables/_05_оцінки_надмірне_використання_хімікатів.xlsx",
        ]
        self.tableamount = len(self.file_paths)

        self.comb = []
        self.pcnorm = []

        for i in range(self.tableamount):
            numbers = [int(re.search(r'_0*(\d+)_', path).group(1)) for path in self.file_paths]

            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"Чинник {numbers[i]}")

            df = self.creatematrixdf(matrixdata[i], columndata[i], rowdata[i])
            datatester = self.transmatrix(self.data_new[i]) + self.transmatrix(self.data_rec)

            tempdata, combtemp, pcnormtemp = matrixchoose(datatester, df)
            self.comb.append(combtemp)
            self.pcnorm.append(pcnormtemp)

            tempdata_transposed = list(zip_longest(*tempdata, fillvalue=np.nan))

            array_str = np.array(tempdata_transposed, dtype=float).astype(str)

            array = array_str

            rows, columns = array.shape
            columnsforbg = len(self.data_new[i][0])

            print("PERERAHUNOK")
            print(array)
            print("PERERAHUNOK")

            rounded_array = np.round(array.astype(float), 3).astype(str)
            l = [f"F{numbers[i]+1}.{j}" for j in range(1, columns + 1)]

            self.data_recal.append(rounded_array)

            self.draw_matrix(frame, l, rows, columns, array, highlight_rows=columnsforbg)


        self.excel_fill(self.data_recal)

        self.helv36 = tkFont.Font(family='Helvetica', size=16, weight=tkFont.BOLD)

        style.configure("Big.TButton", font=self.helv36)

        self.labelbottom = ttk.Label(text="© 2025 Kuniev Maksym. All rights reserved.", font=("Arial", 12))
        self.labelbottom.pack(side="bottom")

        self.buttontest = ttk.Button(self.new_root, text="Матриця узгодженості з наслідками", style="Big.TButton",
                                     command=self.collect_user_data)
        self.buttontest.pack(side="bottom", pady=20, ipadx=20, ipady=20)

        self.matrixdata = []

    def draw_matrix(self, frame, line, rows, columns, array, highlight_rows):
        rows, cols = rows, columns
        container = ttk.Frame(frame)
        container.pack(expand=True)
        font_big = ("Helvetica", 32)
        linebg = [f"F1.{j}" for j in range(1, 9)]
        for j in range(cols):
            if j >= highlight_rows:
                e = tk.Entry(container, width=5, justify='center', bg='lightgray', font=font_big, takefocus=0)
                e.grid(row=0, column=j, padx=1, pady=1)
                e.insert(0, linebg[j-highlight_rows])
                e.config(state='readonly')
            else:
                e = tk.Entry(container, width=5, justify='center', bg='lightgray', font=font_big, takefocus=0)
                e.grid(row=0, column=j, padx=1, pady=1)
                e.insert(0, line[j])
                e.config(state='readonly')



        matrix_entries = []
        for i in range(1, rows + 1):
            for j in range(cols):

                value = array[i - 1][j]
                if j >= highlight_rows:
                    bg_color = 'yellow'
                    entry = tk.Entry(container, width=5, justify='center', font=font_big, takefocus=0,
                                     disabledbackground=bg_color)
                    entry.insert(0, 0)
                else:
                    bg_color = 'lightgreen'
                    entry = tk.Entry(container, width=5, justify='center', font=font_big, takefocus=0,
                                     disabledbackground=bg_color)
                    entry.insert(0, 0)

                if value != '-' and value != 'nan':
                    entry.delete(0, tk.END)
                    entry.insert(0, "-")

                    def on_focus_in(event, e=entry):
                        if e.get() == "-":
                            e.delete(0, tk.END)

                    def on_focus_out(event, e=entry):
                        if e.get() == "":
                            e.insert(0, "-")

                    entry.bind("<FocusIn>", on_focus_in)
                    entry.bind("<FocusOut>", on_focus_out)

                    entry.grid(row=i, column=j, padx=1, pady=1)

                matrix_entries.append((i, j, entry))

        container.pack(expand=True, pady=10)
        self.entry_widgets.append(matrix_entries)

    def collect_user_data(self):
        all_data = []

        for matrix in self.entry_widgets:
            rows_dict = {}
            for i, j, entry in matrix:
                value = entry.get()
                try:
                    number = float(value)
                except ValueError:
                    messagebox.showwarning("ERROR!", "SOMETHING WRONG!")
                    return
                if i not in rows_dict:
                    rows_dict[i] = []
                rows_dict[i].append(value)
            matrix_data = [rows_dict[i] for i in sorted(rows_dict.keys())]
            all_data.append(matrix_data)

        for idx, table in enumerate(all_data):
            print(f"\n--- Таблиця {idx + 1} ---")
            for row in table:
                print(row)

        self.matrixdata = all_data
        self.makematrixnew()

    def excel_fill(self, data):
        for i in range(self.tableamount):
            array = data[i]
            self.load_matrix_to_entries(i, array)
        return

    def load_matrix_to_entries(self, tab_index, matrix_data):

        matrix = self.entry_widgets[tab_index]

        for i, j, entry in matrix:
            value = matrix_data[i - 1][j]
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state='disabled')

    def creatematrixdf(self, data, columns, rows):
        float_data = [[float(x) if x != '' else float('nan') for x in row] for row in data]
        df = pd.DataFrame(float_data, index=rows, columns=columns)
        return df

    def transmatrix(self, matrix):
        result = [
            [float(row[i]) for row in matrix if float(row[i]) != 0.0]
            for i in range(len(matrix[0]))
        ]

        return result

    def makematrixnew(self):
        matrixview = MatrixViewer2(self.new_root, self.comb, self.pcnorm, self.data_recal)
        return
