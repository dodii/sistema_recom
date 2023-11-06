from django.contrib import admin
from .models import (
    Teacher,
    OpenAlexWork,
    TeacherWorkKeyword,
    TeacherKeyword,
    TeacherCourse,
    TeacherCourseKeyword,
    GuidedThesis,
    GuidedThesisKeyword,
)
from django.contrib.auth.models import User, Group


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    search_help_text = "Buscar por nombre"
    list_display = [
        "name",
        "openalex_id",
        "get_keywords",
        "get_courses",
        "get_memories",
    ]

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return [keyword.keyword for keyword in obj.teacherkeyword_set.all()]

    @admin.display(description="courses")
    def get_courses(self, obj):
        return [
            f"{course.course_code} {course.title}"
            for course in obj.teachercourse_set.all()
        ]

    @admin.display(description="thesis")
    def get_memories(self, obj):
        return [
            f"{thesis.ucampus_id}, {thesis.title}"
            for thesis in obj.guidedthesis_set.all()
        ]


class OpenAlexWorkAdmin(admin.ModelAdmin):
    search_fields = ["title", "teacher__name"]
    search_help_text = "Buscar por título o docente"
    list_display = ["title", "year", "get_teachers", "get_keywords"]
    filter_horizontal = ("teacher",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return [keyword.keyword for keyword in obj.teacherworkkeyword_set.all()]


class TeacherWorkKeywordAdmin(admin.ModelAdmin):
    search_fields = ["keyword", "associated_work__title"]
    search_help_text = "Buscar por keyword o título de trabajo"
    list_display = ["keyword", "get_works"]
    filter_horizontal = ("associated_work",)

    @admin.display(description="works")
    def get_works(self, obj):
        return [work.title for work in obj.associated_work.all()]


class TeacherKeywordAdmin(admin.ModelAdmin):
    search_fields = ["keyword", "teacher__name"]
    search_help_text = "Buscar por keyword o docente"
    list_display = ["keyword", "get_teachers"]
    filter_horizontal = ("teacher",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]


class GuidedThesisAdmin(admin.ModelAdmin):
    search_fields = ["title", "year", "teacher__name"]
    search_help_text = "Buscar por título, año o docente"
    list_display = ["title", "year", "get_teachers"]
    filter_horizontal = ("teacher",)
    exclude = ("doi",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]


class TeacherCoursedAdmin(admin.ModelAdmin):
    search_fields = ["title", "course_code", "year", "teacher__name"]
    search_help_text = "Buscar por título, código, año o docente"
    list_display = ["title", "course_code", "year", "get_teachers"]
    filter_horizontal = ("teacher",)
    exclude = ("doi",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]


# Register your models here.
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(OpenAlexWork, OpenAlexWorkAdmin)
admin.site.register(TeacherWorkKeyword, TeacherWorkKeywordAdmin)
admin.site.register(TeacherKeyword, TeacherKeywordAdmin)
admin.site.register(TeacherCourse, TeacherCoursedAdmin)
admin.site.register(TeacherCourseKeyword)
admin.site.register(GuidedThesis, GuidedThesisAdmin)
admin.site.register(GuidedThesisKeyword)

# Unregister user and group
admin.site.unregister(Group)
admin.site.unregister(User)
