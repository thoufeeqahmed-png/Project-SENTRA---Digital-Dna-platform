"""Map Project DNA components to visual kinds, 3D objects, and layout roles."""

from __future__ import annotations

KIND_KEYWORDS = [
    ("sensor", ("sensor", "probe", "moisture", "soil", "telemetry grid")),
    ("camera", ("camera", "rtsp", "webcam", "vision ingest", "image capture")),
    ("person", ("person", "customer", "employee", "student", "user", "face")),
    ("pump", ("pump", "solenoid", "valve", "actuator", "relay")),
    ("pipe", ("pipe", "drip", "irrigation line")),
    ("controller", ("controller", "decision", "state machine", "policy", "orchestr")),
    ("server", ("gateway", "api", "backend", "server", "proxy", "ingest")),
    ("database", ("database", "postgres", "vector", "storage", "store", "inventory")),
    ("ai", ("neural", "ml", "model", "intelligence", "inference", "arcface", "ai ")),
    ("dashboard", ("dashboard", "hud", "portal", "report", "kiosk", "display")),
    ("phone", ("mobile", "phone", "companion app", "ios", "android")),
    ("computer", ("client", "website", "web", "frontend", "presentation")),
    ("robot", ("robot", "motor", "arm", "chassis")),
    ("vehicle", ("courier", "driver", "vehicle", "delivery")),
    ("cloud", ("weather", "cloud", "forecast", "third-party")),
    ("factory", ("warehouse", "kitchen", "factory", "fulfillment")),
    ("payment", ("payment", "stripe", "checkout", "billing")),
]


CATEGORY_KIND = {
    "Input": "sensor",
    "Processing": "server",
    "Intelligence": "ai",
    "Decision": "controller",
    "Storage": "database",
    "Output": "dashboard",
}

STAGE_X = {
    "Input": -8,
    "Processing": -3,
    "Intelligence": 2,
    "Decision": 5,
    "Storage": 0,
    "Output": 8,
}


def infer_visual_kind(component: dict) -> str:
    name = f"{component.get('name', '')} {component.get('purpose', '')} {component.get('category', '')}".lower()
    for kind, keys in KIND_KEYWORDS:
        if any(k in name for k in keys):
            return kind
    return CATEGORY_KIND.get(component.get("category", ""), "server")


def layout_position(index: int, component: dict, total: int) -> dict:
    category = component.get("category") or "Processing"
    x = STAGE_X.get(category, (index % 5) * 3 - 6)
    z = ((index % 3) - 1) * 3.2
    y = 0.4 if category == "Intelligence" else 0.0
    return {"x": float(x), "y": float(y), "z": float(z)}


def enrich_components(components: list) -> list:
    enriched = []
    total = max(len(components), 1)
    for idx, raw in enumerate(components or []):
        item = dict(raw)
        kind = infer_visual_kind(item)
        item["visual_kind"] = kind
        item["visual_stage"] = item.get("category") or "Processing"
        pos = item.get("position") or layout_position(idx, item, total)
        item["position3d"] = pos
        enriched.append(item)
    return enriched


def synthesize_architecture(project) -> dict:
    dna = project.dna_data or {}
    components = list(dna.get("components") or [])
    graph = build_visual_graph(components, None)
    return {
        "pattern": "Component graph derived from Project DNA dependencies",
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "data_flow_sequence": [
            f"{c.get('name')} -> {(c.get('outputs') or ['output'])[0]}" for c in components
        ],
        "synthesized_at": True,
    }


def build_visual_graph(components: list, edges: list | None = None) -> dict:
    nodes = enrich_components(components)
    if edges:
        mapped_edges = edges
    else:
        mapped_edges = []
        id_set = {n.get("id") for n in nodes}
        for n in nodes:
            for dep in n.get("dependencies") or []:
                if dep in id_set:
                    mapped_edges.append({
                        "id": f"e-{dep}-{n.get('id')}",
                        "from": dep,
                        "to": n.get("id"),
                        "label": (n.get("inputs") or ["data"])[0],
                        "animated": True,
                    })
            for name in n.get("connected_components") or []:
                target = next((c for c in nodes if c.get("name") == name), None)
                if target:
                    mapped_edges.append({
                        "id": f"e-{n.get('id')}-{target.get('id')}",
                        "from": n.get("id"),
                        "to": target.get("id"),
                        "label": (n.get("outputs") or ["data"])[0],
                        "animated": True,
                    })
        if not mapped_edges:
            for i in range(len(nodes) - 1):
                mapped_edges.append({
                    "id": f"e-{i}-{i+1}",
                    "from": nodes[i].get("id"),
                    "to": nodes[i + 1].get("id"),
                    "label": (nodes[i].get("outputs") or ["data"])[0],
                    "animated": True,
                })
    return {"nodes": nodes, "edges": mapped_edges}
