#!/usr/bin/env python3

from __future__ import print_function
import sys
import logging
import json

#  Logging for debug messages
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def idstr_to_list(str):
    '''
    Convert a JSON preflist to a list

    Args:
        str: preflist string separated by ','

    Returns:
        list of project or lecturer ids, None if empty
    '''
    preflist = str.strip().split(',')

    for id in range(len(preflist)):
        if preflist[id]:
            preflist[id] = int(preflist[id])
        else:
            preflist[id] = None

    return preflist


class Project(object):
    def __init__(self):
        self.id = 0
        self.name = ''
        self.lid = 0
        self.capacity = 0
        self.matched = 0

    def __repr__(self):
        return ('PID: {}, capacity {} by LID {}'
                .format(self.id, self.capacity, self.lecturer))

    def incr_matched(self):
        self.matched += 1

    def decr_matched(self):
        self.matched -= 1

    def is_undersubscribed(self):
        return self.matched < self.capacity


class Student(object):
    def __init__(self):
        self.id = 0
        self.pid = None
        self.preflist = []

    def __repr__(self):
        return 'SID {}, Preflist {}'.format(self.id, self.preflist)

    def is_preferred(self, pid):
        cur_index = self.preflist.index(self.pid)
        pid_index = self.preflist.index(pid)

        logging.debug('\tCurrent index: {}\tOffered index: {}'
                      .format(cur_index, pid_index))

        return pid_index < cur_index

    def get_pid_index(self):
        if self.pid is not None:
            return self.preflist.index(self.pid)
        else:
            return None


class Lecturer(object):
    def __init__(self):
        self.id = 0
        self.preflist = []
        self.capacity = 0
        self.matched = 0

    def __repr__(self):
        return ('LID: {}, Capacity: {}, Matched: {}, Preflist: {}'
                .format(self.id, self.capacity, self.matched, self.preflist))

    def get_nextstudent(self):
        return None

    def is_undersubscribed(self):
        return self.matched < self.capacity

    def incr_matched(self):
        self.matched += 1

    def decr_matched(self):
        self.matched -= 1

    def print_info(self):
        logging.debug('-' * 40)
        logging.debug('LID: {}\tCapacity: {}'
                      .format(self.id, self.capacity))

        for p in self.preflist:
            logging.debug('PID: {}'.format(p[0]))
            logging.debug('\tPreference: {}'.format(p[1]))

        logging.debug('-' * 40)
        logging.debug('')


class Matching(object):
    def __init__(self, p_dict, s_dict, l_list):
        self.pop_lecturer = {}
        self.p_matched = {}
        self.l_matched = {}
        self.s_matched = {}

        for pid, data in p_dict.items():
            self.p_matched[pid] = []
            self.s_matched[pid] = []

        for l in l_list:
            self.l_matched[l.id] = []

    def assign(self, lid, pid, sid):
        if lid not in self.p_matched[pid]:
            self.p_matched[pid].append(lid)

        if sid not in self.s_matched[pid]:
            self.s_matched[pid].append(sid)

        if pid not in self.l_matched[lid]:
            self.l_matched[lid].append(pid)

        logging.debug('\t*** Assign SID {} with PID {} by LID {} ***'
                      .format(sid, pid, lid))

    def delete(self, lid, pid, sid):
        if lid in self.p_matched[pid]:
            self.p_matched[pid].remove(lid)

        if sid in self.s_matched[pid]:
            self.s_matched[pid].remove(sid)

        if pid in self.l_matched[lid]:
            self.l_matched[lid].remove(pid)

        logging.debug('\t*** Unmatch SID {} with PID {} by LID {} ***'
                      .format(sid, pid, lid))

    def get_length(self, obj):
        if isinstance(obj, Lecturer):
            return len(self.l_matched[obj.id])
        elif isinstance(obj, Project):
            return len(self.p_matched[obj.id])
        else:
            return None

    def get_students(self, pid):
        return self.s_matched[pid]

    def print_project(self):
        logging.debug('Current projects\' matching:')

        for p, v in self.p_matched.items():
            logging.debug('PID {} is matched to {}'.format(p, v))

        logging.debug('')

    def print_lecturer(self):
        logging.debug('Current lecturers\' matching:')

        for l, v in self.l_matched.items():
            logging.debug('LID {} has project(s): {}'.format(l, v))

        logging.debug('')

    def print_student(self):
        logging.debug('Current students\' matching:')

        for s, v in self.s_matched.items():
            logging.debug('PID {} has student(s): {}'.format(s, v))

        logging.debug('')


# List of all projects
project_dict = {}
student_dict = {}
lecturer_list = []

#  Check if the input file available
if len(sys.argv) == 2:
    with open(sys.argv[1], 'r') as f:
        #  Prepare JSON string and read the file
        json_string = ''

        for line in f:
            json_string += line

        f.close()

        #  Decode the JSON
        json_string = json.loads(json_string)

        #  Read project list
        for p in json_string['project_list']:
            project = Project()

            project.id = p['id']
            project.name = p['name']
            project.lid = p['lid']
            project.capacity = p['capacity']

            project_dict[project.id] = project

        #  Read student list
        for s in json_string['student_list']:
            student = Student()

            student.id = s['id']
            student.preflist = idstr_to_list(s['preflist'])

            student_dict[student.id] = student

        #  Read lecturer list
        for l in json_string['lecturer_list']:
            raw_preflist = []

            for p in l['preference']:
                preflist = idstr_to_list(p['preflist'])
                raw_preflist.append(tuple([p['pid'], preflist]))

            lecturer = Lecturer()

            lecturer.id = int(l['id'])
            lecturer.capacity = int(l['capacity'])
            lecturer.preflist = raw_preflist

            lecturer_list.append(lecturer)

#  Otherwise demo set is used
else:
    '''
    p_1: Project A by LID 1, cap.: 1
    p_2: Project B by LID 1, cap.: 1
    p_3: Project C by LID 1, cap.: 1
    p_4: Project D by LID 2, cap.: 1
    '''
    raw_project = [('Project A', 1, 2), ('Project B', 1, 1),
                   ('Project C', 1, 1), ('Project D', 2, 1)]

    for i in range(len(raw_project)):
        p = Project()

        p.id = i + 1
        p.name = raw_project[i][0]
        p.lid = raw_project[i][1]
        p.capacity = raw_project[i][2]

        project_dict[p.id] = p

    '''
    Max. projects = 3
    s_1: A, B
    s_2: D, A
    s_3: B
    s_4: C
    s_5: A, B, C
    '''
    raw_student = [[1, 2], [4, 1], [2], [3], [1, 2, 3]]

    for i in range(len(raw_student)):
        s = Student()

        s.id = i + 1
        s.preflist = raw_student[i]

        student_dict[s.id] = s

    '''
    l_1: A, B, C
    l_2: D
    '''
    raw_lecturer = [(4, [(1, [2, 1, 5]), (2, [1, 3, 5]), (3, [4, 5])]),
                    (1, [(4, [2])])]

    for i in range(len(raw_lecturer)):
        l = Lecturer()

        l.id = i + 1
        l.capacity = raw_lecturer[i][0]
        l.preflist = raw_lecturer[i][1]

        lecturer_list.append(l)

#  Reverse for a more rational order
#  INFO: Remove if necessary
lecturer_list.reverse()

#  Assign lists to a matching
matching = Matching(project_dict, student_dict, lecturer_list)

#  SPA-lecturer Algorithm
while lecturer_list:
    l = lecturer_list.pop()

    matching.pop_lecturer[l.id] = l

    if not l.is_undersubscribed():
        continue

    logging.debug('>> LID {} is under-subscribed...'.format(l.id))

    for pid, preflist in l.preflist:
        p = project_dict[pid]

        if preflist and p.is_undersubscribed():
            logging.debug('\n\tChecking PID {}, Current length {}, '
                          'Preflist: {}'
                          .format(p.id, matching.get_length(p), preflist))
            logging.debug('\t' + '-' * 70)

            for sid in preflist:
                if (sid is None) or (not l.is_undersubscribed()):
                    break

                s = student_dict[sid]
                logging.debug('\t{}'.format(student_dict[s.id]))

                if s.pid is None:
                    matching.assign(l.id, p.id, s.id)
                    s.pid = p.id
                    l.incr_matched()
                    p.incr_matched()

                    if l.is_undersubscribed():
                        lecturer_list.append(l)

                    break
                elif s.is_preferred(pid):
                    freed_p = project_dict[s.pid]
                    freed_l = matching.pop_lecturer[freed_p.lid]

                    matching.delete(freed_p.lid, s.pid, s.id)
                    freed_p.decr_matched()
                    freed_l.decr_matched()

                    matching.assign(l.id, p.id, s.id)
                    s.pid = p.id
                    l.incr_matched()
                    p.incr_matched()

                    if freed_l not in lecturer_list:
                        lecturer_list.append(freed_l)

                    break
                else:
                    continue

logging.debug('')
#  matching.print_project()
#  matching.print_lecturer()

#  logging.debug('Current students\' matching:')
#  for sid, s in student_dict.items():
#  logging.debug('SID {} matched with PID {}, index #{}'
#  .format(sid, s.pid, s.get_pid_index()))

logging.debug('Stability Checking:')
for sid, s in student_dict.items():
    if s.get_pid_index() is None:
        logging.debug('SID {} is unmatched, continue...'.format(sid))
    elif s.get_pid_index() == 0:
        logging.debug('SID {} matched with PID {}, preflist {}, first project'
                      .format(sid, s.pid, s.preflist))
    else:
        index = s.get_pid_index()
        preferred_project = s.preflist[:index]

        logging.debug('SID {} matched with PID {}, index #{}, preflist {}'
                      .format(sid, s.pid, index, s.preflist))

        for pid in preferred_project:
            p = project_dict[pid]
            s_list = matching.get_students(p.id)

            logging.debug('\tChecking PID {}, student(s) matched {}'
                          .format(p.id, s_list))

            for sid in s_list:
                s = student_dict[sid]
                logging.debug('\t> SID {} matched with PID {}, preflist {}'
                              .format(s.id, s.pid, s.preflist))

    logging.debug('')

matching.print_student()
