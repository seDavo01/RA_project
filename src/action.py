from fractions import Fraction

from state import intersection

# Class to handle action, takes as input the corresponding text from the domain file
class Action():
    def __init__(self, text):

        self.__params = list()
        self.__precons = list()
        self.__effects = dict()
        self.__effects['prob'] = False

        splitted = text.split(':')
        for part in splitted:
            if 'action' in part:
                self.__name = part.split(' ')[1]
            # save parameters
            elif 'parameters' in part:
                if part.count('?') == part.count(' - '): 
                    params = part[12:-2].split('?')[1:]
                    for param in params:
                        param = param.split(' - ')
                        self.__params.append({
                            'name': param[0],
                            'type': param[1],
                        })
                else:
                    params = part[12:-2].split(' - ')
                    for param in params[0].split('?'):
                        if param != '':
                            self.__params.append({
                                'name': param.strip(),
                                'type': params[1]
                            })
            # save preconditions
            elif 'precondition' in part:
                precons = part[14:-2]
                if precons[:3] == 'and':
                    precons = precons[5:-1]
                # split them
                precons = precons.split(') (')
                for precon in precons:
                    b = True
                    # negated condition
                    if precon[:4] == 'not ':
                        b = False
                        precon = precon[5:-1]
                    # different cases with and without objects
                    if '?' in precon:
                        precon = precon.split(' ?')
                        self.__precons.append({
                            'predicate': precon[0],
                            'names': precon[1:],
                        })
                    else:
                        self.__precons.append({
                            'predicate': precon,
                            'names': []
                        })
                    self.__precons[-1]['bool'] = b
            # save effects
            elif 'effect' in part:
                line = part[8:-1]
                # if it starts with probabilistic
                if line[:13] == 'probabilistic':
                    self.__effects['prob'] = True
                    self.__effects['effects'] = self.decodeprobeff(line)
                # if probabilistic is inside the effects, limited to some of them
                elif 'probabilistic' in line:
                    self.__effects['prob'] = True
                    self.__effects['effects'] = list()
                    simp_line, prob_line = line.split(' (probabilistic')
                    simp_line += ')'
                    prob_line = '(probabilistic' + prob_line[:-1]
                    common_effects = self.decodesimpeff(simp_line)
                    prob_effects = self.decodeprobeff(prob_line)
                    for prob_effect in prob_effects:
                        self.__effects['effects'].append((prob_effect[0], prob_effect[1] + common_effects))
                    prob_sum = 0
                    for effect in self.__effects['effects']:
                        prob_sum += effect[0]
                    if prob_sum < 1:
                        self.__effects['effects'].append((1 - prob_sum, common_effects))
                else:
                    self.__effects['effects'] = self.decodesimpeff(line)

        _precons = self.__precons
        self.__precons = [None] * len(_precons)
        for i, _p in enumerate(_precons):
            if self.__precons[0] is None:
                self.__precons[0] = _p 
            else:
                if len(_p['names']) >= len(self.__precons[i-1]['names']):
                    self.__precons[i] = _p
                else:
                    for j in range(i,0,-1):
                        self.__precons[j] = self.__precons[j-1]
                    self.__precons[0] = _p


    @property
    def name(self):
        return self.__name

    @property
    def params(self):
        return self.__params
    
    @property
    def precons(self):
        return self.__precons

    @property
    def effects(self):
        return self.__effects

    # method to decode probabilistic effects
    def decodeprobeff(self, line):
        result = list()
        line = line[14:]
        probs = list()
        effects = list()
        temp = ''
        what = 'prob'
        for c in line:
            if what == 'prob' and c == '(':
                probs.append(temp[:-1])
                temp = c
                what = 'effect'
            else:
                temp += c
            if what == 'effect' and temp.count('(') == temp.count(')'):
                effects.append(temp[1:-1])
                temp = ''
                what = 'prob'
        # print(probs, effects)
        for prob, effect in zip(probs, effects):
            encoded_effects = self.decodesimpeff(effect)
            if '/' in prob:
                prob = Fraction(prob)
            result.append((float(prob), encoded_effects))
        return result

    # method to decode deterministic effects
    def decodesimpeff(self, line):
        result = list()
        if line[:3] == 'and':
            line = line[5:-1]
        effects = line.split(') (')
        for effect in effects:
            b = True
            if effect[:4] == 'not ':
                b = False
                effect = effect[5:-1]
            if '?' in effect:
                effect = effect.split(' ?')
                if effect[0][-1] == ')':
                    pred = effect[0][:-1]
                else:
                    pred = effect[0]
                if effect[-1][-1] == ')':
                    names = effect[1:-1] + [effect[-1][:-1]]
                else:
                    names = effect[1:]
                result.append({
                    'predicate': pred,
                    'names': names,
                })
            else:
                if effect[-1] == ')':
                    pred = effect[:-1]
                else:
                    pred = effect
                result.append({
                    'predicate': pred,
                    'names': []
                })
            result[-1]['bool'] = b
        return result

# return not empty parameters
def notemptyparam(params):
    result = list()
    for key in params.keys():
        if not all(v is None for v in params[key]):
            result.append(key)
    return result

# return empty parameters
def emptyparam(params):
    result = list()
    for key in params.keys():
        if all(v is None for v in params[key]):
            result.append(key)
    return result

# method to check if one action (in input) is applicable to one state (in input as well)
# Return one or more combinations of objects that satisfy the preconditions
def checkaction(action, state):
    _params = [x['name'] for x in action.params]
    params = {x : list() for x in _params}
    precons = action.precons
    state_bools = [x['predicate'] for x in state.getbools]
    for precon in precons:
        if len(precon['names']) == 0:
            if precon['bool'] != (precon['predicate'] in state_bools):
                return None

        else:
            lengths = [len(v) for v in params.values()]
            if max(lengths) == 0:
                temp = state.getbypredicate(precon['predicate'])
                if precon['bool'] == (len(temp) == 0):
                    return None
                for v in temp:
                    for n, o in zip(precon['names'], v['objects']):
                        params[n].append(o)
                if len(precon['names']) != len(_params):
                    _ps = _params.copy()
                    for _pre in precon['names']:
                        _ps.remove(_pre)
                    for _p in _ps:
                        params[_p].extend([None] * len(temp))
        
            else:
                k_params = notemptyparam(params)
                e_params = emptyparam(params)
                if precon['predicate'] == '=':
                    if len(e_params) > 0:
                        return None
                    old_params = params.copy()
                    # print(old_params)
                    params = {x : list() for x in _params}
                    for i in range(max(lengths)):
                        if precon['bool'] == (old_params[precon['names'][0]][i] == old_params[precon['names'][1]][i]):
                            for key in params.keys():
                                params[key].append(old_params[key][i])
                    # print(params)
                    lengths = [len(v) for v in params.values()]
                    if max(lengths) == 0:
                        return None

                else:
                    if intersection(k_params, precon['names']) == k_params:

                        values = list()
                        poss = list()
                        for n in range(max(lengths)):
                            values.append(list())
                            poss.append(list())
                            for key in params.keys():
                                if key in precon['names']:
                                    v = params[key][n]
                                    if v is not None:
                                        values[-1].append(v)
                                        poss[-1].append(precon['names'].index(key))
                        temps = list() 
                        for v, p in zip(values, poss):
                            if len(v) > 0 and len(p) > 0:
                                temp = state.getbypredobjectspos(precon['predicate'], v, p)
                                if len(temp) > 0:
                                    temps.append(temp)
                        if precon['bool'] == (len(temps) == 0):
                            return None
                        old_params = params.copy()
                        params = {x : list() for x in _params}
                        for temp in temps:
                            for v in temp:
                                for n, o in zip(precon['names'], v['objects']):
                                    params[n].append(o)
                            if len(precon['names']) != len(_params):
                                _ps = _params.copy()
                                for _pre in precon['names']:
                                    _ps.remove(_pre)
                                for _p in _ps:
                                    params[_p].extend([None] * len(temp))

                    elif intersection(k_params, precon['names']) == []:
                        temp = state.getbypredicate(precon['predicate'])
                        if precon['bool'] == (len(temp) == 0):
                            return None
                        old_params = params.copy()
                        len_old = max(lengths)
                        params = {x : list() for x in _params}
                        for _p in precon['names']:
                            if _p in e_params:
                                e_params.remove(_p)
                        for v in temp:
                            for n, o in zip(precon['names'], v['objects']):
                                params[n].extend([o]*len_old)
                                for _k in k_params:
                                    params[_k].extend(old_params[_k])
                                if len(e_params) > 0:
                                    for _e in e_params:
                                        params[_e].extend([None]*len_old)

                    else:
                        values = list()
                        poss = list()
                        for n in range(max(lengths)):
                            values.append(list())
                            poss.append(list())
                            for key in params.keys():
                                if key in precon['names']:
                                    v = params[key][n]
                                    if v is not None:
                                        values[-1].append(v)
                                        poss[-1].append(precon['names'].index(key))
                        temps = list() 
                        for v, p in zip(values, poss):
                            if len(v) > 0 and len(p) > 0:
                                temp = state.getbypredobjectspos(precon['predicate'], v, p)
                                if len(temp) > 0:
                                    temps.append(temp)
                                else:
                                    temps.append(None)
                        if precon['bool'] == (len(temps) == 0):
                            return None
                        old_params = params.copy()
                        len_old = max(lengths)
                        params = {x : list() for x in _params}
                        for i, temp in enumerate(temps):
                            if temp is not None:
                                for v in temp:
                                    for n, o in zip(precon['names'], v['objects']):
                                        params[n].append(o)
                                _ps = _params.copy()
                                for _pre in precon['names']:
                                    _ps.remove(_pre)
                                _pso = intersection(_ps, k_params)
                                for _p in _pso:
                                    params[_p].append(old_params[_p][i])
                                _pse = intersection(_ps, e_params)
                                for _p in _pse:
                                    params[_p].append(None)
                        

    return params

# check if the goal condition is satisfied in a given state
def checkgoal(state, goal):
    for value in goal:
        if len(value['objects']) == 0:
            if len(state.getbypredicate(value['predicate'])) == 0:
                return False
        elif len(state.getbypredobjectspos(value['predicate'], value['objects'])) == 0:
            return False
    return True

# given an action, a state and a set of (valid) objects, apply the action to the state with them.
def applyactionbase(action, prev_state, params):
    state_list = prev_state.getlist.copy()
    result = list()
    lengths = [len(v) for v in params.values()]
    if lengths == [0]:
        lengths[0] = 1
    for i in range(max(lengths)):
        result.append(prev_state.getlist.copy())
        for effect in action.effects['effects']:
            temp = {
                    'predicate': effect['predicate'],
                    'objects': [params[x][i] for x in effect['names']],
                }
            if effect['bool']:
                if temp not in result[i]:
                    result[i].append(temp)
            else:
                result[i].remove(temp)

    return result

# given an action, a state and a set of (valid) objects, apply the action to the state with them.
# the only difference with respect to applyactionbase is that this is for probabilistic actions,
# the output is actually a list because there are more than one state that are generate (because of the multiple outcomes)
def applyactionprob(action, prev_state, params):
    state_list = prev_state.getlist.copy()
    result = list()
    lengths = [len(v) for v in params.values()]
    if lengths == [0]:
        lengths[0] = 1
    for i in range(max(lengths)):
        probs = [prob_eff[0] for prob_eff in action.effects['effects']]
        prob_sum = sum(probs)
        for prob, effects in action.effects['effects']:
            prob_result = (prob, prev_state.getlist.copy())
            for effect in effects:
                temp = {
                        'predicate': effect['predicate'],
                        'objects': [params[x][i] for x in effect['names']],
                    }
                if effect['bool']:
                    if temp not in prob_result[1]:
                        prob_result[1].append(temp)
                else:
                    prob_result[1].remove(temp)
            result.append(prob_result)
        if prob_sum < 1:
            result.append((1 - prob_sum, prev_state.getlist.copy()))

    return result