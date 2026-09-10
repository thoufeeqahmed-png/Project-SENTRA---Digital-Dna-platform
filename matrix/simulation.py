"""Rule-based project simulation. Results are labeled as simulation, not trained ML."""

from __future__ import annotations


def default_inputs_for_project(project) -> dict:
    dna = project.dna_data or {}
    ptype = (project.project_type or "").lower()
    idea = f"{project.title} {project.idea_input} {ptype}".lower()

    if any(w in idea for w in ("irrigation", "soil", "crop", "farm")):
        return {
            "soil_moisture": 18,
            "temperature": 35,
            "rain_probability": 10,
        }
    if any(w in idea for w in ("attendance", "face", "biometric")):
        return {
            "face_detected": 1,
            "liveness_score": 0.91,
            "match_confidence": 0.84,
        }
    if any(w in idea for w in ("ecommerce", "e-commerce", "shop", "cart", "store")):
        return {
            "cart_items": 2,
            "payment_authorized": 1,
            "stock_available": 1,
        }
    if any(w in idea for w in ("robot", "motor", "arm")):
        return {
            "obstacle_cm": 80,
            "battery_percent": 72,
            "target_distance_cm": 40,
        }
    if any(w in idea for w in ("vision", "camera", "image")):
        return {
            "frame_ready": 1,
            "object_confidence": 0.62,
            "threshold": 0.50,
        }
    if any(w in idea for w in ("analytics", "dashboard", "metric")):
        return {
            "events_per_min": 120,
            "anomaly_score": 0.22,
            "alert_threshold": 0.70,
        }
    inputs = dna.get("inputs") or []
    values = {}
    for i, name in enumerate(inputs[:4]):
        values[f"input_{i+1}"] = 50 if i else 30
        values[f"label_{i+1}"] = name
    if not values:
        values = {"input_signal": 40, "threshold": 50}
    return values


def run_simulation(project, overrides: dict | None = None) -> dict:
    """Deterministic rule-based simulation derived from Project DNA."""
    dna = project.dna_data or {}
    inputs = default_inputs_for_project(project)
    if overrides:
        for key, value in overrides.items():
            if key in inputs or key.startswith("input_"):
                try:
                    inputs[key] = float(value) if not isinstance(value, bool) else int(value)
                except (TypeError, ValueError):
                    inputs[key] = value

    idea = f"{project.title} {project.idea_input}".lower()
    steps = []
    decision = "No action"
    action = "Idle"
    expected = "No change"
    result = "Waiting for a clearer input"
    system_state = "Idle"

    if any(w in idea for w in ("irrigation", "soil", "crop", "farm")):
        moisture = float(inputs.get("soil_moisture", 50))
        rain = float(inputs.get("rain_probability", 0))
        temp = float(inputs.get("temperature", 25))
        system_state = "Dry" if moisture < 30 else ("Wet" if moisture > 55 else "Adequate")
        irrigate = moisture < 30 and rain < 45
        decision = "Irrigation required" if irrigate else "Hold water"
        action = "Pump ON" if irrigate else "Pump OFF"
        expected = "Water supplied to field" if irrigate else "No irrigation cycle"
        result = "Soil moisture expected to rise" if irrigate else "Moisture stays near current reading"
        if rain >= 70:
            decision = "Skip irrigation (rain likely)"
            action = "Pump OFF"
            expected = "Natural rainfall preferred"
            result = "Avoid overwatering"
        steps = [
            {"stage": "INPUT", "title": "Soil moisture", "value": f"{int(moisture)}%"},
            {"stage": "INPUT", "title": "Temperature", "value": f"{int(temp)}°C"},
            {"stage": "INPUT", "title": "Rain probability", "value": f"{int(rain)}%"},
            {"stage": "PROCESS", "title": "Field state", "value": system_state},
            {"stage": "DECISION", "title": "Controller", "value": decision},
            {"stage": "OUTPUT", "title": "Actuator", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]
    elif any(w in idea for w in ("attendance", "face", "biometric")):
        face = float(inputs.get("face_detected", 0)) >= 1
        live = float(inputs.get("liveness_score", 0))
        match = float(inputs.get("match_confidence", 0))
        grant = face and live >= 0.85 and match >= 0.72
        system_state = "Face present" if face else "No face"
        decision = "Grant attendance" if grant else "Reject / retry"
        action = "Log check-in" if grant else "Do not unlock"
        expected = "Attendance record written" if grant else "No record written"
        result = "Access granted (rule-based)" if grant else "Need live face + matching identity"
        steps = [
            {"stage": "INPUT", "title": "Face in frame", "value": "Yes" if face else "No"},
            {"stage": "PROCESS", "title": "Liveness (rule)", "value": f"{live:.2f}"},
            {"stage": "PROCESS", "title": "Match confidence", "value": f"{match:.2f}"},
            {"stage": "DECISION", "title": "Policy", "value": decision},
            {"stage": "OUTPUT", "title": "Turnstile", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]
    elif any(w in idea for w in ("ecommerce", "e-commerce", "shop", "cart", "store")):
        items = float(inputs.get("cart_items", 0))
        pay = float(inputs.get("payment_authorized", 0)) >= 1
        stock = float(inputs.get("stock_available", 0)) >= 1
        ok = items >= 1 and pay and stock
        system_state = "Checkout ready" if items else "Empty cart"
        decision = "Place order" if ok else "Block checkout"
        action = "Capture payment & create order" if ok else "Wait for cart/payment/stock"
        expected = "Order created, packing starts" if ok else "No order"
        result = "Customer receives confirmation" if ok else "Checkout incomplete"
        steps = [
            {"stage": "INPUT", "title": "Cart items", "value": str(int(items))},
            {"stage": "INPUT", "title": "Payment authorized", "value": "Yes" if pay else "No"},
            {"stage": "INPUT", "title": "Stock available", "value": "Yes" if stock else "No"},
            {"stage": "DECISION", "title": "Order engine", "value": decision},
            {"stage": "OUTPUT", "title": "Action", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]
    elif any(w in idea for w in ("robot", "motor")):
        obstacle = float(inputs.get("obstacle_cm", 100))
        battery = float(inputs.get("battery_percent", 50))
        stop = obstacle < 25 or battery < 12
        system_state = "Blocked" if obstacle < 25 else "Path clear"
        decision = "Halt" if stop else "Advance toward target"
        action = "Motors OFF" if stop else "Motors ON"
        expected = "Hold position" if stop else "Move closer to target"
        result = "Safe stop" if stop else "Estimated motion toward waypoint"
        steps = [
            {"stage": "INPUT", "title": "Obstacle distance", "value": f"{int(obstacle)} cm"},
            {"stage": "INPUT", "title": "Battery", "value": f"{int(battery)}%"},
            {"stage": "DECISION", "title": "Controller", "value": decision},
            {"stage": "OUTPUT", "title": "Motors", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]
    elif any(w in idea for w in ("vision", "camera", "image")):
        frame = float(inputs.get("frame_ready", 0)) >= 1
        conf = float(inputs.get("object_confidence", 0))
        thr = float(inputs.get("threshold", 0.5))
        hit = frame and conf >= thr
        system_state = "Frame ready" if frame else "No frame"
        decision = "Emit detection" if hit else "No detection"
        action = "Write event" if hit else "Skip"
        expected = "Application receives a label" if hit else "No event"
        result = "Rule-based detection fired" if hit else "Below threshold"
        steps = [
            {"stage": "INPUT", "title": "Frame", "value": "Ready" if frame else "Missing"},
            {"stage": "PROCESS", "title": "Confidence", "value": f"{conf:.2f}"},
            {"stage": "DECISION", "title": "Threshold {0:.2f}".format(thr), "value": decision},
            {"stage": "OUTPUT", "title": "Event", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]
    else:
        signal = float(inputs.get("input_signal", inputs.get("input_1", 40)))
        threshold = float(inputs.get("threshold", 50))
        fire = signal >= threshold
        system_state = "Above threshold" if fire else "Below threshold"
        decision = "Trigger workflow" if fire else "Stay idle"
        action = "Emit output event" if fire else "No dispatch"
        expected = (dna.get("outputs") or ["System output"])[0] if fire else "No output yet"
        result = "Rule-based path completed" if fire else "Waiting for stronger input"
        steps = [
            {"stage": "INPUT", "title": "Primary signal", "value": str(signal)},
            {"stage": "DECISION", "title": "Threshold", "value": f"{threshold}"},
            {"stage": "OUTPUT", "title": "Action", "value": action},
            {"stage": "RESULT", "title": "Expected outcome", "value": result},
        ]

    components = []
    for c in (dna.get("components") or []):
        components.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "role": c.get("category"),
            "active": c.get("category") in ("Decision", "Output", "Intelligence") and "ON" in action,
        })

    return {
        "mode": "simulation",
        "label": "Simulation / rule-based expected behavior",
        "disclaimer": "This is not a trained ML prediction. Values follow project rules from the current Project DNA.",
        "has_trained_model": False,
        "inputs": inputs,
        "system_state": system_state,
        "decision": decision,
        "action": action,
        "expected_output": expected,
        "result": result,
        "steps": steps,
        "components": components,
        "logic": dna.get("logic") or "",
    }
