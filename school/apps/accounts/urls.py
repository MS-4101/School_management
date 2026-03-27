from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('bus-logout/', views.bus_logout_view, name='bus_logout'),
    path('profile/', views.profile_view, name='profile'),

    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),

    # Permissions
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/create/', views.permission_create, name='permission_create'),
    path('permissions/<int:pk>/delete/', views.permission_delete, name='permission_delete'),

    # ── Access Control Hub ─────────────────────────────────────
    path('access-control/', views.access_control, name='access_control'),
    path('access-control/create-user/', views.create_user, name='create_user'),
    path('access-control/create-school/', views.create_school, name='create_school'),
    path('access-control/save-permissions/', views.save_role_permissions, name='save_role_permissions'),
    path('access-control/create-role/', views.create_role_with_permissions, name='create_role'),
]
