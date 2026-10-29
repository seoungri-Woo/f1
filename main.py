import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F1 3D Real Track Racing & Aerodynamics",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ REAL F1 서킷 레이싱 & 에어로다이나믹스 시뮬레이터")
st.markdown("""
**[조작법]**
- **방향키 (↑ / ↓ / ← / →) 또는 WASD:** 가속 / 브레이크 / **부드러운 핸들 조향**
- **스페이스바 (Space):** 리어 윙 4단계 전환 (**0° ➔ 15° ➔ 30° ➔ 40°**)
- **F1 트랙 체감 포인트:**
  - 🏎️ **넓은 아스팔트 도로 & 코너 연석:** 코너 진입 시 연석을 활용해 최단 라인(In-Course)을 타고 탈출하세요.
  - 🚀 **0° (직선 세팅):** 메인 직선에서 **최대 260 km/h** 극대화!
  - 📐 **40° (코너 세팅):** 최고 속도는 제한되지만, 급코너에서도 미끄러지지 않는 다운포스 확보.
""")

# HTML5 + Three.js Real Circuit Engine
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
            background-color: #050505;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
        }
        #canvas-container {
            width: 100vw;
            height: 620px;
            position: relative;
        }
        
        /* Glassmorphism HUD Overlay */
        .hud-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            display: flex;
            gap: 15px;
            background: rgba(15, 15, 15, 0.85);
            backdrop-filter: blur(10px);
            padding: 12px 22px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
            z-index: 5;
        }
        .hud-item {
            font-size: 15px;
            font-weight: 600;
        }
        .hud-value {
            color: #ffcc00;
            font-weight: bold;
            font-size: 18px;
        }

        .wing-badge {
            background: #e63946;
            color: white;
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: bold;
        }

        /* Race Summary Modal */
        #summaryModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(12, 12, 12, 0.95);
            border: 2px solid #ffcc00;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            width: 360px;
            box-shadow: 0 0 50px rgba(255, 204, 0, 0.5);
            z-index: 100;
            color: white;
        }
        #summaryModal h2 { color: #ffcc00; margin-top: 0; font-size: 24px; }
        .stat-box {
            background: #222;
            margin: 10px 0;
            padding: 12px;
            border-radius: 8px;
            text-align: left;
            border: 1px solid #333;
        }
        .btn-restart {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 12px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            transition: all 0.2s;
        }
        .btn-restart:hover {
            background: #ffd633;
            transform: scale(1.05);
        }
    </style>
    <!-- Three.js Engine -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container">
        <!-- HUD Overlay -->
        <div class="hud-panel">
            <div class="hud-item">🔧 리어 윙 [Space]: <span id="wingBadge" class="wing-badge">15°</span></div>
            <div class="hud-item">⚡ 속도: <span id="speedVal" class="hud-value">0</span> km/h</div>
            <div class="hud-item">🚩 Laps: <span id="lapVal" class="hud-value">1 / 3</span></div>
            <div class="hud-item">⏱️ 타임: <span id="timeVal" class="hud-value">0.00s</span></div>
        </div>

        <!-- Finish Modal -->
        <div id="summaryModal">
            <h2>🏁 레이스 종료!</h2>
            <div class="stat-box">🏆 <b>최단 랩타임 (Best):</b> <span id="bestLap" style="color:#4caf50;">-</span></div>
            <div class="stat-box">🐢 <b>최장 랩타임 (Worst):</b> <span id="worstLap" style="color:#f44336;">-</span></div>
            <div class="stat-box">📊 <b>랩별 기록:</b><div id="lapHistory" style="font-size:14px; margin-top:6px; color:#ccc;"></div></div>
            <button class="btn-restart" onclick="resetGame()">다시 도전하기</button>
        </div>
    </div>

<script>
// --- Three.js Setup ---
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x6ca6cd);
scene.fog = new THREE.FogExp2(0x6ca6cd, 0.0018);

const camera = new THREE.PerspectiveCamera(55, container.clientWidth / 620, 0.1, 1500);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, 620);
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

// Ground (Grass)
const grassGeo = new THREE.PlaneGeometry(2500, 2500);
const grassMat = new THREE.MeshLambertMaterial({ color: 0x225522 });
const grass = new THREE.Mesh(grassGeo, grassMat);
grass.rotation.x = -Math.PI / 2;
grass.position.y = -0.05;
grass.receiveShadow = true;
scene.add(grass);

// --- Real F1 Circuit Geometry Generator ---
const trackPoints = [
    new THREE.Vector3(0, 0, 220),       // Main Straight
    new THREE.Vector3(260, 0, 220),     // Turn 1
    new THREE.Vector3(340, 0, 140),     // Chicane
    new THREE.Vector3(300, 0, 30),      
    new THREE.Vector3(360, 0, -80),     // Hairpin
    new THREE.Vector3(250, 0, -220),    
    new THREE.Vector3(80, 0, -240),     // Back Straight
    new THREE.Vector3(-120, 0, -240),   // High-speed Sweeper
    new THREE.Vector3(-280, 0, -120),   // S-Curve
    new THREE.Vector3(-220, 0, 20),     
    new THREE.Vector3(-300, 0, 120),    // Parabolica
    new THREE.Vector3(-200, 0, 220)     // Final Straight Entry
];

const trackCurve = new THREE.CatmullRomCurve3(trackPoints, true, 'catmullrom', 0.25);
const SEGMENTS = 400;
const ROAD_WIDTH = 28; // 넓은 아스팔트 도로 폭

function buildCircuit() {
    const points = trackCurve.getSpacedPoints(SEGMENTS);
    
    // Road & Kerb Geometry Arrays
    const roadVertices = [];
    const roadUvs = [];
    const roadIndices = [];
    
    const kerbVertices = [];
    const kerbColors = [];
    const kerbIndices = [];

    let kIdx = 0;

    for (let i = 0; i <= SEGMENTS; i++) {
        const p1 = points[i % SEGMENTS];
        const p2 = points[(i + 1) % SEGMENTS];

        // Normal direction vector
        const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();

        // Left / Right Road Edges
        const lRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2));
        const rRoad = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2));

        roadVertices.push(lRoad.x, 0.01, lRoad.z);
        roadVertices.push(rRoad.x, 0.01, rRoad.z);
        roadUvs.push(0, i / SEGMENTS * 20);
        roadUvs.push(1, i / SEGMENTS * 20);

        if (i < SEGMENTS) {
            const row1 = i * 2;
            const row2 = (i + 1) * 2;
            roadIndices.push(row1, row1 + 1, row2);
            roadIndices.push(row1 + 1, row2 + 1, row2);
        }

        // Left & Right Red/White Kerbs (연석)
        const lKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(ROAD_WIDTH / 2 + 2.5));
        const rKerbOuter = new THREE.Vector3().addVectors(p1, norm.clone().multiplyScalar(-ROAD_WIDTH / 2 - 2.5));

        const isRed = (Math.floor(i / 2) % 2 === 0);
        const color = isRed ? [0.9, 0.1, 0.1] : [0.95, 0.95, 0.95];

        // Left Kerb
        kerbVertices.push(lRoad.x, 0.02, lRoad.z, lKerbOuter.x, 0.02, lKerbOuter.z);
        kerbColors.push(...color, ...color);

        // Right Kerb
        kerbVertices.push(rRoad.x, 0.02, rRoad.z, rKerbOuter.x, 0.02, rKerbOuter.z);
        kerbColors.push(...color, ...color);

        if (i < SEGMENTS) {
            const base = i * 4;
            const next = (i + 1) * 4;
            // Left Kerb Triangles
            kerbIndices.push(base, base + 1, next);
            kerbIndices.push(base + 1, next + 1, next);
            // Right Kerb Triangles
            kerbIndices.push(base + 2, base + 3, next + 2);
            kerbIndices.push(base + 3, next + 3, next + 2);
        }
    }

    // Road Mesh
    const roadGeo = new THREE.BufferGeometry();
    roadGeo.setAttribute('position', new THREE.Float32BufferAttribute(roadVertices, 3));
    roadGeo.setAttribute('uv', new THREE.Float32BufferAttribute(roadUvs, 2));
    roadGeo.setIndex(roadIndices);
    roadGeo.computeVertexNormals();

    const roadMat = new THREE.MeshStandardMaterial({ color: 0x222225, roughness: 0.9 });
    const roadMesh = new THREE.Mesh(roadGeo, roadMat);
    roadMesh.receiveShadow = true;
    scene.add(roadMesh);

    // Kerb Mesh
    const kerbGeo = new THREE.BufferGeometry();
    kerbGeo.setAttribute('position', new THREE.Float32BufferAttribute(kerbVertices, 3));
    kerbGeo.setAttribute('color', new THREE.Float32BufferAttribute(kerbColors, 3));
    kerbGeo.setIndex(kerbIndices);
    
    const kerbMat = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide });
    const kerbMesh = new THREE.Mesh(kerbGeo, kerbMat);
    scene.add(kerbMesh);
}

buildCircuit();

// --- Finish Line Gantry (결승선 아치) ---
const gantryGroup = new THREE.Group();
gantryGroup.position.set(0, 0, 220);

const p1 = new THREE.Mesh(new THREE.BoxGeometry(1.5, 12, 1.5), new THREE.MeshStandardMaterial({ color: 0x444444 }));
p1.position.set(-ROAD_WIDTH/2 - 2, 6, 0);
const p2 = p1.clone();
p2.position.set(ROAD_WIDTH/2 + 2, 6, 0);

const topBeam = new THREE.Mesh(new THREE.BoxGeometry(ROAD_WIDTH + 6, 2, 2), new THREE.MeshStandardMaterial({ color: 0xe63946 }));
topBeam.position.set(0, 11, 0);

gantryGroup.add(p1, p2, topBeam);
scene.add(gantryGroup);

// Finish Line Road Stripe
const finishLineGeo = new THREE.PlaneGeometry(ROAD_WIDTH, 6);
const finishLineMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
const finishLineMesh = new THREE.Mesh(finishLineGeo, finishLineMat);
finishLineMesh.rotation.x = -Math.PI / 2;
finishLineMesh.position.set(0, 0.03, 220);
scene.add(finishLineMesh);


// --- Detailed F1 Car Model ---
const carGroup = new THREE.Group();

// Main Body
const bodyGeo = new THREE.BoxGeometry(2.4, 0.75, 5.4);
const bodyMat = new THREE.MeshStandardMaterial({ color: 0xe63946, roughness: 0.2, metalness: 0.6 });
const body = new THREE.Mesh(bodyGeo, bodyMat);
body.position.y = 0.6;
body.castShadow = true;
carGroup.add(body);

// Driver Helmet & Cockpit
const cockpitGeo = new THREE.SphereGeometry(0.6, 16, 16);
const cockpitMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
const cockpit = new THREE.Mesh(cockpitGeo, cockpitMat);
cockpit.position.set(0, 0.9, -0.2);
carGroup.add(cockpit);

// Front Wing
const fWingGeo = new THREE.BoxGeometry(3.8, 0.12, 1.0);
const wingMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
const fWing = new THREE.Mesh(fWingGeo, wingMat);
fWing.position.set(0, 0.35, 2.7);
fWing.castShadow = true;
carGroup.add(fWing);

// Adjustable Rear Wing Group
const rearWingGroup = new THREE.Group();
rearWingGroup.position.set(0, 1.2, -2.5);

const rWingMain = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.2, 1.0), new THREE.MeshStandardMaterial({ color: 0xffcc00 }));
rWingMain.castShadow = true;
rearWingGroup.add(rWingMain);

const rWingPillar1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.65, 0.12), wingMat);
rWingPillar1.position.set(-1.0, -0.3, 0);
rearWingGroup.add(rWingPillar1);
const rWingPillar2 = rWingPillar1.clone();
rWingPillar2.position.set(1.0, -0.3, 0);
rearWingGroup.add(rWingPillar2);

carGroup.add(rearWingGroup);

// Wheels
const wheelGeo = new THREE.CylinderGeometry(0.6, 0.6, 0.5, 16);
const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0d0d0d, roughness: 0.9 });
const wheels = [];
const wheelPositions = [
    [-1.4, 0.6, 1.9], [1.4, 0.6, 1.9],
    [-1.4, 0.6, -1.9], [1.4, 0.6, -1.9]
];

wheelPositions.forEach(pos => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(...pos);
    wheel.castShadow = true;
    carGroup.add(wheel);
    wheels.push(wheel);
});

scene.add(carGroup);
carGroup.position.set(0, 0, 220); // Initial start position


// --- Physics & Aerodynamics Logic ---
const wingPresetAngles = [0, 15, 30, 40];
let wingPresetIndex = 1; // Default 15deg
let wingAngle = 15;

let speed = 0;
let carAngle = -Math.PI / 2; // Facing Direction
let steerSmooth = 0;
let keys = {};

// Race State
let currentLap = 1;
const maxLaps = 3;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

// Event Handlers
window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD"].includes(e.code)) {
        e.preventDefault();
    }
    
    // Spacebar toggles 4 Wing Angles
    if (e.code === 'Space' && !e.repeat) {
        wingPresetIndex = (wingPresetIndex + 1) % wingPresetAngles.length;
        wingAngle = wingPresetAngles[wingPresetIndex];
        
        // Tilt Rear Wing 3D Model
        rearWingGroup.rotation.x = (wingAngle * Math.PI) / 180;
        document.getElementById('wingBadge').innerText = wingAngle + '°';
    }
    
    keys[e.code] = true;
});

window.addEventListener('keyup', e => keys[e.code] = false);

function updatePhysics() {
    if (isFinished) return;

    // Aerodynamics Tuning (0° -> Max Speed ~260km/h, 40° -> Max Speed ~130km/h)
    const maxSpeed = 0.98 - (wingAngle / 40) * 0.48;
    const gripFactor = 0.009 + (wingAngle / 40) * 0.017;

    // Accel & Brake Controls
    if (keys['ArrowUp'] || keys['KeyW']) {
        speed += 0.008;
    } else if (keys['ArrowDown'] || keys['KeyS']) {
        speed -= 0.012;
    } else {
        speed *= 0.985;
    }

    // Speed Cap
    if (speed > maxSpeed) speed = maxSpeed;
    if (speed < -maxSpeed * 0.3) speed = -maxSpeed * 0.3;

    // Smooth Steering Inertia
    const steerTarget = (keys['ArrowLeft'] || keys['KeyA']) ? 1 : ((keys['ArrowRight'] || keys['KeyD']) ? -1 : 0);
    steerSmooth += (steerTarget - steerSmooth) * 0.1;

    if (Math.abs(speed) > 0.02) {
        const dir = speed > 0 ? 1 : -1;
        carAngle += steerSmooth * gripFactor * dir * (speed / maxSpeed);
    }

    // Off-track Check (Distance to Track Center)
    const carPos = carGroup.position;
    const closestPoint = trackCurve.getPointAt((getTrackProgress(carPos) % 1));
    const distToCenter = carPos.distanceTo(closestPoint);
    
    if (distToCenter > ROAD_WIDTH / 2 + 1) {
        speed *= 0.88; // Grass Friction Penalty
    }

    // Movement Translation
    carGroup.position.x += Math.sin(carAngle) * speed;
    carGroup.position.z += Math.cos(carAngle) * speed;
    carGroup.rotation.y = carAngle;

    // Front Wheels Animation
    wheels[0].rotation.y = steerSmooth * 0.4;
    wheels[1].rotation.y = steerSmooth * 0.4;
    wheels.forEach(w => w.rotation.x += speed * 0.4);

    // 3rd Person Chase Camera
    const camOffset = new THREE.Vector3(0, 6, -15).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
    camera.position.lerp(carGroup.position.clone().add(camOffset), 0.2);
    camera.lookAt(carGroup.position.clone().add(new THREE.Vector3(0, 1.2, 0)));

    // Checkpoints & Lap Logic
    if (carGroup.position.z < -180) {
        checkpointPassed = true;
    }

    // Crossing Finish Line
    if (checkpointPassed && Math.abs(carGroup.position.x) < 20 && carGroup.position.z > 215) {
        const now = Date.now();
        const lapTime = (now - lapStartTime) / 1000;
        lapTimes.push(lapTime);
        
        checkpointPassed = false;
        lapStartTime = now;

        if (currentLap < maxLaps) {
            currentLap++;
            document.getElementById('lapVal').innerText = `${currentLap} / ${maxLaps}`;
        } else {
            isFinished = true;
            showSummaryModal();
        }
    }

    // HUD Update
    document.getElementById('speedVal').innerText = Math.round(Math.abs(speed) * 270);
    if (!isFinished) {
        const currentLapTimer = ((Date.now() - lapStartTime) / 1000).toFixed(2);
        document.getElementById('timeVal').innerText = `${currentLapTimer}s`;
    }
}

function getTrackProgress(pos) {
    let minDist = Infinity;
    let closestT = 0;
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
    
    document.getElementById('bestLap').innerText = `${best} 초`;
    document.getElementById('worstLap').innerText = `${worst} 초`;
    
    let historyHtml = "";
    lapTimes.forEach((t, i) => {
        historyHtml += `<div>Lap ${i+1}: <b>${t.toFixed(2)}s</b></div>`;
    });
    document.getElementById('lapHistory').innerHTML = historyHtml;
    
    document.getElementById('summaryModal').style.display = 'block';
}

function resetGame() {
    currentLap = 1;
    lapTimes = [];
    isFinished = false;
    checkpointPassed = false;
    
    carGroup.position.set(0, 0, 220);
    carAngle = -Math.PI / 2;
    speed = 0;
    steerSmooth = 0;
    
    document.getElementById('lapVal').innerText = `1 / ${maxLaps}`;
    document.getElementById('summaryModal').style.display = 'none';
    lapStartTime = Date.now();
}

// Render Loop
function animate() {
    requestAnimationFrame(animate);
    updatePhysics();
    renderer.render(scene, camera);
}

// Start Game
lapStartTime = Date.now();
animate();

</script>
</body>
</html>
"""

# Render Component inside Streamlit
components.html(game_3d_html, height=640)
