import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F1 3D Grand Prix Simulator",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 3D 그랑프리: 스타트 신호등 & 3D 피트 가레지 시뮬레이터")
st.markdown("""
**[게임 조작 및 튜닝 전략]**
- **🚦 스타트 카운트다운:** 5개의 빨간 불이 들어온 뒤 **신호등이 꺼지면(LIGHTS OUT!) 초록불**과 함께 가속이 시작됩니다.
- **방향키 (↑ / ↓ / ← / →) 또는 WASD:** 가속 / 브레이크 / **부드러운 3D 조향**
- **스페이스바 (Space):** 리어 윙 4단계 전환 (**0° ➔ 15° ➔ 30° ➔ 40°**)
- **피트인 (Pit Stop):** 타이어 마모 시 **오른쪽 피트 레이인(가레지 구역)**으로 진입하면 3D 피트 크루 타이어 교체 시작!
""")

# HTML5 + Three.js Real 3D F1 Engine
game_3d_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #030712;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
        }
        #canvas-container {
            width: 100vw;
            height: 630px;
            position: relative;
        }
        
        /* Glassmorphism HUD Overlay */
        .hud-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(10px);
            padding: 10px 18px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
            z-index: 10;
        }
        .hud-item {
            font-size: 13px;
            font-weight: 600;
            color: white;
        }
        .hud-value {
            color: #ffcc00;
            font-weight: bold;
            font-size: 16px;
        }

        .badge {
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: bold;
            color: white;
        }
        .badge-wing { background: #e63946; }
        .badge-soft { background: #e63946; }
        .badge-medium { background: #eab308; color: black; }
        .badge-hard { background: #94a3b8; color: black; }

        /* F1 Start Light Display Overlay */
        #startLightOverlay {
            display: none;
            position: absolute;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 10, 10, 0.9);
            border: 3px solid #333;
            padding: 12px 25px;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
            z-index: 20;
        }
        .light-box {
            display: flex;
            gap: 12px;
            margin-top: 5px;
        }
        .light-bulb {
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background-color: #333;
            border: 2px solid #111;
            box-shadow: inset 0 0 5px rgba(0,0,0,0.8);
        }
        .light-red {
            background-color: #ff0000 !important;
            box-shadow: 0 0 18px #ff0000, inset 0 0 5px #fff !important;
        }
        .light-green {
            background-color: #00ff00 !important;
            box-shadow: 0 0 25px #00ff00, inset 0 0 5px #fff !important;
        }

        /* Start Setup Modal */
        #startModal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.96);
            border: 2px solid #ffcc00;
            padding: 25px 35px;
            border-radius: 16px;
            text-align: center;
            width: 380px;
            box-shadow: 0 0 50px rgba(255, 204, 0, 0.4);
            z-index: 50;
            color: white;
        }
        #startModal h2 { color: #ffcc00; margin-top: 0; }
        .setting-group {
            margin: 15px 0;
            text-align: left;
        }
        .setting-group label {
            display: block;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #cbd5e1;
        }
        select {
            width: 100%;
            padding: 8px 12px;
            background: #1e293b;
            color: white;
            border: 1px solid #475569;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        .btn-start {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 12px 30px;
            font-size: 17px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
            transition: transform 0.2s;
        }
        .btn-start:hover { transform: scale(1.03); background: #ffd633; }

        /* Pit Stop Interactive Modal */
        #pitModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.98);
            border: 3px solid #ea580c;
            padding: 22px 30px;
            border-radius: 16px;
            text-align: center;
            z-index: 60;
            color: white;
            box-shadow: 0 0 40px rgba(234, 88, 12, 0.5);
        }
        #pitModal h3 { margin: 0 0 10px 0; color: #ea580c; }
        .btn-compound {
            padding: 10px 18px;
            margin: 5px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            transition: transform 0.15s;
        }
        .btn-compound:hover { transform: scale(1.05); }

        /* Summary Result Modal */
        #summaryModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.96);
            border: 2px solid #ffcc00;
            padding: 25px 35px;
            border-radius: 16px;
            text-align: center;
            width: 360px;
            box-shadow: 0 0 50px rgba(255, 204, 0, 0.5);
            z-index: 100;
            color: white;
        }
        #summaryModal h2 { color: #ffcc00; margin-top: 0; }
        .stat-box {
            background: #1e293b;
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 8px;
            text-align: left;
            border: 1px solid #334155;
        }
        .btn-restart {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 10px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
        }
    </style>
    <!-- Three.js 3D Engine -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container">
        <!-- Telemetry HUD -->
        <div class="hud-panel">
            <div class="hud-item">🏎️ 순위: <span id="posVal" class="hud-value" style="color:#38bdf8;">2nd / 4</span></div>
            <div class="hud-item">🔧 윙 [Space]: <span id="wingBadge" class="badge badge-wing">15°</span></div>
            <div class="hud-item">🛞 타이어: <span id="tireBadge" class="badge badge-medium">MEDIUM</span> <span id="wearVal" class="hud-value">100%</span></div>
            <div class="hud-item">⚡ 속도: <span id="speedVal" class="hud-value">0</span> km/h</div>
            <div class="hud-item">🚩 Lap: <span id="lapVal" class="hud-value">1 / 5</span></div>
            <div class="hud-item">⏱️ 타임: <span id="timeVal" class="hud-value">0.00s</span></div>
        </div>

        <!-- F1 Lights Out Display Panel -->
        <div id="startLightOverlay">
            <span style="font-size:12px; font-weight:bold; color:#aaa; letter-spacing:1px;">FORMULA 1 START LIGHTS</span>
            <div class="light-box">
                <div class="light-bulb" id="light1"></div>
                <div class="light-bulb" id="light2"></div>
                <div class="light-bulb" id="light3"></div>
                <div class="light-bulb" id="light4"></div>
                <div class="light-bulb" id="light5"></div>
            </div>
            <span id="lightText" style="font-size:13px; font-weight:bold; color:#ffcc00; margin-top:4px;">GRID ALIGNED</span>
        </div>

        <!-- Setup Game Modal -->
        <div id="startModal">
            <h2>🏆 3D F1 챔피언십 설정</h2>
            <div class="setting-group">
                <label>🚩 레이스 랩 수 선택</label>
                <select id="selectLaps">
                    <option value="3">3 Laps (스프린트 레이스)</option>
                    <option value="5" selected>5 Laps (표준 레이스)</option>
                    <option value="8">8 Laps (전략 레이스)</option>
                    <option value="12">12 Laps (풀 피트스탑 레이스)</option>
                </select>
            </div>
            <div class="setting-group">
                <label>🛞 스타트 타이어 선택</label>
                <select id="selectTire">
                    <option value="SOFT">🔴 Soft (최고 속도, 빠른 마모)</option>
                    <option value="MEDIUM" selected>🟡 Medium (표준 밸런스)</option>
                    <option value="HARD">⚪ Hard (느린 속도, 강한 내구성)</option>
                </select>
            </div>
            <button class="btn-start" onclick="initGame()">3D 레이스 스타트!</button>
        </div>

        <!-- Pit Stop Interactive Modal -->
        <div id="pitModal">
            <h3>⛽ F1 PIT STOP! 타이어 교체</h3>
            <p style="font-size:13px; margin-bottom:12px;">피트 크루 대기 중! 새 타이어를 선택하세요:</p>
            <button class="btn-compound" style="background:#e63946; color:white;" onclick="changeTire('SOFT')">🔴 SOFT</button>
            <button class="btn-compound" style="background:#eab308; color:black;" onclick="changeTire('MEDIUM')">🟡 MEDIUM</button>
            <button class="btn-compound" style="background:#94a3b8; color:black;" onclick="changeTire('HARD')">⚪ HARD</button>
        </div>

        <!-- Summary Result Modal -->
        <div id="summaryModal">
            <h2>🏁 레이스 종료!</h2>
            <div class="stat-box">🥇 <b>최종 순위:</b> <span id="finalPos" style="color:#ffcc00;">-</span></div>
            <div class="stat-box">🏆 <b>최단 랩타임 (Best):</b> <span id="bestLap" style="color:#4caf50;">-</span></div>
            <div class="stat-box">🐢 <b>최장 랩타임 (Worst):</b> <span id="worstLap" style="color:#f44336;">-</span></div>
            <div class="stat-box">📊 <b>각 랩별 기록:</b><div id="lapHistory" style="font-size:13px; margin-top:5px; color:#cbd5e1;"></div></div>
            <button class="btn-restart" onclick="location.reload()">다시 시작하기</button>
        </div>
    </div>

<script>
// --- Three.js Initialization ---
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x6ca6cd);
scene.fog = new THREE.FogExp2(0x6ca6cd, 0.0012);

const camera = new THREE.PerspectiveCamera(55, container.clientWidth / 630, 0.1, 1500);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, 630);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// --- Lighting ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
dirLight.position.set(200, 300, 150);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.near = 10;
dirLight.shadow.camera.far = 800;
dirLight.shadow.camera.left = -300;
dirLight.shadow.camera.right = 300;
dirLight.shadow.camera.top = 300;
dirLight.shadow.camera.bottom = -300;
scene.add(dirLight);

// Grass Surface
const grassGeo = new THREE.PlaneGeometry(2500, 2500);
const grassMat = new THREE.MeshLambertMaterial({ color: 0x225522 });
const grass = new THREE.Mesh(grassGeo, grassMat);
grass.rotation.x = -Math.PI / 2;
grass.position.y = -0.05;
grass.receiveShadow = true;
scene.add(grass);

// --- 3D Real F1 Track Ribbon Generator ---
const trackPoints = [
    new THREE.Vector3(0, 0, 220),       // Start / Main Straight
    new THREE.Vector3(260, 0, 220),     // Turn 1
    new THREE.Vector3(340, 0, 140),     // Chicane
    new THREE.Vector3(300, 0, 30),      
    new THREE.Vector3(360, 0, -80),     // Hairpin
    new THREE.Vector3(250, 0, -220),    
    new THREE.Vector3(80, 0, -240),     // Back Straight
    new THREE.Vector3(-120, 0, -240),   // High Speed Sweeper
    new THREE.Vector3(-280, 0, -120),   // S-Curve
    new THREE.Vector3(-220, 0, 20),     
    new THREE.Vector3(-300, 0, 120),    // Parabolica
    new THREE.Vector3(-200, 0, 220)     // Final Corner to Main Straight
];

const trackCurve = new THREE.CatmullRomCurve3(trackPoints, true, 'catmullrom', 0.25);
const SEGMENTS = 360;
const ROAD_WIDTH = 34;

function build3DTrack() {
    const points = trackCurve.getSpacedPoints(SEGMENTS);
    const roadVertices = [], roadIndices = [];
    const kerbVertices = [], kerbColors = [], kerbIndices = [];

    for (let i = 0; i <= SEGMENTS; i++) {
        const p1 = points[i % SEGMENTS];
        const p2 = points[(i + 1) % SEGMENTS];

        const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();

        const lRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2));
        const rRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2));

        roadVertices.push(lRoad.x, 0.01, lRoad.z);
        roadVertices.push(rRoad.x, 0.01, rRoad.z);

        if (i < SEGMENTS) {
            const r1 = i * 2, r2 = (i + 1) * 2;
            roadIndices.push(r1, r1 + 1, r2);
            roadIndices.push(r1 + 1, r2 + 1, r2);
        }

        // Red/White Kerb Borders
        const lKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2 + 3.0));
        const rKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2 - 3.0));
        const color = (Math.floor(i / 2) % 2 === 0) ? [0.9, 0.1, 0.1] : [0.95, 0.95, 0.95];

        kerbVertices.push(lRoad.x, 0.02, lRoad.z, lKerbOuter.x, 0.02, lKerbOuter.z);
        kerbColors.push(...color, ...color);

        kerbVertices.push(rRoad.x, 0.02, rRoad.z, rKerbOuter.x, 0.02, rKerbOuter.z);
        kerbColors.push(...color, ...color);

        if (i < SEGMENTS) {
            const k1 = i * 4, k2 = (i + 1) * 4;
            kerbIndices.push(k1, k1 + 1, k2, k1 + 1, k2 + 1, k2);
            kerbIndices.push(k1 + 2, k1 + 3, k2 + 2, k1 + 3, k2 + 3, k2 + 2);
        }
    }

    const roadGeo = new THREE.BufferGeometry();
    roadGeo.setAttribute('position', new THREE.Float32BufferAttribute(roadVertices, 3));
    roadGeo.setIndex(roadIndices);
    roadGeo.computeVertexNormals();

    const roadMat = new THREE.MeshStandardMaterial({ color: 0x222226, roughness: 0.85 });
    const roadMesh = new THREE.Mesh(roadGeo, roadMat);
    roadMesh.receiveShadow = true;
    scene.add(roadMesh);

    const kerbGeo = new THREE.BufferGeometry();
    kerbGeo.setAttribute('position', new THREE.Float32BufferAttribute(kerbVertices, 3));
    kerbGeo.setAttribute('color', new THREE.Float32BufferAttribute(kerbColors, 3));
    kerbGeo.setIndex(kerbIndices);
    
    const kerbMesh = new THREE.Mesh(kerbGeo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
    scene.add(kerbMesh);
}
build3DTrack();

// --- Outer 3D Guardrails & Wall Barriers ---
function buildGuardrails() {
    const points = trackCurve.getSpacedPoints(180);
    const railMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8, roughness: 0.3 });

    for (let i = 0; i < points.length; i += 2) {
        const p1 = points[i];
        const p2 = points[(i + 1) % points.length];
        const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();

        const postPos = p1.clone().add(norm.multiplyScalar(ROAD_WIDTH / 2 + 4.5));
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 3), railMat);
        post.position.set(postPos.x, 1.5, postPos.z);
        scene.add(post);
    }
}
buildGuardrails();

// --- Detailed 3D Pit Lane & Pit Garages ---
const pitGroup = new THREE.Group();
pitGroup.position.set(0, 0, 220);

// Pit Wall Separation Barrier
const pitWall = new THREE.Mesh(
    new THREE.BoxGeometry(100, 2.2, 1.2),
    new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.5 })
);
pitWall.position.set(20, 1.1, ROAD_WIDTH / 2 + 1.5);
pitGroup.add(pitWall);

// Pit Lane Asphalt
const pitAsphalt = new THREE.Mesh(
    new THREE.PlaneGeometry(100, 16),
    new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 })
);
pitAsphalt.rotation.x = -Math.PI / 2;
pitAsphalt.position.set(20, 0.02, ROAD_WIDTH / 2 + 10);
pitGroup.add(pitAsphalt);

// 3D Pit Garage Buildings (4 Team Garages)
const garageColors = [0xef4444, 0x1e3a8a, 0x06b6d4, 0xf97316];
for (let i = 0; i < 4; i++) {
    const gBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(20, 6, 12),
        new THREE.MeshStandardMaterial({ color: garageColors[i], metalness: 0.4 })
    );
    gBuilding.position.set(-20 + i * 24, 3, ROAD_WIDTH / 2 + 19);
    pitGroup.add(gBuilding);
}

// Interactive Pit Stop Target Box Marking (Orange Outline)
const pitBoxGeo = new THREE.PlaneGeometry(16, 10);
const pitBoxMat = new THREE.MeshBasicMaterial({ color: 0xea580c, side: THREE.DoubleSide });
const pitBoxMesh = new THREE.Mesh(pitBoxGeo, pitBoxMat);
pitBoxMesh.rotation.x = -Math.PI / 2;
pitBoxMesh.position.set(20, 0.04, ROAD_WIDTH / 2 + 10);
pitGroup.add(pitBoxMesh);

scene.add(pitGroup);

// --- Finish Line Gantry & Start Lights Mesh ---
const gantryGroup = new THREE.Group();
gantryGroup.position.set(0, 0, 220);

const p1 = new THREE.Mesh(new THREE.BoxGeometry(1.5, 12, 1.5), new THREE.MeshStandardMaterial({ color: 0x333333 }));
p1.position.set(-ROAD_WIDTH/2 - 3, 6, 0);
const p2 = p1.clone();
p2.position.set(ROAD_WIDTH/2 + 3, 6, 0);

const topBeam = new THREE.Mesh(new THREE.BoxGeometry(ROAD_WIDTH + 8, 2, 2), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
topBeam.position.set(0, 11, 0);
gantryGroup.add(p1, p2, topBeam);
scene.add(gantryGroup);

// --- 3D Car Factory Mesh Generator ---
function create3DCar(colorHex, rWingColorHex) {
    const carGroup = new THREE.Group();

    // Body Chassis
    const body = new THREE.Mesh(
        new THREE.BoxGeometry(2.4, 0.75, 5.4),
        new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.2, metalness: 0.6 })
    );
    body.position.y = 0.6;
    body.castShadow = true;
    carGroup.add(body);

    // Cockpit
    const cockpit = new THREE.Mesh(
        new THREE.SphereGeometry(0.6, 16, 16),
        new THREE.MeshStandardMaterial({ color: 0x111111 })
    );
    cockpit.position.set(0, 0.9, -0.2);
    carGroup.add(cockpit);

    // Front Wing
    const fWing = new THREE.Mesh(
        new THREE.BoxGeometry(3.8, 0.12, 1.0),
        new THREE.MeshStandardMaterial({ color: 0x111111 })
    );
    fWing.position.set(0, 0.35, 2.7);
    fWing.castShadow = true;
    carGroup.add(fWing);

    // Rear Wing
    const rearWingGroup = new THREE.Group();
    rearWingGroup.position.set(0, 1.2, -2.5);
    const rWingMain = new THREE.Mesh(
        new THREE.BoxGeometry(3.4, 0.2, 1.0),
        new THREE.MeshStandardMaterial({ color: rWingColorHex })
    );
    rWingMain.castShadow = true;
    rearWingGroup.add(rWingMain);

    const rWingPillar1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.65, 0.12), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    rWingPillar1.position.set(-1.0, -0.3, 0);
    rearWingGroup.add(rWingPillar1);
    const rWingPillar2 = rWingPillar1.clone();
    rWingPillar2.position.set(1.0, -0.3, 0);
    rearWingGroup.add(rWingPillar2);

    carGroup.add(rearWingGroup);

    // Wheels
    const wheels = [];
    const wheelPositions = [[-1.4, 0.6, 1.9], [1.4, 0.6, 1.9], [-1.4, 0.6, -1.9], [1.4, 0.6, -1.9]];
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0d0d0d, roughness: 0.9 });

    wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.5, 16), wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(...pos);
        wheel.castShadow = true;
        carGroup.add(wheel);
        wheels.push(wheel);
    });

    return { group: carGroup, rearWingGroup, wheels, wheelMat };
}

// Player 3D Car Model
const playerObj = create3DCar(0xef4444, 0xffcc00);
scene.add(playerObj.group);

// 3 AI Rival Cars Model
const aiCarData = [
    { name: "Red Bull", color: 0x1e3a8a, rWing: 0xf59e0b, gridX: -30, gridZ: 226, offset: -6, speed: 0.82 },
    { name: "Mercedes", color: 0x64748b, rWing: 0x06b6d4, gridX: 20, gridZ: 226, offset: 6, speed: 0.80 },
    { name: "McLaren", color: 0xf97316, rWing: 0x111827, gridX: -45, gridZ: 214, offset: -10, speed: 0.78 }
];

const aiCars = aiCarData.map(d => {
    const obj = create3DCar(d.color, d.rWing);
    scene.add(obj.group);
    return { ...d, obj, lap: 0, progress: 0 };
});

// Grid Alignment Setup (Start Facing Forward +X Direction)
function alignGridPositions() {
    // Player P2 Slot (Grid Position)
    playerObj.group.position.set(-5, 0, 214);
    playerObj.group.rotation.y = Math.PI / 2; // Facing +X down main straight
    
    // AI Grid Slots (P1, P3, P4)
    aiCars.forEach(ai => {
        ai.obj.group.position.set(ai.gridX, 0, ai.gridZ);
        ai.obj.group.rotation.y = Math.PI / 2;
        ai.progress = (ai.gridX + 300) / 1000;
    });
}
alignGridPositions();

// Aerodynamics & Tire Mechanics
const wingPresetAngles = [0, 15, 30, 40];
let wingPresetIndex = 1;
let wingAngle = 15;

const TIRE_SPECS = {
    'SOFT': { speedMult: 1.08, gripMult: 1.25, wearRate: 0.28, badgeClass: 'badge-soft', wheelColor: 0xe63946 },
    'MEDIUM': { speedMult: 1.00, gripMult: 1.00, wearRate: 0.14, badgeClass: 'badge-medium', wheelColor: 0xeab308 },
    'HARD': { speedMult: 0.94, gripMult: 0.82, wearRate: 0.06, badgeClass: 'badge-hard', wheelColor: 0x94a3b8 }
};

let currentTire = 'MEDIUM';
let tireWear = 100.0;
let keys = {};

// Physics Variables
let speed = 0;
let carAngle = Math.PI / 2; // Starting facing +X direction
let steerSmooth = 0;
let inPit = false;

// Race Flow State
let startState = 'WAITING'; // WAITING -> COUNTDOWN -> GO
let maxLaps = 5;
let playerLap = 0;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

// Key Handlers
window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD"].includes(e.code)) {
        e.preventDefault();
    }
    if (e.code === 'Space' && !e.repeat && startState === 'GO' && !isFinished) {
        wingPresetIndex = (wingPresetIndex + 1) % wingPresetAngles.length;
        wingAngle = wingPresetAngles[wingPresetIndex];
        playerObj.rearWingGroup.rotation.x = (wingAngle * Math.PI) / 180;
        document.getElementById('wingBadge').innerText = wingAngle + '°';
    }
    keys[e.code] = true;
});
window.addEventListener('keyup', e => keys[e.code] = false);

// F1 Start Lights Sequence (5 Red Lights -> Lights Out!)
function initGame() {
    maxLaps = parseInt(document.getElementById('selectLaps').value);
    currentTire = document.getElementById('selectTire').value;
    updateTireUI();

    document.getElementById('startModal').style.display = 'none';
    document.getElementById('startLightOverlay').style.display = 'flex';
    document.getElementById('lapVal').innerText = `1 / ${maxLaps}`;

    startState = 'COUNTDOWN';
    runStartLightsSequence();
}

function runStartLightsSequence() {
    let lightStep = 1;
    document.getElementById('lightText').innerText = 'GET READY...';

    const interval = setInterval(() => {
        if (lightStep <= 5) {
            document.getElementById(`light${lightStep}`).classList.add('light-red');
            lightStep++;
        } else {
            clearInterval(interval);
            // Random delay between 0.8s and 2.0s before Lights Out
            const randomDelay = 800 + Math.random() * 1200;
            setTimeout(() => {
                // LIGHTS OUT & AWAY WE GO!
                for (let i = 1; i <= 5; i++) {
                    const el = document.getElementById(`light${i}`);
                    el.classList.remove('light-red');
                    el.classList.add('light-green');
                }
                document.getElementById('lightText').innerText = 'LIGHTS OUT & AWAY WE GO!';
                
                startState = 'GO';
                lapStartTime = Date.now();

                // Hide light panel after 2.5s
                setTimeout(() => {
                    document.getElementById('startLightOverlay').style.display = 'none';
                }, 2500);
            }, randomDelay);
        }
    }, 1000);
}

function updateTireUI() {
    const spec = TIRE_SPECS[currentTire];
    const badge = document.getElementById('tireBadge');
    badge.innerText = currentTire;
    badge.className = `badge ${spec.badgeClass}`;
    playerObj.wheelMat.color.setHex(spec.wheelColor);
}

function updatePhysics() {
    // Lock physics before GO signal (Prevents False Start)
    if (startState !== 'GO' || isFinished) return;

    if (inPit) {
        speed *= 0.8;
        return;
    }

    const spec = TIRE_SPECS[currentTire];
    const wearGripPenalty = tireWear < 30 ? (tireWear / 30) : 1.0;

    const maxSpeed = (0.98 - (wingAngle / 40) * 0.48) * spec.speedMult * wearGripPenalty;
    const gripFactor = (0.009 + (wingAngle / 40) * 0.017) * spec.gripMult * wearGripPenalty;

    // Throttle & Brake Controls
    if (keys['ArrowUp'] || keys['KeyW']) speed += 0.008;
    else if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.012;
    else speed *= 0.985;

    if (speed > maxSpeed) speed = maxSpeed;
    if (speed < -maxSpeed * 0.3) speed = -maxSpeed * 0.3;

    // Smooth Steering Inertia
    const steerTarget = (keys['ArrowLeft'] || keys['KeyA']) ? 1 : ((keys['ArrowRight'] || keys['KeyD']) ? -1 : 0);
    steerSmooth += (steerTarget - steerSmooth) * 0.1;

    if (Math.abs(speed) > 0.02) {
        const dir = speed > 0 ? 1 : -1;
        carAngle += steerSmooth * gripFactor * dir * (speed / maxSpeed);
    }

    if (Math.abs(speed) > 0.05) {
        tireWear -= spec.wearRate * (1 + Math.abs(steerSmooth) * 0.5) * 0.05;
        if (tireWear < 0) tireWear = 0;
    }

    // Off-Track Grass Drag Penalty
    const carPos = playerObj.group.position;
    const currentProgress = getTrackProgress(carPos);
    const closestPoint = trackCurve.getPointAt(currentProgress % 1);
    if (carPos.distanceTo(closestPoint) > ROAD_WIDTH / 2 + 1) {
        speed *= 0.88;
    }

    // Move Player 3D Mesh
    carPos.x += Math.sin(carAngle) * speed;
    carPos.z += Math.cos(carAngle) * speed;
    playerObj.group.rotation.y = carAngle;

    playerObj.wheels[0].rotation.y = steerSmooth * 0.4;
    playerObj.wheels[1].rotation.y = steerSmooth * 0.4;
    playerObj.wheels.forEach(w => w.rotation.x += speed * 0.4);

    // 3rd Person Chase Camera Follow
    const camOffset = new THREE.Vector3(0, 5.5, -14).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
    camera.position.lerp(carPos.clone().add(camOffset), 0.2);
    camera.lookAt(carPos.clone().add(new THREE.Vector3(0, 1.2, 0)));

    // Pit Stop Area Check (Garage Box Area)
    if (carPos.x > 10 && carPos.x < 30 && carPos.z > 220 && carPos.z < 240 && !inPit) {
        inPit = true;
        document.getElementById('pitModal').style.display = 'block';
    }

    // Checkpoints & Finish Line Crossing
    if (carPos.z < -180) checkpointPassed = true;

    if (checkpointPassed && Math.abs(carPos.x) < 25 && carPos.z > 215) {
        const now = Date.now();
        const lapTime = (now - lapStartTime) / 1000;
        lapTimes.push(lapTime);

        checkpointPassed = false;
        lapStartTime = now;
        playerLap++;

        if (playerLap < maxLaps) {
            document.getElementById('lapVal').innerText = `${playerLap + 1} / ${maxLaps}`;
        } else {
            isFinished = true;
            showSummaryModal();
        }
    }

    // Move AI Competitors
    aiCars.forEach(ai => {
        ai.progress = (ai.progress + ai.speed * 0.0004) % 1;
        const pt = trackCurve.getPointAt(ai.progress);
        const nextPt = trackCurve.getPointAt((ai.progress + 0.005) % 1);
        
        const dir = new THREE.Vector3().subVectors(nextPt, pt).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();
        
        const aiPos = pt.clone().add(norm.multiplyScalar(ai.offset));
        ai.obj.group.position.copy(aiPos);
        ai.obj.group.rotation.y = Math.atan2(dir.x, dir.z);
    });

    calculateStandings(currentProgress);

    // Telemetry Update
    document.getElementById('speedVal').innerText = Math.round(Math.abs(speed) * 270);
    document.getElementById('wearVal').innerText = `${Math.round(tireWear)}%`;
    if (!isFinished) {
        document.getElementById('timeVal').innerText = `${((Date.now() - lapStartTime) / 1000).toFixed(2)}s`;
    }
}

function calculateStandings(playerProgress) {
    const standings = [
        { name: "Player", score: playerLap + playerProgress, isPlayer: true },
        ...aiCars.map(ai => ({ name: ai.name, score: ai.lap + ai.progress, isPlayer: false }))
    ];
    standings.sort((a, b) => b.score - a.score);

    const rank = standings.findIndex(s => s.isPlayer) + 1;
    const suffix = rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th';
    document.getElementById('posVal').innerText = `${rank}${suffix} / 4`;
}

function getTrackProgress(pos) {
    let minDist = Infinity, closestT = 0;
    for (let t = 0; t <= 1; t += 0.01) {
        const pt = trackCurve.getPointAt(t);
        const d = pt.distanceTo(pos);
        if (d < minDist) {
            minDist = d;
            closestT = t;
        }
    }
    return closestT;
}

function changeTire(newCompound) {
    currentTire = newCompound;
    tireWear = 100.0;
    updateTireUI();

    setTimeout(() => {
        inPit = false;
        document.getElementById('pitModal').style.display = 'none';
    }, 1500);
}

function showSummaryModal() {
    const best = Math.min(...lapTimes).toFixed(2);
    const worst = Math.max(...lapTimes).toFixed(2);
    
    document.getElementById('finalPos').innerText = document.getElementById('posVal').innerText;
    document.getElementById('bestLap').innerText = `${best} 초`;
    document.getElementById('worstLap').innerText = `${worst} 초`;
    
    let historyHtml = "";
    lapTimes.forEach((t, i) => {
        historyHtml += `<div>Lap ${i+1}: <b>${t.toFixed(2)}s</b></div>`;
    });
    document.getElementById('lapHistory').innerHTML = historyHtml;
    
    document.getElementById('summaryModal').style.display = 'block';
}

function animate() {
    requestAnimationFrame(animate);
    updatePhysics();
    renderer.render(scene, camera);
}
animate();

</script>
</body>
</html>
"""

components.html(game_3d_html, height=640)
