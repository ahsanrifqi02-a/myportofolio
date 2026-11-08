import re
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Experience, Project

_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)


def sanitize_text(value):
    """Remove script/style blocks and strip remaining HTML tags."""
    if value is None:
        return ""
    cleaned = _SCRIPT_STYLE_RE.sub("", str(value))
    return strip_tags(cleaned)


class StarredModelSerializerMixin(serializers.Serializer):
    """
    Reusable read-only computed fields for models supporting user stars.
    Exposes only non-sensitive public information (count, current user star
    status, and comma-separated usernames).
    """

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ProjectSerializer(StarredModelSerializerMixin, serializers.ModelSerializer):
    """Serializer for Project instances with XSS tag stripping and star metrics."""

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = sanitize_text(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return sanitize_text(value)

    def validate_tech_stack(self, value):
        return sanitize_text(value)


class EducationSerializer(StarredModelSerializerMixin, serializers.ModelSerializer):
    """
    Serializer for Education instances.
    Sanitizes text fields with strip_tags and computes read-only star and
    ongoing status fields without exposing sensitive user credentials.
    """

    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Education
        fields = [
            "id",
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "is_ongoing",
            "description",
            "logo_url",
            "star_count",
            "is_starred",
            "starred_by_names",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_ongoing", "created_at", "updated_at"]

    def validate_institution(self, value):
        value = sanitize_text(value).strip()
        if not value:
            raise serializers.ValidationError("Institution cannot be empty.")
        return value

    def validate_degree(self, value):
        value = sanitize_text(value).strip()
        if not value:
            raise serializers.ValidationError("Degree cannot be empty.")
        return value

    def validate_field_of_study(self, value):
        return sanitize_text(value).strip()

    def validate_description(self, value):
        return sanitize_text(value).strip()

    def validate_start_year(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("Start year must be between 1900 and 2100.")
        return value

    def validate_end_year(self, value):
        if value is not None and (value < 1900 or value > 2100):
            raise serializers.ValidationError("End year must be between 1900 and 2100.")
        return value

    def validate(self, attrs):
        start_year = attrs.get(
            "start_year",
            getattr(self.instance, "start_year", None),
        )
        end_year = attrs.get(
            "end_year",
            getattr(self.instance, "end_year", None) if "end_year" not in attrs else None,
        )
        if start_year is not None and end_year is not None and end_year < start_year:
            raise serializers.ValidationError(
                {"end_year": "End year cannot be earlier than start year."}
            )
        return attrs


class ExperienceSerializer(StarredModelSerializerMixin, serializers.ModelSerializer):
    """
    Serializer for Experience instances.
    Sanitizes text fields with strip_tags and exposes read-only star and
    category display fields.
    """

    is_ongoing = serializers.BooleanField(read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "category",
            "category_display",
            "description",
            "started_at",
            "ended_at",
            "is_ongoing",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id", "is_ongoing", "category_display"]

    def validate_title(self, value):
        value = sanitize_text(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        value = sanitize_text(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def validate(self, attrs):
        started_at = attrs.get(
            "started_at",
            getattr(self.instance, "started_at", None),
        )
        ended_at = attrs.get(
            "ended_at",
            getattr(self.instance, "ended_at", None) if "ended_at" not in attrs else None,
        )
        if started_at is not None and ended_at is not None and ended_at < started_at:
            raise serializers.ValidationError(
                {"ended_at": "End date cannot be earlier than start date."}
            )
        return attrs
