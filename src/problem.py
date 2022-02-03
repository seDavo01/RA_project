from domain import Domain

class Problem():
    def __init__(self, 
                 file_name: str, 
                 domain: Domain):

        self.__domain = domain

        with open(file_name) as f:
            
            temp_type = None
            temp_text = ''
            for line in f:
                line = line.split(';')[0]
                line = line.strip()
                if len(line) > 0:
                    if temp_text != '':
                        temp_text += line
                        if temp_text.count('(') <= temp_text.count(')'):
                            if temp_type == 'objects':
                                text = temp_text[1:-1]
                                self.__objects = self.encodeobjects(text)
                            elif temp_type == 'init':
                                text = temp_text[1:-1]
                                self.__init_state = self.encodeinit(text)
                            elif temp_type == 'goal':
                                text = temp_text[1:-1]
                                if temp_text.count('(') == temp_text.count(')') - 1:
                                    text = text[:-1]
                                self.__goal = self.encodeinit(text)
                            
                            temp_type = None
                            temp_text = ''
                        else:
                            temp_text += ' '
                    else:
                        if line[:9] == '(:objects':
                            if line.count('(') == line.count(')'):
                                line = line[1:-1]
                                self.__objects = self.encodeobjects(line)
                            else:
                                temp_text += line + ' '
                                temp_type = 'objects'
                        elif line[:6] == '(:init':
                            if line.count('(') == line.count(')'):
                                line = line[1:]
                                self.__init_state = self.encodeinit(line)
                            else:
                                temp_text += line + ' '
                                temp_type = 'init'
                        elif line[:6] == '(:goal':
                            if line.count('(') <= line.count(')'):
                                if line.count('(') == line.count(')'):
                                    line = line[1:]
                                elif line.count('(') == line.count(')') - 1:
                                    line = line[1:-1]
                                self.__goal = self.encodeinit(line)
                            else:
                                temp_text += line + ' '
                                temp_type = 'goal'

    @property
    def objects(self):
        return self.__objects

    @property
    def init_state(self):
        return self.__init_state

    @property
    def goal(self):
        return self.__goal

    def encodeobjects(self, line):
        result = list()
        line = line[9:]
        possible_types = self.__domain.types
        if len(possible_types) > 0:
            if ' - ' in line:
                objs, t = line.split(' - ')
                if t == possible_types[0]:
                    for obj in objs.split(' '):
                        result.append({
                            'name': obj,
                            'type': t
                        })
        return result

    def encodeinit(self, line):
        result = list()
        line = line[7:-2]
        if line[:4] == 'and ':
            line = line[5:-1]
        if ')(' in line:
            sep = ')('
        else:
            sep = ') ('
        for predicate in line.split(sep):
            values = predicate.split(' ')
            result.append({
                'predicate': values[0],
                'objects': list()
            })
            if len(values) > 1:
                result[-1]['objects'].extend(values[1:])
        return result