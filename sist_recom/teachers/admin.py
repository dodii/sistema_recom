from django.contrib import admin
from .models import Teacher, WordEmbedding, DBLPWork, OpenAlexWork
from django.contrib.auth.models import User, Group


class TeacherAdmin(admin.ModelAdmin):
    list_display = ["name", "dblp_id", "openalex_id"]


class DBLPWorkAdmin(admin.ModelAdmin):
    list_display = ["title", "teacher", "year"]


class OpenAlexAdmin(admin.ModelAdmin):
    list_display = ["title", "teacher", "year"]


# Register your models here.
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(DBLPWork, DBLPWorkAdmin)
admin.site.register(OpenAlexWork, OpenAlexAdmin)
admin.site.register(WordEmbedding)

# Unregister user and group
admin.site.unregister(Group)
admin.site.unregister(User)
