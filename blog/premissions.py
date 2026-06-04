from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
    
class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if request.method in ['GET','HEAD','OPTIONS']:
            return True
        return (
            request.user.is_authenticated and request.user.is_staff
        )
    
class IsCommentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user