import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
import pandas as pd
from tkinter import PhotoImage
from PIL import Image, ImageTk
from collections import defaultdict
import numpy as np
from finalresults import MatrixViewer2
import os

class MatrixMethods:
    def __init__(self, parent, toplevel, consequences, recal):
        self.recal = recal
        self.consequences = consequences
        for i in range(len(self.consequences)):
            print("ОТРИМАНІ ДАНІ НАСЛІДКИ")
            print(self.consequences[i])
            print("ОТРИМАНІ ДАНІ НАСЛІДКИ")

        self.toplevelclass = toplevel
        self.toplevelclass.destroy()

        self.parentclass = parent
        self.parentclass.destroy()

        self.rows_names = []
        self.cols_names = []

        self.root = tk.Tk()
        self.root.title("Matrix Viewer")
        self.root.resizable(False, False)
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

        self.entry_widgets = []
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TABLES_DIR = os.path.join(BASE_DIR, "..", "Tables")

        self.file_paths = [
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
            os.path.join(TABLES_DIR, "example_table.xlsx"),
        ]

        self.tableamount = len(self.consequences)

        for i in range(self.tableamount):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"Матриця {i+1}")
            df = self.findmatrix_df(self.file_paths[i])
            rowsname = df.index.tolist()
            columnsname = df.columns.tolist()
            array = df.to_numpy()
            rows_amount, columns_amount = array.shape
            self.draw_matrix(frame, rowsname, columnsname, rows_amount, columns_amount)

        self.matrixdata = []

        self.helv36 = tkFont.Font(family='Helvetica', size=12, weight=tkFont.BOLD)

        style.configure("Big.TButton", font=self.helv36)

        self.buttonfix = ttk.Button(self.root, text="Розрахунок оцінок для методів", style="Big.TButton", command = self.collect_user_data)
        self.buttonfix.pack(side="bottom", pady=20, ipadx=10, ipady=10)

        original_image = Image.open("excel.png")
        resized_image = original_image.resize((24, 24), Image.Resampling.LANCZOS)
        self.icon_excel = ImageTk.PhotoImage(resized_image)
        self.buttonexcel = ttk.Button(self.root, text="EXCEL FILL", image=self.icon_excel, style="Big.TButton",
                                      compound="left", command=self.excel_fill)
        self.buttonexcel.pack(side="bottom", pady=20, ipadx=10, ipady=10)

    def draw_matrix(self, frame, rowsname, columnsname, rows_amount, columns_amount):
        rowsname = self.auto_map(rowsname)
        columnsname = self.auto_map(columnsname)

        self.rows_names.append(rowsname)
        self.cols_names.append(columnsname)

        container = ttk.Frame(frame)
        container.pack(expand=True, pady=10)
        font_big = ("Helvetica", 12)
        for j in range(columns_amount):
            e = tk.Entry(container, width=5, justify='center', bg='lightgray', font=font_big, takefocus=0)
            e.grid(row=0, column=j + 1, padx=1, pady=1)
            e.insert(0, columnsname[j])
            e.config(state='readonly')

        matrix_entries = []
        for i in range(rows_amount):
            e = tk.Entry(container, width=5, justify='left', bg='lightgray', font=font_big, takefocus=0)
            e.grid(row=i + 1, column=0, padx=1, pady=1)
            e.insert(0, rowsname[i])
            e.config(state='readonly')

            row_entries = []
            for j in range(columns_amount):
                if self.get_prefix(rowsname[i]) == self.get_prefix(columnsname[j]):
                    entry = tk.Entry(container, width=5, justify='center', font=font_big, disabledbackground='orange')
                    entry.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                    entry.config(state='disabled')
                    row_entries.append(entry)
                    matrix_entries.append((i, j, entry))

                else:
                    entry = tk.Entry(container, width=5, justify='center', font=font_big)
                    entry.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                    row_entries.append(entry)

                    matrix_entries.append((i, j, entry))

        self.entry_widgets.append(matrix_entries)

    def get_prefix(self, s):
        return '.'.join(s.split('.')[:2])

    def findmatrix_df(self, path):

        df = pd.read_excel(path, sheet_name=0, header=[0, 1])

        df.iloc[:, 0] = df.iloc[:, 0].ffill()

        df.columns = df.columns.to_frame().fillna('').agg(' '.join, axis=1).str.strip()

        row_index = df.iloc[:, :2].fillna('').agg(' '.join, axis=1).str.strip()
        df = df.iloc[:, 2:]
        df.index = row_index
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
        df.index.name = None
        return df

    def auto_map(self, rows):
        groups = defaultdict(list)
        for row in rows:
            prefix = ' '.join(row.split()[:2])
            groups[prefix].append(row)

        updated_rows = []
        for group in groups.values():
            for idx, name in enumerate(group, start=1):
                code = name.split()[0] + f'.{idx}'
                updated_rows.append(code)

        return updated_rows

    def collect_user_data(self):
        all_data = []

        for matrix in self.entry_widgets:
            rows_dict = {}
            for i, j, entry in matrix:
                value = entry.get()
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
        self.matrixmethods()

    def excel_fill(self):
        for i in range(self.tableamount):
            df = self.findmatrix_df(self.file_paths[i])
            df = df.fillna("0")
            df = df.astype(str).apply(lambda col: col.str.replace(",", ".", regex=False))
            array = df.to_numpy()
            np.set_printoptions(threshold=np.inf, linewidth=200)
            """print(array)"""
            self.load_matrix_to_entries(i, array)
        return

    def load_matrix_to_entries(self, tab_index, matrix_data):

        matrix = self.entry_widgets[tab_index]

        for i, j, entry in matrix:
            value = matrix_data[i][j]
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def matrixmethods(self):
        matrixnew = MatrixViewer2(self.root, self.matrixdata, self.rows_names, self.cols_names, self.consequences, self.recal)
        return
