class State():
    def __init__(self, list_state):

        self.__list = list_state.copy()

    @property
    def getlist(self):
        return self.__list.copy()
        
    @property
    def getbools(self):
        return self.getbyn(0)

    def getbyn(self, n):
        result = list()
        for single in self.__list:
            if len(single['objects']) == n:
                result.append(single)
        return result.copy()

    def getbypredicate(self, pred):
        result = list()
        for single in self.__list:
            if single['predicate'] == pred:
                result.append(single)
        return result.copy()

    def getbyobject(self, obj):
        result = list()
        for single in self.__list:
            if obj in single['objects']:
                result.append(single)
        return result.copy()

    def getbyobjectpos(self, obj, n):
        result = list()
        for single in self.__list:
            if len(single['objects']) > n and obj == single['objects'][n]:
                result.append(single)
        return result.copy()

    def getbyobjectspos(self, objs, ns=None):
        result = list()
        if ns is None:
            ns = [x for x in range(len(objs))]
        max_n = max(ns)
        for single in self.__list:
            if len(single['objects']) > max_n:
                to_check = [single['objects'][i] for i in ns]
                if objs == to_check:
                    result.append(single)
        return result.copy()

    def getbypredobjectspos(self, pred, objs, ns=None):
        result = list()
        if ns is None:
            ns = [x for x in range(len(objs))]
        max_n = max(ns)
        for single in self.__list:
            if single['predicate'] == pred and len(single['objects']) > max_n:
                to_check = [single['objects'][i] for i in ns]
                if objs == to_check:
                    result.append(single)
        return result.copy()

def samestate(state_a, state_b, changingpredicates):
    list_a = state_a.getlist
    list_b = state_b.getlist
    if len(list_a) != len(list_b):
        return False
    for predicate in changingpredicates:
        for va in state_a.getbypredicate(predicate):
            if va not in state_b.getbypredicate(predicate):
                return False
    return True

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3