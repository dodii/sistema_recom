from django.contrib import admin
from .models import (
    Keyword,
    Teacher,
    TeacherKeywordRelationship,
    ScholarWork,
    ScholarWorkKeywordRelationship,
    FCFMCourse,
    FCFMCourseKeywordRelationship,
    GuidedThesis,
    GuidedThesisKeywordRelationship,
)
from django.contrib.auth.models import User, Group


class KeywordAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    search_help_text = "Buscar por keyword"
    list_display = [
        "keyword",
    ]


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    search_help_text = "Buscar por nombre"
    list_display = [
        "name",
        "rut",
        "openalex_id",
        "dblp_id",
        "get_keywords",
        "get_courses",
        "get_memories",
        "get_works",
    ]
    readonly_fields = ("openalex_id",)

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return [
            f"{kw.keyword}: {kw.score}"
            for kw in obj.teacherkeywordrelationship_set.all()
        ]

    @admin.display(description="courses")
    def get_courses(self, obj):
        return [
            f"{course.course_code}: {course.title}"
            for course in obj.fcfmcourse_set.all()
        ]

    @admin.display(description="thesis")
    def get_memories(self, obj):
        return [
            f"{thesis.ucampus_id}: {thesis.title}"
            for thesis in obj.guidedthesis_set.all()
        ]

    @admin.display(description="works")
    def get_works(self, obj):
        return [
            f"{work.openalex_id}: {work.title}" for work in obj.scholarwork_set.all()
        ]


class ScholarWorkAdmin(admin.ModelAdmin):
    search_fields = ["title", "teacher__name"]
    search_help_text = "Buscar por título o docente"
    list_display = ["title", "year", "get_teachers", "get_keywords"]
    filter_horizontal = ("teacher",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return sorted(
            [
                (keyword.keyword.keyword, keyword.score)
                for keyword in obj.scholarworkkeywordrelationship_set.all()
            ],
            key=lambda x: x[1],
            reverse=True,
        )


class ScholarWorkKeywordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["keyword__keyword", "scholar_work__title"]
    search_help_text = "Buscar por keyword o nombre de trabajo"
    list_display = ["keyword", "score", "scholar_work"]


class TeacherKeywordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["keyword__keyword", "teacher__name"]
    search_help_text = "Buscar por keyword o docente"
    list_display = ["keyword", "teacher", "score"]


class GuidedThesisAdmin(admin.ModelAdmin):
    search_fields = ["title", "year", "ucampus_id", "teacher__name"]
    search_help_text = "Buscar por título, año o docente"
    list_display = ["title", "ucampus_id", "year", "get_keywords", "get_teachers"]
    filter_horizontal = ("teacher",)
    exclude = ("doi",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return sorted(
            [
                (keyword.keyword.keyword, keyword.score)
                for keyword in obj.guidedthesiskeywordrelationship_set.all()
            ],
            key=lambda x: x[1],
            reverse=True,
        )


class GuidedThesisKeywordRelationshipdAdmin(admin.ModelAdmin):
    search_fields = ["keyword__keyword", "guided_thesis__title"]
    search_help_text = "Buscar por keyword o memoria/tesis"
    list_display = ["keyword", "score", "guided_thesis"]


class FCFMCoursedAdmin(admin.ModelAdmin):
    search_fields = ["title", "course_code", "year", "teacher__name"]
    search_help_text = "Buscar por título, código, año o docente"
    list_display = ["title", "course_code", "year", "get_keywords", "get_teachers"]
    filter_horizontal = ("teacher",)
    exclude = ("doi",)

    @admin.display(description="teachers")
    def get_teachers(self, obj):
        return [teacher.name for teacher in obj.teacher.all()]

    @admin.display(description="keywords")
    def get_keywords(self, obj):
        return sorted(
            [
                (keyword.keyword.keyword, keyword.score)
                for keyword in obj.fcfmcoursekeywordrelationship_set.all()
            ],
            key=lambda x: x[1],
            reverse=True,
        )


class FCFMCourseKeywordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["keyword__keyword", "fcfm_course__title"]
    search_help_text = "Buscar por keyword o curso"
    list_display = ["keyword", "score", "fcfm_course"]


# Register your models here.
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(TeacherKeywordRelationship, TeacherKeywordRelationshipAdmin)
admin.site.register(ScholarWork, ScholarWorkAdmin)
admin.site.register(ScholarWorkKeywordRelationship, ScholarWorkKeywordRelationshipAdmin)
admin.site.register(FCFMCourse, FCFMCoursedAdmin)
admin.site.register(FCFMCourseKeywordRelationship, FCFMCourseKeywordRelationshipAdmin)
admin.site.register(GuidedThesis, GuidedThesisAdmin)
admin.site.register(
    GuidedThesisKeywordRelationship, GuidedThesisKeywordRelationshipdAdmin
)

# Unregister user and group
admin.site.unregister(Group)
admin.site.unregister(User)
