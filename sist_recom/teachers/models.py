from django.db import models
from pgvector.django import VectorField

# Create your models here.


class Teacher(models.Model):
    repository_id = models.IntegerField()
    dblp_id = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    external_name = models.CharField(max_length=200, blank=True, null=True)

    openalex_id = models.CharField(blank=True, null=True)
    openalex_works_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}".strip()


class AbstractTeacherWork(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=1000)
    teacher = models.ManyToManyField(Teacher)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    doi = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class DBLPWork(AbstractTeacherWork):
    pass


class OpenAlexWork(AbstractTeacherWork):
    openalex_id = models.CharField(max_length=100, null=True, blank=True)
    abstract = models.TextField(max_length=10000, blank=True, null=True)


class GuidedThesis(AbstractTeacherWork):
    def __str__(self):
        return f"{self.title} guiado por {self.teacher}"


# Es abstracta para poder ligarla a diferentes elementos como
# docentes, tipos distintos de trabajos, etc.
class AbstractKeyword(models.Model):
    class Meta:
        abstract = True

    keyword = models.CharField(max_length=100)
    embedding = VectorField(dimensions=768, null=True, blank=True)


class TeacherKeyword(AbstractKeyword):
    teacher = models.ManyToManyField(Teacher)


class TeacherWorkKeyword(AbstractKeyword):
    associated_work = models.ManyToManyField(OpenAlexWork)


class GuidedThesisKeyword(AbstractKeyword):
    associated_thesis = models.ManyToManyField(GuidedThesis)
