from pysat.formula import CNF
import itertools
from collections import Counter

ids = ['313329666', '206330342']


def create_symbols(b, n_rows, n_cols):
    symbol_dict = {}
    status_action_list = ['H', 'S', 'I', 'U', 'Q', 'q', 'v']
    counter = 1
    for sa in status_action_list:
        symbol_dict[sa].append([])
        x = b
        if sa == 'q' or sa == 'v':
            x = b -1
        for t in range(x):
            symbol_dict[sa][t].append([])
            for i in range(n_rows):
                symbol_dict[sa][t][i].append([])
                for j in range(n_cols):
                    symbol_dict[sa][t][i][j].append(counter)
                    counter += 1
    return symbol_dict, counter


def update_known_stat(KB, t, i, j, symbol_dict, cur_stat, b):
    U_flag = 1
    if cur_stat != 'U':
        U_flag = -1
    for k in range(b):
        KB.append([U_flag*symbol_dict[k][i][j]])
    if cur_stat == 'I':
        for k in range(t, b):
            KB.append(symbol_dict[k][i][j])
    if cur_stat != 'U' and cur_stat != 'I':
        KB.append(symbol_dict[t][i][j])


def create_KB(observations, police, medics, symbol_dict, b, n_rows, n_cols):
    KB = CNF()
    for t in range(b):
        for i in range(n_rows):
            for j in range(n_cols):
                cur_stat = observations[t][i][j]
                if cur_stat != '?':
                    update_known_stat(KB, t, i, j, symbol_dict, cur_stat, b)
    return KB


def solve_problem(input):
    # parse input:
    police = input["police"]
    medics = input["medics"]
    observations = input["observations"]
    queries = input["queries"]
    b = len(observations)
    n_rows = len(observations[0])
    n_cols = len(observations[0][0])

    symbol_dict, biggest_symbol = create_symbols(b, n_rows, n_cols)
    cnf = create_KB(observations, police, medics, symbol_dict, n_rows, n_cols)
