import time
from pysat.formula import CNF
from pysat.solvers import Solver
import itertools
from itertools import combinations
from collections import Counter
from pysat.solvers import Glucose3

ids = ['313329666', '206330342']
PRE = 0
ADD = 1
DEL = 2
WITHOUT_QUESTION_MARK = 0
WITH_QUESTION_MARK = 1


def is_valid(coordinate, max_row, max_col):
    if 0 <= coordinate[0] < max_row and 0 <= coordinate[1] < max_col:
        return True
    return False


def create_symbols(b, n_rows, n_cols):
    symbol_dict = {}
    status_action_list = ['H', 'S', 'I', 'U', 'Q', 'q', 'v']
    counter = 1
    for sa in status_action_list:
        symbol_dict[sa] = []
        x = b
        if sa == 'q' or sa == 'v':
            x = b - 1
        for t in range(x):
            symbol_dict[sa].append([])
            for i in range(n_rows):
                symbol_dict[sa][t].append([])
                for j in range(n_cols):
                    symbol_dict[sa][t][i].append(counter)
                    counter += 1
    return symbol_dict, counter


def update_known_stat(t, i, j, symbol_dict, cur_stat, b):
    temp_cnf = CNF()
    U_flag = 1
    if cur_stat != 'U':
        U_flag = -1
    for k in range(b):
        temp_cnf.append([U_flag * symbol_dict['U'][k][i][j]])
    if cur_stat == 'I':
        for k in range(t, b):
            temp_cnf.append([symbol_dict['I'][k][i][j]])
    if cur_stat != 'U' and cur_stat != 'I':
        temp_cnf.append([symbol_dict[cur_stat][t][i][j]])
    return temp_cnf


def update_count_actions_dicts(count_H_S_dict, possible_actions_tiles, t, i, j, cur_stat):
    # Update count_H_S_dict
    if cur_stat == '?':
        count_H_S_dict['H'][t][WITH_QUESTION_MARK] += 1
        count_H_S_dict['S'][t][WITH_QUESTION_MARK] += 1
    elif cur_stat == 'H' or cur_stat == 'S':
        count_H_S_dict[cur_stat][t][WITHOUT_QUESTION_MARK] += 1
        count_H_S_dict[cur_stat][t][WITH_QUESTION_MARK] += 1

    # Update possible_actions_tiles
    if cur_stat == 'S' or cur_stat == '?':
        possible_actions_tiles['q'][t].add((i, j))
    if cur_stat == 'H' or cur_stat == '?':
        possible_actions_tiles['v'][t].add((i, j))


def single_status(symbol_dict, t, i, j):
    # Add single status constraints
    """
    Updating cnf by adding clauses according to the following rules:
    1. each tile at time t has at least one status (or_temp_clause)
    2. each tile at time t has at most one status (implies_temp_caluse)
    """
    status_list = ['H', 'S', 'I', 'Q', 'U']
    temp_cnf = CNF()
    or_temp_clause = []
    for status in status_list:
        or_temp_clause.append(symbol_dict[status][t][i][j])
        different_statuses = [s for s in status_list if s != status]
        for ds in different_statuses:
            temp_cnf.append([-symbol_dict[status][t][i][j], -symbol_dict[ds][t][i][j]])

    temp_cnf.append(or_temp_clause)
    return temp_cnf


def immune_quarantine_axioms(symbol_dict, b, t, i, j):
    # If at time t (i,j) is I, then exits k<t such that v(i,j) at k
    clause = []
    for k in range(min(t, b - 1)):
        clause.append(symbol_dict['v'][k][i][j])
    clause.append(-symbol_dict['I'][t][i][j])
    I_Q_clause = CNF()
    I_Q_clause.append(clause)

    # Add Q axiom
    if t >= 1:
        if t < b - 1:
            I_Q_clause.extend(
                [[-symbol_dict['Q'][t][i][j], symbol_dict['Q'][t - 1][i][j], symbol_dict['S'][t - 1][i][j]],
                 [-symbol_dict['Q'][t][i][j], symbol_dict['Q'][t - 1][i][j], symbol_dict['q'][t - 1][i][j]]])
        else:
            I_Q_clause.append([-symbol_dict['Q'][t][i][j], symbol_dict['Q'][t - 1][i][j]])

    return I_Q_clause


def actions_clauses(symbol_dict, t, i, j, actions_dict):
    symbol_v = symbol_dict['v'][t][i][j]
    # Precondition for vaccinate
    pre_v = [-symbol_v, symbol_dict['H'][t][i][j]]
    # Add for vaccinate
    add_v = [-symbol_v, symbol_dict['I'][t + 1][i][j]]
    # Del for vaccinate
    del_v = [-symbol_v, -symbol_dict['H'][t + 1][i][j]]

    symbol_q = symbol_dict['q'][t][i][j]
    # Precondition for quarantine
    pre_q = [-symbol_q, symbol_dict['S'][t][i][j]]
    # Add for quarantine
    add_q = [-symbol_q, symbol_dict['Q'][t + 1][i][j]]
    # Del for quarantine
    del_q = [-symbol_q, -symbol_dict['S'][t + 1][i][j]]

    actions_dict[symbol_v] = (
        symbol_dict['H'][t][i][j], symbol_dict['I'][t + 1][i][j], symbol_dict['H'][t + 1][i][j])
    actions_dict[symbol_q] = (
        symbol_dict['S'][t][i][j], symbol_dict['Q'][t + 1][i][j], symbol_dict['S'][t + 1][i][j])

    clause = CNF(from_clauses=[pre_v, add_v, del_v, pre_q, add_q, del_q])
    return clause


def create_KB(observations, symbol_dict, b, n_rows, n_cols):
    KB = CNF()
    count_H_S_dict = {'H': [], 'S': []}
    possible_actions_tiles = {'q': [], 'v': []}
    action_effects_dict = {}
    for t in range(b):
        # Start new H_S count for t
        count_H_S_dict['H'].append([0, 0])
        count_H_S_dict['S'].append([0, 0])
        # Start new q_v tile list for t
        possible_actions_tiles['q'].append(set())
        possible_actions_tiles['v'].append(set())
        for i in range(n_rows):
            for j in range(n_cols):
                cur_stat = observations[t][i][j]
                if cur_stat != '?':
                    # Add known status
                    KB.extend(update_known_stat(t, i, j, symbol_dict, cur_stat, b))
                # Update count_H_S and possible_actions dicts
                update_count_actions_dicts(count_H_S_dict, possible_actions_tiles, t, i, j, cur_stat)
                #  Add single status constraints
                KB.extend(single_status(symbol_dict, t, i, j))
                # Add I, Q axioms + at t=0 no Q or I
                KB.extend(immune_quarantine_axioms(symbol_dict, b, t, i, j))
                if t == 0:
                    KB.append([-symbol_dict['Q'][t][i][j]])
                    KB.append([-symbol_dict['I'][t][i][j]])
                # Add actions effects and precondtions clauses
                if t < b - 1:
                    KB.extend(actions_clauses(symbol_dict, t, i, j, action_effects_dict))
                    # Single actions
                    KB.append([-symbol_dict['q'][t][i][j], -symbol_dict['v'][t][i][j]])
                    KB.append([-symbol_dict['v'][t][i][j], -symbol_dict['q'][t][i][j]])
    return KB, count_H_S_dict, possible_actions_tiles, action_effects_dict


#
# def is_unpopulated_immune(observations, t, i, j, b):
#     for k in range(b):
#         if observations[k][i][j] == 'U' or (k <= t and observations[k][i][j] == 'I'):
#             return True
#     return False
#
#
# def check_valid_action(sub_action, observations, t, i, j, b):
#     cur_cord = observations[t][i][j]
#     if sub_action is None:
#         return True
#     elif sub_action == 'v' and cur_cord != 'H' and \
#             cur_cord == '?' and is_unpopulated_immune(observations, t, i, j, b):
#         return False
#     elif sub_action == 'q' and cur_cord != 'S' and \
#             cur_cord == '?' and is_unpopulated_immune(observations, t, i, j, b):
#         return False
#     return True
#
#
# def action_to_conjunction_and_axioms(cnf, locs, action, t, symbol_dict, actions_dict, observations, b):
#     proposition_not_in_del = []  # a.k.a p(t)
#     proposition_not_in_del_next_time = []  # a.k.a p(t+1)
#     proposition_not_in_add = []  # a.k.a p(t)
#     proposition_not_in_add_next_time = []  # a.k.a p(t+1)
#     all_sub_actions_clause = []
#     action_symbol_list = []
#     temp_cnf = cnf
#     for loc, sub_action in zip(locs, action):
#         i = loc[0]
#         j = loc[1]
#         if not check_valid_action(sub_action, observations, t, i, j, b):
#             return False, cnf, action_symbol_list
#         if sub_action is None:
#             # all_sub_actions_clause = all_sub_actions_clause | symbol_dict['q'][t][i][j] | symbol_dict['v'][t][i][j]
#             all_sub_actions_clause.append(symbol_dict['q'][t][i][j])
#             all_sub_actions_clause.append(symbol_dict['v'][t][i][j])
#             action_symbol_list.append(-symbol_dict['q'][t][i][j])
#             action_symbol_list.append(-symbol_dict['v'][t][i][j])
#         else:
#             # all_sub_actions_clause = all_sub_actions_clause | ~symbol_dict[sub_action][t][i][j]
#             all_sub_actions_clause.append(-symbol_dict[sub_action][t][i][j])
#             action_symbol_list.append(symbol_dict[sub_action][t][i][j])
#
#     #     proposition_not_in_del, proposition_not_in_del_next_time, proposition_not_in_add, \
#     #     proposition_not_in_add_next_time = update_not_in_action_effects(sub_action, symbol_dict, actions_dict, t,
#     #                                                                     proposition_not_in_del,
#     #                                                                     proposition_not_in_del_next_time,
#     #                                                                     proposition_not_in_add,
#     #                                                                     proposition_not_in_add_next_time, i, j)
#     #
#     # for pt1, pt2 in zip(proposition_not_in_del, proposition_not_in_del_next_time):
#     #     status, time, row, col = str(pt1).split('_')
#     #     if status == 'H':
#     #         clause = all_sub_actions_clause | ~pt1 | (pt2 | symbol_dict['S'][int(time) + 1][int(row)][int(col)])
#     #     elif status == 'S':
#     #         clause = all_sub_actions_clause | ~pt1 | (pt2 | symbol_dict['H'][int(time) + 1][int(row)][int(col)])
#     #     elif status == 'Q':
#     #         clause = all_sub_actions_clause | ~pt1 | (pt2 | symbol_dict['H'][int(time) + 1][int(row)][int(col)])
#     #     else:
#     #         clause = all_sub_actions_clause | ~pt1 | pt2
#     #     temp_cnf = temp_cnf & clause
#     #
#     # for pt1, pt2 in zip(proposition_not_in_add, proposition_not_in_add_next_time):
#     #     status, time, row, col = str(pt1).split('_')
#     #     if status != 'S' and status != 'H':
#     #         clause = all_sub_actions_clause | pt1 | ~pt2
#     #         temp_cnf = temp_cnf & clause
#     #
#     # cnf = cnf & temp_cnf
#     return all_sub_actions_clause, cnf, action_symbol_list
#
#
# def positive_negative_frame_axioms_and_linearity(n_rows, n_cols, b, symbol_dict, actions_effects_dict, medics, police,
#                                                  count_H_S_dict, observations, biggest_symbol, possible_action_tiles):
#     cnf = CNF()
#     symbol_dict['flags'] = []
#     curr_biggest_symbol = biggest_symbol
#     # create list of all locations:
#     locs = []
#     for i in range(n_rows):
#         for j in range(n_cols):
#             locs.append((i, j))
#
#     temp_cnf = CNF()
#     # linearity and axioms
#     for t in range(b - 1):
#         lower_q = min(police, count_H_S_dict['S'][t][WITHOUT_QUESTION_MARK])
#         upper_q = min(police, count_H_S_dict['S'][t][WITH_QUESTION_MARK])
#         lower_v = min(medics, count_H_S_dict['H'][t][WITHOUT_QUESTION_MARK])
#         upper_v = min(medics, count_H_S_dict['H'][t][WITH_QUESTION_MARK])
#         or_temp_clause = []
#         possible_actions_clauses_dict = {}
#         symbol_dict['flags'].append([])
#         for action in itertools.product(['v', 'q', None], repeat=len(locs)):
#             counter = Counter(action)
#             if lower_q <= counter['q'] <= upper_q and lower_v <= counter['v'] <= upper_v:
#                 symbol_dict['flags'][t].append(curr_biggest_symbol)
#                 curr_biggest_symbol += 1
#                 iff_action_flag_implied = [symbol_dict['flags'][t][-1]]
#                 iff_action_flag_implies = []
#                 not_all_sub_actions_clause, temp_cnf, action_symbol_list = action_to_conjunction_and_axioms(temp_cnf,
#                                                                                                             locs,
#                                                                                                             action, t,
#                                                                                                             symbol_dict,
#                                                                                                             actions_effects_dict,
#                                                                                                             observations,
#                                                                                                             b)
#                 if not not_all_sub_actions_clause:
#                     continue
#
#                 for sym in action_symbol_list:
#                     iff_action_flag_implied.append(-sym)
#                     iff_action_flag_implies.append([-symbol_dict['flags'][t][-1], sym])
#
#                 temp_cnf.extend(iff_action_flag_implies)
#                 temp_cnf.append(iff_action_flag_implied)
#                 possible_actions_clauses_dict[action] = not_all_sub_actions_clause
#                 or_temp_clause.append(symbol_dict['flags'][t][-1])
#
#         cnf.extend(temp_cnf)
#         for (not_action_clause_1, not_action_clause_2) in itertools.combinations(possible_actions_clauses_dict.values(),
#                                                                                  2):
#             cnf.extend([not_action_clause_1, not_action_clause_2])
#
#         cnf.append(or_temp_clause)
#
#     return cnf


def force_only_one(flags):
    or_temp = []
    cnf = CNF()
    for f1 in flags:
        or_temp.append(f1)
        for f2 in flags:
            if f1 != f2:
                cnf.append([-f1, -f2])
    cnf.append(or_temp)
    return cnf


def action_to_cnf(locs, tiles_to_v, tiles_to_q, flag_symbol, symbol_dict, t):
    """
    :param locs: all locs in map
    :param tiles_to_v: tiles to operate v
    :param tiles_to_q: tiles to operate q
    :param flag_symbol: flag for iff action is happening
    :param symbol_dict:
    :param t: current time
    :return: Create iff clause between a flag and set of actions cnf from tiles
    """
    # cls = ((a >> (b1 & b2 & b3)) & ((b1 & b2 & b3) >> a))
    # (b1 | ~a) & (b2 | ~a) & (b3 | ~a) & (a | ~b1 | ~b2 | ~b3)
    q_v_noop_clause_implies_flag = []
    flag_implies_q_v_noop_clause = [flag_symbol]
    for loc_to_q in tiles_to_q:
        i = loc_to_q[0]
        j = loc_to_q[1]
        flag_implies_q_v_noop_clause.append(-symbol_dict['q'][t][i][j])
        q_v_noop_clause_implies_flag.append([-flag_symbol, symbol_dict['q'][t][i][j]])
    for loc_to_v in tiles_to_v:
        i = loc_to_v[0]
        j = loc_to_v[1]
        flag_implies_q_v_noop_clause.append(-symbol_dict['v'][t][i][j])
        q_v_noop_clause_implies_flag.append([-flag_symbol, symbol_dict['v'][t][i][j]])
    for loc_to_noop in locs - tiles_to_v - tiles_to_q:
        i = loc_to_noop[0]
        j = loc_to_noop[1]

        flag_implies_q_v_noop_clause.append(symbol_dict['q'][t][i][j])
        flag_implies_q_v_noop_clause.append(symbol_dict['v'][t][i][j])

        q_v_noop_clause_implies_flag.append([-flag_symbol, -symbol_dict['q'][t][i][j]])
        q_v_noop_clause_implies_flag.append([-flag_symbol, -symbol_dict['v'][t][i][j]])

    cnf = CNF(from_clauses=[flag_implies_q_v_noop_clause])
    cnf.extend(q_v_noop_clause_implies_flag)

    return cnf


def positive_negative_frame_axioms_and_linearity(n_rows, n_cols, b, symbol_dict, actions_effects_dict, medics, police,
                                                 count_H_S_dict, biggest_symbol, possible_action_tiles):
    symbol_dict['flags'] = []
    curr_biggest_symbol = biggest_symbol + 1
    # create list of all locations:
    locs = set()
    for i in range(n_rows):
        for j in range(n_cols):
            locs.add((i, j))

    linearity_cnf = CNF()
    # linearity
    for t in range(b - 1):
        lower_q = min(police, count_H_S_dict['S'][t][WITHOUT_QUESTION_MARK])
        upper_q = min(police, count_H_S_dict['S'][t][WITH_QUESTION_MARK])
        lower_v = min(medics, count_H_S_dict['H'][t][WITHOUT_QUESTION_MARK])
        upper_v = min(medics, count_H_S_dict['H'][t][WITH_QUESTION_MARK])
        symbol_dict['flags'].append([])
        for q_runner in range(lower_q, upper_q + 1):
            for v_runner in range(lower_v, upper_v + 1):
                # Choose from every possible tile in possible_action_tiles
                for tiles_to_q in itertools.combinations(possible_action_tiles['q'][t], q_runner):
                    for tiles_to_v in itertools.combinations(possible_action_tiles['v'][t], v_runner):
                        # Add new symbol to flag an action
                        symbol_dict['flags'][t].append(curr_biggest_symbol)
                        cur_op_iff_flag = action_to_cnf(locs, set(tiles_to_v), set(tiles_to_q), curr_biggest_symbol, symbol_dict, t)
                        curr_biggest_symbol += 1
                        linearity_cnf.extend(cur_op_iff_flag)

        force_one_action_cnf = force_only_one(symbol_dict['flags'][t])
        linearity_cnf.extend(force_one_action_cnf)

    return linearity_cnf


# def force(t, symbol_dict, flag_symbol, operation, to_op, not_to_op, locs):
#     states_mapper = {
#         'v': 'H',
#         'q': 'S'
#     }
#     state = states_mapper[operation]
#     flag_implies_clause = []
#     and_implies_flag_clause = [flag_symbol]
#
#     for l in to_op:
#         i, j = l[0], l[1]
#         flag_implies_clause.append([-flag_symbol, symbol_dict[state][t][i][j]])
#         flag_implies_clause.append([-flag_symbol, symbol_dict[operation][t][i][j]])
#         and_implies_flag_clause.append(-symbol_dict[operation][t][i][j])
#         and_implies_flag_clause.append(-symbol_dict[state][t][i][j])
#         # configuration_clause = configuration_clause & symbol_dict[state][t][i][j] & symbol_dict[operation][t][i][j]
#     for l in not_to_op:
#         i, j = l[0], l[1]
#         flag_implies_clause.append([-flag_symbol, symbol_dict[state][t][i][j]])
#         flag_implies_clause.append([-flag_symbol, -symbol_dict[operation][t][i][j]])
#         and_implies_flag_clause.append(symbol_dict[operation][t][i][j])
#         and_implies_flag_clause.append(-symbol_dict[state][t][i][j])  # TODO: maybe not necessary
#
#         # configuration_clause = configuration_clause & symbol_dict[state][t][i][j] & ~symbol_dict[operation][t][i][j]
#     for l in set(locs) - to_op - not_to_op:
#         i, j = l[0], l[1]
#         flag_implies_clause.append([-flag_symbol, -symbol_dict[state][t][i][j]])
#         and_implies_flag_clause.append(symbol_dict[state][t][i][j])  # TODO: maybe not necessary
#
#         # configuration_clause = configuration_clause & ~symbol_dict[state][t][i][j]
#
#     cnf = CNF(from_clauses=flag_implies_clause)
#     cnf.append(and_implies_flag_clause)
#     return cnf
#
#
# def number_of_actions_constraints(n_rows, n_cols, b, symbol_dict, operation, allowed, biggest_symbol):
#     # create list of all locations:
#     cnf = CNF()
#     locs = []
#     locs_num = 0
#     for i in range(n_rows):
#         for j in range(n_cols):
#             locs.append((i, j))
#             locs_num += 1
#
#     serial = biggest_symbol + 1
#     for t in range(b - 1):
#         flags = []
#         # print('start first leg of time {}'.format(t))
#         # configurations where number of teams available is enough to operate on all legal locs
#         for i in range(allowed + 1):  # todo
#             for locs_to_op in combinations(locs, i):
#                 # flag_sign = str(t) + str(i) + str(serial)
#                 temp_cnf = force(t, symbol_dict, serial, operation, set(locs_to_op), set(), locs)
#                 cnf.extend(temp_cnf)
#                 flags.append(serial)
#                 serial += 1
#
#         # print('start second leg of time {}'.format(t))
#         # configurations where number of teams available is NOT enough to operate on all legal locs
#         for legal_num in range(allowed + 1, locs_num):
#             for total in combinations(locs, legal_num):
#                 for to_op in combinations(total, allowed):
#                     not_to_op = set(total) - set(to_op)
#                     # flag_sign = str(t) + str(i) + str(serial)
#                     temp_cnf = force(t, symbol_dict, serial, operation,
#                                       set(to_op), not_to_op, locs)
#                     cnf.extend(temp_cnf)
#                     flags.append(serial)
#                     serial += 1
#
#         cnf.extend(force_only_one(flags))
#
#     return cnf, serial


def spread_healing_clauses(n_rows, n_cols, b, symbol_dict):
    """
    Adding spread clauses to cnf (Sick coordinate implies that it was sick at t-1 or it got infected by one of its neighbors)
    :return:
    """
    backward_healing_cnf = CNF()
    backward_spread_cnf = CNF()
    for t in range(b):
        for i in range(n_rows):
            for j in range(n_cols):
                # Backward spread
                not_sick_at_t = -symbol_dict['S'][t][i][j]
                sick_t_minus_1 = [symbol_dict['S'][t - 1][i][j], -symbol_dict['q'][t - 1][i][j]]  # S and not q
                sick_neighbors = []
                neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
                for neighbor in neighbors:
                    if is_valid(neighbor, n_rows, n_cols):
                        sick_neighbors.append([symbol_dict['H'][t - 1][i][j], -symbol_dict['v'][t - 1][i][j],
                                               symbol_dict['S'][t - 1][neighbor[0]][neighbor[1]],
                                               -symbol_dict['q'][t - 1][neighbor[0]][
                                                   neighbor[1]]])  # OR between neighbors if S and not q

                for symbol_prod in itertools.product(sick_t_minus_1, *sick_neighbors):
                    backward_spread_cnf.append(list(symbol_prod) + [not_sick_at_t])

                # Backward healing
                if t > 2:
                    k = symbol_dict['H'][t][i][j]
                    a = symbol_dict['H'][t - 1][i][j]
                    e = symbol_dict['v'][t - 1][i][j]
                    c = symbol_dict['S'][t - 1][i][j]
                    d = symbol_dict['S'][t - 3][i][j]
                    x = symbol_dict['S'][t - 2][i][j]
                    y = symbol_dict['q'][t - 1][i][j]
                    z = symbol_dict['Q'][t - 1][i][j]
                    w = symbol_dict['Q'][t - 2][i][j]
                    backward_healing_cnf.extend([[a, c, w, -k], [a, c, z, -k], [a, d, w, -k], [a, d, z, -k],
                                                 [a, w, x, -k], [a, x, z, -k], [a, w, -k, -y], [a, z, -k, -y],
                                                 [c, w, -e, -k], [c, z, -e, -k], [d, w, -e, -k], [d, z, -e, -k],
                                                 [w, x, -e, -k], [x, z, -e, -k], [w, -e, -k, -y], [z, -e, -k, -y]])

                elif t > 0:
                    backward_healing_cnf.append([-symbol_dict['H'][t][i][j], symbol_dict['H'][t - 1][i][j]])
                    backward_healing_cnf.append([-symbol_dict['H'][t][i][j], -symbol_dict['v'][t - 1][i][j]])

    backward_healing_cnf.extend(backward_spread_cnf)
    return backward_healing_cnf


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
    KB, count_H_S_dict, possible_actions_tiles, action_effects_dict = create_KB(observations, symbol_dict, b, n_rows,
                                                                                n_cols)
    KB.extend(spread_healing_clauses(n_rows, n_cols, b, symbol_dict))
    KB.extend(positive_negative_frame_axioms_and_linearity(n_rows, n_cols, b, symbol_dict, action_effects_dict, medics, police,
                                                 count_H_S_dict, biggest_symbol, possible_actions_tiles))

    res = {}
    statuses = ['H', 'Q', 'U', 'S', 'I']

    # s = Solver(bootstrap_with=KB)
    # print(s.solve())
    # g = Glucose3(bootstrap_with=KB.clauses)
    # print(g.propagate())

    for q in queries:
        status = q[2]
        t = q[1]
        loc = q[0]
        i = loc[0]
        j = loc[1]
        q_symbol = symbol_dict[status][t][i][j]
        q_cnf = KB
        q_cnf.append([q_symbol])
        g = Glucose3(bootstrap_with=q_cnf.clauses)
        if not g.propagate()[0]:
            res[tuple(q)] = 'F'
        else:
            for s in statuses:
                if s != status:
                    q_cnf = KB
                    q_cnf.append([symbol_dict[s][t][i][j]])
                    g = Glucose3(bootstrap_with=q_cnf.clauses)
                    if g.propagate()[0]:
                        res[tuple(q)] = '?'
                        print(s)
                        # break
        if q not in res.keys():
            res[tuple(q)] = 'T'

    return res