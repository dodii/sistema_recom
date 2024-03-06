import ast
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from teachers.utils.input_processing import extract_input_keywords
from teachers.transformers.embeddings_download import (
    teacher_ranking_keywords_approach,
)


def index(request):
    return render(request, "index.html")


def keywords_result(request):
    if request.method == "POST":
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")

        keywords_result, scores = extract_input_keywords(title, content)
        keywords_scores = zip(keywords_result, scores)

        return render(
            request,
            "keywords_result.html",
            {
                "keywords_scores": keywords_scores,  # pairs
                "keywords_result": keywords_result,
                "scores": scores,
                "title": title,
            },
        )

        # return HttpResponseRedirect(
        #     reverse("ranking_result"),
        #     {"keywords_result": keywords_result, "scores": scores},
        # )

    else:
        return redirect("/")


def ranking_result(request):
    if request.method == "POST":
        keywords = request.POST.get("keywords", "").split(",")
        scores = request.POST.get("scores", "").split(",")
        parsed_scores = [float(score) for score in scores]
        # # top_n = request.POST.get("top_n", "")
        title = request.POST.get("title", "")

        # por ahora top_n hardcoded
        teachers = teacher_ranking_keywords_approach(keywords, parsed_scores, 7)

        return render(
            request,
            "ranking_result.html",
            {"teachers": teachers[0].items(), "title": title},
        )

    else:
        return redirect(request, "index.html")
