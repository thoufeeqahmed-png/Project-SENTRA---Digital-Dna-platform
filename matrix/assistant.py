"""Project-aware engineering assistant. Answers from DNA; returns visual actions."""

from __future__ import annotations

import json
import re

def _components(project):
    dna = project.dna_data or {}
    return list(dna.get("components") or [])


def _find_component(project, message: str):
    msg = message.lower()
    best = None
    best_score = 0
    for c in _components(project):
        name = (c.get("name") or "").lower()
        words = [w for w in re.findall(r"[a-z0-9]+", name) if len(w) > 3]
        score = sum(1 for w in words if w in msg)
        if any(w in msg for w in ("sensor", "camera", "database", "controller", "pump", "ai", "dashboard", "server")):
            kind_hits = {
                "sensor": "sensor" in name or "probe" in name or "moisture" in name,
                "camera": "camera" in name or "rtsp" in name or "vision" in name,
                "database": "database" in name or "vector" in name or "store" in name,
                "controller": "controller" in name or "decision" in name,
                "pump": "pump" in name or "valve" in name or "actuator" in name,
                "dashboard": "dashboard" in name or "hud" in name or "portal" in name,
                "ai": "neural" in name or "model" in name or "intelligence" in name or "arcface" in name,
                "server": "gateway" in name or "api" in name or "server" in name,
            }
            for key, hit in kind_hits.items():
                if key in msg and hit:
                    score += 3
        if score > best_score:
            best_score = score
            best = c
    if best_score == 0:
        for c in _components(project):
            name = (c.get("name") or "").lower()
            if any(w in name for w in msg.split() if len(w) > 4):
                return c
    return best if best_score else None


def _dependents(project, component):
    cid = component.get("id")
    name = component.get("name")
    affected = []
    for c in _components(project):
        deps = c.get("dependencies") or []
        connected = c.get("connected_components") or []
        if cid in deps or name in connected:
            affected.append(c)
    return affected


def _view_action(view: str):
    return {"type": "switch_view", "view": view}


def _highlight(comp):
    if not comp:
        return []
    return [
        {"type": "highlight", "component_id": comp.get("id"), "name": comp.get("name")},
        {"type": "focus_3d", "component_id": comp.get("id")},
    ]


def parse_visual_intents(project, message: str):
    msg = message.lower()
    actions = []
    if any(k in msg for k in ("show architecture", "show the architecture", "architecture view")):
        actions.append(_view_action("architecture"))
    if any(k in msg for k in ("data flow", "where does the data", "data go", "show flow")):
        actions.append(_view_action("data-flow"))
    if any(k in msg for k in ("3d", "3-d", "model", "show the project")) and "component" not in msg:
        if "show" in msg or "open" in msg:
            actions.append(_view_action("model-3d"))
    if any(k in msg for k in ("simulation", "expected output", "prediction", "what happens if soil")):
        if "show" in msg or "expected" in msg:
            actions.append(_view_action("prediction"))
    if any(k in msg for k in ("feasibility", "is this feasible")):
        actions.append(_view_action("feasibility"))
    if any(k in msg for k in ("build plan", "build first", "roadmap")):
        actions.append(_view_action("build-plan"))
    if any(k in msg for k in ("dna", "overview")):
        actions.append(_view_action("overview"))

    target = _find_component(project, message)
    if target and any(k in msg for k in ("show", "highlight", "where is", "select", "explain this", "explain the")):
        actions.append(_view_action("model-3d"))
        actions.extend(_highlight(target))
        if "data" in msg or "flow" in msg:
            path = [component.get("id") for component in _components(project)]
            actions.append({"type": "highlight_path", "component_ids": [target.get("id")] + [d.get("id") for d in _dependents(project, target)]})
    elif target and any(k in msg for k in ("show me", "highlight")):
        actions.extend(_highlight(target))
    return actions, target


def answer_engineering_question(project, message: str):
    dna = project.dna_data or {}
    comps = _components(project)
    msg = message.lower().strip()
    actions, target = parse_visual_intents(project, message)
    title = project.title

    def join_names(items, key="name"):
        return ", ".join(c.get(key) for c in items if c.get(key)) or "the connected modules"

    # How it works
    if any(p in msg for p in ("how does this", "how does it work", "how the project work", "explain this project", "explain the project")):
        flow = dna.get("workflow") or " → ".join(c.get("name", "") for c in comps)
        pieces = []
        for c in comps[:6]:
            inn = (c.get("inputs") or ["input"])[0]
            out = (c.get("outputs") or ["output"])[0]
            pieces.append(f"{c.get('name')} takes {inn} and produces {out}.")
        body = " ".join(pieces[:4]) if pieces else (project.summary or "")
        reply = f"{body} End-to-end path: {flow}"
        actions = [_view_action("data-flow")] + actions
        return reply, actions

    if any(p in msg for p in ("what should i build first", "build first", "where do i start", "first step")):
        steps = project.build_plan or []
        first = steps[0] if steps else None
        if first:
            comps_needed = ", ".join(first.get("required_components") or []) or "the first component"
            reply = (
                f"Start with {first.get('title')}. {first.get('description')} "
                f"You need: {comps_needed}. Done means: {first.get('expected_result')}."
            )
        else:
            first_comp = comps[0]["name"] if comps else "the input layer"
            reply = f"Start by getting {first_comp} working in isolation, then connect the next stage."
        actions = [_view_action("build-plan")] + actions
        return reply, actions

    if target and (msg.startswith("why") or "why do i need" in msg or "why the" in msg):
        reply = (
            f"{target.get('name')} exists because {target.get('purpose') or target.get('description')}. "
            f"It consumes {(target.get('inputs') or ['upstream data'])[0]} and emits {(target.get('outputs') or ['downstream data'])[0]}."
        )
        actions = _highlight(target) + actions
        return reply, actions

    if target and any(p in msg for p in ("if i remove", "remove this", "if the", "fails", "fail", "what happens if")):
        affected = _dependents(project, target)
        names = join_names(affected)
        fail = "fails" in msg or "fail" in msg
        if fail:
            reply = (
                f"If {target.get('name')} fails, downstream stages lose {(target.get('outputs') or ['their input'])[0]}. "
                f"Affected: {names}. Add a health check and a safe fallback before automatic actuation."
            )
        else:
            reply = (
                f"Removing {target.get('name')} breaks {names or 'later stages'} because they depend on "
                f"{(target.get('outputs') or ['its output'])[0]}. The remaining DNA would have a missing {target.get('category') or 'layer'}."
            )
        actions = [_view_action("data-flow"), {"type": "highlight_path", "component_ids": [target.get("id")] + [a.get("id") for a in affected]}]
        return reply, actions

    if "data go" in msg or "where does the data" in msg or "data flow" in msg:
        chain = []
        for c in comps:
            chain.append(f"{c.get('name')} ({c.get('category')})")
        reply = " → ".join(chain) if chain else (dna.get("workflow") or "No data-flow graph yet. Synthesize architecture first.")
        actions = [_view_action("data-flow"), {"type": "highlight_path", "component_ids": [c.get("id") for c in comps]}]
        return reply, actions

    if target and ("explain" in msg or "what is" in msg or "what does" in msg):
        ins = ", ".join(target.get("inputs") or ["none listed"])
        outs = ", ".join(target.get("outputs") or ["none listed"])
        deps = ", ".join(target.get("dependencies") or ["none"])
        reply = (
            f"{target.get('name')} is a {target.get('category') or 'component'} layer. "
            f"{target.get('purpose') or target.get('description')} "
            f"Enters: {ins}. Leaves: {outs}. Depends on: {deps}."
        )
        actions = _highlight(target) + [_view_action("components")]
        return reply, actions

    if "risk" in msg:
        risks = project.risks_mitigations or dna.get("risks") or []
        if isinstance(risks, list) and risks:
            items = []
            for r in risks[:4]:
                items.append(r if isinstance(r, str) else r.get("risk", str(r)))
            reply = "Main risks: " + "; ".join(items) + ". Treat them as engineering constraints, not as scored predictions."
        else:
            reply = f"No explicit risk list stored for {title}. Add sensor failure, connectivity loss, and bad input handling at minimum."
        actions = [_view_action("feasibility")]
        return reply, actions

    if "feasib" in msg:
        fd = project.feasibility_details or {}
        reply = (
            f"Technical feasibility is {fd.get('technical') or 'qualitative only'}. "
            f"Complexity: {fd.get('complexity') or 'unspecified'}. "
            f"{project.feasibility_summary or ''} The score is a heuristic label, not a measured metric."
        )
        actions = [_view_action("feasibility")]
        return reply, actions

    if "expected output" in msg or "prediction" in msg or "simulate" in msg:
        outs = ", ".join(dna.get("outputs") or ["the system output"])
        reply = (
            f"Expected outputs for {title}: {outs}. Open Simulation to change inputs. "
            "Results are rule-based simulation, not a trained model score."
        )
        actions = [_view_action("prediction")]
        return reply, actions

    if comps and len(msg.split()) <= 4 and target:
        reply = f"{target.get('name')}: {target.get('purpose') or target.get('description')}"
        actions = _highlight(target)
        return reply, actions

    # Generic but still project-specific — never the same canned sentence.
    first = comps[0] if comps else None
    last = comps[-1] if comps else None
    mid = f" From {first.get('name')} to {last.get('name')}." if first and last else ""
    reply = (
        f"{title} currently has {len(comps)} mapped components.{mid} "
        f"Ask how a named part works, what to build first, or say 'show the controller' to highlight it."
    )
    return reply, actions


def apply_architecture_change(project, message: str):
    from .models import ComponentNode
    from .visual_map import synthesize_architecture

    dna = project.dna_data or {}
    components = list(dna.get("components") or [])
    msg = message.lower()
    updated = False
    change_desc = ""
    actions = []

    def persist():
        dna["components"] = components
        project.dna_data = dna
        project.architecture_data = synthesize_architecture(project)
        project.save(update_fields=["dna_data", "architecture_data", "updated_at"])
        project.components.all().delete()
        for idx, c in enumerate(components):
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
                position_y=140 + (idx // 5) * 180,
            )

    if "mobile" in msg and "add" in msg:
        if not any("mobile" in c.get("name", "").lower() for c in components):
            components.insert(0, {
                "id": f"comp-mobile-{len(components)+1}",
                "name": "Mobile companion app",
                "category": "Input",
                "purpose": "Lets operators monitor status and send remote commands from a phone.",
                "description": "Phone client talking to the existing API/gateway.",
                "inputs": ["Operator taps", "Push permission"],
                "outputs": ["Remote commands", "Device token"],
                "technologies": ["Flutter or React Native"],
                "dependencies": [],
                "connected_components": [components[0]["name"] if components else "API"],
            })
            updated = True
            change_desc = "Added a mobile companion app at the input edge of the architecture."
    elif "remove" in msg:
        target = _find_component(project, message)
        if target:
            affected = _dependents(project, target)
            components[:] = [c for c in components if c.get("id") != target.get("id")]
            for c in components:
                c["dependencies"] = [d for d in (c.get("dependencies") or []) if d != target.get("id")]
            updated = True
            extra = ", ".join(a.get("name") for a in affected) or "no remaining dependents"
            change_desc = f"Removed {target.get('name')}. Still depending on it: {extra}."
            actions = [_view_action("architecture"), {"type": "highlight_path", "component_ids": [a.get("id") for a in affected]}]

    if updated:
        persist()
        actions = actions or [_view_action("architecture"), _view_action("model-3d")]
        return True, change_desc, actions
    return False, "", []
