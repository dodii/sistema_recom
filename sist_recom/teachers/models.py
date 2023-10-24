from django.db import models
from pgvector.django import VectorField, HnswIndex

# Create your models here.


class Teacher(models.Model):
    # Esta id es del repositorio de docentes que construyó Ignacio
    repository_id = models.IntegerField()
    name = models.CharField(max_length=200)
    external_name = models.CharField(max_length=200, blank=True, null=True)

    openalex_id = models.CharField(blank=True, null=True)
    openalex_works_url = models.URLField(blank=True, null=True)

    # El RUT viene de U-Campus
    rut = models.CharField(max_length=50, null=True, blank=True)

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


# Publicaciones
class OpenAlexWork(AbstractTeacherWork):
    openalex_id = models.CharField(max_length=100)
    abstract = models.TextField(max_length=10000, blank=True, null=True)


# Memorias, tesis de magíster y doctorado en las que participaron
class GuidedThesis(AbstractTeacherWork):
    ucampus_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} guiado por {self.teacher}"


# Cursos dictados en la FCFM
class TeacherCourse(AbstractTeacherWork):
    course_code = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} dictado por {self.teacher}"


# Es abstracta para poder ligarla a diferentes elementos como
# docentes, tipos distintos de trabajos, etc., sin la necesidad
# de crear tantos campos que queden null.
class AbstractKeyword(models.Model):
    class Meta:
        abstract = True
        # indexes = [
        #     HnswIndex(
        #         name="embeddings_index",
        #         fields=["embedding"],
        #         m=16,
        #         ef_construction=64,
        #         opclasses=["vector_cosine_ops"],
        #     )
        # ]

    keyword = models.CharField(max_length=100)
    embedding = VectorField(dimensions=768, null=True, blank=True)


class TeacherKeyword(AbstractKeyword):
    teacher = models.ManyToManyField(Teacher)


class TeacherWorkKeyword(AbstractKeyword):
    associated_work = models.ManyToManyField(OpenAlexWork)


class TeacherCourseKeyword(AbstractKeyword):
    associated_course = models.ManyToManyField(TeacherCourse)


class GuidedThesisKeyword(AbstractKeyword):
    associated_thesis = models.ManyToManyField(GuidedThesis)
