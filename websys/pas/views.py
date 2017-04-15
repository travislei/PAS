from django.shortcuts import render
from django.http import JsonResponse
import json
import subprocess

from .models import *


# Create your views here.
def index(request):
    return render(request, 'pas/index.html')


def student(request, sid):
    info = Student.objects.filter(pk=sid)
    groups = Group.objects.filter(members=info)

    info = info.values()
    groups = groups.values()

    data = {
        'id': info[0]['id'],
        'name': info[0]['name'],
        'preflist': info[0]['preflist'],
        'groups': list(groups)
    }

    return JsonResponse(data)


def studentList(request):
    info = Student.objects.all().values()

    data = []

    for s in info:
        sid = int(s['id'])
        groups = Group.objects.filter(members__id=sid).values()

        try:
            assg_id = int(s['assignment_id'])
        except:
            assg_id = 0

        assg_proj = ''

        if assg_id != 0:
            assg_proj = Project.objects.filter(pk=assg_id).values()
            assg_proj = assg_proj[0]['name']

        json = {
            'id': s['id'],
            'name': s['name'],
            'preflist': s['preflist'],
            'assignment_id': s['assignment_id'],
            'assignment_name': assg_proj,
            'groups': list(groups)
        }

        data.append(json)

    response = {
        'student_list': list(data)
    }

    return JsonResponse(response)


def lecturer(request, lid):
    info = Lecturer.objects.filter(pk=lid)
    projects = Project.objects.filter(supervisor=lid)

    info = info.values()
    projects = projects.values()

    for p in projects:
        enrolled = Group.objects.filter(preflist__contains=p['id']).values()
        sid = [s['id'] for s in enrolled]

        if len(sid) != 0:
            p['enrolled'] = ','.join(str(s) for s in sid)
        else:
            p['enrolled'] = ''

        #  Prepare preflist
        preflist = LecturerPreflist.objects.filter(lecturer_id=lid,
                                                   project_id=p['id']).values()

        if not preflist:
            p['preflist'] = ''
        else:
            p['preflist'] = preflist[0]['preflist']

        #  Prepare matched group
        row = LecturerPreflist.objects.filter(lecturer_id=lid, project_id=p['id'])
        if not row:
            p['matched'] = ''
            continue

        matched = Group.objects.filter(matched=row).values()
        sid = [s['id'] for s in matched]

        if len(sid) != 0:
            p['matched'] = ','.join(str(s) for s in sid)
        else:
            p['matched'] = ''


    data = {
        'id': info[0]['id'],
        'name': info[0]['name'],
        'capacity': info[0]['capacity'],
        'projects': list(projects),
    }

    return JsonResponse(data)


def lecturerList(request):
    info = Lecturer.objects.all().values()

    data = {
        'lecturer_list': list(info)
    }

    return JsonResponse(data)


def group(request, gid):
    info = Group.objects.filter(pk=gid)
    rep_name = Student.objects.filter(pk=info.values('representative_id'))
    members = Student.objects.filter(members=info)
    capacity = members.count()

    info = info.values()
    rep_name = rep_name.values()
    members = members.values()

    data = {
        'id': info[0]['id'],
        'name': info[0]['name'],
        'preflist': info[0]['preflist'],
        'capacity': capacity,
        'sid': info[0]['representative_id'],
        'sid_name': rep_name[0]['name'],
        'members': list(members)
    }

    return JsonResponse(data)


def groupList(request):
    info = Group.objects.all().values()

    for p in info:
        try:
            assg_id = int(p['assignment_id'])
        except:
            assg_id = 0

        assg_proj = ''

        if assg_id != 0:
            assg_proj = Project.objects.filter(pk=assg_id).values()
            assg_proj = assg_proj[0]['name']

        p['assignment_name'] = assg_proj

        members = Student.objects.filter(members=p['id'])
        p['capacity'] = members.count()

        tmp = []
        for s in members.values():
            tmp.append(s['id'])

        p['members'] = ','.join(map(str, tmp))

    data = {
        'group_list': list(info)
    }

    return JsonResponse(data)


def project(request, pid):
    info = Project.objects.filter(pk=pid)
    supervisor = Lecturer.objects.filter(project__pk=pid)

    info = info.values()
    supervisor = supervisor.values()

    data = {
        'id': info[0]['id'],
        'name': info[0]['name'],
        'description': info[0]['description'],
        'capacity': info[0]['capacity'],
        'lid': info[0]['supervisor_id'],
        'lid_name': supervisor[0]['name']
    }

    return JsonResponse(data)


def projectList(request):
    info = Project.objects.all().values()

    tmp = []

    for p in info:
        pid = int(p['id'])
        tmp.append(json.loads(project(request, pid).content.decode()))

    data = {
        'project_list': tmp
    }

    return JsonResponse(data)


def listAll(request):
    projects = json.loads(projectList(request).content.decode())
    groups = json.loads(groupList(request).content.decode())
    lecturers = Lecturer.objects.all().values()

    tmp = []
    for l in lecturers:
        lid = int(l['id'])
        tmp.append(json.loads(lecturer(request, lid).content.decode()))

    data = {
        'project_list': projects['project_list'],
        'group_list': groups['group_list'],
        'lecturer_list': list(tmp)
    }

    with open('data.json', 'w+') as file:
        file.write(json.dumps(data))
        file.close()

    return JsonResponse(data)


def matching(request):
    listAll(request)
    open('matching.json', 'w').close()

    proc = subprocess.run(['./spa_group.py', 'data.json'])

    result = ''

    with open('matching.json', 'r') as f:
        result = json.loads(f.read())

    for p in result['group_matched'][0]:
        pid = int(p)
        assignment = result['group_matched'][0][p]

        if assignment:
            for g in assignment:
                gid = int(g)
                Group.objects.filter(pk=gid).update(assignment_id=pid)

                Student.objects.filter(members=gid).update(
                    assignment_id=pid
                )

    for l in result['lecturer_matched'][0]:
        lid = int(l)
        assignment = result['lecturer_matched'][0][l]

        if assignment:
            for p in assignment:
                pid = int(p)

                gp_list = result['group_matched'][0][str(p)]

                row = LecturerPreflist.objects.get(lecturer_id=lid,
                                                   project_id=pid)

                row.matched.add(*gp_list)

    return JsonResponse(result)


def clearMatching(request):
    Group.objects.all().update(assignment_id=0)
    Student.objects.all().update(assignment_id=0)
    l_list = LecturerPreflist.objects.all()

    for l in l_list:
        l.matched.clear()

    return JsonResponse({ 'status': 'success'})
