import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="EA SPORTS F1® 25 - 2026 Season Simulator",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ EA SPORTS F1® 25: 2026 SEASON PACK SIMULATOR")
st.markdown("""
**[EA F1® 25 조작 및 시스템 가이드]**
- ⚡ **[Space] 액티브 에어로 (Active Aero):** `X-MODE` (직선 초고속 모드) ↔ `Z-MODE` (코너링 고다운포스 모드) 가변 플랩 조절.
- 🚀 **[Shift / E] ERS 오버테이크 부스트:** 배터리 에너지를 소비하여 폭발적인 출력을 얻습니다.
- 🛑 **[L] 피트 리미터 (Pit Limiter):** 피트 레이인 80 km/h 속도 제한 작동.
- 🛞 **피트스탑:** 피트 차선(오른쪽 구역)에 정지 후 타이어 선택 시 **피트 신호등(Red→Green)**과 함께 3D 크루가 바퀴를 교체합니다.
""")

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
            font-family: 'Segoe UI', Roboto, sans-serif;
            user-select: none;
        }
        #canvas-container {
            width: 100vw;
            height: 650px;
            position: relative;
        }
        
        /* EA F1 25 Style Broadcast Top Telemetry HUD */
        .hud-top {
            position: absolute;
            top: 15px;
            left: 20px;
            display: flex;
            gap: 15px;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(12px);
            padding: 10px 20px;
            border-radius: 10px;
            border-left: 4px solid #ef4444;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            z-index: 10;
        }
        .hud-item {
            font-size: 13px;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
        }
        .hud-value {
            color: #ffffff;
            font-size: 16px;
            font-weight: 800;
            margin-left: 4px;
        }

        /* EA F1 25 Steering Wheel & RPM Tachometer Bottom HUD */
        .hud-bottom {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 460px;
            background: rgba(10, 15, 26, 0.92);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 12px 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.9);
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* RPM LEDs Bar */
        .rpm-bar {
            display: flex;
            gap: 5px;
            margin-bottom: 8px;
            width: 100%;
            justify-content: center;
        }
        .rpm-led {
            width: 22px;
            height: 10px;
            border-radius: 3px;
            background: #1e293b;
            border: 1px solid #0f172a;
        }
        .led-green.active { background: #22c55e !important; box-shadow: 0 0 10px #22c55e; }
        .led-red.active { background: #ef4444 !important; box-shadow: 0 0 10px #ef4444; }
        .led-blue.active { background: #3b82f6 !important; box-shadow: 0 0 12px #3b82f6; }

        .telemetry-main {
            display: flex;
            width: 100%;
            justify-content: space-between;
            align-items: center;
        }
        .gear-display {
            font-size: 38px;
            font-weight: 900;
            color: #ffcc00;
            width: 60px;
            text-align: center;
            background: #0f172a;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .speed-display {
            text-align: center;
        }
        .speed-num {
            font-size: 32px;
            font-weight: 900;
            color: #ffffff;
            line-height: 1;
        }
        .speed-unit {
            font-size: 11px;
            color: #64748b;
            font-weight: 700;
        }

        /* Active Aero Mode Badge */
        .aero-badge {
            padding: 5px 12px;
            border-radius: 6px;
            font-weight: 900;
            font-size: 13px;
            letter-spacing: 1px;
        }
        .mode-z { background: #0284c7; color: white; box-shadow: 0 0 12px rgba(2, 132, 199, 0.6); }
        .mode-x { background: #e11d48; color: white; box-shadow: 0 0 12px rgba(225, 29, 72, 0.8); animation: pulse 0.8s infinite alternate; }

        /* Bars (Throttle / Brake / ERS) */
        .gauge-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
            width: 100px;
        }
        .gauge-bar-bg {
            width: 100%;
            height: 6px;
            background: #1e293b;
            border-radius: 3px;
            overflow: hidden;
        }
        .gauge-fill { height: 100%; width: 0%; transition: width 0.05s; }
        .fill-throttle { background: #22c55e; }
        .fill-brake { background: #ef4444; }
        .fill-ers { background: #3b82f6; }

        /* Pit Release Light Banner */
        #pitLightBanner {
            display: none;
            position: absolute;
            top: 75px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid #ea580c;
            padding: 10px 25px;
            border-radius: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 0 30px rgba(234, 88, 12, 0.6);
            z-index: 20;
        }
        .pit-light-dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #333;
        }
        .pit-light-red { background: #ff0000; box-shadow: 0 0 15px #ff0000; }
        .pit-light-green { background: #00ff00; box-shadow: 0 0 20px #00ff00; }

        /* F1 Start Lights Overlay */
        #startLightOverlay {
            display: none;
            position: absolute;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 10, 10, 0.95);
            border: 3px solid #333;
            padding: 12px 25px;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 0 30px rgba(0,0,0,0.9);
            z-index: 30;
        }
        .light-box { display: flex; gap: 12px; margin-top: 5px; }
        .light-bulb { width: 26px; height: 26px; border-radius: 50%; background-color: #333; border: 2px solid #111; }
        .light-red { background-color: #ff0000 !important; box-shadow: 0 0 18px #ff0000, inset 0 0 5px #fff !important; }
        .light-green { background-color: #00ff00 !important; box-shadow: 0 0 25px #00ff00, inset 0 0 5px #fff !important; }

        /* Setup Modal */
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
        .setting-group { margin: 15px 0; text-align: left; }
        .setting-group label { display: block; font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #cbd5e1; }
        select { width: 100%; padding: 8px 12px; background: #1e293b; color: white; border: 1px solid #475569; border-radius: 8px; font-size: 14px; font-weight: bold; }
        .btn-start { background: #ffcc00; color: #000; border: none; padding: 12px 30px; font-size: 17px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; transition: transform 0.2s; }
        .btn-start:hover { transform: scale(1.03); background: #ffd633; }

        /* Pit Stop Interactive Modal */
        #pitModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.96);
            border: 3px solid #ea580c;
            padding: 22px 30px;
            border-radius: 16px;
            text-align: center;
            z-index: 60;
            color: white;
            min-width: 340px;
            box-shadow: 0 0 40px rgba(234, 88, 12, 0.7);
        }
        #pitModal h3 { margin: 0 0 10px 0; color: #ea580c; }
        .btn-compound { padding: 10px 18px; margin: 5px; border: none; border-radius: 8px; font-weight: bold; font-size: 14px; cursor: pointer; transition: transform 0.15s; }
        .btn-compound:hover { transform: scale(1.08); }

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
        .stat-box { background: #1e293b; margin: 10px 0; padding: 10px 15px; border-radius: 8px; text-align: left; border: 1px solid #334155; }
        .btn-restart { background: #ffcc00; color: #000; border: none; padding: 10px 25px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; }
    </style>
    <!-- Three.js 3D Engine -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container">
        <!-- Top Broadcast Telemetry HUD -->
        <div class="hud-top">
            <div class="hud-item">POS <span id="posVal" class="hud-value" style="color:#38bdf8;">P2 / 4</span></div>
            <div class="hud-item">LAP <span id="lapVal" class="hud-value">1 / 5</span></div>
            <div class="hud-item">DELTA <span id="deltaVal" class="hud-value" style="color:#22c55e;">-0.142s</span></div>
            <div class="hud-item">TYRE <span id="tireBadge" class="hud-value" style="color:#eab308;">MEDIUM</span> <span id="wearVal" class="hud-value">100%</span></div>
        </div>

        <!-- Pit Release Traffic Light Banner -->
        <div id="pitLightBanner">
            <div class="pit-light-dot" id="pitRedLight"></div>
            <span id="pitStatusText" style="font-weight:bold; font-size:14px;">PIT CREW AT WORK...</span>
            <div class="pit-light-dot" id="pitGreenLight"></div>
        </div>

        <!-- Steering Wheel / Tachometer Bottom HUD -->
        <div class="hud-bottom">
            <!-- 10 LED RPM Gauge -->
            <div class="rpm-bar">
                <div class="rpm-led led-green" id="led0"></div>
                <div class="rpm-led led-green" id="led1"></div>
                <div class="rpm-led led-green" id="led2"></div>
                <div class="rpm-led led-green" id="led3"></div>
                <div class="rpm-led led-red" id="led4"></div>
                <div class="rpm-led led-red" id="led5"></div>
                <div class="rpm-led led-red" id="led6"></div>
                <div class="rpm-led led-red" id="led7"></div>
                <div class="rpm-led led-blue" id="led8"></div>
                <div class="rpm-led led-blue" id="led9"></div>
            </div>

            <div class="telemetry-main">
                <!-- Gear Number -->
                <div class="gear-display" id="gearVal">N</div>

                <!-- Speedometer -->
                <div class="speed-display">
                    <div class="speed-num" id="speedVal">0</div>
                    <div class="speed-unit">KM/H</div>
                </div>

                <!-- 2026 Active Aero Mode -->
                <div id="aeroBadge" class="aero-badge mode-z">Z-MODE</div>

                <!-- Throttle, Brake & ERS Bars -->
                <div class="gauge-group">
                    <div style="font-size:9px; color:#aaa; font-weight:bold;">THR / BRK / ERS</div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-throttle" id="thrBar"></div></div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-brake" id="brkBar"></div></div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-ers" id="ersBar"></div></div>
                </div>
            </div>
        </div>

        <!-- F1 Lights Out Display Panel -->
        <div id="startLightOverlay">
            <span style="font-size:12px; font-weight:bold; color:#aaa; letter-spacing:1px;">EA SPORTS F1® LIGHTS OUT</span>
            <div class="light-box">
                <div class="light-bulb" id="light1"></div>
                <div class="light-bulb" id="light2"></div>
                <div class="light-bulb" id="light3"></div>
                <div class="light-bulb" id="light4"></div>
                <div class="light-bulb" id="light5"></div>
            </div>
            <span id="lightText" style="font-size:13px; font-weight:bold; color:#ffcc00; margin-top:4px;">FORMATION LAP COMPLETE</span>
        </div>

        <!-- Setup Game Modal -->
        <div id="startModal">
            <h2>🏎️ F1® 25 챔피언십 설정</h2>
            <div class="setting-group">
                <label>🚩 레이스 랩 수 선택</label>
                <select id="selectLaps">
                    <option value="3">3 Laps (스프린트 레이스)</option>
                    <option value="5" selected>5 Laps (표준 레이스)</option>
                    <option value="8">8 Laps (전략 레이스)</option>
                </select>
            </div>
            <div class="setting-group">
                <label>🛞 스타트 타이어 선택</label>
                <select id="selectTire">
                    <option value="SOFT">🔴 Soft (최고 속도, 빠른 마모)</option>
                    <option value="MEDIUM" selected>🟡 Medium (표준 밸런스)</option>
                    <option value="HARD">⚪ Hard (강한 내구성)</option>
                </select>
            </div>
            <button class="btn-start" onclick="initGame()">2026 SEASON START</button>
        </div>

        <!-- Pit Stop Interactive Modal -->
        <div id="pitModal">
            <h3>⛽ F1 PIT STOP! 타이어 선택</h3>
            <p style="font-size:13px; margin-bottom:12px;">교체할 컴파운드를 선택하세요:</p>
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
// --- Three.js Engine Setup ---
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x4a7c9d);
scene.fog = new THREE.FogExp2(0x4a7c9d, 0.0008);

const camera = new THREE.PerspectiveCamera(55, container.clientWidth / 650, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, 650);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(250, 400, 150);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
scene.add(dirLight);

// Ground Grass Plane
const grassGeo = new THREE.PlaneGeometry(3500, 3500);
const grassMat = new THREE.MeshLambertMaterial({ color: 0x1c421e });
const grass = new THREE.Mesh(grassGeo, grassMat);
grass.rotation.x = -Math.PI / 2;
grass.position.y = -0.05;
grass.receiveShadow = true;
scene.add(grass);

// --- 2026 Circuit Geometry (Main Straight along X-Axis) ---
const trackPoints = [
    new THREE.Vector3(-250, 0, 220),
    new THREE.Vector3(250, 0, 220),
    new THREE.Vector3(380, 0, 120),
    new THREE.Vector3(320, 0, -40),
    new THREE.Vector3(390, 0, -200),
    new THREE.Vector3(140, 0, -280),
    new THREE.Vector3(-140, 0, -280),
    new THREE.Vector3(-360, 0, -180),
    new THREE.Vector3(-260, 0, 0),
    new THREE.Vector3(-380, 0, 140)
];

const trackCurve = new THREE.CatmullRomCurve3(trackPoints, true, 'catmullrom', 0.25);
const SEGMENTS = 450;
const ROAD_WIDTH = 34;

function build3DTrack() {
    const points = trackCurve.getSpacedPoints(SEGMENTS);
    const roadVertices = [], roadIndices = [];
    const kerbVertices = [], kerbColors = [], kerbIndices = [];
    const rubberVertices = [], rubberIndices = [];

    for (let i = 0; i <= SEGMENTS; i++) {
        const p1 = points[i % SEGMENTS];
        const p2 = points[(i + 1) % SEGMENTS];

        const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();

        const lRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2));
        const rRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2));

        roadVertices.push(lRoad.x, 0.01, lRoad.z);
        roadVertices.push(rRoad.x, 0.01, rRoad.z);

        // Dark Rubber Racing Line Mesh
        const lRub = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(4));
        const rRub = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-4));
        rubberVertices.push(lRub.x, 0.015, lRub.z);
        rubberVertices.push(rRub.x, 0.015, rRub.z);

        if (i < SEGMENTS) {
            const r1 = i * 2, r2 = (i + 1) * 2;
            roadIndices.push(r1, r1 + 1, r2);
            roadIndices.push(r1 + 1, r2 + 1, r2);
            rubberIndices.push(r1, r1 + 1, r2);
            rubberIndices.push(r1 + 1, r2 + 1, r2);
        }

        // FIA Red/White Kerb Borders
        const lKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2 + 3.2));
        const rKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2 - 3.2));
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

    const roadMesh = new THREE.Mesh(roadGeo, new THREE.MeshStandardMaterial({ color: 0x222228, roughness: 0.85 }));
    roadMesh.receiveShadow = true;
    scene.add(roadMesh);

    // Rubber Racing Line
    const rubGeo = new THREE.BufferGeometry();
    rubGeo.setAttribute('position', new THREE.Float32BufferAttribute(rubberVertices, 3));
    rubGeo.setIndex(rubberIndices);
    const rubMesh = new THREE.Mesh(rubGeo, new THREE.MeshBasicMaterial({ color: 0x111115, opacity: 0.5, transparent: true }));
    scene.add(rubMesh);

    const kerbGeo = new THREE.BufferGeometry();
    kerbGeo.setAttribute('position', new THREE.Float32BufferAttribute(kerbVertices, 3));
    kerbGeo.setAttribute('color', new THREE.Float32BufferAttribute(kerbColors, 3));
    kerbGeo.setIndex(kerbIndices);
    scene.add(new THREE.Mesh(kerbGeo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide })));
}
build3DTrack();

// --- 150m / 100m / 50m Brake Marker Distance Boards ---
function buildBrakeDistanceMarkers() {
    const pCorner = trackCurve.getPointAt(0.18); // Turn 1 entrance
    const tangent = trackCurve.getTangentAt(0.18);
    const norm = new THREE.Vector3(-tangent.z, 0, tangent.x).normalize();

    [150, 100, 50].forEach((dist, i) => {
        const boardPos = pCorner.clone().sub(tangent.clone().multiplyScalar(dist)).add(norm.clone().multiplyScalar(ROAD_WIDTH / 2 + 4));
        const boardGroup = new THREE.Group();
        boardGroup.position.copy(boardPos);

        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 3.0), new THREE.MeshStandardMaterial({ color: 0x333333 }));
        post.position.y = 1.5;
        boardGroup.add(post);

        const sign = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.4, 0.15), new THREE.MeshStandardMaterial({ color: 0xffffff }));
        sign.position.y = 2.4;
        boardGroup.add(sign);

        scene.add(boardGroup);
    });
}
buildBrakeDistanceMarkers();

// --- EA Grandstand & Pit Lane ---
function buildGrandstand() {
    const standGroup = new THREE.Group();
    standGroup.position.set(0, 0, 160);

    const tierGeo = new THREE.BoxGeometry(260, 12, 26);
    const tierMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
    const tier = new THREE.Mesh(tierGeo, tierMat);
    tier.position.set(0, 6, 0);
    standGroup.add(tier);

    const roofGeo = new THREE.BoxGeometry(270, 1.5, 38);
    const roofMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.6 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.set(0, 18, 4);
    roof.rotation.x = 0.08;
    standGroup.add(roof);

    scene.add(standGroup);
}
buildGrandstand();

// Pit Lane (z=245~265)
const pitGroup = new THREE.Group();

const pitWall = new THREE.Mesh(new THREE.BoxGeometry(160, 2.4, 1.6), new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.4 }));
pitWall.position.set(20, 1.2, 238);
pitGroup.add(pitWall);

const pitAsphalt = new THREE.Mesh(new THREE.PlaneGeometry(160, 24), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 }));
pitAsphalt.rotation.x = -Math.PI / 2;
pitAsphalt.position.set(20, 0.02, 252);
pitGroup.add(pitAsphalt);

const garageColors = [0xef4444, 0x1e3a8a, 0x06b6d4, 0xf97316];
for (let i = 0; i < 4; i++) {
    const gBuilding = new THREE.Mesh(new THREE.BoxGeometry(28, 7.0, 14), new THREE.MeshStandardMaterial({ color: garageColors[i], metalness: 0.3 }));
    gBuilding.position.set(-30 + i * 32, 3.5, 268);
    pitGroup.add(gBuilding);
}

const pitBoxMesh = new THREE.Mesh(new THREE.PlaneGeometry(22, 12), new THREE.MeshBasicMaterial({ color: 0xea580c, side: THREE.DoubleSide }));
pitBoxMesh.rotation.x = -Math.PI / 2;
pitBoxMesh.position.set(40, 0.04, 252);
pitGroup.add(pitBoxMesh);

scene.add(pitGroup);

// --- Horizontal Finish Line ---
const finishLineMesh = new THREE.Mesh(new THREE.PlaneGeometry(4, ROAD_WIDTH), new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }));
finishLineMesh.rotation.x = -Math.PI / 2;
finishLineMesh.position.set(0, 0.03, 220);
scene.add(finishLineMesh);

// --- 3D Pit Crew Members ---
function createPitCrewMember() {
    const crewGroup = new THREE.Group();
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.3, 8), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
    torso.position.y = 0.95;
    crewGroup.add(torso);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.28, 12, 12), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    head.position.y = 1.75;
    crewGroup.add(head);
    const spareTireMat = new THREE.MeshStandardMaterial({ color: 0xeab308, roughness: 0.8 });
    const spareTire = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.45, 16), spareTireMat);
    spareTire.geometry.rotateZ(Math.PI / 2);
    spareTire.position.set(0, 1.0, 0.4);
    crewGroup.add(spareTire);
    return { crewGroup, spareTireMat };
}

const pitCrewData = [createPitCrewMember(), createPitCrewMember(), createPitCrewMember(), createPitCrewMember()];
const pitCrewMembers = pitCrewData.map(d => d.crewGroup);
const pitCrewTireMats = pitCrewData.map(d => d.spareTireMat);

const pitCrewIdleOffsets = [{ x: 34, z: 264 }, { x: 46, z: 264 }, { x: 34, z: 266 }, { x: 46, z: 266 }];
pitCrewMembers.forEach((member, i) => {
    member.position.set(pitCrewIdleOffsets[i].x, 0, pitCrewIdleOffsets[i].z);
    scene.add(member);
});

// --- High-Detail 2026 F1 Machine with Active Aero Flaps ---
function create3DCar(colorHex, rWingColorHex) {
    const carGroup = new THREE.Group();

    // Body Nose
    const body = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.6, 5.4), new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.2, metalness: 0.6 }));
    body.position.y = 0.55;
    body.castShadow = true;
    carGroup.add(body);

    // Halo Structure
    const haloRing = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.08, 8, 16, Math.PI), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    haloRing.rotation.x = Math.PI / 2;
    haloRing.position.set(0, 0.95, 0.3);
    carGroup.add(haloRing);

    // Cockpit
    const cockpit = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 16), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    cockpit.position.set(0, 0.85, -0.2);
    carGroup.add(cockpit);

    // Front Wing
    const fWingMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
    const fWing = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.1, 1.0), fWingMat);
    fWing.position.set(0, 0.3, 2.7);
    carGroup.add(fWing);

    // Rear Wing Group with Animated Active Aero Flap!
    const rearWingGroup = new THREE.Group();
    rearWingGroup.position.set(0, 1.15, -2.5);

    const rWingMain = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.12, 1.0), new THREE.MeshStandardMaterial({ color: rWingColorHex }));
    rearWingGroup.add(rWingMain);

    // Active Aero DRM Flap (Rotates on Active Aero X-MODE!)
    const activeFlap = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.06, 0.45), new THREE.MeshStandardMaterial({ color: 0xffffff }));
    activeFlap.position.set(0, 0.15, 0.1);
    rearWingGroup.add(activeFlap);

    carGroup.add(rearWingGroup);

    // Straight Rolling Wheels (Baked rotateZ)
    const wheelGeo = new THREE.CylinderGeometry(0.6, 0.6, 0.5, 24);
    wheelGeo.rotateZ(Math.PI / 2);

    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0d0d0d, roughness: 0.9 });
    const wheels = [];
    const wheelPositions = [[-1.4, 0.6, 1.9], [1.4, 0.6, 1.9], [-1.4, 0.6, -1.9], [1.4, 0.6, -1.9]];

    wheelPositions.forEach((pos) => {
        const wheelPivot = new THREE.Group();
        wheelPivot.position.set(...pos);
        const wheelMesh = new THREE.Mesh(wheelGeo, wheelMat);
        wheelMesh.castShadow = true;
        wheelPivot.add(wheelMesh);
        carGroup.add(wheelPivot);
        wheels.push(wheelMesh);
    });

    return { group: carGroup, activeFlap, wheels, wheelMat };
}

// Player 3D F1 Car Model
const playerObj = create3DCar(0xef4444, 0xffcc00);
scene.add(playerObj.group);

// 3 AI Rival Cars
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

function alignGridPositions() {
    playerObj.group.position.set(-5, 0, 214);
    playerObj.group.rotation.y = Math.PI / 2;
    aiCars.forEach(ai => {
        ai.obj.group.position.set(ai.gridX, 0, ai.gridZ);
        ai.obj.group.rotation.y = Math.PI / 2;
        ai.progress = (ai.gridX + 300) / 1000;
    });
}
alignGridPositions();

// Mechanics & Active Aero Variables
let activeAeroXMode = false; // False = Z-MODE, True = X-MODE
let ersBattery = 100.0;
let isErsBoosting = false;

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
let carAngle = Math.PI / 2;
let steerSmooth = 0;
let inPit = false;
let isPitChanging = false;
let pitCooldown = false;
let pitLimiter = false;

// Race Flow State
let startState = 'WAITING';
let maxLaps = 5;
let playerLap = 0;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD","KeyE","ShiftLeft","KeyL"].includes(e.code)) {
        e.preventDefault();
    }
    // [Space] Active Aero Toggle (X-MODE ↔ Z-MODE)
    if (e.code === 'Space' && !e.repeat && startState === 'GO' && !isFinished && !inPit) {
        activeAeroXMode = !activeAeroXMode;
        const badge = document.getElementById('aeroBadge');
        if (activeAeroXMode) {
            badge.innerText = 'X-MODE';
            badge.className = 'aero-badge mode-x';
            playerObj.activeFlap.rotation.x = -0.45; // Open wing flap
        } else {
            badge.innerText = 'Z-MODE';
            badge.className = 'aero-badge mode-z';
            playerObj.activeFlap.rotation.x = 0; // Close wing flap
        }
    }
    // [L] Pit Limiter
    if (e.code === 'KeyL' && !e.repeat) {
        pitLimiter = !pitLimiter;
    }
    keys[e.code] = true;
});
window.addEventListener('keyup', e => keys[e.code] = false);

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
            const randomDelay = 800 + Math.random() * 1200;
            setTimeout(() => {
                for (let i = 1; i <= 5; i++) {
                    const el = document.getElementById(`light${i}`).classList.remove('light-red');
                    document.getElementById(`light${i}`).classList.add('light-green');
                }
                document.getElementById('lightText').innerText = 'LIGHTS OUT & AWAY WE GO!';
                startState = 'GO';
                lapStartTime = Date.now();
                setTimeout(() => { document.getElementById('startLightOverlay').style.display = 'none'; }, 2500);
            }, randomDelay);
        }
    }, 1000);
}

function updateTireUI() {
    const spec = TIRE_SPECS[currentTire];
    document.getElementById('tireBadge').innerText = currentTire;
    playerObj.wheelMat.color.setHex(spec.wheelColor);
    pitCrewTireMats.forEach(m => m.color.setHex(spec.wheelColor));
}

function updatePhysics() {
    if (startState !== 'GO' || isFinished) return;

    if (inPit) {
        speed *= 0.8;
        return;
    }

    const spec = TIRE_SPECS[currentTire];
    const wearPenalty = tireWear < 30 ? (tireWear / 30) : 1.0;

    // Active Aero Mechanics: X-MODE (Speed boost, less grip) vs Z-MODE (High grip)
    const aeroSpeedBoost = activeAeroXMode ? 1.14 : 0.96;
    const aeroGripMult = activeAeroXMode ? 0.75 : 1.25;

    // ERS Overtake Boost
    isErsBoosting = (keys['ShiftLeft'] || keys['KeyE']) && ersBattery > 0;
    const ersMult = isErsBoosting ? 1.20 : 1.0;
    if (isErsBoosting) {
        ersBattery -= 0.35;
        if (ersBattery < 0) ersBattery = 0;
    } else if (ersBattery < 100) {
        ersBattery += 0.08; // Recharge on braking/coasting
    }

    let maxSpeed = 0.98 * spec.speedMult * aeroSpeedBoost * ersMult * wearPenalty;
    if (pitLimiter) maxSpeed = 0.30; // 80 km/h limiter

    const gripFactor = 0.014 * spec.gripMult * aeroGripMult * wearPenalty;

    const isAccel = (keys['ArrowUp'] || keys['KeyW']);
    const isBrake = (keys['ArrowDown'] || keys['KeyS']);

    if (isAccel) speed += 0.008 * ersMult;
    else if (isBrake) speed -= 0.014;
    else speed *= 0.985;

    if (speed > maxSpeed) speed = maxSpeed;
    if (speed < -maxSpeed * 0.3) speed = -maxSpeed * 0.3;

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

    const carPos = playerObj.group.position;
    const currentProgress = getTrackProgress(carPos);
    const closestPoint = trackCurve.getPointAt(currentProgress % 1);
    
    if (carPos.distanceTo(closestPoint) > ROAD_WIDTH / 2 + 1 && carPos.z < 238) {
        speed *= 0.88;
    }

    if (pitCooldown && (carPos.x > 80 || carPos.z < 235)) {
        pitCooldown = false;
    }

    carPos.x += Math.sin(carAngle) * speed;
    carPos.z += Math.cos(carAngle) * speed;
    playerObj.group.rotation.y = carAngle;

    // Straight Wheel Rolling
    playerObj.wheels.forEach(w => w.rotation.x += speed * 0.5);

    // Dynamic Camera View
    if (inPit || isPitChanging) {
        const pitCamPos = new THREE.Vector3(carPos.x - 4, 3.5, carPos.z + 10);
        camera.position.lerp(pitCamPos, 0.15);
        camera.lookAt(carPos.x, 1.2, carPos.z);
    } else {
        const camOffset = new THREE.Vector3(0, 5.5, -14).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
        camera.position.lerp(carPos.clone().add(camOffset), 0.2);
        camera.lookAt(carPos.clone().add(new THREE.Vector3(0, 1.2, 0)));
    }

    // STRICT PIT STOP TRIGGER
    if (carPos.z > 244 && carPos.z < 260 && carPos.x > 25 && carPos.x < 55 && !inPit && !isPitChanging && !pitCooldown) {
        inPit = true;
        speed = 0;
        carPos.set(40, 0, 252);
        carAngle = Math.PI / 2;
        playerObj.group.rotation.y = carAngle;
        document.getElementById('pitModal').style.display = 'block';
    }

    if (carPos.z < -180) checkpointPassed = true;

    if (checkpointPassed && Math.abs(carPos.x) < 25 && carPos.z > 215 && carPos.z < 235) {
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

    // AI Cars Motion
    aiCars.forEach(ai => {
        ai.progress = (ai.progress + ai.speed * 0.0004) % 1;
        const pt = trackCurve.getPointAt(ai.progress);
        const nextPt = trackCurve.getPointAt((ai.progress + 0.005) % 1);
        const dir = new THREE.Vector3().subVectors(nextPt, pt).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();
        
        const aiPos = pt.clone().add(norm.multiplyScalar(ai.offset));
        ai.obj.group.position.copy(aiPos);
        ai.obj.group.rotation.y = Math.atan2(dir.x, dir.z);
        ai.obj.wheels.forEach(w => w.rotation.x += ai.speed * 0.4);
    });

    calculateStandings(currentProgress);
    updateHUDTelemetry(isAccel, isBrake);
}

// EA F1 25 Tachometer & RPM Telemetry Renderer
function updateHUDTelemetry(isAccel, isBrake) {
    const speedKmh = Math.round(Math.abs(speed) * 310);
    document.getElementById('speedVal').innerText = speedKmh;

    // Gear Calculation (1~8 Gears)
    let gear = 'N';
    if (speedKmh === 0) gear = 'N';
    else if (speedKmh < 45) gear = '1';
    else if (speedKmh < 85) gear = '2';
    else if (speedKmh < 130) gear = '3';
    else if (speedKmh < 175) gear = '4';
    else if (speedKmh < 220) gear = '5';
    else if (speedKmh < 260) gear = '6';
    else if (speedKmh < 295) gear = '7';
    else gear = '8';
    document.getElementById('gearVal').innerText = gear;

    // RPM LEDs Lighting Logic
    const rpmPercent = (speedKmh % 45) / 45;
    const activeLeds = Math.floor(rpmPercent * 10);
    for (let i = 0; i < 10; i++) {
        const led = document.getElementById(`led${i}`);
        if (i < activeLeds) led.classList.add('active');
        else led.classList.remove('active');
    }

    // Throttle / Brake / ERS Bars
    document.getElementById('thrBar').style.width = isAccel ? '100%' : '0%';
    document.getElementById('brkBar').style.width = isBrake ? '100%' : '0%';
    document.getElementById('ersBar').style.width = `${ersBattery}%`;

    document.getElementById('wearVal').innerText = `${Math.round(tireWear)}%`;
}

// 3D Pit Crew Action with Release Traffic Light
function changeTire(newCompound) {
    if (isPitChanging) return;
    isPitChanging = true;

    currentTire = newCompound;
    tireWear = 100.0;
    updateTireUI();

    document.getElementById('pitModal').style.display = 'none';
    const pitBanner = document.getElementById('pitLightBanner');
    const pitRed = document.getElementById('pitRedLight');
    const pitGreen = document.getElementById('pitGreenLight');
    const pitText = document.getElementById('pitStatusText');

    pitBanner.style.display = 'flex';
    pitRed.className = 'pit-light-dot pit-light-red';
    pitGreen.className = 'pit-light-dot';
    pitText.innerText = 'PIT CREW CHANGING TIRES...';

    const carPos = playerObj.group.position;
    const wheelTargets = [
        { x: carPos.x - 2.0, z: carPos.z + 2.0 },
        { x: carPos.x + 2.0, z: carPos.z + 2.0 },
        { x: carPos.x - 2.0, z: carPos.z - 2.0 },
        { x: carPos.x + 2.0, z: carPos.z - 2.0 }
    ];

    let crewStep = 0;
    const animateCrewIn = setInterval(() => {
        crewStep += 0.1;
        pitCrewMembers.forEach((member, i) => {
            member.position.x += (wheelTargets[i].x - member.position.x) * 0.25;
            member.position.z += (wheelTargets[i].z - member.position.z) * 0.25;
            member.rotation.y += 0.3;
        });

        if (crewStep >= 1.0) {
            clearInterval(animateCrewIn);
            setTimeout(() => {
                const animateCrewOut = setInterval(() => {
                    pitCrewMembers.forEach((member, i) => {
                        member.position.x += (pitCrewIdleOffsets[i].x - member.position.x) * 0.25;
                        member.position.z += (pitCrewIdleOffsets[i].z - member.position.z) * 0.25;
                    });
                }, 40);

                setTimeout(() => {
                    clearInterval(animateCrewOut);
                    pitCrewMembers.forEach((member, i) => {
                        member.position.set(pitCrewIdleOffsets[i].x, 0, pitCrewIdleOffsets[i].z);
                    });

                    // Pit Light GREEN: Release Car!
                    pitRed.className = 'pit-light-dot';
                    pitGreen.className = 'pit-light-dot pit-light-green';
                    pitText.innerText = 'GO GO GO!';

                    setTimeout(() => {
                        pitBanner.style.display = 'none';
                        speed = 0.55;
                        carPos.x += 12;
                        inPit = false;
                        isPitChanging = false;
                        pitCooldown = true;
                    }, 600);
                }, 700);
            }, 1800);
        }
    }, 40);
}

function calculateStandings(playerProgress) {
    const standings = [
        { name: "Player", score: playerLap + playerProgress, isPlayer: true },
        ...aiCars.map(ai => ({ name: ai.name, score: ai.lap + ai.progress, isPlayer: false }))
    ];
    standings.sort((a, b) => b.score - a.score);

    const rank = standings.findIndex(s => s.isPlayer) + 1;
    const suffix = rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th';
    document.getElementById('posVal').innerText = `P${rank} / 4`;
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

function showSummaryModal() {
    const best = Math.min(...lapTimes).toFixed(2);
    const worst = Math.max(...lapTimes).toFixed(2);
    document.getElementById('finalPos').innerText = document.getElementById('posVal').innerText;
    document.getElementById('bestLap').innerText = `${best} 초`;
    document.getElementById('worstLap').innerText = `${worst} 초`;
    
    let historyHtml = "";
    lapTimes.forEach((t, i) => { historyHtml += `<div>Lap ${i+1}: <b>${t.toFixed(2)}s</b></div>`; });
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

components.html(game_3d_html, height=660)
