from django.contrib import admin
from .models import *

admin.site.site_header = 'PAS Adminstrataion'
admin.site.index_title = 'PAS adminstration'


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'preflist')


class LecturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'preflist')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'description')


# Register your models here.
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(LecturerPreflist)
