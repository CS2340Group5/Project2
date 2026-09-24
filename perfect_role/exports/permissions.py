from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def is_platform_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'ADMIN')


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_platform_admin(request.user):
            return HttpResponseForbidden('Admin privileges required to export platform data!')
        return view_func(request, *args, **kwargs)
    return wrapper