from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """
    Allow read-only access to all users, and full write access only to the
    portfolio owner (superuser).
    """

    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """
    Enforce 4-role portfolio access control on API endpoints:
    - Guest (unauthenticated) & Regular User: read-only (SAFE_METHODS).
    - Editor (member of 'Editor' group): read + update (PUT, PATCH), no create/delete.
    - Portfolio Owner (superuser): full CRUD access (GET, POST, PUT, PATCH, DELETE).
    """

    message = "You do not have permission to perform this action on this portfolio resource."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
