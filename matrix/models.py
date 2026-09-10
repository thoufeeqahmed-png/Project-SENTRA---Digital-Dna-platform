from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=255)
    project_type = models.CharField(max_length=100, default="Software System")
    idea_input = models.TextField(blank=True, default="")
    problem_statement = models.TextField(blank=True, default="")
    goal = models.TextField(blank=True, default="")
    summary = models.TextField(blank=True, default="")
    target_users = models.JSONField(default=list, blank=True)
    
    is_synthesized = models.BooleanField(default=False)
    
    feasibility_score = models.IntegerField(default=85)
    feasibility_summary = models.TextField(blank=True, default="")
    feasibility_breakdown = models.JSONField(default=dict, blank=True)
    feasibility_details = models.JSONField(default=dict, blank=True)
    
    tech_stack = models.JSONField(default=dict, blank=True)
    dna_data = models.JSONField(default=dict, blank=True)
    architecture_data = models.JSONField(default=dict, blank=True)
    build_plan = models.JSONField(default=list, blank=True)
    risks_mitigations = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def build_progress_percent(self):
        if not self.build_plan:
            return 0
        total = len(self.build_plan)
        completed = sum(1 for step in self.build_plan if step.get('status') == 'completed')
        return int((completed / total) * 100)


class ComponentNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='components')
    node_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default="Core Logic")
    purpose = models.CharField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    inputs = models.JSONField(default=list, blank=True)
    outputs = models.JSONField(default=list, blank=True)
    technologies = models.JSONField(default=list, blank=True)
    dependencies = models.JSONField(default=list, blank=True)
    connected_components = models.JSONField(default=list, blank=True)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} ({self.project.title})"


class ConversationMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    action_applied = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."
