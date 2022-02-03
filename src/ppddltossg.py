import sys
from time import time, sleep
from tqdm import tqdm
import pandas as pd
import pulp as lp

from domain import *
from problem import * 
from action import *
from state import *

def checklp(nodes_df, edges_df):

    variables = list()
    nodes = list()
    for n, t in zip(nodes_df['n'], nodes_df['type']):
        variables.append(lp.LpVariable('x'+str(int(n)), lowBound = 0))
        nodes.append((n, t))

    Lp_prob = lp.LpProblem('Problem', lp.LpMinimize) 
    exp = 0
    for v in variables:
        exp += v
    Lp_prob += exp

    for n in nodes:
        temp_df = edges_df['from'] == n[0]
        temp_df = edges_df[temp_df]
        if n[1] == 'one':
            for f, t in zip(temp_df['from'], temp_df['to']):
                if f != t:
                    Lp_prob += variables[int(f)+1] >= variables[int(t)+1]
        elif n[1] == 'avg':
            probs = temp_df['prob'].tolist()
            tos = temp_df['to'].tolist()
            Lp_prob += variables[int(n[0])+1] >= [prob * variables[int(to)+1] for prob, to in zip(probs, tos)]
        elif n[1] == '1-s':
            Lp_prob += variables[int(n[0])+1] == 100

    status = Lp_prob.solve()

    return lp.value(variables[1]) == 100


def main(domain_file, problem_file):

    domain = Domain(domain_file)
    problem = Problem(problem_file, domain)
    state = State(problem.init_state)

    nodes_df = pd.DataFrame({'n': [], 'type': []})
    edges_df = pd.DataFrame({'from': [], 'to': [], 'prob': []})

    states = [state]
    n = 0
    nodes_df = nodes_df.append(pd.Series([-1, '1-s'], index=nodes_df.columns), 
        ignore_index=True)
    nodes_df = nodes_df.append(pd.Series([0, 'one'], index=nodes_df.columns), 
        ignore_index=True)
    search = True
    start_time = time()
    last_time = start_time
    max_time = 300
    step_update = 1
    diff_tot_n = 0
    goal_reached = 0
    not_satisfied = True
    with tqdm(total=max_time, 
            desc='generating', 
            bar_format = "{desc}: |{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] [tot-n={postfix[0]}, goal={postfix[1]}]",
                            postfix=[diff_tot_n, goal_reached]) as pbar:
        while n < len(states) and time() - start_time < max_time and not_satisfied:
            if states[n] is not None:
                if not checkgoal(states[n], problem.goal):
                    no_action = True
                    for action in domain.actions:
                        possible_values = checkaction(action, states[n])
                        if possible_values == {}:
                            possible_values['placeholder'] = []
                        if possible_values is not None:
                            no_action = False
                            if action.effects['prob']:
                                tot_prob = 1
                                for _p_ns, _new_state in applyactionprob(action, states[n], possible_values):
                                    if tot_prob == 1:
                                        states.append(None)
                                        _n = len(states) - 1
                                        nodes_df = nodes_df.append(pd.Series([_n, 'avg'], index=nodes_df.columns), 
                                            ignore_index=True)
                                        edges_df = edges_df.append(pd.Series([n, _n, 1], index=edges_df.columns), 
                                            ignore_index=True)
                                        tot_prob = 0
                                    new = True
                                    new_state = State(_new_state)
                                    for _ni, _state in enumerate(states):
                                        if _state != None and samestate(new_state, _state, domain.changingpredicates):
                                            new = False
                                            break
                                    if new:
                                        states.append(new_state)
                                        _ni = len(states) - 1
                                        nodes_df = nodes_df.append(pd.Series([_ni, 'one'], index=nodes_df.columns), 
                                            ignore_index=True)
                                    edges_df = edges_df.append(pd.Series([_n, _ni, _p_ns], index=edges_df.columns), 
                                        ignore_index=True)
                                    tot_prob += _p_ns
                            else:
                                for _new_state in applyactionbase(action, states[n], possible_values):
                                    new = True
                                    new_state = State(_new_state)
                                    for _ni, _state in enumerate(states):
                                        if _state != None and samestate(new_state, _state, domain.changingpredicates):
                                            new = False
                                            break
                                    if new:
                                        states.append(new_state)
                                        _ni = len(states) - 1 
                                        nodes_df = nodes_df.append(pd.Series([_ni, 'one'], index=nodes_df.columns), 
                                            ignore_index=True)
                                    edges_df = edges_df.append(pd.Series([n, _ni, 1], index=edges_df.columns), 
                                        ignore_index=True)
                    if no_action:
                        edges_df = edges_df.append(pd.Series([n, n, 1], index=edges_df.columns), 
                            ignore_index=True)
                else:
                    goal_reached += 1
                    edges_df = edges_df.append(pd.Series([n, -1, 1], index=edges_df.columns), 
                        ignore_index=True)
                    
                    #if checklp(nodes_df, edges_df):
                        #not_satisfied = False

                    

            n += 1
            if time() - last_time > step_update:
                diff_tot_n = len(states) - n
                _ = pbar.postfix[0] = diff_tot_n
                _ = pbar.postfix[1] = goal_reached
                _ = pbar.update(step_update)
                last_time = time()
                _ = tqdm._instances.clear()

    nodes_df.to_csv('./output/nodes.csv')
    edges_df.to_csv('./output/edges.csv')


if __name__ == "__main__":
    in_0 = sys.argv[1]
    in_1 = sys.argv[2]

    main(in_0, in_1)
