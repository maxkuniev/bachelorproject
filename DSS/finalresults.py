import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
import pandas as pd
from tkinter import PhotoImage
from PIL import Image, ImageTk
from collections import defaultdict
import numpy as np
from backendcalculation_df import search_c_null
from backendcalculation_df import search_r
import os

class MatrixViewer2:
    def __init__(self, parent, data, rows, cols, cons, recal):
        self.recal = recal

        self.parent = parent
        self.parent.destroy()

        self.datamethods = data
        self.rowsmethods = rows
        self.colsmethods = cols
        self.consmethods = cons

        self.pcnorm = []
        self.comb = []

        self.addedelements = []
        for i in range(len(self.recal)):
            self.addedelements.append(self.extract_different_tail_elements_v2(self.rowsmethods[i]))


        for i in range(len(self.datamethods)):
            if self.addedelements[i] != []:
                column_index = int(self.addedelements[i][0].split('.')[1])
                column = self.recal[i][:, column_index - 1]
                column_float = [float(x) if x != 'nan' else np.nan for x in column]
                filtered = [x for x in column_float if not np.isnan(x)]
                second_array = self.convertdftomatrix(self.consmethods[i])
                second_array.append(filtered)
                recaltemp, pctemp, combtemp = search_c_null(second_array,
                                                            self.rowsmethods[i])
                self.pcnorm.append(pctemp)
                self.comb.append(combtemp)
            else:
                recaltemp, pctemp, combtemp = search_c_null(self.convertdftomatrix(self.consmethods[i]), self.rowsmethods[i])
                self.pcnorm.append(pctemp)
                self.comb.append(combtemp)

        self.dfses = self.finrses()

        self.root = tk.Tk()
        self.root.title("Final results")
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

        self.tableamount = len(self.file_paths)
        self.matrixdata = []

        for i in range(self.tableamount):
            temp = (self.findmatrix_df(self.file_paths[i]))
            self.matrixdata.append(temp)

        for i in range(self.tableamount):
            print("МЕТОДИ")
            print(self.dfses[i])
            print("МЕТОДИ")

        for i in range(self.tableamount):
            listtemp = list(self.matrixdata[i].columns)
            result = [f"F9.1.{i + 1} {item.split('Заходи запобігання')[-1]}" for i, item in enumerate(listtemp)]

            l = self.dfses[i][self.dfses[i].columns[0]].tolist()

            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"Чинник {i+1}")
            self.draw_matrix(frame, result, l)

    def extract_different_tail_elements_v2(self, lst):
        if not lst or len(lst) < 2:
            return []

        last_prefix = lst[-1].split('.')[0]

        tail_elements = []
        for i in range(len(lst) - 1, -1, -1):
            current_prefix = lst[i].split('.')[0]
            if current_prefix == last_prefix:
                tail_elements.append(lst[i])
            else:
                break

        if tail_elements:
            start_index = len(lst) - len(tail_elements)
            if start_index > 0:
                prev_prefix = lst[start_index - 1].split('.')[0]
                if prev_prefix != last_prefix:
                    return list(reversed(tail_elements))

        return []

    def finrses(self):
        test = search_r(self.pcnorm, self.comb, self.datamethods, self.rowsmethods, self.colsmethods)
        dfs = [self.flatten_series_list(entry) for entry in test]
        for i in range(len(dfs)):
            print(dfs[i])
        return dfs


    def flatten_series_list(self, series_list):
        col_dict = {}
        max_len = 0

        for s in series_list:
            col_name = '.'.join(s.index[0].split('.')[:2])
            col_dict[col_name] = list(s.values)
            max_len = max(max_len, len(s))

        for k in col_dict:
            if len(col_dict[k]) < max_len:
                col_dict[k] += [float('nan')] * (max_len - len(col_dict[k]))

        return pd.DataFrame(col_dict)

    def draw_matrix(self, frame, row_headers, values):
        rows = len(row_headers)
        container = ttk.Frame(frame)
        container.pack(expand=True)
        font_big = ("Helvetica", 14)

        matrix_entries = []

        header1 = tk.Entry(container, width=40, justify='center', bg='lightgray',
                           font=font_big, takefocus=0)
        header1.insert(0, "Метод запобігання")
        header1.config(state='readonly')
        header1.grid(row=0, column=0, padx=1, pady=1)

        header2 = tk.Entry(container, width=10, justify='center', bg='lightgray',
                           font=font_big, takefocus=0)
        header2.insert(0, "Значення")
        header2.config(state='readonly')
        header2.grid(row=0, column=1, padx=1, pady=1)

        for i in range(rows):
            label_entry = tk.Entry(container, width=40, justify='left',
                                   bg='lightgray', font=font_big, takefocus=0)
            label_entry.insert(0, row_headers[i])
            label_entry.config(state='readonly')
            label_entry.grid(row=i + 1, column=0, padx=1, pady=1)

            value = values[i] if i < len(values) else ""
            val_entry = tk.Entry(container, width=10, justify='center',
                                 font=font_big, takefocus=1)
            if isinstance(value, (int, float)):
                value = round(value, 3)
            val_entry.insert(0, value)
            val_entry.grid(row=i + 1, column=1, padx=1, pady=1)
            val_entry.config(state='readonly')

            matrix_entries.append((i, row_headers[i], val_entry))

        container.pack(expand=True, pady=10)
        self.entry_widgets.append(matrix_entries)

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

    def convertdftomatrix(self, df):
        return [df[col].dropna().tolist() for col in df.columns]

