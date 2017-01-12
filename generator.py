#!/usr/bin/env python3

from __future__ import print_function
import sys
import random
import json


#  Maximum parameters
MAX_PROJECT_CAPACITY = 5
MAX_PREFLIST = 6


#  Check if given value is an integer
def is_int(n):
    try:
        int(n)
        return True
    except:
        return False


#  Check if input argumnet is valid
if len(sys.argv) != 4:
    print('Please enter the number of projects, students and lecturers!')
    sys.exit()

if not (is_int(sys.argv[1]) and is_int(sys.argv[2]) and is_int(sys.argv[3])):
    print('ERROR: Cannot parase as integer!')
    sys.exit()


f = open('normal.json', 'w')

projects_no = int(sys.argv[1])
students_no = int(sys.argv[2])
lecturers_no = int(sys.argv[3])

lecturer_dict = {}
project_dict = {}

#  A dict to store the PID for a lecturer
for l in enumerate(range(lecturers_no), 1):
    lecturer_dict[l[0]] = []

#  A dict to store the SID in a project
for p in enumerate(range(projects_no), 1):
    project_dict[p[0]] = []


#  Generate projects' list
project_list = []
for p in enumerate(range(projects_no), 1):
    pid = p[0]
    name = 'Project {}'.format(pid)
    lid = int(random.uniform(1, lecturers_no + 1))
    cap = int(random.uniform(1, MAX_PROJECT_CAPACITY + 1))

    lecturer_dict[lid].append((pid, cap))
    project_list.append({
        'id': pid,
        'name': name,
        'lid': lid,
        'capacity': cap
    })

#  Generate students' list
student_list = []
for s in enumerate(range(students_no), 1):
    sid = s[0]

    max_preflist = int(random.uniform(1, MAX_PREFLIST))

    preflist = []
    for p in range(max_preflist):
        pid = int(random.uniform(1, projects_no + 1))

        #  Uniqueness checked!
        while pid in preflist:
            pid = int(random.uniform(1, projects_no + 1))

        project_dict[pid].append(sid)
        preflist.append(pid)

    preflist_str = ','.join(map(str, preflist))
    student_list.append({
        'id': sid,
        'preflist': preflist_str
    })

#  Generate lecturers' list
lecturer_list = []
for lid, list in lecturer_dict.items():
    preflist = []
    capacity = 0

    for pid, cap in list:
        capacity += cap

        pl = project_dict[pid]
        random.shuffle(pl)
        pl_str = ','.join(map(str, pl))
        preflist.append({
            'pid': pid,
            'preflist': pl_str
        })

    #  Randomly add an offset
    capacity += int(random.uniform(0, len(list) + 1))

    lecturer_list.append({
        'id': lid,
        'capacity': capacity,
        'preference': preflist
    })

#  Print as JSON format
print(json.dumps({
    'project_list': project_list,
    'student_list': student_list,
    'lecturer_list': lecturer_list
}, indent=2))

f.close()
