from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Experience, Project
from main.permissions import (
    IsPortfolioOwnerOrEditorOrReadOnly,
    IsPortfolioOwnerOrReadOnly,
)
from main.serializers import (
    EducationSerializer,
    ExperienceSerializer,
    ProjectSerializer,
)


def _toggle_star(instance, user):
    """Toggle a user's star on a portfolio model instance."""
    if instance.starred_by.filter(pk=user.pk).exists():
        instance.starred_by.remove(user)
    else:
        instance.starred_by.add(user)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    """List all projects (with optional ?title= filter) or create a new project."""
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    """Retrieve, update, or delete a specific project by UUID."""
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    """Toggle the authenticated user's star on a project."""
    project = get_object_or_404(Project, pk=project_id)
    _toggle_star(project, request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    """
    List education entries (supporting ?institution=, ?search=, or ?q= query
    filtering across institution, degree, and field_of_study) or create a new
    education entry (superuser only).
    """
    if request.method in ("GET", "HEAD"):
        educations = Education.objects.prefetch_related("starred_by").order_by(
            "-start_year", "-created_at", "id"
        )
        query = (
            request.query_params.get("institution", "")
            or request.query_params.get("search", "")
            or request.query_params.get("q", "")
        ).strip()
        if query:
            educations = educations.filter(
                Q(institution__icontains=query)
                | Q(degree__icontains=query)
                | Q(field_of_study__icontains=query)
            )
        serializer = EducationSerializer(
            educations, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    """
    Retrieve, update (Editor or superuser via PUT/PATCH), or delete (superuser
    only via DELETE) an education entry by UUID.
    """
    education = get_object_or_404(
        Education.objects.prefetch_related("starred_by"), pk=education_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = EducationSerializer(education, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    """Toggle the authenticated user's star on an education entry."""
    education = get_object_or_404(Education, pk=education_id)
    _toggle_star(education, request.user)
    serializer = EducationSerializer(education, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    """
    List experience entries (supporting ?title=, ?search=, or ?q= query
    filtering across title, description, and category) or create a new
    experience entry (superuser only).
    """
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.prefetch_related("starred_by").order_by(
            "-started_at", "title", "id"
        )
        query = (
            request.query_params.get("title", "")
            or request.query_params.get("search", "")
            or request.query_params.get("q", "")
        ).strip()
        if query:
            experiences = experiences.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__icontains=query)
            )
        serializer = ExperienceSerializer(
            experiences, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    """
    Retrieve, update (Editor or superuser via PUT/PATCH), or delete (superuser
    only via DELETE) an experience entry by UUID.
    """
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"), pk=experience_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ExperienceSerializer(experience, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    """Toggle the authenticated user's star on an experience entry."""
    experience = get_object_or_404(Experience, pk=experience_id)
    _toggle_star(experience, request.user)
    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)
