from action import Action

class Domain():
    def __init__(self, file_name):

        self.__types = list()
        self.__predicates = list()
        self.__actions = list()
        
        with open(file_name) as f:
            
            temp_type = None
            temp_text = ''
            for line in f:
                # print(type(str(line.strip())))
                # print(line)
                line = line.split(';')[0]
                line = line.strip()
                if len(line) > 0:
                    if temp_text != '':
                        temp_text += line
                        if temp_text.count('(') <= temp_text.count(')'):
                            if temp_type == 'types':
                                text = temp_text[1:-1]
                                self.__types = text[7:].split(' ')
                            elif temp_type == 'predicates':
                                text = temp_text[1:-1]
                                predicates = text[13:-1].split(') (')
                                self.encodepredicates(predicates)
                            elif temp_type == 'action':
                                text = temp_text[1:-1]
                                if temp_text.count('(') == temp_text.count(')') - 1:
                                    text = text[:-1]
                                self.__actions.append(Action(text))
                            temp_type = None
                            temp_text = ''
                        else:
                            temp_text += ' '
                    else:
                        if line[:7] == '(:types':
                            if line.count('(') == line.count(')'):
                                line = line[1:-1]
                                self.__types = line[7:].split(' ')
                            else:
                                temp_text += line + ' '
                                temp_type = 'types'
                        elif line[:12] == '(:predicates':
                            if line.count('(') == line.count(')'):
                                line = line[1:-1]
                                predicates = line[13:-1].split(') (')
                                self.encodepredicates(predicates)
                            else:
                                temp_text += line + ' '
                                temp_type = 'predicates'
                        elif line[:8] == '(:action':
                            temp_text += line + ' '
                            temp_type = 'action'

        temp = list()
        for action in self.__actions:
            effects = list()
            if action.effects['prob']:
                for _, _e in action.effects['effects']:
                    effects.extend(_e)
            else:
                effects = action.effects['effects']
            for effect in effects:
                tp = (effect['predicate'], len(effect['names']))
                if tp not in temp:
                    temp.append(tp)
        temp = sorted(temp, key=lambda x: x[1])
        self.__changingpredicates = [x for x, _ in temp]

    @property
    def types(self):
        return self.__types
    
    @property
    def predicates(self):
        return self.__predicates

    @property
    def actions(self):
        return self.__actions

    @property
    def changingpredicates(self):
        return self.__changingpredicates

    def encodepredicates(self, row_list):
        self.__predicates = dict()
        for v in row_list:
            if '?' in v:
                if v.count(' ?') == v.count(' - '):
                    values = v.split(' ?')
                    pred = list()
                    for value in values[1:]:
                        value = value.split(' - ')
                        pred.append((value[0], value[1]))
                    self.__predicates[values[0]] = pred
                else:
                    values = v.split(' - ')
                    names = values[0].split(' ?')
                    pred = list()
                    for name in names[1:]:
                        pred.append((name, values[1]))
                    self.__predicates[names[0]] = pred
            else:
                self.__predicates[v] = list()