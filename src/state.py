# Class to handle the state, takes as input the list of predicates that characterize a state
class State():
    def __init__(self, list_state):

        self.__list = list_state.copy()

    @property
    def getlist(self):
        return self.__list.copy()
    
    # return only predicates free of objects
    @property
    def getbools(self):
        return self.getbyn(0)

    # return only predicates with n objects
    def getbyn(self, n):
        result = list()
        for single in self.__list:
            if len(single['objects']) == n:
                result.append(single)
        return result.copy()

    # return only instances of a predicate (specified in the input)
    def getbypredicate(self, pred):
        result = list()
        for single in self.__list:
            if single['predicate'] == pred:
                result.append(single)
        return result.copy()

    # return only instances with a certain object
    def getbyobject(self, obj):
        result = list()
        for single in self.__list:
            if obj in single['objects']:
                result.append(single)
        return result.copy()

    # return only instances with a given object in a specific position (first or second or third and so on)
    def getbyobjectpos(self, obj, n):
        result = list()
        for single in self.__list:
            if len(single['objects']) > n and obj == single['objects'][n]:
                result.append(single)
        return result.copy()

    # return only instances with a set of objects in a particular order specified through a list (default is [1, 2, ..., n])
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

    # return only instances of a certain predicate with a set of objects in a particular order specified through a list (default is [1, 2, ..., n])
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

# method that taking as input two states and the predicates that are allowed to change in the domain,
# return False as soon as it discover that they are not the same, otherwise it return True
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

# return the intersection of two lists given as input
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3