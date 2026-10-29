import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F1 3D Real Racing & Aerodynamics",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 3D 3인칭 레이싱 시뮬레이터")
st.markdown("""
**[게임 조작 방법]**
- **방향키 (↑ / ↓ / ← / →) 또는 WASD:** 가속 / 브레이크 및 후진 / 핸들 조향
- **스페이스바 (Space):** 리어 윙 각도 4단계 전환 (**0° ➔ 15° ➔ 30° ➔ 40°**)
- **리어 윙 물리 엔진:** 
  - **0° (직선 특화):** 최대 속도 증가, 코너링 시 접지력 저하 (접지력 부족 시 미끄러짐)
  - **40° (코너 특화):** 코너링 고속 안정성 증가, 최고 속도 감소 (공기저항 증가)
""")

# HTML5 + Three.js 3D Racing Engine
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
            height: 600px;
            position: relative;
        }
        
        /* Glassmorphism HUD Overlay */
        .hud-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            display: flex;
            gap: 15px;
            background: rgba(20, 20, 20, 0.75);
            backdrop-filter: blur(8px);
            padding: 12px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: white;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            z-index: 5;
        }
        .hud-item {
            font-size: 15px;
            font-weight: 600;
        }
        .hud-value {
            color: #ffcc00;
            font-weight: bold;
            font-size: 17px;
        }

        /* Wing Badge Indicator */
        .wing-badge {
            background: #e63946;
            color: white;
            padding: 3px 10px;
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
            background: rgba(15, 15, 15, 0.95);
            border: 2px solid #ffcc00;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            width: 350px;
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
    <!-- Three.js 3D Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container">
        <!-- HUD Overlay -->
        <div class="hud-panel">
            <div class="hud-item">🔧 리어 윙 각도 [Space]: <span id="wingBadge" class="wing-badge">15°</span></div>
            <div class="hud-item">⚡ 속도: <span id="speedVal" class="hud-value">0</span> km/h</div>
            <div class="hud-item">🚩 Laps: <span id="lapVal" class="hud-value">1 / 3</span></div>
            <div class="hud-item">⏱️ 현재 랩: <span id="timeVal" class="hud-value">0.00s</span></div>
        </div>

        <!-- Finish Modal -->
        <div id="summaryModal">
            <h2>🏁 레이스 종료!</h2>
            <div class="stat-box">🏆 <b>최단 랩타임 (Best):</b> <span id="bestLap" style="color:#4caf50;">-</span></div>
            <div class="stat-box">🐢 <b>최장 랩타임 (Worst):</b> <span id="worstLap" style="color:#f44336;">-</span></div>
            <div class="stat-box">📊 <b>각 랩별 기록:</b><div id="lapHistory" style="font-size:14px; margin-top:6px; color:#ccc;"></div></div>
            <button class="btn-restart" onclick="resetGame()">다시 도전하기</button>
        </div>
    </div>

<script>
// --- Three.js & Setup ---
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb); // Sky blue
scene.fog = new THREE.FogExp2(0x87ceeb, 0.003);

const camera = new THREE.PerspectiveCamera(60, container.clientWidth / 600, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, 600);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// --- Lighting ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(100, 150, 50);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.near = 10;
dirLight.shadow.camera.far = 400;
dirLight.shadow.camera.left = -150;
dirLight.shadow.camera.right = 150;
dirLight.shadow.camera.top = 150;
dirLight.shadow.camera.bottom = -150;
scene.add(dirLight);

// --- Track Circuit Definition ---
const trackCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 100),
    new THREE.Vector3(120, 0, 100),
    new THREE.Vector3(180, 0, 40),
    new THREE.Vector3(150, 0, -80),
    new THREE.Vector3(60, 0, -120),
    new THREE.Vector3(-60, 0, -120),
    new THREE.Vector3(-150, 0, -60),
    new THREE.Vector3(-120, 0, 40)
], true, 'catmullrom', 0.2);

// Ground (Grass)
const grassGeo = new THREE.PlaneGeometry(1000, 1000);
const grassMat = new THREE.MeshLambertMaterial({ color: 0x2e7d32 });
const grass = new THREE.Mesh(grassGeo, grassMat);
grass.rotation.x = -Math.PI / 2;
grass.position.y = -0.1;
grass.receiveShadow = true;
scene.add(grass);

// Track Mesh
const trackGeometry = new THREE.TubeGeometry(trackCurve, 120, 16, 2, true);
const trackMaterial = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.8 });
const trackMesh = new THREE.Mesh(trackGeometry, trackMaterial);
trackMesh.scale.set(1, 0.01, 1); // Flatten to asphalt road
trackMesh.receiveShadow = true;
scene.add(trackMesh);

// Finish Line Banner
const finishLineGeo = new THREE.BoxGeometry(20, 0.1, 4);
const finishLineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
const finishLine = new THREE.Mesh(finishLineGeo, finishLineMat);
finishLine.position.set(0, 0.05, 100);
scene.add(finishLine);

// --- F1 Car Construction ---
const carGroup = new THREE.Group();

// Body Chassis
const bodyGeo = new THREE.BoxGeometry(2, 0.8, 5);
const bodyMat = new THREE.MeshStandardMaterial({ color: 0xe63946, roughness: 0.3, metalness: 0.5 });
const body = new THREE.Mesh(bodyGeo, bodyMat);
body.position.y = 0.6;
body.castShadow = true;
carGroup.add(body);

// Cockpit
const cockpitGeo = new THREE.SphereGeometry(0.6, 16, 16);
const cockpitMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
const cockpit = new THREE.Mesh(cockpitGeo, cockpitMat);
cockpit.position.set(0, 0.9, -0.2);
carGroup.add(cockpit);

// Front Wing
const fWingGeo = new THREE.BoxGeometry(3.2, 0.1, 0.8);
const wingMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
const fWing = new THREE.Mesh(fWingGeo, wingMat);
fWing.position.set(0, 0.3, 2.5);
fWing.castShadow = true;
carGroup.add(fWing);

// Adjustable Rear Wing Group
const rearWingGroup = new THREE.Group();
rearWingGroup.position.set(0, 1.1, -2.3);

const rWingMain = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.15, 0.8), new THREE.MeshStandardMaterial({ color: 0xffcc00 }));
rWingMain.castShadow = true;
rearWingGroup.add(rWingMain);

const rWingPillar1 = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 0.1), wingMat);
rWingPillar1.position.set(-0.8, -0.3, 0);
rearWingGroup.add(rWingPillar1);
const rWingPillar2 = rWingPillar1.clone();
rWingPillar2.position.set(0.8, -0.3, 0);
rearWingGroup.add(rWingPillar2);

carGroup.add(rearWingGroup);

// Wheels
const wheelGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 16);
const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.9 });

const wheels = [];
const wheelPositions = [
    [-1.2, 0.5, 1.8], [1.2, 0.5, 1.8],
    [-1.2, 0.5, -1.8], [1.2, 0.5, -1.8]
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

// Initial Car Position
carGroup.position.set(0, 0, 100);

// --- Game Physics & Aerodynamics Logic ---
const wingPresetAngles = [0, 15, 30, 40];
let wingPresetIndex = 1; // Default 15deg
let wingAngle = 15;

let speed = 0;
let carAngle = -Math.PI / 2; // Facing along start line
let keys = {};

// Race State
let currentLap = 1;
const maxLaps = 3;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

// Key Handlers
window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD"].includes(e.code)) {
        e.preventDefault();
    }
    
    // Spacebar toggles 4 Wing Angles: 0 -> 15 -> 30 -> 40
    if (e.code === 'Space' && !e.repeat) {
        wingPresetIndex = (wingPresetIndex + 1) % wingPresetAngles.length;
        wingAngle = wingPresetAngles[wingPresetIndex];
        
        // Update Rear Wing visual tilt
        rearWingGroup.rotation.x = (wingAngle * Math.PI) / 180;
        document.getElementById('wingBadge').innerText = wingAngle + '°';
    }
    
    keys[e.code] = true;
});

window.addEventListener('keyup', e => keys[e.code] = false);

function updatePhysics() {
    if (isFinished) return;

    // Aerodynamic Math Equations
    // Drag reduces max top speed
    const maxSpeed = 2.2 - (wingAngle / 40) * 0.7; // 0° -> 2.2 (~180km/h), 40° -> 1.5 (~120km/h)
    
    // Downforce increases steering grip / response
    const turnGrip = 0.015 + (wingAngle / 40) * 0.02;

    // Acceleration & Braking Controls
    if (keys['ArrowUp'] || keys['KeyW']) {
        speed += 0.02;
    } else if (keys['ArrowDown'] || keys['KeyS']) {
        speed -= 0.025;
    } else {
        speed *= 0.96; // Friction
    }

    // Speed Cap
    if (speed > maxSpeed) speed = maxSpeed;
    if (speed < -maxSpeed * 0.3) speed = -maxSpeed * 0.3;

    // Distance to Track Centerline (Off-Track Check)
    const carPos = carGroup.position;
    const closestPoint = trackCurve.getPointAt((getTrackProgress(carPos) % 1));
    const distToCenter = carPos.distanceTo(closestPoint);
    
    if (distToCenter > 14) {
        speed *= 0.85; // Off-track grass penalty
    }

    // Steering Adjustment
    if (Math.abs(speed) > 0.05) {
        const dir = speed > 0 ? 1 : -1;
        if (keys['ArrowLeft'] || keys['KeyA']) carAngle += turnGrip * dir;
        if (keys['ArrowRight'] || keys['KeyD']) carAngle -= turnGrip * dir;
    }

    // Movement Vector
    carGroup.position.x += Math.sin(carAngle) * speed;
    carGroup.position.z += Math.cos(carAngle) * speed;
    carGroup.rotation.y = carAngle;

    // Rotate Wheels during movement
    wheels.forEach(w => w.rotation.x += speed * 0.5);

    // 3rd Person Chase Camera Logic
    const camOffset = new THREE.Vector3(0, 6, -16).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
    camera.position.copy(carGroup.position).add(camOffset);
    camera.lookAt(carGroup.position.clone().add(new THREE.Vector3(0, 1.5, 0)));

    // Checkpoints & Laps
    if (carGroup.position.z < -90) {
        checkpointPassed = true;
    }

    // Crossing Finish Line (z >= 100, x around 0)
    if (checkpointPassed && Math.abs(carGroup.position.x) < 20 && carGroup.position.z > 95) {
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
    document.getElementById('speedVal').innerText = Math.round(Math.abs(speed) * 85);
    if (!isFinished) {
        const currentLapTimer = ((Date.now() - lapStartTime) / 1000).toFixed(2);
        document.getElementById('timeVal').innerText = `${currentLapTimer}s`;
    }
}

// Approximate position on track loop
function getTrackProgress(pos) {
    let minDist = Infinity;
    let closestT = 0;
    for (let t = 0; t <= 1; t += 0.02) {
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
    
    carGroup.position.set(0, 0, 100);
    carAngle = -Math.PI / 2;
    speed = 0;
    
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

// Start
lapStartTime = Date.now();
animate();

</script>
</body>
</html>
"""

# Render Component inside Streamlit
components.html(game_3d_html, height=620)
