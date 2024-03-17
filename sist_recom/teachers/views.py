import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from teachers.utils.input_processing import extract_input_keywords
from teachers.transformers.embeddings_and_filtering import (
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

    else:
        return redirect("/")


def ranking_result(request):
    if request.method == "POST":
        try:
            json_data = json.loads(request.POST["form_data"])
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        title = json_data["title"]
        keywords = json_data["keywords"]
        scores = [float(score) for score in json_data["scores"]]

        # top_n = request.POST.get("top_n", "")

        teachers = teacher_ranking_keywords_approach(keywords, scores)

        return render(
            request,
            "ranking_result.html",
            {
                "teachers": teachers[0].items(),
                "title": title,
                "works": teachers[1].items(),
            },
        )

    else:
        return redirect(request, "index.html")
