import json
import os
import re
import urllib.request
import urllib.error

DEFAULT_ASSISTANT_INTRO = "I am the AI assistant of Thoufeeq Ahmed."

def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY") or os.environ.get("AI_API_KEY")


def call_llm_json(prompt, system_instruction):
    """Calls live LLM if key is present, returning parsed JSON dict or None."""
    api_key = get_api_key()
    if not api_key:
        return None

    # Try Gemini first if Gemini key
    if os.environ.get("GEMINI_API_KEY") or api_key.startswith("AIza"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text = data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text)
        except Exception as e:
            print("Gemini API call failed:", e)

    # Try OpenAI/Groq compatible
    base_url = "https://api.openai.com/v1/chat/completions"
    model = "gpt-4o-mini"
    if os.environ.get("GROQ_API_KEY"):
        base_url = "https://api.groq.com/openai/v1/chat/completions"
        model = "llama-3.3-70b-versatile"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    try:
        req = urllib.request.Request(base_url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method='POST')
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data['choices'][0]['message']['content']
            return json.loads(text)
    except Exception as e:
        print("OpenAI/Groq API call failed:", e)

    return None


def generate_project_dna(idea_text):
    """
    Analyzes project idea and generates comprehensive structured Project DNA.
    Uses live LLM if configured; otherwise utilizes semantic domain decomposition.
    """
    sys_prompt = """You are a senior system architect and AI assistant of Thoufeeq Ahmed for Project DNA Matrix.
Analyze the user's project idea and return a strictly valid JSON object representing its complete Project DNA.
Output format must match:
{
  "project_name": "...",
  "project_type": "IoT / Cyber-Physical | AI/ML System | Mobile / Web Application | Cloud / Data Platform | E-Commerce",
  "problem": "Clear problem statement",
  "goal": "Core objective and outcome",
  "summary": "High level architecture summary",
  "target_users": ["User group 1", "User group 2"],
  "inputs": ["Input 1", "Input 2"],
  "outputs": ["Output 1", "Output 2"],
  "software": ["Framework 1", "Language 1"],
  "hardware": ["Hardware 1 or 'Cloud Compute Server'"],
  "data": ["Data types & schemas"],
  "ai_ml_requirements": "AI models / algorithms required",
  "components": [
    {
      "id": "comp-1",
      "name": "Component Name",
      "category": "Input | Processing | Intelligence | Decision | Storage | Output",
      "purpose": "What this component does",
      "description": "Technical details",
      "inputs": ["data received"],
      "outputs": ["data produced"],
      "technologies": ["tools used"],
      "dependencies": ["other component ids"],
      "connected_components": ["connected component names"]
    }
  ],
  "dependencies": ["Key external services and libraries"],
  "logic": "Decision logic and execution sequence",
  "workflow": "End-to-end data flow narrative",
  "risks": ["Risk 1", "Risk 2"],
  "constraints": ["Constraint 1", "Constraint 2"],
  "feasibility": {
    "score": 88,
    "technical": "High/Moderate",
    "software": "Readily available open source tools",
    "hardware": "Required hardware specs",
    "data_requirements": "Training/streaming data needs",
    "complexity": "Moderate/High",
    "assessment": "Detailed feasibility explanation"
  },
  "build_steps": [
    {
      "step_number": 1,
      "title": "Phase 1 Title",
      "description": "Step detail",
      "required_components": ["Comp 1"],
      "expected_result": "Concrete output",
      "status": "current"
    }
  ]
}
Ensure all components, inputs, outputs, and build steps are specifically customized to the project idea.
"""
    llm_res = call_llm_json(f"Generate Project DNA for: {idea_text}", sys_prompt)
    if llm_res and "project_name" in llm_res and "components" in llm_res:
        return llm_res

    # Dynamic Semantic Domain Generator for guaranteed resilience
    return generate_semantic_dna(idea_text)


def generate_semantic_dna(idea):
    """Deep domain analyzer that creates custom DNA for different project types."""
    low = idea.lower()
    
    is_irrigation = any(w in low for w in ["irrigation", "agriculture", "crop", "farming", "soil", "water", "plant"])
    is_attendance = any(w in low for w in ["attendance", "facial", "face", "biometric", "student", "employee", "clock"])
    is_food = any(w in low for w in ["food", "delivery", "restaurant", "order", "driver", "meal"])
    is_analytics = any(w in low for w in ["analytics", "dashboard", "metric", "bi", "telemetry", "data platform"])
    is_ecommerce = any(w in low for w in ["ecommerce", "e-commerce", "shop", "cart", "store", "product", "checkout"])
    is_smarthome = any(w in low for w in ["smart home", "home automation", "thermostat", "lighting", "doorbell", "hvac"])
    is_iot = is_irrigation or is_smarthome or any(w in low for w in ["iot", "sensor", "drone", "hardware", "arduino", "esp32", "robot"])

    # 1. Irrigation / Agriculture
    if is_irrigation:
        return {
            "project_name": "AI-Powered Smart Precision Irrigation System",
            "project_type": "IoT & Cyber-Physical AI System",
            "problem": "Over-irrigation and water wastage in commercial crops leading to soil nutrient depletion and elevated operational costs.",
            "goal": "Optimize water consumption by 40% through autonomous soil-moisture sensor arrays, weather forecasting APIs, and edge valve control.",
            "summary": "A closed-loop cyber-physical architecture coupling field sensors, wireless LoRa/ESP32 gateways, a predictive evapotranspiration model, and solenoid actuators.",
            "target_users": ["Agriculturalists", "Commercial Farm Managers", "Greenhouse Technicians"],
            "inputs": ["Soil moisture level (VWC %)", "Soil temperature", "Ambient humidity", "Rainfall forecast telemetry", "Flow meter rates"],
            "outputs": ["Valve actuation commands (PWM)", "Water consumption metrics", "Irrigation schedule dashboard", "Moisture alert push notifications"],
            "software": ["Python / Django", "FastAPI Edge Gateway", "PostgreSQL / TimescaleDB", "MQTT Broker (Mosquitto)", "PyTorch (ET0 prediction)"],
            "hardware": ["Capacitive Soil Moisture Sensors", "ESP32 LoRaWAN Transceivers", "12V Solenoid Water Valves", "Ultrasonic Water Flow Meters", "Raspberry Pi Local Gateway"],
            "data": ["Time-series sensor telemetry", "Agronomic crop coefficient tables", "Weather forecast JSON streams", "Valve activation logs"],
            "ai_ml_requirements": "Random Forest Regressor / LSTM for calculating Penman-Monteith reference evapotranspiration (ET0) and predicting irrigation duration.",
            "components": [
                {
                    "id": "comp-sensor-grid",
                    "name": "Soil & Environmental Sensor Grid",
                    "category": "Input",
                    "purpose": "Collects multi-depth soil moisture, temperature, and ambient humidity across crop sectors.",
                    "description": "Low-power analog capacitive moisture probes sampling every 60 seconds with SPI analog-to-digital conversion.",
                    "inputs": ["Analog soil resistivity", "Ambient thermal radiation"],
                    "outputs": ["Raw calibrated moisture %", "Temperature float in Celsius"],
                    "technologies": ["ESP32", "LoRa SX1276", "Capacitive V1.2 Sensors"],
                    "dependencies": [],
                    "connected_components": ["Telemetry Ingestion Gateway"]
                },
                {
                    "id": "comp-gateway",
                    "name": "Edge Telemetry Gateway",
                    "category": "Processing",
                    "purpose": "Aggregates field LoRa packets, verifies payload checksums, and forwards JSON packets over MQTT.",
                    "description": "Secure edge gateway running mutual TLS with offline buffering on local flash storage.",
                    "inputs": ["LoRa radio packets (868/915 MHz)"],
                    "outputs": ["Structured MQTT JSON envelopes"],
                    "technologies": ["Mosquitto MQTT", "Python", "SQLite Buffer"],
                    "dependencies": ["comp-sensor-grid"],
                    "connected_components": ["Evapotranspiration Neural Model", "Telemetry Time-Series Store"]
                },
                {
                    "id": "comp-ai-engine",
                    "name": "Evapotranspiration Neural Model",
                    "category": "Intelligence",
                    "purpose": "Calculates soil water deficit and predicts precise required irrigation volume in liters.",
                    "description": "Trained ML model combining soil moisture decay curves with 48-hour NOAA precipitation forecasts.",
                    "inputs": ["Moisture historical delta", "Weather forecast precipitation %", "Crop growth stage coefficient"],
                    "outputs": ["Irrigation duration in minutes", "Target water volume in liters"],
                    "technologies": ["Scikit-Learn", "ONNX Runtime", "OpenWeather API"],
                    "dependencies": ["comp-gateway"],
                    "connected_components": ["Irrigation Decision Controller"]
                },
                {
                    "id": "comp-decision-controller",
                    "name": "Irrigation Decision Controller",
                    "category": "Decision",
                    "purpose": "Enforces safety interlocks (e.g. freeze prevention, leak detection) and issues valve open/close commands.",
                    "description": "Rule-based finite state machine converting ML irrigation recommendations into relay pin triggers.",
                    "inputs": ["Irrigation duration recommendations", "Line pressure readings", "Emergency manual overrides"],
                    "outputs": ["Solenoid valve toggle commands", "Safety valve cutoffs"],
                    "technologies": ["State Pattern Logic", "Celery Task Runner"],
                    "dependencies": ["comp-ai-engine"],
                    "connected_components": ["Solenoid Valve Actuators"]
                },
                {
                    "id": "comp-actuators",
                    "name": "Solenoid Valve Actuator Mesh",
                    "category": "Output",
                    "purpose": "Physically regulates pressurized water flow to drip lines across distinct farming zones.",
                    "description": "12V latching solenoid valves driven by MOSFET relay banks with optical isolation.",
                    "inputs": ["Relay high/low digital pulses"],
                    "outputs": ["Physical pressurized water flow to drip emitters"],
                    "technologies": ["Optocoupled Relay Modules", "12V DC Solenoid Valves"],
                    "dependencies": ["comp-decision-controller"],
                    "connected_components": []
                },
                {
                    "id": "comp-dashboard",
                    "name": "Agronomist Telemetry Dashboard",
                    "category": "Output",
                    "purpose": "Interactive web interface displaying live soil hydration maps, valve status, and water savings analytics.",
                    "description": "Real-time dashboard with WebSocket telemetry streams, manual valve override buttons, and historical graphs.",
                    "inputs": ["Time-series sensor telemetry", "Valve status states"],
                    "outputs": ["Visual heatmaps", "Water conservation audit reports"],
                    "technologies": ["HTML5 Canvas", "WebSockets", "Chart.js"],
                    "dependencies": ["comp-gateway", "comp-decision-controller"],
                    "connected_components": []
                }
            ],
            "dependencies": ["Paho MQTT", "TimescaleDB", "Weather Forecast API", "Django REST Framework"],
            "logic": "If current soil moisture < field capacity threshold AND rain forecast probability < 40%: trigger ML duration calculation -> dispatch relay OPEN -> monitor flow meter -> auto CLOSE on target volume.",
            "workflow": "Soil Sensors -> Edge Gateway -> Telemetry Store -> Neural ET0 Model -> Decision Logic -> Solenoid Valves -> Flow Verification -> Dashboard Report.",
            "risks": ["Sensor drift due to salinity in fertilizer", "Wireless packet attenuation in dense foliage", "Valve mechanical freeze"],
            "constraints": ["Battery power longevity (target: 12 months on 18650 cells)", "Sub-second emergency cutoff on pipe rupture"],
            "feasibility": {
                "score": 92,
                "technical": "High feasibility with standard off-the-shelf LoRa microcontrollers and solenoid relays.",
                "software": "Standard Django backend, Mosquitto MQTT, and Scikit-Learn models.",
                "hardware": "ESP32, capacitive moisture probes, optocoupled relays, 12V DC valves.",
                "data_requirements": "Requires local field soil calibration curves for sandy vs clay soil types.",
                "complexity": "Moderate (cyber-physical integration and power management).",
                "assessment": "Proven architecture with high commercial ROI in water conservation and crop yield stability."
            },
            "build_steps": [
                {
                    "step_number": 1,
                    "title": "Sensor Calibration & Edge LoRa Node Scaffolding",
                    "description": "Wire capacitive soil probes to ESP32 ADC, calibrate dry/saturated voltage readings, and establish packet transmission over LoRa.",
                    "required_components": ["Soil & Environmental Sensor Grid"],
                    "expected_result": "Stable telemetry packets broadcasted over radio every 60s.",
                    "status": "current"
                },
                {
                    "step_number": 2,
                    "title": "MQTT Ingestion Gateway & Database Pipeline",
                    "description": "Configure Mosquitto broker, parse incoming JSON sensor payloads, and persist normalized readings into PostgreSQL/TimescaleDB.",
                    "required_components": ["Edge Telemetry Gateway"],
                    "expected_result": "Real-time queryable sensor records in PostgreSQL with sub-100ms latency.",
                    "status": "next"
                },
                {
                    "step_number": 3,
                    "title": "Evapotranspiration ML Engine & Decision Rules",
                    "description": "Implement Penman-Monteith ET0 formula, integrate weather API forecasts, and construct safety interlock state machine.",
                    "required_components": ["Evapotranspiration Neural Model", "Irrigation Decision Controller"],
                    "expected_result": "Automated calculation of irrigation runtimes with precipitation override.",
                    "status": "next"
                },
                {
                    "step_number": 4,
                    "title": "Actuator Relay Integration & Flow Telemetry",
                    "description": "Interface 12V solenoid valves to MOSFET relays, connect pulse flow meters, and verify closed-loop water shutoff.",
                    "required_components": ["Solenoid Valve Actuator Mesh"],
                    "expected_result": "Controlled water release matching targeted liter volume accurately.",
                    "status": "next"
                },
                {
                    "step_number": 5,
                    "title": "Agronomist Dashboard & Alert System",
                    "description": "Deploy web interface showing field moisture maps, valve statuses, manual override buttons, and SMS/push warnings.",
                    "required_components": ["Agronomist Telemetry Dashboard"],
                    "expected_result": "Production-ready agricultural dashboard accessible from mobile and desktop.",
                    "status": "next"
                }
            ]
        }

    # 2. Food Delivery Application
    elif is_food:
        return {
            "project_name": "Autonomous On-Demand Food Delivery Platform",
            "project_type": "Distributed Multi-Tenant Mobile & Web Platform",
            "problem": "High delivery commission fees, delayed dispatch times, and poor order tracking transparency between restaurants, couriers, and hungry customers.",
            "goal": "Build an end-to-end multi-sided delivery platform with sub-second order state synchronization, geospatial courier dispatch, and dynamic ETA estimation.",
            "summary": "Event-driven microservices architecture connecting Customer mobile client, Restaurant kitchen terminal, Courier GPS tracker, and central dispatch engine.",
            "target_users": ["Consumers", "Restaurant Owners", "Delivery Drivers", "Platform Operations"],
            "inputs": ["Customer orders", "GPS coordinate streams", "Restaurant menu items", "Payment authorizations", "Driver acceptance pings"],
            "outputs": ["Live courier map tracking", "Kitchen order tickets (KOT)", "Automated payment receipts", "Driver routing turn-by-turn"],
            "software": ["React Native (iOS/Android)", "Django REST Framework", "PostgreSQL / PostGIS", "Redis Streams", "Stripe API", "Google Maps Platform"],
            "hardware": ["Cloud Multi-AZ Compute Nodes", "Driver Smartphone GPS/Cellular"],
            "data": ["Menu catalog JSON", "Geospatial PostGIS driver coordinates", "Transactional order logs", "Rating & feedback records"],
            "ai_ml_requirements": "Hungarian algorithm for bipartite matching + Gradient Boosted Trees for dynamic kitchen preparation and delivery ETA estimation.",
            "components": [
                {
                    "id": "comp-client-app",
                    "name": "Customer Mobile Experience",
                    "category": "Input",
                    "purpose": "Enables customers to browse menus, customize dishes, execute payments, and track courier movement on a live map.",
                    "description": "Cross-platform mobile application with offline menu caching and real-time WebSocket location feeds.",
                    "inputs": ["Touch interactions", "Search filters", "Credit card credentials"],
                    "outputs": ["Order placement envelopes", "Courier tipping intents"],
                    "technologies": ["React Native", "Tailwind CSS", "WebSocket Client"],
                    "dependencies": [],
                    "connected_components": ["API Gateway & Auth Proxy"]
                },
                {
                    "id": "comp-gateway",
                    "name": "API Gateway & Auth Proxy",
                    "category": "Processing",
                    "purpose": "Authenticates user JWT tokens, enforces role-based access (Customer/Merchant/Driver), and routes requests.",
                    "description": "High-throughput reverse proxy with Redis token bucket rate limiting and SSL termination.",
                    "inputs": ["HTTP/WebSocket requests from all 3 apps"],
                    "outputs": ["Sanitized internal microservice calls"],
                    "technologies": ["Kong / Envoy", "JWT Auth", "Redis Rate Limiter"],
                    "dependencies": ["comp-client-app"],
                    "connected_components": ["Order Lifecycle State Machine", "Geospatial Dispatch Engine"]
                },
                {
                    "id": "comp-order-engine",
                    "name": "Order Lifecycle State Machine",
                    "category": "Processing",
                    "purpose": "Manages transactional order states: Placed -> Accepted -> Cooking -> Ready -> Picked Up -> Delivered.",
                    "description": "ACID transactional workflow with idempotent payment captures via Stripe and event publication to Redis bus.",
                    "inputs": ["Order requests", "Merchant status changes"],
                    "outputs": ["Kitchen dispatch events", "State transition broadcasts"],
                    "technologies": ["Django State Machine", "Stripe API", "PostgreSQL 16"],
                    "dependencies": ["comp-gateway"],
                    "connected_components": ["Geospatial Dispatch Engine", "Restaurant Kitchen Portal"]
                },
                {
                    "id": "comp-dispatch-engine",
                    "name": "Geospatial Dispatch Engine",
                    "category": "Intelligence",
                    "purpose": "Optimally pairs ready orders with nearest available couriers using distance, traffic, and vehicle type.",
                    "description": "Real-time dispatch algorithm clustering nearby pick-ups and estimating travel times using PostGIS and OSRM.",
                    "inputs": ["Active driver GPS streams", "Order ready notifications"],
                    "outputs": ["Driver offer dispatch requests", "Live ETA predictions"],
                    "technologies": ["PostGIS", "Redis GeoSets", "Scikit-Learn ETA Model"],
                    "dependencies": ["comp-order-engine"],
                    "connected_components": ["Courier Driver Navigation App"]
                },
                {
                    "id": "comp-merchant-portal",
                    "name": "Restaurant Kitchen Portal",
                    "category": "Output",
                    "purpose": "Kitchen display system (KDS) showing pending orders, prep times, and driver arrival counters.",
                    "description": "Responsive tablet interface with audio order chimes and one-tap prep time adjustments.",
                    "inputs": ["New order incoming alerts"],
                    "outputs": ["Order confirmation pings", "KOT print triggers"],
                    "technologies": ["React / Vite", "Web Audio API", "Thermal Printer SDK"],
                    "dependencies": ["comp-order-engine"],
                    "connected_components": []
                },
                {
                    "id": "comp-driver-app",
                    "name": "Courier Driver Navigation App",
                    "category": "Output",
                    "purpose": "Provides delivery drivers with order acceptance cards, turn-by-turn routing, and proof-of-delivery photo capture.",
                    "description": "Mobile app streaming background GPS telemetry every 3 seconds while on an active delivery run.",
                    "inputs": ["Driver acceptance taps", "Delivery confirmation photos"],
                    "outputs": ["Live GPS coordinates", "Completed delivery signatures"],
                    "technologies": ["React Native", "Background Geolocation", "Mapbox SDK"],
                    "dependencies": ["comp-dispatch-engine"],
                    "connected_components": []
                }
            ],
            "dependencies": ["Stripe Payments", "PostgreSQL/PostGIS", "Redis Streams", "Mapbox Navigation", "Firebase Cloud Messaging"],
            "logic": "Customer checks out -> Stripe authorizes funds -> Kitchen receives order -> Kitchen taps Ready -> Geospatial Dispatch queries nearby drivers -> Driver accepts -> Route calculated -> Driver delivers -> Funds captured.",
            "workflow": "Customer App -> Gateway -> Order State Machine -> Kitchen Acceptance -> Geospatial Dispatcher -> Driver App -> GPS Stream -> Real-time Customer Map.",
            "risks": ["Driver shortage during bad weather surges", "GPS drift in urban high-rise canyons", "Payment fraud via stolen credit cards"],
            "constraints": ["Sub-3 second dispatch broadcast latency", "PCI-DSS compliance for payment tokenization"],
            "feasibility": {
                "score": 89,
                "technical": "High feasibility using proven open-source geospatial databases and standard mobile frameworks.",
                "software": "PostGIS spatial indexes, Redis geospatial primitives, React Native clients.",
                "hardware": "Standard cloud infrastructure (PostgreSQL RDS, Redis ElastiCache).",
                "data_requirements": "Requires local road network vector tiles and initial merchant menu catalogs.",
                "complexity": "Moderate to High (multi-party real-time coordination).",
                "assessment": "Technically straightforward with clear established architectural patterns."
            },
            "build_steps": [
                {
                    "step_number": 1,
                    "title": "Domain Data Models & Menu Scaffolding",
                    "description": "Build PostgreSQL schemas for Restaurants, Menus, Dish Options, Orders, and User Profiles with Django migrations.",
                    "required_components": ["Order Lifecycle State Machine"],
                    "expected_result": "Fully testable database models with seed menu records and REST CRUD endpoints.",
                    "status": "current"
                },
                {
                    "step_number": 2,
                    "title": "Payment Integration & Order Workflow",
                    "description": "Implement Stripe payment intents, idempotent checkout endpoints, and order state transition triggers.",
                    "required_components": ["API Gateway & Auth Proxy", "Order Lifecycle State Machine"],
                    "expected_result": "Secure order placement with automated card authorization and webhook verification.",
                    "status": "next"
                },
                {
                    "step_number": 3,
                    "title": "Geospatial Driver Tracking & Dispatch Mesh",
                    "description": "Configure PostGIS and Redis GeoSets to ingest driver location coordinates and execute nearest-courier matching.",
                    "required_components": ["Geospatial Dispatch Engine"],
                    "expected_result": "Sub-second nearest driver query returning optimal courier within 3km radius.",
                    "status": "next"
                },
                {
                    "step_number": 4,
                    "title": "Restaurant Kitchen Terminal Interface",
                    "description": "Construct tablet web UI with audio order alerts, prep time adjuster, and kitchen status toggles.",
                    "required_components": ["Restaurant Kitchen Portal"],
                    "expected_result": "Real-time kitchen order ticket dashboard updating instantly over WebSockets.",
                    "status": "next"
                },
                {
                    "step_number": 5,
                    "title": "Courier App & Customer Live Map Tracking",
                    "description": "Build mobile views with Mapbox maps showing animated courier pin moving smoothly along street routes.",
                    "required_components": ["Customer Mobile Experience", "Courier Driver Navigation App"],
                    "expected_result": "End-to-end customer order delivery testing completed with real GPS updates.",
                    "status": "next"
                }
            ]
        }

    # 3. AI Facial Recognition Attendance System
    elif is_attendance:
        return {
            "project_name": "AI Facial Recognition & Liveness Attendance Matrix",
            "project_type": "Edge AI & Biometrics Computer Vision System",
            "problem": "Manual roll calls and fingerprint scanners are slow, vulnerable to buddy punching, and cause bottle-necks during peak entry hours.",
            "goal": "Automate attendance recording with 99.2% accuracy in under 300ms using camera stream face embeddings and 3D liveness detection.",
            "summary": "Dual-stage edge computer vision architecture combining face detection (RetinaFace), anti-spoofing liveness, ArcFace embedding vectors, and real-time attendance logging.",
            "target_users": ["HR Personnel", "School Administrators", "Employees", "Students"],
            "inputs": ["RTSP HD camera video stream (1080p 30fps)", "Employee registration headshots", "Classroom/shift schedules"],
            "outputs": ["Automated attendance timestamp records", "Real-time recognition overlay HUD", "Liveness spoofing alert notifications", "Daily PDF/CSV attendance reports"],
            "software": ["Python 3.13", "OpenCV", "InsightFace / ArcFace", "FastAPI / Django", "PostgreSQL + pgvector", "WebRTC Video Stream"],
            "hardware": ["HD RTSP IP Camera (2MP or 4MP)", "Edge AI Compute (NVIDIA Jetson Orin Nano / RTX 4060 GPU)", "Wall Mounted Verification Tablet"],
            "data": ["512-dimensional facial embedding vectors", "Facial landmark bounding boxes", "Employee biometric profile records", "Access audit logs"],
            "ai_ml_requirements": "RetinaFace for localization + MiniFASNet for anti-spoofing photo/screen detection + ArcFace ResNet50 for 512D biometric embedding extraction.",
            "components": [
                {
                    "id": "comp-camera-ingest",
                    "name": "RTSP Video Stream Ingest",
                    "category": "Input",
                    "purpose": "Captures raw 1080p video frames from network IP cameras at entrance turnstiles.",
                    "description": "Hardware-accelerated GStreamer / FFmpeg pipeline decoding H.264 video frames into GPU memory buffers.",
                    "inputs": ["RTSP/ONVIF camera video stream"],
                    "outputs": ["Decoded BGR video frames in CUDA memory"],
                    "technologies": ["OpenCV VideoCapture", "GStreamer", "NVIDIA NVDEC"],
                    "dependencies": [],
                    "connected_components": ["Face Detection & Alignment Engine"]
                },
                {
                    "id": "comp-face-detect",
                    "name": "Face Detection & Alignment Engine",
                    "category": "Processing",
                    "purpose": "Detects all faces in frame, tracks bounding boxes, and aligns 5 facial landmarks (eyes, nose, mouth corners).",
                    "description": "RetinaFace neural model executing in 12ms per frame, supporting simultaneous multi-face tracking.",
                    "inputs": ["Raw video frames"],
                    "outputs": ["Cropped 112x112 normalized facial chips", "Landmark coordinates"],
                    "technologies": ["RetinaFace", "TensorRT", "CUDA"],
                    "dependencies": ["comp-camera-ingest"],
                    "connected_components": ["Anti-Spoofing Liveness Classifier", "ArcFace Biometric Extractor"]
                },
                {
                    "id": "comp-liveness",
                    "name": "Anti-Spoofing Liveness Classifier",
                    "category": "Intelligence",
                    "purpose": "Prevents spoofing attacks using printed photos, mobile screens, or video replays.",
                    "description": "Lightweight CNN analyzing micro-texture reflections, moiré patterns, and optical depth cues.",
                    "inputs": ["Aligned face chips"],
                    "outputs": ["Liveness score (0.0 - 1.0) & Real/Fake label"],
                    "technologies": ["MiniFASNet", "PyTorch ONNX"],
                    "dependencies": ["comp-face-detect"],
                    "connected_components": ["Attendance Commit Logic"]
                },
                {
                    "id": "comp-biometric-extractor",
                    "name": "ArcFace Biometric Extractor & Vector Matcher",
                    "category": "Intelligence",
                    "purpose": "Extracts unique 512-dimensional facial embedding and searches registered vector database using cosine similarity.",
                    "description": "Deep metric learning model computing vector embeddings and querying pgvector index under 5ms.",
                    "inputs": ["Verified live face chips"],
                    "outputs": ["Employee ID match with confidence percentage"],
                    "technologies": ["ArcFace (InsightFace)", "pgvector", "PostgreSQL 16"],
                    "dependencies": ["comp-face-detect"],
                    "connected_components": ["Attendance Commit Logic"]
                },
                {
                    "id": "comp-attendance-logic",
                    "name": "Attendance Validation & Commit Logic",
                    "category": "Decision",
                    "purpose": "Validates shift rules (prevent double check-ins within 15 minutes), commits timestamp, and triggers door unlock relay.",
                    "description": "Business rules engine logging verified entries, flags tardiness, and dispatches webhook notifications.",
                    "inputs": ["Employee ID match", "Liveness score > 0.85", "Current timestamp"],
                    "outputs": ["Committed attendance record", "Door access relay signal"],
                    "technologies": ["Django ORM", "Redis Cooldown Cache"],
                    "dependencies": ["comp-liveness", "comp-biometric-extractor"],
                    "connected_components": ["Turnstile Access Display HUD"]
                },
                {
                    "id": "comp-display-hud",
                    "name": "Turnstile Access Display HUD",
                    "category": "Output",
                    "purpose": "Visual tablet display welcoming the recognized user with photo, name, and green access granted chime.",
                    "description": "High-framerate kiosk interface displaying real-time bounding boxes and personalized greeting.",
                    "inputs": ["Verified employee name and photo URL"],
                    "outputs": ["Visual verification graphic", "Audio chime confirmation"],
                    "technologies": ["WebSockets", "HTML5 Canvas", "Audio Synthesis"],
                    "dependencies": ["comp-attendance-logic"],
                    "connected_components": []
                }
            ],
            "dependencies": ["InsightFace", "pgvector", "OpenCV", "TensorRT", "Django 6.1"],
            "logic": "RTSP Stream -> Frame Grab -> RetinaFace Detect -> Liveness Check (Must be > 0.85) -> ArcFace 512D Extraction -> Cosine Similarity >= 0.72 -> Check Cooldown -> Log Attendance -> Display Welcome.",
            "workflow": "Camera -> Frame Buffer -> RetinaFace -> Liveness Filter -> pgvector Similarity -> Attendance Record -> Turnstile HUD.",
            "risks": ["Drastic lighting changes at entrance doors", "Identical twin classification edge cases", "Network camera disconnects"],
            "constraints": ["Recognition under 300ms total latency", "Local biometric data encryption (GDPR compliance)"],
            "feasibility": {
                "score": 94,
                "technical": "High feasibility with mature open-source face recognition models and pgvector indexing.",
                "software": "InsightFace, PyTorch, PostgreSQL, Django.",
                "hardware": "Standard RTSP camera and GPU compute (or Jetson edge board).",
                "data_requirements": "Requires 3-5 clean registration photos per person for initial gallery embedding.",
                "complexity": "Moderate (CUDA optimization and liveness tuning).",
                "assessment": "Very high accuracy and fast deployment with proven commercial reliability."
            },
            "build_steps": [
                {
                    "step_number": 1,
                    "title": "Camera Ingestion & Face Detection Pipeline",
                    "description": "Establish RTSP video decoding with OpenCV and integrate RetinaFace bounding box extraction.",
                    "required_components": ["RTSP Video Stream Ingest", "Face Detection & Alignment Engine"],
                    "expected_result": "Real-time 30fps face tracking bounding boxes with landmark alignment.",
                    "status": "current"
                },
                {
                    "step_number": 2,
                    "title": "ArcFace Embedding & Vector Database Indexing",
                    "description": "Integrate ArcFace 512D feature extractor and setup PostgreSQL with pgvector for HNSW cosine similarity search.",
                    "required_components": ["ArcFace Biometric Extractor & Vector Matcher"],
                    "expected_result": "Vector query recognizing registered faces in under 5ms with >99% accuracy.",
                    "status": "next"
                },
                {
                    "step_number": 3,
                    "title": "Anti-Spoofing Liveness Verification",
                    "description": "Deploy MiniFASNet liveness classifier to flag photo printouts and mobile video replay attempts.",
                    "required_components": ["Anti-Spoofing Liveness Classifier"],
                    "expected_result": "Spoof attempts rejected with visual on-screen fraud warning.",
                    "status": "next"
                },
                {
                    "step_number": 4,
                    "title": "Attendance Policy Engine & Shift Rules",
                    "description": "Construct check-in cooldowns, late arrival penalties, holiday calendars, and SQLite/PostgreSQL logging.",
                    "required_components": ["Attendance Validation & Commit Logic"],
                    "expected_result": "Accurate, tamper-proof attendance journal with automated CSV exports.",
                    "status": "next"
                },
                {
                    "step_number": 5,
                    "title": "Turnstile Kiosk HUD & Admin Dashboard",
                    "description": "Build interactive kiosk screen with greeting animations and admin portal with daily attendance analytics.",
                    "required_components": ["Turnstile Access Display HUD"],
                    "expected_result": "Complete turnkey facial attendance system ready for organizational deployment.",
                    "status": "next"
                }
            ]
        }

    # 4. Default High-Tech Cloud & Distributed Platform
    else:
        words = [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{3,}\b', idea)]
        p_title = " ".join(words[:4]) if words else "Universal System Core"
        if not any(k in p_title.lower() for k in ["system", "platform", "matrix", "network", "lab", "hub", "engine"]):
            p_title += " Platform"

        return {
            "project_name": p_title,
            "project_type": "Cloud & Distributed Platform",
            "problem": f"Lack of scalable, low-latency automated workflows in addressing {idea[:80]}.",
            "goal": "Deliver an automated, resilient, and highly scalable software platform with modular services and telemetry.",
            "summary": "Decoupled microservices architecture with an API gateway, asynchronous queue workers, relational database, and responsive frontend client.",
            "target_users": ["System Engineers", "End Users", "Enterprise Administrators"],
            "inputs": ["User commands", "API payloads", "Authentication tokens", "Configuration parameters"],
            "outputs": ["Processed analytical insights", "Real-time state telemetry", "Exportable reports", "Audit journals"],
            "software": ["Python 3.13", "Django REST Framework", "PostgreSQL 16", "Redis 7.2", "Celery", "Modern Vanilla JS"],
            "hardware": ["Cloud VPS / Container Cluster (4 vCPU, 16GB RAM)"],
            "data": ["Structured transactional records", "User identities", "Session caches", "Event audit streams"],
            "ai_ml_requirements": "Heuristic optimization engine with predictive caching and anomaly classification.",
            "components": [
                {
                    "id": "comp-client",
                    "name": "Universal Client Presentation Layer",
                    "category": "Input",
                    "purpose": "Provides a clean, responsive engineering workspace for user interaction and real-time telemetry feeds.",
                    "description": "Single-page interface communicating via secure REST endpoints and WebSockets.",
                    "inputs": ["User input actions", "Voice audio commands"],
                    "outputs": ["Encrypted JSON API requests", "Session headers"],
                    "technologies": ["HTML5 Canvas", "Modern JavaScript (ES2024)", "CSS Variables"],
                    "dependencies": [],
                    "connected_components": ["API Gateway & Security Proxy"]
                },
                {
                    "id": "comp-gateway",
                    "name": "API Gateway & Security Proxy",
                    "category": "Processing",
                    "purpose": "Enforces token authentication, mutual TLS, rate limiting, and request validation.",
                    "description": "Secure entrypoint routing verified traffic to internal application microservices.",
                    "inputs": ["Inbound client requests"],
                    "outputs": ["Validated internal payloads", "Audit trace logs"],
                    "technologies": ["Nginx / Envoy", "OAuth 2.1", "JWT HMAC-SHA256"],
                    "dependencies": ["comp-client"],
                    "connected_components": ["Core Orchestration Engine", "Relational Database Layer"]
                },
                {
                    "id": "comp-core-logic",
                    "name": "Core Orchestration Engine",
                    "category": "Processing",
                    "purpose": "Executes domain business workflows, state transitions, and dispatches background tasks.",
                    "description": "Modular Python service implementing transactional boundaries and domain entities.",
                    "inputs": ["Sanitized user commands", "Scheduled cron triggers"],
                    "outputs": ["Calculated domain states", "Queued asynchronous tasks"],
                    "technologies": ["Python / Django", "Pydantic", "Celery Task Queue"],
                    "dependencies": ["comp-gateway"],
                    "connected_components": ["Analytics & Intelligence Model", "In-Memory Cache & Message Broker"]
                },
                {
                    "id": "comp-intelligence",
                    "name": "Analytics & Intelligence Model",
                    "category": "Intelligence",
                    "purpose": "Analyzes usage patterns, detects operational bottlenecks, and computes predictive optimizations.",
                    "description": "Machine learning inference pipeline executing continuous feature scoring.",
                    "inputs": ["Aggregated telemetry metrics", "Historical activity logs"],
                    "outputs": ["Optimization recommendations", "Anomaly trigger alerts"],
                    "technologies": ["PyTorch / ONNX", "Pandas", "Scikit-Learn"],
                    "dependencies": ["comp-core-logic"],
                    "connected_components": ["Decision & Dispatch Controller"]
                },
                {
                    "id": "comp-decision",
                    "name": "Decision & Dispatch Controller",
                    "category": "Decision",
                    "purpose": "Evaluates intelligence metrics against business constraints and routes operational actions.",
                    "description": "Deterministic decision matrix managing notifications and policy enforcement.",
                    "inputs": ["ML anomaly scores", "Configured SLA thresholds"],
                    "outputs": ["Dispatched events", "Automated scaling signals"],
                    "technologies": ["State Pattern Logic", "Celery Beat"],
                    "dependencies": ["comp-intelligence"],
                    "connected_components": ["Relational Database Layer", "Universal Client Presentation Layer"]
                },
                {
                    "id": "comp-database",
                    "name": "Relational Database Layer",
                    "category": "Storage",
                    "purpose": "Maintains persistent, ACID-compliant transactional state and audit history.",
                    "description": "PostgreSQL relational engine with automated daily backups and read replicas.",
                    "inputs": ["SQL Read/Write queries", "Transactional commits"],
                    "outputs": ["Consistent record sets", "Replication WAL logs"],
                    "technologies": ["PostgreSQL 16", "Django ORM", "PgBouncer"],
                    "dependencies": ["comp-core-logic", "comp-decision"],
                    "connected_components": []
                }
            ],
            "dependencies": ["Django 6.1", "PostgreSQL", "Redis", "Celery"],
            "logic": "Inbound User Action -> Gateway Token Check -> Core Orchestrator -> Intelligence Analysis -> Decision Validation -> Database Commit -> WebSocket Client Broadcast.",
            "workflow": "Client UI -> API Gateway -> Orchestrator -> Intelligence -> Decision Rules -> Database.",
            "risks": ["Concurrency conflicts during peak read/write spikes", "Third-party service API rate limits"],
            "constraints": ["Sub-200ms API response time (p95)", "Full horizontal scalability without state lock"],
            "feasibility": {
                "score": 90,
                "technical": "High feasibility with standard modular cloud primitives.",
                "software": "Django REST, PostgreSQL, Redis, Celery.",
                "hardware": "Standard cloud compute cluster.",
                "data_requirements": "Schema-validated relational records.",
                "complexity": "Moderate.",
                "assessment": "Robust and proven architecture with standard maintenance protocols."
            },
            "build_steps": [
                {
                    "step_number": 1,
                    "title": "Architecture Setup & Database Models",
                    "description": "Initialize database schemas, migrations, and Docker Compose configurations.",
                    "required_components": ["Relational Database Layer"],
                    "expected_result": "Operational local database with schema migrations.",
                    "status": "current"
                },
                {
                    "step_number": 2,
                    "title": "API Gateway & Authentication Service",
                    "description": "Implement JWT authentication, user registration, and rate limiting middlewares.",
                    "required_components": ["API Gateway & Security Proxy"],
                    "expected_result": "Protected endpoints rejecting unauthorized callers.",
                    "status": "next"
                },
                {
                    "step_number": 3,
                    "title": "Core Orchestration & Worker Pipeline",
                    "description": "Develop core business logic handlers and asynchronous task worker queues.",
                    "required_components": ["Core Orchestration Engine"],
                    "expected_result": "Asynchronous tasks processing successfully via Celery.",
                    "status": "next"
                },
                {
                    "step_number": 4,
                    "title": "Intelligence Engine & Decision Matrix",
                    "description": "Implement telemetry processing, analytical scoring, and decision rules.",
                    "required_components": ["Analytics & Intelligence Model", "Decision & Dispatch Controller"],
                    "expected_result": "Automated scoring and decision dispatches triggered by events.",
                    "status": "next"
                },
                {
                    "step_number": 5,
                    "title": "Frontend Workspace & Telemetry Visualizer",
                    "description": "Deploy interactive client UI with real-time WebSocket feeds and export tools.",
                    "required_components": ["Universal Client Presentation Layer"],
                    "expected_result": "Production-ready web application fully interactive and tested.",
                    "status": "next"
                }
            ]
        }


def synthesize_project_architecture(project):
    """
    Performs deep synthesis on an existing project DNA, generating detailed
    component relationships, data flow, processing sequences, decision logic, and architecture graph.
    """
    dna = project.dna_data or {}
    components = dna.get("components", [])

    nodes = []
    edges = []

    # Map components to sequential horizontal layers
    for idx, c in enumerate(components):
        layer_x = 120 + (idx % 5) * 190
        layer_y = 140 + (idx // 5) * 180

        node_dict = {
            "id": c.get("id", f"node-{idx}"),
            "name": c.get("name", f"Component {idx}"),
            "category": c.get("category", "Processing"),
            "purpose": c.get("purpose", ""),
            "description": c.get("description", ""),
            "inputs": c.get("inputs", []),
            "outputs": c.get("outputs", []),
            "technologies": c.get("technologies", []),
            "dependencies": c.get("dependencies", []),
            "position": {"x": layer_x, "y": layer_y}
        }
        nodes.append(node_dict)

        # Create data flow edges to next component
        if idx < len(components) - 1:
            edges.append({
                "id": f"edge-{idx}-{idx+1}",
                "from": c.get("id", f"node-{idx}"),
                "to": components[idx+1].get("id", f"node-{idx+1}"),
                "label": f"{c.get('outputs', ['Data'])[0]}",
                "protocol": "Internal Bus / Async",
                "animated": True
            })

    architecture_data = {
        "pattern": "Decoupled Event-Driven Microkernel Architecture",
        "nodes": nodes,
        "edges": edges,
        "data_flow_sequence": [f"{c.get('name')} -> {c.get('outputs', ['Output'])[0]}" for c in components],
        "synthesized_at": "True",
    }

    return architecture_data


def process_project_assistant_interaction(project, message):
    """
    Project-aware assistant that answers questions OR modifies the project DNA.
    Returns (reply_text, project_updated_flag).
    """
    msg_low = message.lower()
    
    # Check if modification requested:
    # "add mobile application", "add machine learning", "remove X", "change database to MongoDB", etc.
    is_modification = any(k in msg_low for k in ["add ", "remove ", "change ", "replace ", "integrate ", "modify "])
    
    if is_modification:
        # Perform real modification on project DNA
        dna = project.dna_data or {}
        components = dna.get("components", [])
        updated = False
        change_desc = ""

        if "mobile" in msg_low and not any("mobile" in c.get("name", "").lower() for c in components):
            new_comp = {
                "id": f"comp-mobile-{len(components)+1}",
                "name": "Mobile Companion App (iOS & Android)",
                "category": "Input",
                "purpose": "Allows on-the-go monitoring, push alerts, and remote parameter control from mobile devices.",
                "description": "Cross-platform Flutter / React Native client interfacing with backend REST API.",
                "inputs": ["User touch inputs", "Biometric unlock credentials"],
                "outputs": ["Remote dispatch requests", "Push token registers"],
                "technologies": ["Flutter", "Dart", "Firebase Cloud Messaging"],
                "dependencies": [],
                "connected_components": [components[0]["name"] if components else "Backend API"]
            }
            components.insert(0, new_comp)
            dna["components"] = components
            dna["software"] = list(set(dna.get("software", []) + ["Flutter", "Dart", "Firebase"]))
            updated = True
            change_desc = "Added Mobile Companion App (iOS & Android) to the architecture."

        elif "authentication" in msg_low or "auth" in msg_low:
            new_comp = {
                "id": f"comp-auth-{len(components)+1}",
                "name": "Zero-Trust Identity & Auth Service",
                "category": "Processing",
                "purpose": "Provides OAuth 2.1, JWT validation, role-based permissions, and multi-factor authentication.",
                "description": "Hardened identity provider ensuring cryptographically signed request validation.",
                "inputs": ["Login credentials", "MFA TOTP tokens"],
                "outputs": ["RS256 signed JWT tokens", "Access audit events"],
                "technologies": ["OAuth 2.1", "JWT", "Redis Session Store"],
                "dependencies": [],
                "connected_components": ["Core Logic"]
            }
            components.insert(1, new_comp)
            dna["components"] = components
            updated = True
            change_desc = "Integrated Zero-Trust Identity & Auth Service."

        elif "machine learning" in msg_low or "ai" in msg_low:
            new_comp = {
                "id": f"comp-ml-{len(components)+1}",
                "name": "Predictive AI Inference Engine",
                "category": "Intelligence",
                "purpose": "Performs continuous pattern detection, automated anomaly classification, and predictive telemetry.",
                "description": "Containerized neural model executing low-latency ONNX inference.",
                "inputs": ["Normalized system feature vectors"],
                "outputs": ["Confidence matrices", "Predictive triggers"],
                "technologies": ["PyTorch", "ONNX Runtime", "FastAPI"],
                "dependencies": [],
                "connected_components": ["Core Logic"]
            }
            components.append(new_comp)
            dna["components"] = components
            updated = True
            change_desc = "Integrated Predictive AI Inference Engine."

        elif "remove" in msg_low:
            # find matching component
            for idx, c in enumerate(components):
                name_words = c.get("name", "").lower().split()
                if any(w in msg_low for w in name_words if len(w) > 3):
                    removed = components.pop(idx)
                    dna["components"] = components
                    updated = True
                    change_desc = f"Removed component '{removed.get('name')}' from Project DNA."
                    break

        if updated:
            project.dna_data = dna
            # Re-synthesize architecture with updated components
            project.architecture_data = synthesize_project_architecture(project)
            project.save()

            # Synchronize ComponentNode database table
            project.components.all().delete()
            for idx, c in enumerate(dna.get("components", [])):
                from .models import ComponentNode
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

            reply = f"{DEFAULT_ASSISTANT_INTRO} Architecture modification executed: {change_desc} The Digital DNA and architecture diagram have been updated live in the database."
            return reply, True

    # Informational question answering with current project context
    title = project.title
    p_type = project.project_type
    goal = project.goal
    steps = project.build_plan or []
    first_step = steps[0].get("title", "Foundational setup") if steps else "Scaffolding"

    if "first" in msg_low or "what should i build" in msg_low or "start" in msg_low:
        return f"{DEFAULT_ASSISTANT_INTRO} For {title}, the first critical milestone you should build is: '{first_step}'. Focus on establishing data contracts, sensor/client schemas, and local test harnesses before building downstream logic.", False

    if "explain" in msg_low:
        return f"{DEFAULT_ASSISTANT_INTRO} {title} is an architectural system in the domain of '{p_type}'. Goal: {goal}. Its Digital DNA decouples raw inputs into intelligent processing and autonomous decision outputs.", False

    if "risk" in msg_low:
        risks = project.risks_mitigations or project.dna_data.get("risks", ["Network latency", "Data integrity"])
        risk_str = "; ".join(risks[:2]) if isinstance(risks, list) else str(risks)
        return f"{DEFAULT_ASSISTANT_INTRO} Key engineering risks identified for {title}: {risk_str}. Mitigate these by introducing buffering queues and strict data contract schemas.", False

    if "feasibility" in msg_low:
        return f"{DEFAULT_ASSISTANT_INTRO} The calculated feasibility score for {title} is {project.feasibility_score}%. {project.feasibility_summary}", False

    return f"{DEFAULT_ASSISTANT_INTRO} I am actively monitoring {title}. You can inspect the Digital DNA components, review the 5-phase build plan, or ask me to modify the architecture (e.g., 'Add a mobile application', 'Add authentication').", False
