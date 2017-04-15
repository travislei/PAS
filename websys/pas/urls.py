from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /pas/
    url(r'^$', views.index, name='index'),
    url(r'^get/student/(?P<sid>[0-9]+)/$', views.student, name='student'),
    url(r'^get/studentList/', views.studentList, name='studentList'),
    url(r'^get/lecturer/(?P<lid>[0-9]+)/$', views.lecturer, name='lecturer'),
    url(r'^get/lecturerList/', views.lecturerList, name='lecturerList'),
    url(r'^get/group/(?P<gid>[0-9]+)/$', views.group, name='group'),
    url(r'^get/groupList/', views.groupList, name='groupList'),
    url(r'^get/project/(?P<pid>[0-9]+)/$', views.project, name='project'),
    url(r'^get/projectList/', views.projectList, name='projectList'),
    url(r'^get/listAll/', views.listAll, name='listAll'),
    url(r'^get/matching/', views.matching, name='matching'),
    url(r'^get/clearMatching/', views.clearMatching, name='clearMatching'),
]
