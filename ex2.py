from pysat.formula import CNF
from pysat.solvers import Solver
import itertools

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


def update_known_stat(t, i, j, symbol_dict, b):
    temp_cnf = CNF()
    for k in range(b):
        temp_cnf.append([-symbol_dict['U'][t][i][j], symbol_dict['U'][k][i][j]])
        temp_cnf.append([symbol_dict['U'][t][i][j], -symbol_dict['U'][k][i][j]])
    for k in range(t, b):
        temp_cnf.append([-symbol_dict['I'][t][i][j], symbol_dict['I'][k][i][j]])

    return temp_cnf


def update_count_actions_dicts(count_H_S_dict, possible_actions_tiles, t, i, j, cur_stat, next_stat):
    # Update count_H_S_dict
    if cur_stat == '?':
        count_H_S_dict['H'][t][WITH_QUESTION_MARK] += 1
        count_H_S_dict['S'][t][WITH_QUESTION_MARK] += 1
    elif cur_stat == 'H' or cur_stat == 'S':
        count_H_S_dict[cur_stat][t][WITHOUT_QUESTION_MARK] += 1
        count_H_S_dict[cur_stat][t][WITH_QUESTION_MARK] += 1

    # Update possible_actions_tiles
    if (cur_stat == 'S' or cur_stat == '?') and (next_stat == 'Q' or next_stat == '?'):
        possible_actions_tiles['q'][t].add((i, j))
    if cur_stat == 'H' or cur_stat == '?' and (next_stat == 'I' or next_stat == '?'):
        possible_actions_tiles['v'][t].add((i, j))


def single_status(symbol_dict, t, i, j):
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

    # Add Q axiom: Q at t >> either Q at t-1 or (S at t-1 & q at t-1)
    if t >= 1:
        I_Q_clause.extend(
            [[-symbol_dict['Q'][t][i][j], symbol_dict['Q'][t - 1][i][j], symbol_dict['S'][t - 1][i][j]],
             [-symbol_dict['Q'][t][i][j], symbol_dict['Q'][t - 1][i][j], symbol_dict['q'][t - 1][i][j]]])

    return I_Q_clause


def actions_clauses(symbol_dict, t, i, j, actions_dict):
    clause = CNF()
    if (i,j) in actions_dict['v'][t]:
        symbol_v = symbol_dict['v'][t][i][j]
        # Precondition for vaccinate
        pre_v = [-symbol_v, symbol_dict['H'][t][i][j]]
        # Add for vaccinate
        add_v = [-symbol_v, symbol_dict['I'][t + 1][i][j]]
        # Del for vaccinate
        del_v = [-symbol_v, -symbol_dict['H'][t + 1][i][j]]
        clause.append(pre_v)
        clause.append(add_v)
        clause.append(del_v)

    if (i, j) in actions_dict['q'][t]:
        symbol_q = symbol_dict['q'][t][i][j]
        # Precondition for quarantine
        pre_q = [-symbol_q, symbol_dict['S'][t][i][j]]
        # Add for quarantine
        add_q = [-symbol_q, symbol_dict['Q'][t + 1][i][j]]
        # Del for quarantine
        del_q = [-symbol_q, -symbol_dict['S'][t + 1][i][j]]
        clause.append(pre_q)
        clause.append(add_q)
        clause.append(del_q)

    # clause = CNF(from_clauses=[pre_v, add_v, del_v, pre_q, add_q, del_q])
    return clause


def create_KB(observations, symbol_dict, b, n_rows, n_cols):
    KB = CNF()
    count_H_S_dict = {'H': [], 'S': []}
    possible_actions_tiles = {'q': [], 'v': []}
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
                    KB.append([symbol_dict[cur_stat][t][i][j]])
                KB.extend(update_known_stat(t, i, j, symbol_dict, b))
                # Update count_H_S and possible_actions dicts, actions take place only before b - 1
                if t < b - 1:
                    update_count_actions_dicts(count_H_S_dict, possible_actions_tiles, t, i, j, cur_stat,
                                               observations[t + 1][i][j])
                    # Add actions effects and precondtions clauses
                    KB.extend(actions_clauses(symbol_dict, t, i, j, possible_actions_tiles))
                    # Single actions
                    KB.append([-symbol_dict['q'][t][i][j], -symbol_dict['v'][t][i][j]])
                    KB.append([-symbol_dict['v'][t][i][j], -symbol_dict['q'][t][i][j]])

                #  Add single status constraints
                KB.extend(single_status(symbol_dict, t, i, j))
                # Add I, Q axioms + at t=0 no Q or I
                KB.extend(immune_quarantine_axioms(symbol_dict, b, t, i, j))
                if t == 0:
                    KB.append([-symbol_dict['Q'][t][i][j]])
                    KB.append([-symbol_dict['I'][t][i][j]])

    return KB, count_H_S_dict, possible_actions_tiles


def force_only_one(flags):
    or_temp = []
    cnf = CNF()
    l = len(flags)
    for i in range(l):
        f1 = flags[i]
        or_temp.append(f1)
        for j in range(i + 1, l):
            f2 = flags[j]
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


def linearity(n_rows, n_cols, b, symbol_dict, medics, police,
              count_H_S_dict, biggest_symbol, possible_action_tiles):
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
        flags = []
        for q_runner in range(lower_q, upper_q + 1):
            for v_runner in range(lower_v, upper_v + 1):
                # Choose from every possible tile in possible_action_tiles
                for p in itertools.product(
                        itertools.combinations(possible_action_tiles['q'][t], q_runner),
                        itertools.combinations(possible_action_tiles['v'][t], v_runner)):
                    tiles_to_q, tiles_to_v = p[0], p[1]

                    # Add new symbol to flag an action
                    flags.append(curr_biggest_symbol)
                    cur_op_iff_flag = action_to_cnf(locs, set(tiles_to_v), set(tiles_to_q), curr_biggest_symbol,
                                                    symbol_dict, t)
                    curr_biggest_symbol += 1
                    linearity_cnf.extend(cur_op_iff_flag)

        force_one_action_cnf = force_only_one(flags)
        linearity_cnf.extend(force_one_action_cnf)

    return linearity_cnf


def s_iff_have_sick_neighbor(n_rows, n_cols, symbol_dict, t, s, neighbors):
    sick_neighbors = []
    flag_implies_sick_neighbor_clause = []
    sick_neighbors_implies_flag_clause = []
    for neighbor in neighbors:
        if is_valid(neighbor, n_rows, n_cols):
            sick_neighbors.append([symbol_dict['S'][t - 1][neighbor[0]][neighbor[1]],
                                   -symbol_dict['q'][t - 1][neighbor[0]][neighbor[1]]])
            sick_neighbors_implies_flag_clause.append([s, -symbol_dict['S'][t - 1][neighbor[0]][neighbor[1]],
                                                       symbol_dict['q'][t - 1][neighbor[0]][neighbor[1]]])

    for symbol_prod in itertools.product(*sick_neighbors):
        flag_implies_sick_neighbor_clause.append([-s] + list(symbol_prod))

    cnf = CNF()
    cnf.extend(flag_implies_sick_neighbor_clause)
    cnf.extend(sick_neighbors_implies_flag_clause)
    return cnf


def backward_healing(cur_symbol, symbol_dict, n_rows, n_cols, t, neighbors, i, j):
    cnf = CNF()
    s = cur_symbol
    s_iff_have_sick_neighbor_clause = s_iff_have_sick_neighbor(n_rows, n_cols, symbol_dict, t, s, neighbors)
    cnf.extend(s_iff_have_sick_neighbor_clause)
    k = symbol_dict['H'][t][i][j]
    a = symbol_dict['H'][t - 1][i][j]
    e = symbol_dict['v'][t - 1][i][j]
    c = symbol_dict['S'][t - 1][i][j]
    d = symbol_dict['S'][t - 3][i][j]
    x = symbol_dict['S'][t - 2][i][j]
    y = symbol_dict['q'][t - 1][i][j]
    z = symbol_dict['Q'][t - 1][i][j]
    w = symbol_dict['Q'][t - 2][i][j]

    cnf.extend([[a, c, w, -k], [a, c, z, -k], [a, d, w, -k], [a, d, z, -k],
                [a, w, x, -k], [a, x, z, -k], [a, w, -k, -y], [a, z, -k, -y], [c, w, -e, -k],
                [c, w, -k, -s], [c, z, -e, -k], [c, z, -k, -s], [d, w, -e, -k],
                [d, w, -k, -s], [d, z, -e, -k], [d, z, -k, -s], [w, x, -e, -k],
                [w, x, -k, -s], [x, z, -e, -k], [x, z, -k, -s], [w, -e, -k, -y],
                [w, -k, -s, -y], [z, -e, -k, -y], [z, -k, -s, -y]])

    return cnf


def forward_healing(symbol_dict, t, i, j):
    cnf = CNF()

    cnf.append([-symbol_dict['S'][t - 1][i][j], -symbol_dict['S'][t - 2][i][j], -symbol_dict['S'][t - 3][i][j],
                symbol_dict['q'][t - 1][i][j], symbol_dict['H'][t][i][j]])

    cnf.append([-symbol_dict['Q'][t - 1][i][j], -symbol_dict['Q'][t - 2][i][j], symbol_dict['H'][t][i][j]])

    return cnf


def spread_healing_clauses(n_rows, n_cols, b, symbol_dict, biggest_cur_symbol):
    """
    Adding spread clauses to cnf (Sick coordinate implies that it was sick at t-1 or it got infected by one of its neighbors)
    :return:
    """
    healing_cnf = CNF()
    backward_spread_cnf = CNF()
    cur_symbol = biggest_cur_symbol + 1
    for t in range(b):
        for i in range(n_rows):
            for j in range(n_cols):
                # Backward spread
                neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
                if t > 0:
                    not_sick_at_t = -symbol_dict['S'][t][i][j]
                    sick_t_minus_1 = [symbol_dict['S'][t - 1][i][j], -symbol_dict['q'][t - 1][i][j]]  # S and not q
                    sick_neighbors = []
                    for neighbor in neighbors:
                        if is_valid(neighbor, n_rows, n_cols):
                            sick_neighbors.append([symbol_dict['H'][t - 1][i][j], -symbol_dict['v'][t - 1][i][j],
                                                   symbol_dict['S'][t - 1][neighbor[0]][neighbor[1]],
                                                   -symbol_dict['q'][t - 1][neighbor[0]][
                                                       neighbor[1]]])  # OR between neighbors if S and not q

                    for symbol_prod in itertools.product(sick_t_minus_1, *sick_neighbors):
                        backward_spread_cnf.append(list(symbol_prod) + [not_sick_at_t])

                if t > 2:
                    healing_cnf.extend(backward_healing(cur_symbol, symbol_dict, n_rows, n_cols, t, neighbors, i, j))
                    healing_cnf.extend(forward_healing(symbol_dict, t, i, j))
                    cur_symbol += 1

                # Backward healing
                elif t == 1 or t == 2:
                    s = cur_symbol
                    s_iff_have_sick_neighbor_clause = s_iff_have_sick_neighbor(n_rows, n_cols, symbol_dict, t, s,
                                                                               neighbors)
                    healing_cnf.extend(s_iff_have_sick_neighbor_clause)
                    healing_cnf.append([-symbol_dict['H'][t][i][j], symbol_dict['H'][t - 1][i][j]])
                    healing_cnf.append([-symbol_dict['H'][t][i][j], -symbol_dict['v'][t - 1][i][j]])
                    healing_cnf.append([-symbol_dict['H'][t][i][j], -s])
                    cur_symbol += 1

    healing_cnf.extend(backward_spread_cnf)
    return healing_cnf, cur_symbol


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

    KB, count_H_S_dict, possible_actions_tiles = create_KB(observations, symbol_dict, b, n_rows, n_cols)

    temp_cnf, biggest_symbol = spread_healing_clauses(n_rows, n_cols, b, symbol_dict, biggest_symbol)
    KB.extend(temp_cnf)

    KB.extend(linearity(n_rows, n_cols, b, symbol_dict, medics, police, count_H_S_dict, biggest_symbol,
                        possible_actions_tiles))

    res = {}
    statuses = ['H', 'Q', 'U', 'S', 'I']

    s = Solver(bootstrap_with=KB)

    for q in queries:
        status = q[2]
        t = q[1]
        loc = q[0]
        i = loc[0]
        j = loc[1]
        q_symbol = symbol_dict[status][t][i][j]
        if not s.solve(assumptions=[q_symbol]):
            res[tuple(q)] = 'F'
        else:
            for sa in statuses:
                if sa != status:
                    if s.solve(assumptions=[symbol_dict[sa][t][i][j]]):
                        res[tuple(q)] = '?'
                        break
        if q not in res.keys():
            res[tuple(q)] = 'T'

    return res