from django.contrib import admin
from .models import Project, ComponentNode, ConversationMessage

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_type', 'is_synthesized', 'feasibility_score', 'created_at')
    search_fields = ('title', 'problem_statement', 'project_type')
    list_filter = ('project_type', 'is_synthesized', 'created_at')

@admin.register(ComponentNode)
class ComponentNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'category', 'node_id')
    search_fields = ('name', 'description', 'purpose')
    list_filter = ('category',)

@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('role', 'project', 'created_at')
    list_filter = ('role', 'created_at')
