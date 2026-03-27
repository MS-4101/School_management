from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*role_names):
    """Decorator that checks if the user has any of the specified roles."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if any(request.user.has_role(r) for r in role_names):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:home')
        return _wrapped
    return decorator


def permission_required(codename):
    """Decorator that checks if the user's roles grant a specific permission codename."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.has_perm_code(codename):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to perform this action.')
            return redirect('dashboard:home')
        return _wrapped
    return decorator


def section_required(section_codename, required_level='view'):
    """Decorator that checks if the user has access to a specific system section/module."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if request.user.has_section_access(section_codename, required_level):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, f'Access Denied: You do not have {required_level} permission for the {section_codename} module.')
            return redirect('dashboard:home')
        return _wrapped
    return decorator


class SectionRequiredMixin:
    """Mixin for Class-Based Views to enforce section-based permissions."""
    section_codename = None
    required_level = 'view'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        if not self.section_codename:
            # If no codename set, allow by default (or you could choose to deny)
            return super().dispatch(request, *args, **kwargs)

        if request.user.has_section_access(self.section_codename, self.required_level):
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, f'Access Denied: You do not have {self.required_level} permission for the {self.section_codename} module.')
        return redirect('dashboard:home')
