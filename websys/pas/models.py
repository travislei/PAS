from django.db import models


# Create your models here.
class Lecturer(models.Model):
    name = models.CharField(max_length=128)
    capacity = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    capacity = models.PositiveSmallIntegerField(default=0)
    supervisor = models.ForeignKey(Lecturer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=128)
    preflist = models.CharField(max_length=255,
                                blank=True,
                                verbose_name='Project(s) Preflist')
    assignment = models.ForeignKey(Project,
                                   null=True,
                                   blank=True,
                                   default=0,
                                   verbose_name='Assigned Project')

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=128)
    representative = models.ForeignKey(Student,
                                       related_name='representative',
                                       on_delete=models.CASCADE)
    members = models.ManyToManyField(Student, related_name='members')
    preflist = models.CharField(max_length=255,
                                blank=True,
                                verbose_name='Project(s) Preflist')
    assignment = models.ForeignKey(Project,
                                   null=True,
                                   blank=True,
                                   default=0,
                                   verbose_name='Assigned Project')

    def __str__(self):
        return self.name


#  class GroupPreflist(models.Model):
    #  group = models.ForeignKey(Group)
    #  project = models.ForeignKey(Project)


class LecturerPreflist(models.Model):
    lecturer = models.ForeignKey(Lecturer)
    project = models.ForeignKey(Project)
    preflist = models.CharField(max_length=255,
                                verbose_name='Group(s) Preflist')
    matched = models.ManyToManyField(Group,
                                     blank=True,
                                     default=0,
                                     related_name='matched',
                                     verbose_name='Assigned Group')

    def __str__(self):
        return '%s, %s' % (self.lecturer, self.project)
