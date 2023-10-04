from django.db import models
from pgvector.django import VectorField
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Teacher(models.Model):
    repository_id = models.IntegerField()
    dblp_id = models.CharField(blank=True, null=True)
    name = models.CharField(max_length=200)
    external_name = models.CharField(max_length=200, blank=True, null=True)

    openalex_id = models.CharField(blank=True, null=True)
    openalex_works_url = models.URLField(blank=True, null=True)
    # concepts = ArrayField(models.CharField(max_length=200))

    def __str__(self):
        return f"{self.name}".strip()


class WordEmbedding(models.Model):
    embedding = VectorField(dimensions=768)
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)


class AbstractTeacherWork(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=1000)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.title) + " de " + str(self.teacher)


class DBLPWork(AbstractTeacherWork):
    class Meta:
        db_table = "teachers_dblpworkmodel"


class OpenAlexWork(AbstractTeacherWork):
    abstract = models.TextField(max_length=10000, blank=True, null=True)
    openalex_concepts = ArrayField(
        models.CharField(max_length=200), blank=True, null=True
    )

    class Meta:
        db_table = "teachers_openalexworkmodel"
