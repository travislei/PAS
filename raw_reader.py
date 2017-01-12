#!/usr/bin/env python3

import sys
import json

with open('normal.txt', 'r') as f:
    if f.readline() != 'BEGIN_PROJECT_LIST\n':
        print('ERROR: BEGIN_PROJECT_LIST not found!')
        f.close()
        sys.exit()

    p = f.readline()

    raw_project = []
    while p != 'END_PROJECT_LIST\n':
        p = p.strip().split("\t")
        p[1] = int(p[1])
        p[2] = int(p[2])

        raw_project.append(tuple(p))
        p = f.readline()

    #  print(raw_project)

    #  Now read student list
    if f.readline() != 'BEGIN_STUDENT_LIST\n':
        print('ERROR: BEGIN_STUDENT_LIST not found!')
        f.close()
        sys.exit()

    p = f.readline()

    raw_student = []
    while p != 'END_STUDENT_LIST\n':
        p = p.strip().split('\t')

        s = []
        for i in p:
            s.append(int(i))

        raw_student.append(s)
        p = f.readline()

    #  print(raw_student)

    if f.readline() != 'BEGIN_LECTURER_LIST\n':
        print('ERROR: BEGIN_LECTURER_LIST not found!')
        f.close()
        sys.exit()

    p = f.readline()
    lecturer_json = ''

    while p != 'END_LECTURER_LIST\n':
        lecturer_json += p
        p = f.readline()

    #  JSON decode
    lecturer_json = json.loads(lecturer_json)

    raw_lecturer = []
    for l in lecturer_json['lecturer_list']:
        raw_preflist = []
        for p in l['preference']:
            preflist = p['preflist'].strip().split(',')

            for sid in range(len(preflist)):
                if preflist[sid]:
                    preflist[sid] = int(preflist[sid])
                else:
                    preflist[sid] = None

            raw_preflist.append(tuple([p['pid'], preflist]))

        raw_lecturer.append(tuple([l['capacity'], raw_preflist]))

    print(raw_lecturer)

    f.close()
