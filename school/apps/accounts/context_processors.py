from .models import SectionPermission


def section_access(request):
    """
    Context processor: injects `user_section_access` dict into every template.
    Format: {'library': 'full', 'lab': 'view', 'inventory': 'none', ...}
    Superusers get 'full' access to everything.
    """
    access = {}

    if not request.user.is_authenticated:
        return {'user_section_access': access}

    if request.user.is_superuser:
        # Superuser gets full access to all sections
        try:
            from .models import Section
            for section in Section.objects.all():
                access[section.codename] = 'full'
        except Exception:
            pass
        return {'user_section_access': access}

    # RBAC: aggregate access from all user roles
    try:
        sp_qs = SectionPermission.objects.filter(
            role__users=request.user
        ).select_related('section')

        for sp in sp_qs:
            existing = access.get(sp.section.codename, 'none')
            # Escalate: full > view > none
            if existing == 'none' or (existing == 'view' and sp.access_level == 'full'):
                access[sp.section.codename] = sp.access_level
    except Exception:
        pass

    return {'user_section_access': access}
