import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Project, ComponentNode, ConversationMessage
from .ai_service import (
    generate_project_dna,
    synthesize_project_architecture,
    process_project_assistant_interaction,
    DEFAULT_ASSISTANT_INTRO
)


# ---------------- PAGE VIEWS ---------------- #

def home_view(request):
    """Home page with input 'What do you want to build?'"""
    recent_projects = Project.objects.all()[:6]
    return render(request, "matrix/home.html", {
        "recent_projects": recent_projects,
        "assistant_intro": DEFAULT_ASSISTANT_INTRO
    })


def projects_list_view(request):
    """Projects history directory page."""
    projects = Project.objects.all()
    return render(request, "matrix/projects_list.html", {
        "projects": projects
    })


def project_workspace_view(request, project_id):
    """Central interactive Project Workspace page."""
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "matrix/project_workspace.html", {
        "project": project,
        "assistant_intro": DEFAULT_ASSISTANT_INTRO
    })


# ---------------- API ENDPOINTS ---------------- #

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_projects_collection(request):
    """
    GET: List all projects.
    POST: Create project from idea, generate DNA, save to DB, and return redirect URL.
    """
    if request.method == "GET":
        projects = Project.objects.all()[:50]
        data = [
            {
                "id": p.id,
                "title": p.title,
                "project_type": p.project_type,
                "feasibility_score": p.feasibility_score,
                "is_synthesized": p.is_synthesized,
                "build_progress": p.build_progress_percent,
                "created_at": p.created_at.strftime("%b %d, %Y %H:%M"),
            }
            for p in projects
        ]
        return JsonResponse({"projects": data})

    # POST: Generate Project DNA
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    idea = body.get("idea", "").strip()
    if not idea:
        return JsonResponse({"error": "Please describe what you want to build."}, status=400)

    try:
        # 1. Call AI Service to generate structured Project DNA
        dna = generate_project_dna(idea)

        # 2. Persist Project in Database
        project = Project.objects.create(
            title=dna.get("project_name", "Autonomous System"),
            project_type=dna.get("project_type", "Software System"),
            idea_input=idea,
            problem_statement=dna.get("problem", ""),
            goal=dna.get("goal", ""),
            summary=dna.get("summary", ""),
            target_users=dna.get("target_users", []),
            feasibility_score=dna.get("feasibility", {}).get("score", 88),
            feasibility_summary=dna.get("feasibility", {}).get("assessment", ""),
            feasibility_details=dna.get("feasibility", {}),
            tech_stack={
                "software": dna.get("software", []),
                "hardware": dna.get("hardware", []),
                "data": dna.get("data", [])
            },
            dna_data=dna,
            build_plan=dna.get("build_steps", []),
            risks_mitigations=dna.get("risks", [])
        )

        # 3. Create ComponentNode records
        for idx, c in enumerate(dna.get("components", [])):
            ComponentNode.objects.create(
                project=project,
                node_id=c.get("id", f"comp-{idx}"),
                name=c.get("name", "Component"),
                category=c.get("category", "Processing"),
                purpose=c.get("purpose", ""),
                description=c.get("description", ""),
                inputs=c.get("inputs", []),
                outputs=c.get("outputs", []),
                technologies=c.get("technologies", []),
                dependencies=c.get("dependencies", []),
                connected_components=c.get("connected_components", []),
                position_x=120 + (idx % 5) * 190,
                position_y=140 + (idx // 5) * 180
            )

        # 4. Initial Assistant Welcome Message
        welcome_msg = (
            f"{DEFAULT_ASSISTANT_INTRO} I have completed the architectural deconstruction for '{project.title}'. "
            f"You are now inside the Project Workspace. You can inspect your Digital DNA, synthesize deeper system architecture, "
            f"review the 5-phase build plan, or ask me to modify components."
        )
        ConversationMessage.objects.create(
            project=project,
            role="assistant",
            content=welcome_msg
        )

        return JsonResponse({
            "success": True,
            "id": project.id,
            "redirect": f"/projects/{project.id}/",
            "project_name": project.title
        })

    except Exception as e:
        print("Project creation failed:", e)
        return JsonResponse({"error": "Something went wrong while generating your Project DNA. Please try again."}, status=500)


@require_http_methods(["GET"])
def api_project_detail(request, project_id):
    """Returns complete project representation."""
    p = get_object_or_404(Project, pk=project_id)
    components = [
        {
            "id": c.node_id,
            "name": c.name,
            "category": c.category,
            "purpose": c.purpose,
            "description": c.description,
            "inputs": c.inputs,
            "outputs": c.outputs,
            "technologies": c.technologies,
            "dependencies": c.dependencies,
            "connected_components": c.connected_components,
            "position": {"x": c.position_x, "y": c.position_y}
        }
        for c in p.components.all()
    ]
    messages = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.strftime("%H:%M")
        }
        for m in p.messages.all()
    ]
    return JsonResponse({
        "id": p.id,
        "title": p.title,
        "project_type": p.project_type,
        "problem": p.problem_statement,
        "goal": p.goal,
        "summary": p.summary,
        "target_users": p.target_users,
        "is_synthesized": p.is_synthesized,
        "feasibility_score": p.feasibility_score,
        "feasibility_summary": p.feasibility_summary,
        "feasibility_details": p.feasibility_details,
        "tech_stack": p.tech_stack,
        "dna_data": p.dna_data,
        "architecture_data": p.architecture_data,
        "build_plan": p.build_plan,
        "build_progress": p.build_progress_percent,
        "components": components,
        "messages": messages,
        "created_at": p.created_at.strftime("%b %d, %Y %H:%M")
    })


@require_http_methods(["GET"])
def api_project_dna(request, project_id):
    """Returns pure Project DNA structure."""
    p = get_object_or_404(Project, pk=project_id)
    return JsonResponse({"dna": p.dna_data})


@csrf_exempt
@require_http_methods(["POST"])
def api_project_analyze(request, project_id):
    """Re-analyzes and regenerates Project DNA from current or updated idea."""
    p = get_object_or_404(Project, pk=project_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        idea = data.get("idea", p.idea_input)
    except Exception:
        idea = p.idea_input

    dna = generate_project_dna(idea)
    p.title = dna.get("project_name", p.title)
    p.project_type = dna.get("project_type", p.project_type)
    p.problem_statement = dna.get("problem", p.problem_statement)
    p.goal = dna.get("goal", p.goal)
    p.summary = dna.get("summary", p.summary)
    p.target_users = dna.get("target_users", p.target_users)
    p.feasibility_score = dna.get("feasibility", {}).get("score", p.feasibility_score)
    p.dna_data = dna
    p.build_plan = dna.get("build_steps", p.build_plan)
    p.save()

    return JsonResponse({"success": True, "dna": dna})


@csrf_exempt
@require_http_methods(["POST"])
def api_project_synthesize(request, project_id):
    """
    SYNTHESIZE PROJECT: Uses Project DNA to generate deep system architecture,
    component relationships, data flow sequences, and decision logic.
    """
    p = get_object_or_404(Project, pk=project_id)
    
    try:
        # Perform architectural synthesis
        arch = synthesize_project_architecture(p)
        p.architecture_data = arch
        p.is_synthesized = True
        p.save()

        # Record synthesis event in assistant chat
        ConversationMessage.objects.create(
            project=p,
            role="assistant",
            content=f"{DEFAULT_ASSISTANT_INTRO} System architecture synthesis complete. Component relationships, data flow pipes, and decision states have been mapped. You can now proceed to [View Architecture] or [Check Feasibility]."
        )

        return JsonResponse({
            "success": True,
            "architecture": arch,
            "message": "Project synthesized successfully."
        })
    except Exception as e:
        print("Synthesis failed:", e)
        return JsonResponse({"error": "Failed to synthesize project architecture. Please try again."}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_project_assistant(request, project_id):
    """
    Project-aware AI assistant endpoint:
    Answers project questions OR performs live AI modifications to Project DNA.
    """
    p = get_object_or_404(Project, pk=project_id)
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_message = body.get("message", "").strip()
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)

    # Save user message
    ConversationMessage.objects.create(
        project=p,
        role="user",
        content=user_message
    )

    # Process via AI Service
    reply, modified = process_project_assistant_interaction(p, user_message)

    # Save assistant message
    ConversationMessage.objects.create(
        project=p,
        role="assistant",
        content=reply,
        action_applied=modified
    )

    # If modified, refresh project data
    if modified:
        p.refresh_from_db()

    return JsonResponse({
        "success": True,
        "reply": reply,
        "modified": modified,
        "build_progress": p.build_progress_percent
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_project_build_step(request, project_id):
    """
    Toggles completion of a build step in the database and recalculates progress.
    """
    p = get_object_or_404(Project, pk=project_id)
    try:
        body = json.loads(request.body.decode('utf-8'))
        step_number = int(body.get("step_number", 1))
        is_completed = bool(body.get("completed", False))
    except Exception:
        return JsonResponse({"error": "Invalid step parameters."}, status=400)

    plan = p.build_plan or []
    for step in plan:
        if step.get("step_number") == step_number:
            step["status"] = "completed" if is_completed else "current"
            break

    p.build_plan = plan
    p.save()

    return JsonResponse({
        "success": True,
        "build_progress": p.build_progress_percent,
        "build_plan": p.build_plan
    })
