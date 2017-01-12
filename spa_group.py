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

    def incr_matched(self, size):
        self.matched += size

    def decr_matched(self, size):
        self.matched -= size

    def is_undersubscribed(self):
        return self.matched < self.capacity


class Group(object):
    def __init__(self):
        self.id = 0
        self.capacity = 0
        self.pid = None
        self.preflist = []

    def __repr__(self):
        return 'GID {}, Preflist {}'.format(self.id, self.preflist)

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

    def incr_matched(self, size):
        self.matched += size

    def decr_matched(self, size):
        self.matched -= size

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

        logging.debug('\t*** Assign GID {} with PID {} by LID {} ***'
                      .format(sid, pid, lid))

    def delete(self, lid, pid, sid):
        if lid in self.p_matched[pid]:
            self.p_matched[pid].remove(lid)

        if sid in self.s_matched[pid]:
            self.s_matched[pid].remove(sid)

        if pid in self.l_matched[lid]:
            self.l_matched[lid].remove(pid)

        logging.debug('\t*** Unmatch GID {} with PID {} by LID {} ***'
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
            logging.debug('PID {} has group(s): {}'.format(s, v))

        logging.debug('')


# List of all projects
project_dict = {}
group_dict = {}
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
            project.lid = p['supervisor_id']
            project.capacity = p['capacity']

            project_dict[project.id] = project

        #  Read group list
        for s in json_string['group_list']:
            group = Group()

            group.id = s['id']
            group.capacity = s['capacity']
            group.preflist = idstr_to_list(s['preflist'])

            group_dict[group.id] = group

        #  Read lecturer list
        for l in json_string['lecturer_list']:
            raw_preflist = []

            for p in l['projects']:
                preflist = ''

                if 'preflist' in p:
                    preflist = idstr_to_list(p['preflist'])

                raw_preflist.append(tuple([p['id'], preflist]))

            lecturer = Lecturer()

            lecturer.id = int(l['id'])
            lecturer.capacity = int(l['capacity'])
            lecturer.preflist = raw_preflist

            lecturer_list.append(lecturer)

#  Otherwise Exit
else:
    sys.exit(0)

#  Reverse for a more rational order
#  INFO: Remove if necessary
lecturer_list.reverse()

#  Assign lists to a matching
matching = Matching(project_dict, group_dict, lecturer_list)

#  SPA-Group Algorithm
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

                g = group_dict[sid]
                logging.debug('\t{}'.format(group_dict[g.id]))

                if g.capacity > l.capacity - l.matched:
                    logging.debug('\tDo not have enought capacity!')
                    continue

                if g.pid is None:
                    matching.assign(l.id, p.id, g.id)
                    g.pid = p.id
                    l.incr_matched(g.capacity)
                    p.incr_matched(g.capacity)

                    if l.is_undersubscribed():
                        lecturer_list.append(l)

                    break
                elif g.is_preferred(pid):
                    freed_p = project_dict[g.pid]
                    freed_l = matching.pop_lecturer[freed_p.lid]

                    matching.delete(freed_p.lid, g.pid, g.id)
                    freed_p.decr_matched(g.capacity)
                    freed_l.decr_matched(g.capacity)

                    matching.assign(l.id, p.id, g.id)
                    g.pid = p.id
                    l.incr_matched(g.capacity)
                    p.incr_matched(g.capacity)

                    if freed_l not in lecturer_list:
                        lecturer_list.append(freed_l)

                    break
                else:
                    continue

logging.debug('')
#  matching.print_project()
#  matching.print_lecturer()

#  logging.debug('Current students\' matching:')
#  for sid, g in group_dict.items():
#  logging.debug('GID {} matched with PID {}, index #{}'
#  .format(sid, s.pid, s.get_pid_index()))

logging.debug('Stability Checking:')
for sid, s in group_dict.items():
    if s.get_pid_index() is None:
        logging.debug('GID {} is unmatched, continue...'.format(sid))
    elif s.get_pid_index() == 0:
        logging.debug('GID {} matched with PID {}, preflist {}, first project'
                      .format(sid, s.pid, s.preflist))
    else:
        index = s.get_pid_index()
        preferred_project = s.preflist[:index]

        logging.debug('GID {} matched with PID {}, index #{}, preflist {}'
                      .format(sid, s.pid, index, s.preflist))

        for pid in preferred_project:
            p = project_dict[pid]
            s_list = matching.get_students(p.id)

            logging.debug('\tChecking PID {}, student(s) matched {}'
                          .format(p.id, s_list))

            for sid in s_list:
                s = group_dict[sid]
                logging.debug('\t> GID {} matched with PID {}, preflist {}'
                              .format(s.id, s.pid, s.preflist))

    logging.debug('')

matching.print_student()
