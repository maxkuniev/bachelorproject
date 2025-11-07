import numpy as np
import pandas as pd
from itertools import combinations
from itertools import product
from pprint import pprint
import copy
from itertools import zip_longest
from collections import defaultdict

def search_c(matrica, dfstart):


    unique_combinations = list(combinations(range(len(matrica)), 2))

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

    df = dfstart

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

    transposed = list(zip_longest(*matrica, fillvalue=np.nan))
    dftest = pd.DataFrame(transposed, columns=dictionary)
    df_named = dftest.copy().astype("object")
    for row_idx in dftest.index:
        for col in dftest.columns:
            if not pd.isna(dftest.at[row_idx, col]):
                df_named.at[row_idx, col] = f"{col}.{row_idx + 1}"
            else:
                df_named.at[row_idx, col] = np.nan

    df_transposed_clean = df_named.T.dropna(how='all', axis=1)

    clean_matrix = [
        [item for item in row if not pd.isna(item)]
        for row in df_transposed_clean.values.tolist()
    ]

    unique_combinations_names = list(product(*clean_matrix))


    for i, (key, value) in enumerate(matrices.items()):
        matrix = findmatrix(df, dictionary[key[0]],dictionary[key[1]])
        matrices_list[i] = matrix.to_numpy()

    for comb in unique_combinations:
        matrices[comb] = matrices_list[unique_combinations.index(comb)]


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



    for lst in matrica_recalc:
        print(sum(lst))

    return matrica_recalc, unique_combinations_names, pc_product_norm

def search_r(pc, comb, matrixes, rows, cols):
    dfall = []
    for i in range(len(matrixes)):
        df=pd.DataFrame(matrixes[i], columns = cols[i], index = rows[i])
        dfall.append(df)
    sumstables = []
    for i in range(len(dfall)):
        tempdf = dfall[i]
        tempcomb = comb[i]
        pcnormtemp = pc[i]
        finalsums = splitdf(tempdf, tempcomb, pcnormtemp)
        sumstables.append(finalsums)

    return sumstables



def splitdf(df, combination, pc):
    sub_dfs = {}
    for col in df.columns:
        parts = col.split('.')
        group_key = parts[1]

        if group_key not in sub_dfs:
            sub_dfs[group_key] = []
        sub_dfs[group_key].append(col)

    result = {}

    for key, cols in sub_dfs.items():
        result[key] = df[cols]
    sums_all = []
    for i in range(len(result)):
        dfr, sums = findr(result[f'{i+1}'], combination, pc)
        sums_all.append(sums)

    return sums_all


def findr(df, combination, pc):
    columns = df.columns
    dfr = pd.DataFrame(columns=columns)

    raw_r = []

    for i, config in enumerate(combination):
        r_config = []
        for col in columns:
            value_product = 1
            for row in config:
                value = df.loc[row, col]
                value_product *= (1 + float(value))

            r_config.append(value_product)
        raw_r.append(r_config)

    raw_r_df = pd.DataFrame(raw_r, columns=columns)

    normalized_r_df = raw_r_df.div(raw_r_df.sum(axis=1), axis=0)

    for idx, col in enumerate(columns):
        dfr[col] = normalized_r_df[col] * pc

    sums = dfr.sum()
    return dfr, sums

def matrixchoose(matrica_, df):
    return search_c(matrica_, df)

def search_c_null(matrica, rowsnas):

    unique_combinations = list(combinations(range(len(matrica)), 2))


    matrices = {}

    matrices_list = []
    for comb in unique_combinations:
        list1 = matrica[comb[0]]
        list2 = matrica[comb[1]]
        matrix = np.zeros((len(list1), len(list2)))
        matrices[comb] = matrix
        matrices_list.append(matrix)

    for comb in unique_combinations:
        matrices[comb] = matrices_list[unique_combinations.index(comb)]


    parameter_values_combinations = list(product(*matrica))

    p_matrix = [(float(np.prod(comb))) for comb in parameter_values_combinations]

    index_ranges = [range(len(lst)) for lst in matrica]
    index_combinations = list(product(*index_ranges))

    c_matrix = []

    for combs in index_combinations:
        temp = 1
        for key, value in matrices.items():
            temp *= 1 + (value[combs[key[0]]][combs[key[1]]])
        c_matrix.append(temp)

    pc_product = [p * c for p, c in zip(p_matrix, c_matrix)]

    pc_sum = sum(pc_product)

    pc_product_norm = [pc_product / pc_sum for pc_product in pc_product]

    matrica_recalc = copy.deepcopy(matrica)
    matrica_recalc = [[0] * len(sublist) for sublist in matrica_recalc]

    for param_tuple in range(len(index_combinations)):
        for item in range(len(index_combinations[param_tuple])):
            matrica_recalc[item][index_combinations[param_tuple][item]] += pc_product_norm[param_tuple]

    grouped = defaultdict(list)

    for item in rowsnas:
        prefix = '.'.join(item.split('.')[:2])
        grouped[prefix].append(item)

    result = list(grouped.values())

    unique_combinations_names = list(product(*result))

    return matrica_recalc, pc_product_norm, unique_combinations_names