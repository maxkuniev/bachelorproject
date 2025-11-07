import numpy as np
import pandas as pd
from itertools import combinations
from itertools import product
from pprint import pprint
import copy

def search_c(matrica, file_path):

    def findmatrix_df(file_path):
        np.set_printoptions(threshold=np.inf, linewidth=200)

        df = pd.read_excel(file_path, sheet_name=0, header=[0, 1])

        df.iloc[:, 0] = df.iloc[:, 0].ffill()

        df.columns = df.columns.to_frame().fillna('').agg(' '.join, axis=1).str.strip()

        row_index = df.iloc[:, :2].fillna('').agg(' '.join, axis=1).str.strip()
        df = df.iloc[:, 2:]
        df.index = row_index
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
        df.index.name = None
        return df

    unique_combinations = list(combinations(range(len(matrica)), 2))
    print("unique combinations",unique_combinations)

    matrices = {}

    matrices_list = []
    for comb in unique_combinations:
        list1 = matrica[comb[0]]
        list2 = matrica[comb[1]]
        matrix = np.zeros((len(list1), len(list2)))
        matrices[comb] = matrix
        matrices_list.append(matrix)



    def findmatrix(df, prefix_col, prefix_row):
        def get_matching_columns(df, prefix):
            return [col for col in df.columns if str(col).startswith(prefix)]

        def get_matching_rows(df, prefix):
            return [idx for idx in df.index if str(idx).startswith(prefix)]

        cols = get_matching_columns(df, prefix_col)
        rows = get_matching_rows(df, prefix_row)

        if cols and rows:
            matrix = df.loc[rows, cols]
            if matrix.isna().any().any():

                cols_alt = get_matching_columns(df, prefix_row)
                rows_alt = get_matching_rows(df, prefix_col)

                if cols_alt and rows_alt:
                    matrix_alt = df.loc[rows_alt, cols_alt]
                    return matrix_alt
                else:
                    return None
            else:
                return matrix.T

        cols_alt = get_matching_columns(df, prefix_row)
        rows_alt = get_matching_rows(df, prefix_col)

        if cols_alt and rows_alt:
            matrix = df.loc[rows_alt, cols_alt]
            return matrix

        return None

    df = findmatrix_df(file_path)
    print(df)

    rows_names = df.index
    colum_names = df.columns

    all_names = list(colum_names) + list(rows_names)

    codes_only = [col.split()[0] for col in all_names]

    def sort_key(code):
        prefix, suffix = code.split('.')
        main_num = int(prefix[1:])
        sub_num = int(suffix)
        return (-main_num, sub_num)

    unique_codes = sorted(codes_only, key=sort_key)
    unique_codes = list(dict.fromkeys(unique_codes))



    dictionary = unique_codes
    print("sdads")
    print(dictionary)
    print("sdads")


    for i, (key, value) in enumerate(matrices.items()):
        matrix = findmatrix(df, dictionary[key[0]],dictionary[key[1]])

        matrices_list[i] = matrix.to_numpy()

    for comb in unique_combinations:
        matrices[comb] = matrices_list[unique_combinations.index(comb)]



    print("amount of elements",len(list(product(*matrica))))
    parameter_values_combinations = list(product(*matrica))
    combination_dict = {comb: round(float(np.prod(comb)), 7) for comb in parameter_values_combinations}

    p_matrix = [(float(np.prod(comb))) for comb in parameter_values_combinations]


    index_ranges = [range(len(lst)) for lst in matrica]
    index_combinations = list(product(*index_ranges))

    c_matrix = []

    for combs in index_combinations:
        temp = 1
        for key,value in matrices.items():
            temp *= 1+(value[combs[key[0]]][combs[key[1]]])
        c_matrix.append(temp)


    pc_product = [p*c for p,c in zip(p_matrix,c_matrix)]

    pc_sum = sum(pc_product)

    pc_product_norm = [pc_product/pc_sum for pc_product in pc_product]

    matrica_recalc = copy.deepcopy(matrica)
    matrica_recalc = [[0] * len(sublist) for sublist in matrica_recalc]

    for param_tuple in range(len(index_combinations)):
        for item in range(len(index_combinations[param_tuple])):
            matrica_recalc[item][index_combinations[param_tuple][item]] += pc_product_norm[param_tuple]

    


def search_r(pc):



    return

def matrixchoose(matrica_, file_path):
    matrica = matrica_


    file = file_path

    search_c(matrica, file)

matrixchoose([[0.5, 0.3, 0.2],
                  [0.4, 0.3, 0.3],
                  [0.5, 0.25, 0.25],
                  [0.3, 0.4, 0.3],
                  [0.2, 0.2, 0.2, 0.2, 0.2],
                  [0.3, 0.4, 0.3],
                  [0.3, 0.4, 0.3]], "C:\\Users\\maks\\Desktop\\Диплом\\Tables\\1_Промислові_викиди.xlsx")