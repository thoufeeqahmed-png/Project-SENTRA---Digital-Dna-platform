from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("", views.home_view, name="home"),
    path("projects/", views.projects_list_view, name="projects_list"),
    path("projects/<int:project_id>/", views.project_workspace_view, name="project_workspace"),

    # REST APIs
    path("api/projects/", views.api_projects_collection, name="api_projects_collection"),
    path("api/projects/<int:project_id>/", views.api_project_detail, name="api_project_detail"),
    path("api/projects/<int:project_id>/dna/", views.api_project_dna, name="api_project_dna"),
    path("api/projects/<int:project_id>/analyze/", views.api_project_analyze, name="api_project_analyze"),
    path("api/projects/<int:project_id>/synthesize/", views.api_project_synthesize, name="api_project_synthesize"),
    path("api/projects/<int:project_id>/assistant/", views.api_project_assistant, name="api_project_assistant"),
    path("api/projects/<int:project_id>/build-step/", views.api_project_build_step, name="api_project_build_step"),
]