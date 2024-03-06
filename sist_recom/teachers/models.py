from django.db import models
from pgvector.django import VectorField, HnswIndex

# Create your models here.


class Keyword(models.Model):
    keyword = models.CharField(max_length=100, primary_key=True)
    embedding = VectorField(dimensions=768, null=True, blank=True)

    def __str__(self):
        return self.keyword


class Teacher(models.Model):
    # El RUT viene de U-Campus
    rut = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200, blank=True, null=True)

    # datos que se recogen manualmente
    openalex_id = models.CharField(blank=True, null=True)
    openalex_works_url = models.URLField(blank=True, null=True)
    dblp_id = models.CharField(blank=True, null=True)

    keyword = models.ManyToManyField(Keyword, through="TeacherKeywordRelationship")

    def __str__(self):
        return f"{self.name}".strip()


class BaseTeacherWork(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=1000)
    teacher = models.ManyToManyField(Teacher)
    year = models.CharField(max_length=50, blank=True, null=True)

    embedding_name = VectorField(dimensions=768)

    def __str__(self):
        return f"{self.title} ({self.year})"


# Publicaciones
class ScholarWork(BaseTeacherWork):
    keyword = models.ManyToManyField(Keyword, through="ScholarWorkKeywordRelationship")

    openalex_id = models.CharField(max_length=100, primary_key=True)
    abstract = models.TextField(max_length=10000, blank=True, null=True)
    doi = models.CharField(max_length=500, blank=True, null=True)


# Memorias, tesis de magíster y doctorado que han guiado/co-guiado
class GuidedThesis(BaseTeacherWork):
    keyword = models.ManyToManyField(Keyword, through="GuidedThesisKeywordRelationship")
    ucampus_id = models.CharField(max_length=100, primary_key=True)


# Cursos dictados en la FCFM
class FCFMCourse(BaseTeacherWork):
    keyword = models.ManyToManyField(Keyword, through="FCFMCourseKeywordRelationship")
    course_code = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"{self.course_code} - {self.title} ({self.year})"


class BaseKeywordRelationship(models.Model):
    class Meta:
        abstract = True

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)


class TeacherKeywordRelationship(BaseKeywordRelationship):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("teacher", "keyword")


class ScholarWorkKeywordRelationship(BaseKeywordRelationship):
    scholar_work = models.ForeignKey(ScholarWork, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("scholar_work", "keyword")


class FCFMCourseKeywordRelationship(BaseKeywordRelationship):
    fcfm_course = models.ForeignKey(FCFMCourse, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("fcfm_course", "keyword")


class GuidedThesisKeywordRelationship(BaseKeywordRelationship):
    guided_thesis = models.ForeignKey(GuidedThesis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("guided_thesis", "keyword")
