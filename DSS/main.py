# ╔═════════════════════════════════════════════════════╗
# ║                     main.py                         ║
# ║        Головний файл запуску системи СППР           ║
# ╚═════════════════════════════════════════════════════╝


import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
import pandas as pd
from tkinter import PhotoImage
from PIL import Image, ImageTk
from main2 import MatrixViewer
import re
import os

class FrontEnd(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("СППР")
        self.geometry("1100x800")
        self.resizable(False, False)

        style = ttk.Style()

        style.theme_use("classic")

        style.configure("TNotebook.Tab",
                        font=("Arial", 16),
                        padding=[10, 5],
                        borderwidth=2,
                        relief="raised",
                        background="lightgray",
                        )

        style.map("TNotebook.Tab",
                  background=[("selected", "#f0f6d0")],
                  expand=[("selected", [0, 0, 0, 0])]
                  )

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True);
        notebook.pack(anchor='n', pady=20, padx=30)

        self.entry_widgets = []

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TABLES_DIR = os.path.join(BASE_DIR, "..", "Tables")


        self.file_paths = [
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
        ]
        self.tableamount = len(self.file_paths)

        for i in range(self.tableamount):
            numbers = [int(re.search(r'_0*(\d+)_', path).group(1)) for path in self.file_paths]
            l = []
            if i == 0:
                l = [f"F{i + 1}.{j}" for j in range(1, 9)]
            else:
                l = [f"F{numbers[i]+1}.{j}" for j in range(1, 9)]

            frame = ttk.Frame(notebook)
            if i == 0:
                notebook.add(frame, text=f"Спільні")
            else:
                notebook.add(frame, text=f"Чинник {i}")
            df = pd.read_excel(self.file_paths[i])
            df = df.fillna("-")
            df = df.astype(str).apply(lambda col: col.str.replace(",", ".", regex=False))
            array = df.to_numpy()
            rows, columns = array.shape

            self.draw_matrix(frame, l, rows, columns, array)

        self.helv36 = tkFont.Font(family='Helvetica', size=16, weight=tkFont.BOLD)

        style.configure("Big.TButton", font=self.helv36, anchor="center")

        self.labelbottom = ttk.Label(text="© 2025 Kuniev Maksym. All rights reserved.", font=("Arial", 12))
        self.labelbottom.pack(side="bottom")

        self.buttonfix = ttk.Button(self, text = "Оновити дані", style="Big.TButton")
        self.buttonfix.pack(side = "bottom", pady=20, ipadx=20, ipady=20)

        self.buttontest = ttk.Button(self, text="Побудова матриці\nвзаємної узгодженості", style="Big.TButton", command = self.collect_user_data)
        self.buttontest.pack(side="bottom", pady=20)


        original_image = Image.open("excel.png")
        resized_image = original_image.resize((24, 24), Image.Resampling.LANCZOS)
        self.icon_excel = ImageTk.PhotoImage(resized_image)
        self.buttonexcel = ttk.Button(self, text="EXCEL FILL", image=self.icon_excel, style="Big.TButton", compound="left", command=self.excel_fill)
        self.buttonexcel.pack(side="bottom", pady=20, ipadx=20, ipady=20)

        self.matrixdata = []


    def draw_matrix(self, frame, line, rows, columns, array):
        rows, cols = rows, columns
        container = ttk.Frame(frame)
        container.pack(expand=True)
        font_big = ("Helvetica", 32)
        for j in range(cols):
            e = tk.Entry(container, width=5, justify='center', bg='lightgray', font=font_big, takefocus=0)
            e.grid(row=0, column=j, padx=1, pady=1)
            e.insert(0, line[j])
            e.config(state='readonly')

        matrix_entries = []
        for i in range(1, rows + 1):
            for j in range(cols):

                value = array[i - 1][j]

                entry = tk.Entry(container, width=5, justify='center', font=font_big, takefocus=0)
                entry.insert(0, 0)

                if value != "-":
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
                    messagebox.showwarning("Attention!", "You didn’t enter a valid number or have empty cells!")
                    return
                if i not in rows_dict:
                    rows_dict[i] = []
                rows_dict[i].append(value)
            matrix_data = [rows_dict[i] for i in sorted(rows_dict.keys())]
            all_data.append(matrix_data)

        """for idx, table in enumerate(all_data):
            print(f"\n--- Таблиця {idx + 1} ---")
            for row in table:
                print(row)"""

        self.matrixdata = all_data
        print(self.matrixdata[0])

        print(self.transmatrix(self.matrixdata[0]))
        self.makematrix()

    def transmatrix(self, matrix):
        result = [
            [float(row[i]) for row in matrix if float(row[i]) != 0.0]
            for i in range(len(matrix[0]))
        ]

        return result

    def excel_fill(self):
        for i in range(self.tableamount):
            df = pd.read_excel(self.file_paths[i])
            df = df.fillna("0")
            df = df.astype(str).apply(lambda col: col.str.replace(",", ".", regex=False))
            array = df.to_numpy()
            self.load_matrix_to_entries(i, array)
        return

    def load_matrix_to_entries(self, tab_index, matrix_data):

        matrix = self.entry_widgets[tab_index]

        for i, j, entry in matrix:
            value = matrix_data[i - 1][j]
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def makematrix(self):
        matrixview = MatrixViewer(self, self.matrixdata)

if __name__ == "__main__":
    app = FrontEnd()
    app.mainloop()