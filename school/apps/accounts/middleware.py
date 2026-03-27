class SchoolTenantMiddleware:
    """
    Middleware to attach the current School (tenant) to the request.
    For school admins: request.school = their school.
    For parents: request.school = parent's linked school.
    For bus sessions: request.school derived from bus.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.school = None

        if request.user.is_authenticated:
            if hasattr(request.user, 'school'):
                try:
                    request.school = request.user.school
                except Exception:
                    pass
            if request.school is None and hasattr(request.user, 'parent_profile'):
                try:
                    request.school = request.user.parent_profile.school
                except Exception:
                    pass

        # Bus session-based school
        if request.school is None and request.session.get('bus_login'):
            bus_id = request.session.get('bus_id')
            if bus_id:
                try:
                    from apps.buses.models import Bus
                    bus = Bus.objects.select_related('school').get(id=bus_id)
                    request.school = bus.school
                except Exception:
                    pass

        return self.get_response(request)
