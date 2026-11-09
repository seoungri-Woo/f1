import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="EA SPORTS F1® 25 - Full Edition",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ EA SPORTS F1® 25: 2026 ULTIMATE CHAMPIONSHIP")
st.markdown("""
**[수정 및 보완 완료 기능]**
- 🛡️ **양쪽 3D 가드레일:** 트랙 좌우 양쪽에 은색 3D 가드레일과 스폰서 배너가 1인칭 시야에 명확히 표시됩니다.
- 🚀 **`[Shift]` ERS 부스터:** Shift 키를 누르고 있으면 배터리를 차출하여 폭발적으로 가속합니다 (FOV 75° 확대).
- ⛔ **트랙 이탈 감속:** 잔디밭으로 이탈 시 최고 속도가 **시속 70 km/h**로 제한됩니다.
- 🌧️ **날씨 예보 & WET 타이어:** 비가 오면 WET 타이어만 정속 주행 가능하며, 📻 F1 팀 라디오 무전이 상황을 알려줍니다.
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
        
        /* EA F1 25 Top Telemetry HUD */
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
            font-size: 12px;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
        }
        .hud-value {
            color: #ffffff;
            font-size: 15px;
            font-weight: 800;
            margin-left: 4px;
        }

        /* F1 Team Radio HUD Banner */
        #teamRadioBanner {
            display: none;
            position: absolute;
            top: 75px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid #22c55e;
            padding: 10px 24px;
            border-radius: 30px;
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 0 25px rgba(34, 197, 94, 0.6);
            z-index: 25;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .radio-pulse {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #22c55e;
            box-shadow: 0 0 10px #22c55e;
            animation: pulseRadio 0.8s infinite alternate;
        }
        @keyframes pulseRadio { 0% { opacity: 0.3; } 100% { opacity: 1; } }

        /* Steering Wheel Bottom HUD */
        .hud-bottom {
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 480px;
            background: rgba(10, 15, 26, 0.94);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 10px 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.9);
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .rpm-bar {
            display: flex;
            gap: 5px;
            margin-bottom: 6px;
            width: 100%;
            justify-content: center;
        }
        .rpm-led {
            width: 22px;
            height: 8px;
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
            font-size: 34px;
            font-weight: 900;
            color: #ffcc00;
            width: 55px;
            text-align: center;
            background: #0f172a;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .speed-display { text-align: center; }
        .speed-num { font-size: 28px; font-weight: 900; color: #ffffff; line-height: 1; }
        .speed-unit { font-size: 10px; color: #64748b; font-weight: 700; }

        .aero-badge { padding: 4px 10px; border-radius: 6px; font-weight: 900; font-size: 12px; }
        .mode-z { background: #0284c7; color: white; }
        .mode-x { background: #e11d48; color: white; animation: pulse 0.8s infinite alternate; }

        .gauge-group { display: flex; flex-direction: column; gap: 4px; width: 90px; }
        .gauge-bar-bg { width: 100%; height: 5px; background: #1e293b; border-radius: 3px; overflow: hidden; }
        .gauge-fill { height: 100%; width: 0%; transition: width 0.05s; }
        .fill-throttle { background: #22c55e; }
        .fill-brake { background: #ef4444; }
        .fill-ers { background: #3b82f6; }

        #audioNotice {
            position: absolute;
            top: 15px;
            right: 20px;
            background: rgba(234, 88, 12, 0.9);
            color: white;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            z-index: 15;
            cursor: pointer;
        }

        #offTrackWarning {
            display: none;
            position: absolute;
            top: 125px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(239, 68, 68, 0.95);
            color: white;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            z-index: 20;
        }

        /* Setup Modal */
        #startModal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.97);
            border: 2px solid #ffcc00;
            padding: 25px 35px;
            border-radius: 16px;
            text-align: center;
            width: 420px;
            box-shadow: 0 0 50px rgba(255, 204, 0, 0.4);
            z-index: 50;
            color: white;
        }
        #startModal h2 { color: #ffcc00; margin-top: 0; }
        .setting-group { margin: 12px 0; text-align: left; }
        .setting-group label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 4px; color: #cbd5e1; }
        select { width: 100%; padding: 8px 12px; background: #1e293b; color: white; border: 1px solid #475569; border-radius: 8px; font-size: 13px; font-weight: bold; }
        .btn-start { background: #ffcc00; color: #000; border: none; padding: 12px 30px; font-size: 17px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; transition: transform 0.2s; }
        .btn-start:hover { transform: scale(1.03); background: #ffd633; }

        /* Pit Stop Modal */
        #pitModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.96);
            border: 3px solid #ea580c;
            padding: 20px 25px;
            border-radius: 16px;
            text-align: center;
            z-index: 60;
            color: white;
            min-width: 360px;
            box-shadow: 0 0 40px rgba(234, 88, 12, 0.7);
        }
        #pitModal h3 { margin: 0 0 10px 0; color: #ea580c; }
        .btn-compound { padding: 8px 14px; margin: 4px; border: none; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }

        /* Summary Modal */
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
    <!-- Three.js Engine -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container">
        <div id="audioNotice" onclick="initAudio()">🔊 클릭하여 사운드/무전 활성화</div>
        <div id="offTrackWarning">⚠️ OFF TRACK! SPEED LIMITED TO 70 KM/H</div>

        <!-- F1 Team Radio HUD Banner -->
        <div id="teamRadioBanner">
            <div class="radio-pulse"></div>
            <span id="radioText">📻 TEAM RADIO: "Radio Check, Loud and Clear."</span>
        </div>

        <!-- Top Telemetry HUD -->
        <div class="hud-top">
            <div class="hud-item">POS <span id="posVal" class="hud-value" style="color:#38bdf8;">P2 / 4</span></div>
            <div class="hud-item">LAP <span id="lapVal" class="hud-value">1 / 5</span></div>
            <div class="hud-item">CAM <span id="camVal" class="hud-value" style="color:#a855f7;">CHASE</span></div>
            <div class="hud-item">WEATHER <span id="weatherVal" class="hud-value" style="color:#38bdf8;">DRY ☀️</span></div>
            <div class="hud-item">TYRE <span id="tireBadge" class="hud-value" style="color:#eab308;">MEDIUM</span> <span id="wearVal" class="hud-value">100%</span></div>
        </div>

        <!-- Steering Wheel Bottom HUD -->
        <div class="hud-bottom">
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
                <div class="gear-display" id="gearVal">N</div>
                <div class="speed-display">
                    <div class="speed-num" id="speedVal">0</div>
                    <div class="speed-unit">KM/H</div>
                </div>
                <div id="aeroBadge" class="aero-badge mode-z">Z-MODE</div>
                <div class="gauge-group">
                    <div style="font-size:9px; color:#aaa; font-weight:bold;">THR / BRK / ERS[Shift]</div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-throttle" id="thrBar"></div></div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-brake" id="brkBar"></div></div>
                    <div class="gauge-bar-bg"><div class="gauge-fill fill-ers" id="ersBar"></div></div>
                </div>
            </div>
        </div>

        <!-- Setup Game Modal -->
        <div id="startModal">
            <h2>🏎️ F1® 25 ULTIMATE 설정</h2>
            <div class="setting-group">
                <label>🚩 레이스 랩 수 선택</label>
                <select id="selectLaps">
                    <option value="3">3 Laps (스프린트 레이스)</option>
                    <option value="5" selected>5 Laps (표준 레이스)</option>
                    <option value="8">8 Laps (전략 레이스)</option>
                </select>
            </div>
            <div class="setting-group">
                <label>☀️ 시작 날씨 선택</label>
                <select id="selectInitialWeather">
                    <option value="DRY" selected>☀️ Dry (맑음)</option>
                    <option value="RAIN">🌧️ Wet (우천/비)</option>
                </select>
            </div>
            <div class="setting-group">
                <label>🔮 미래 날씨 변화 예보 (Forecast)</label>
                <select id="selectWeatherTrend">
                    <option value="STABLE" selected>🔒 날씨 변화 없음 (고정)</option>
                    <option value="DRY_TO_RAIN">🌧️ 맑다가 비 옴 (2~3 Lap 비예보)</option>
                    <option value="RAIN_TO_DRY">☀️ 비 오다가 맑아짐 (2~3 Lap 건조)</option>
                </select>
            </div>
            <div class="setting-group">
                <label>🛞 스타트 타이어 선택</label>
                <select id="selectTire">
                    <option value="SOFT">🔴 Soft (슬릭 Dry)</option>
                    <option value="MEDIUM" selected>🟡 Medium (슬릭 Dry)</option>
                    <option value="HARD">⚪ Hard (슬릭 Dry)</option>
                    <option value="INTERMEDIATE">🟢 Intermediate (웨트 Rain)</option>
                    <option value="WET">🔵 Full Wet (폭우 Rain)</option>
                </select>
            </div>
            <button class="btn-start" onclick="initGame()">2026 RACE START</button>
        </div>

        <!-- Pit Stop Modal -->
        <div id="pitModal">
            <h3>⛽ F1 PIT STOP 타이어 교체</h3>
            <p style="font-size:12px; margin-bottom:10px;">노면 상태에 적합한 컴파운드를 선택하세요:</p>
            <button class="btn-compound" style="background:#e63946; color:white;" onclick="changeTire('SOFT')">🔴 SOFT</button>
            <button class="btn-compound" style="background:#eab308; color:black;" onclick="changeTire('MEDIUM')">🟡 MEDIUM</button>
            <button class="btn-compound" style="background:#94a3b8; color:black;" onclick="changeTire('HARD')">⚪ HARD</button><br>
            <button class="btn-compound" style="background:#10b981; color:white;" onclick="changeTire('INTERMEDIATE')">🟢 INTERMEDIATE</button>
            <button class="btn-compound" style="background:#3b82f6; color:white;" onclick="changeTire('WET')">🔵 FULL WET</button>
        </div>

        <!-- Summary Modal -->
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
// --- Web Audio API & Team Radio Synthesizer ---
let audioCtx = null;
let engineOsc = null;
let engineGain = null;

function initAudio() {
    if (audioCtx) return;
    try {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        engineOsc = audioCtx.createOscillator();
        engineGain = audioCtx.createGain();

        engineOsc.type = 'sawtooth';
        engineOsc.frequency.value = 75;
        engineGain.gain.value = 0.04;

        engineOsc.connect(engineGain);
        engineGain.connect(audioCtx.destination);
        engineOsc.start();
        document.getElementById('audioNotice').innerText = '🔊 Audio Active';
        playTeamRadio("Radio check. Engine parameters nominal.");
    } catch(e) { console.log(e); }
}
window.addEventListener('click', initAudio);

function updateAudioEngine(speedKmh) {
    if (!audioCtx || !engineOsc) return;
    const rpmPitch = 70 + (speedKmh % 45) * 7.5 + (speedKmh / 300) * 120;
    engineOsc.frequency.setTargetAtTime(rpmPitch, audioCtx.currentTime, 0.05);
}

function playTeamRadio(msg) {
    const banner = document.getElementById('teamRadioBanner');
    const txt = document.getElementById('radioText');
    txt.innerText = `📻 TEAM RADIO: "${msg}"`;
    banner.style.display = 'flex';

    if (audioCtx) {
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.value = 650;
        g.gain.value = 0.06;
        osc.connect(g);
        g.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.25);
    }
    setTimeout(() => { banner.style.display = 'none'; }, 4500);
}

// --- Dynamic Canvas Sponsor Banners (ROLEX, PIRELLI, ARAMCO, DHL, HEINEKEN) ---
function createSponsorTexture(text, bgColor, textColor) {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, 512, 128);
    ctx.fillStyle = textColor;
    ctx.font = 'bold 54px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 256, 64);

    return new THREE.CanvasTexture(canvas);
}

const sponsorTextures = [
    createSponsorTexture('ROLEX', '#006039', '#eab308'),
    createSponsorTexture('PIRELLI', '#eab308', '#dc2626'),
    createSponsorTexture('ARAMCO', '#00a389', '#ffffff'),
    createSponsorTexture('DHL', '#ffcc00', '#d97706'),
    createSponsorTexture('HEINEKEN', '#008234', '#ffffff')
];

// --- Three.js Setup ---
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
const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(250, 400, 150);
dirLight.castShadow = true;
scene.add(dirLight);

// Ground Grass Plane
const grassGeo = new THREE.PlaneGeometry(3500, 3500);
const grassMat = new THREE.MeshLambertMaterial({ color: 0x1c421e });
const grass = new THREE.Mesh(grassGeo, grassMat);
grass.rotation.x = -Math.PI / 2;
grass.position.y = -0.05;
scene.add(grass);

// --- 3D Track & Guardrails & Sponsor Banners ---
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
let roadMaterial;

function build3DTrackAndGuardrails() {
    const points = trackCurve.getSpacedPoints(SEGMENTS);
    const roadVertices = [], roadIndices = [];
    const kerbVertices = [], kerbColors = [], kerbIndices = [];

    const guardrailMat = new THREE.MeshStandardMaterial({ color: 0xd1d5db, metalness: 0.85, roughness: 0.25 });
    const postMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.7 });

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

        // Kerbs
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

        // 🛡️ BOTH INNER & OUTER 3D METALLIC GUARDRAILS (Dense spacing for 1st person view!)
        if (i % 4 === 0) {
            const rotY = Math.atan2(dir.x, dir.z);

            // Outer Guardrail (Left)
            const lPos = p1.clone().add(norm.clone().multiplyScalar(ROAD_WIDTH / 2 + 4.5));
            const lRail = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.4, 0.35), guardrailMat);
            lRail.position.set(lPos.x, 1.4, lPos.z);
            lRail.rotation.y = rotY;
            scene.add(lRail);

            const lPost = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 2.8), postMat);
            lPost.position.set(lPos.x, 1.4, lPos.z);
            scene.add(lPost);

            // Inner Guardrail (Right)
            const rPos = p1.clone().add(norm.clone().multiplyScalar(-ROAD_WIDTH / 2 - 4.5));
            const rRail = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.4, 0.35), guardrailMat);
            rRail.position.set(rPos.x, 1.4, rPos.z);
            rRail.rotation.y = rotY;
            scene.add(rRail);

            const rPost = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 2.8), postMat);
            rPost.position.set(rPos.x, 1.4, rPos.z);
            scene.add(rPost);

            // 🏢 Sponsor Banner Attachment (Every 16 segments)
            if (i % 16 === 0) {
                const sponsorTex = sponsorTextures[(i / 16) % sponsorTextures.length];
                const bannerMesh = new THREE.Mesh(
                    new THREE.PlaneGeometry(7.5, 1.8),
                    new THREE.MeshBasicMaterial({ map: sponsorTex, side: THREE.DoubleSide })
                );
                bannerMesh.position.set(lPos.x, 2.5, lPos.z);
                bannerMesh.rotation.y = rotY;
                scene.add(bannerMesh);
            }
        }
    }

    const roadGeo = new THREE.BufferGeometry();
    roadGeo.setAttribute('position', new THREE.Float32BufferAttribute(roadVertices, 3));
    roadGeo.setIndex(roadIndices);
    roadGeo.computeVertexNormals();

    roadMaterial = new THREE.MeshStandardMaterial({ color: 0x222228, roughness: 0.85, metalness: 0.1 });
    const roadMesh = new THREE.Mesh(roadGeo, roadMaterial);
    roadMesh.receiveShadow = true;
    scene.add(roadMesh);

    const kerbGeo = new THREE.BufferGeometry();
    kerbGeo.setAttribute('position', new THREE.Float32BufferAttribute(kerbVertices, 3));
    kerbGeo.setAttribute('color', new THREE.Float32BufferAttribute(kerbColors, 3));
    kerbGeo.setIndex(kerbIndices);
    scene.add(new THREE.Mesh(kerbGeo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide })));
}
build3DTrackAndGuardrails();

// --- Real 3D Pit Lane Geometry ---
function buildRealisticPitLane() {
    const pitAsphaltMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(160, 22),
        new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 })
    );
    pitAsphaltMesh.rotation.x = -Math.PI / 2;
    pitAsphaltMesh.position.set(20, 0.02, 252);
    scene.add(pitAsphaltMesh);

    const pitWall = new THREE.Mesh(new THREE.BoxGeometry(160, 2.4, 1.6), new THREE.MeshStandardMaterial({ color: 0x475569 }));
    pitWall.position.set(20, 1.2, 238);
    scene.add(pitWall);

    const entryTaper = new THREE.Mesh(new THREE.PlaneGeometry(40, 16), new THREE.MeshStandardMaterial({ color: 0x334155 }));
    entryTaper.rotation.x = -Math.PI / 2;
    entryTaper.rotation.z = -0.25;
    entryTaper.position.set(-70, 0.02, 236);
    scene.add(entryTaper);

    const exitTaper = new THREE.Mesh(new THREE.PlaneGeometry(40, 16), new THREE.MeshStandardMaterial({ color: 0x334155 }));
    exitTaper.rotation.x = -Math.PI / 2;
    exitTaper.rotation.z = 0.25;
    exitTaper.position.set(110, 0.02, 236);
    scene.add(exitTaper);

    const pitBoxMesh = new THREE.Mesh(new THREE.PlaneGeometry(22, 12), new THREE.MeshBasicMaterial({ color: 0xea580c, side: THREE.DoubleSide }));
    pitBoxMesh.rotation.x = -Math.PI / 2;
    pitBoxMesh.position.set(40, 0.04, 252);
    scene.add(pitBoxMesh);

    const garageColors = [0xef4444, 0x1e3a8a, 0x06b6d4, 0xf97316];
    for (let i = 0; i < 4; i++) {
        const gBuilding = new THREE.Mesh(new THREE.BoxGeometry(28, 7.0, 14), new THREE.MeshStandardMaterial({ color: garageColors[i] }));
        gBuilding.position.set(-30 + i * 32, 3.5, 268);
        scene.add(gBuilding);
    }
}
buildRealisticPitLane();

// Weather System Particles
const rainGeo = new THREE.BufferGeometry();
const rainCount = 1800;
const rainPos = new Float32Array(rainCount * 3);
for(let i=0; i<rainCount*3; i+=3) {
    rainPos[i] = (Math.random() - 0.5) * 800;
    rainPos[i+1] = Math.random() * 120;
    rainPos[i+2] = (Math.random() - 0.5) * 800;
}
rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
const rainPoints = new THREE.Points(rainGeo, new THREE.PointsMaterial({ color: 0xaaaaee, size: 0.6, transparent: true, opacity: 0.7 }));
rainPoints.visible = false;
scene.add(rainPoints);

let isRaining = false;
function setWeatherState(rainBool) {
    isRaining = rainBool;
    rainPoints.visible = isRaining;
    const wBadge = document.getElementById('weatherVal');
    if (isRaining) {
        wBadge.innerText = 'RAIN 🌧️';
        wBadge.style.color = '#60a5fa';
        scene.background.setHex(0x233342);
        scene.fog.color.setHex(0x233342);
        roadMaterial.roughness = 0.15;
        roadMaterial.metalness = 0.75;
    } else {
        wBadge.innerText = 'DRY ☀️';
        wBadge.style.color = '#38bdf8';
        scene.background.setHex(0x4a7c9d);
        scene.fog.color.setHex(0x4a7c9d);
        roadMaterial.roughness = 0.85;
        roadMaterial.metalness = 0.10;
    }
}

// 3D Pit Crew Members
function createPitCrewMember() {
    const crewGroup = new THREE.Group();
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.3, 8), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
    torso.position.y = 0.95;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.28, 12, 12), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    head.position.y = 1.75;
    const spareTireMat = new THREE.MeshStandardMaterial({ color: 0xeab308 });
    const spareTire = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.45, 16), spareTireMat);
    spareTire.geometry.rotateZ(Math.PI / 2);
    spareTire.position.set(0, 1.0, 0.4);
    crewGroup.add(torso, head, spareTire);
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

// F1 Car Mesh
function create3DCar(colorHex, rWingColorHex) {
    const carGroup = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.6, 5.4), new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.2, metalness: 0.6 }));
    body.position.y = 0.55;
    carGroup.add(body);

    const haloRing = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.08, 8, 16, Math.PI), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    haloRing.rotation.x = Math.PI / 2;
    haloRing.position.set(0, 0.95, 0.3);
    carGroup.add(haloRing);

    const fWing = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.1, 1.0), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    fWing.position.set(0, 0.3, 2.7);
    carGroup.add(fWing);

    const rearWingGroup = new THREE.Group();
    rearWingGroup.position.set(0, 1.15, -2.5);
    const rWingMain = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.12, 1.0), new THREE.MeshStandardMaterial({ color: rWingColorHex }));
    rearWingGroup.add(rWingMain);
    const activeFlap = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.06, 0.45), new THREE.MeshStandardMaterial({ color: 0xffffff }));
    activeFlap.position.set(0, 0.15, 0.1);
    rearWingGroup.add(activeFlap);
    carGroup.add(rearWingGroup);

    const wheelGeo = new THREE.CylinderGeometry(0.6, 0.6, 0.5, 24);
    wheelGeo.rotateZ(Math.PI / 2);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0d0d0d, roughness: 0.9 });
    const wheels = [];
    const wheelPositions = [[-1.4, 0.6, 1.9], [1.4, 0.6, 1.9], [-1.4, 0.6, -1.9], [1.4, 0.6, -1.9]];

    wheelPositions.forEach((pos) => {
        const wheelPivot = new THREE.Group();
        wheelPivot.position.set(...pos);
        const wheelMesh = new THREE.Mesh(wheelGeo, wheelMat);
        wheelPivot.add(wheelMesh);
        carGroup.add(wheelPivot);
        wheels.push(wheelMesh);
    });

    return { group: carGroup, activeFlap, wheels, wheelMat };
}

const playerObj = create3DCar(0xef4444, 0xffcc00);
scene.add(playerObj.group);

const aiCars = [
    { name: "Red Bull", color: 0x1e3a8a, rWing: 0xf59e0b, gridX: -30, gridZ: 226, offset: -6, speed: 0.82 },
    { name: "Mercedes", color: 0x64748b, rWing: 0x06b6d4, gridX: 20, gridZ: 226, offset: 6, speed: 0.80 },
    { name: "McLaren", color: 0xf97316, rWing: 0x111827, gridX: -45, gridZ: 214, offset: -10, speed: 0.78 }
].map(d => {
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

// Tyre Mechanics Physics
const TIRE_SPECS = {
    'SOFT': { speedMult: 1.08, gripMult: 1.25, wearRate: 0.28, wetOk: false, wheelColor: 0xe63946 },
    'MEDIUM': { speedMult: 1.00, gripMult: 1.00, wearRate: 0.14, wetOk: false, wheelColor: 0xeab308 },
    'HARD': { speedMult: 0.94, gripMult: 0.82, wearRate: 0.06, wetOk: false, wheelColor: 0x94a3b8 },
    'INTERMEDIATE': { speedMult: 0.96, gripMult: 1.15, wearRate: 0.12, wetOk: true, wheelColor: 0x10b981 },
    'WET': { speedMult: 0.92, gripMult: 1.35, wearRate: 0.08, wetOk: true, wheelColor: 0x3b82f6 }
};

let currentTire = 'MEDIUM';
let tireWear = 100.0;
let cameraMode = 0;
let activeAeroXMode = false;
let weatherTrend = 'STABLE';

// ERS & Key Tracking
let ersBattery = 100.0;
let isErsBoosting = false;
let keys = {};

let speed = 0;
let carAngle = Math.PI / 2;
let steerSmooth = 0;
let inPit = false;
let isPitChanging = false;
let pitCooldown = false;

let startState = 'WAITING';
let maxLaps = 5;
let playerLap = 0;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD","KeyC","ShiftLeft","ShiftRight","KeyE"].includes(e.code)) {
        e.preventDefault();
    }
    if (e.code === 'KeyC' && !e.repeat) {
        cameraMode = (cameraMode + 1) % 3;
        const camNames = ['CHASE', 'T-CAM', 'COCKPIT'];
        document.getElementById('camVal').innerText = camNames[cameraMode];
    }
    if (e.code === 'Space' && !e.repeat && startState === 'GO' && !isFinished && !inPit) {
        activeAeroXMode = !activeAeroXMode;
        const badge = document.getElementById('aeroBadge');
        if (activeAeroXMode) {
            badge.innerText = 'X-MODE';
            badge.className = 'aero-badge mode-x';
            playerObj.activeFlap.rotation.x = -0.45;
        } else {
            badge.innerText = 'Z-MODE';
            badge.className = 'aero-badge mode-z';
            playerObj.activeFlap.rotation.x = 0;
        }
    }
    keys[e.code] = true;
});
window.addEventListener('keyup', e => keys[e.code] = false);

function initGame() {
    maxLaps = parseInt(document.getElementById('selectLaps').value);
    const initialWeather = document.getElementById('selectInitialWeather').value;
    weatherTrend = document.getElementById('selectWeatherTrend').value;
    currentTire = document.getElementById('selectTire').value;

    setWeatherState(initialWeather === 'RAIN');
    updateTireUI();

    document.getElementById('startModal').style.display = 'none';
    document.getElementById('lapVal').innerText = `1 / ${maxLaps}`;
    startState = 'GO';
    lapStartTime = Date.now();
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

    // 🚀 SHIFT ERS BOOST MECHANICS
    isErsBoosting = (keys['ShiftLeft'] || keys['ShiftRight'] || keys['KeyE']) && ersBattery > 0;
    const ersMult = isErsBoosting ? 1.25 : 1.0;
    if (isErsBoosting) {
        ersBattery -= 0.40;
        if (ersBattery < 0) ersBattery = 0;
    } else if (ersBattery < 100) {
        ersBattery += 0.10; // Recharge
    }

    // Weather Penalty Logic
    let weatherPenalty = 1.0;
    if (isRaining && !spec.wetOk) {
        weatherPenalty = 0.35;
    } else if (!isRaining && spec.wetOk) {
        weatherPenalty = 0.80;
    }

    const aeroSpeedBoost = activeAeroXMode ? 1.14 : 0.96;
    let maxSpeed = 0.98 * spec.speedMult * aeroSpeedBoost * ersMult * weatherPenalty;

    // ⛔ OFF-TRACK DETECTION (70 KM/H STRICT SPEED LIMIT)
    const carPos = playerObj.group.position;
    const currentProgress = getTrackProgress(carPos);
    const closestPoint = trackCurve.getPointAt(currentProgress % 1);

    const distFromCenter = carPos.distanceTo(closestPoint);
    const isOffTrack = (distFromCenter > ROAD_WIDTH / 2 + 1.2) && (carPos.z < 235);
    const OFF_TRACK_MAX_SPEED = 70 / 310; // 70 km/h in world scale (approx 0.225)

    if (isOffTrack) {
        document.getElementById('offTrackWarning').style.display = 'block';
        if (maxSpeed > OFF_TRACK_MAX_SPEED) {
            maxSpeed = OFF_TRACK_MAX_SPEED;
        }
        if (speed > OFF_TRACK_MAX_SPEED) {
            speed *= 0.92; // Rapid deceleration to 70 km/h
        }
    } else {
        document.getElementById('offTrackWarning').style.display = 'none';
    }

    const gripFactor = 0.014 * spec.gripMult * weatherPenalty;
    const isAccel = (keys['ArrowUp'] || keys['KeyW']);
    const isBrake = (keys['ArrowDown'] || keys['KeyS']);

    if (isAccel) speed += 0.008 * ersMult;
    else if (isBrake) speed -= 0.014;
    else speed *= 0.985;

    if (speed > maxSpeed) speed = maxSpeed;

    const steerTarget = (keys['ArrowLeft'] || keys['KeyA']) ? 1 : ((keys['ArrowRight'] || keys['KeyD']) ? -1 : 0);
    steerSmooth += (steerTarget - steerSmooth) * 0.1;

    if (Math.abs(speed) > 0.02) {
        const dir = speed > 0 ? 1 : -1;
        carAngle += steerSmooth * gripFactor * dir * (speed / Math.max(0.1, maxSpeed));
    }

    if (Math.abs(speed) > 0.05) {
        tireWear -= spec.wearRate * (1 + Math.abs(steerSmooth) * 0.5) * 0.05;
        if (tireWear < 0) tireWear = 0;
    }

    if (pitCooldown && (carPos.x > 80 || carPos.z < 235)) {
        pitCooldown = false;
    }

    carPos.x += Math.sin(carAngle) * speed;
    carPos.z += Math.cos(carAngle) * speed;
    playerObj.group.rotation.y = carAngle;

    playerObj.wheels.forEach(w => w.rotation.x += speed * 0.5);

    // Dynamic Camera View & ERS Dynamic FOV (75deg on Boost)
    const targetFov = (isErsBoosting || activeAeroXMode) ? 75 : 55;
    camera.fov += (targetFov - camera.fov) * 0.1;
    camera.updateProjectionMatrix();

    if (inPit || isPitChanging) {
        const pitCamPos = new THREE.Vector3(carPos.x - 4, 3.5, carPos.z + 10);
        camera.position.lerp(pitCamPos, 0.15);
        camera.lookAt(carPos.x, 1.2, carPos.z);
    } else {
        if (cameraMode === 0) { // Chase
            const camOffset = new THREE.Vector3(0, 5.5, -14).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
            camera.position.lerp(carPos.clone().add(camOffset), 0.2);
            camera.lookAt(carPos.clone().add(new THREE.Vector3(0, 1.2, 0)));
        } else if (cameraMode === 1) { // T-Cam
            const tCamOffset = new THREE.Vector3(0, 1.55, -0.4).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
            camera.position.copy(carPos.clone().add(tCamOffset));
            camera.lookAt(carPos.clone().add(new THREE.Vector3(Math.sin(carAngle)*20, 1.0, Math.cos(carAngle)*20)));
        } else if (cameraMode === 2) { // Cockpit 1st Person
            const cCamOffset = new THREE.Vector3(0, 0.85, 0.1).applyAxisAngle(new THREE.Vector3(0, 1, 0), carAngle);
            camera.position.copy(carPos.clone().add(cCamOffset));
            camera.lookAt(carPos.clone().add(new THREE.Vector3(Math.sin(carAngle)*20, 0.85, Math.cos(carAngle)*20)));
        }
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

    // Lap Completion & Weather Forecast Progression Trigger
    if (checkpointPassed && Math.abs(carPos.x) < 25 && carPos.z > 215 && carPos.z < 235) {
        const now = Date.now();
        lapTimes.push((now - lapStartTime) / 1000);
        checkpointPassed = false;
        lapStartTime = now;
        playerLap++;

        if (weatherTrend === 'DRY_TO_RAIN' && playerLap === 2 && !isRaining) {
            setWeatherState(true);
            playTeamRadio("Rain is falling heavily! Box now for WET tyres!");
        } else if (weatherTrend === 'RAIN_TO_DRY' && playerLap === 2 && isRaining) {
            setWeatherState(false);
            playTeamRadio("Track is drying up rapidly! Box for SOFT tyres!");
        }

        if (playerLap < maxLaps) {
            document.getElementById('lapVal').innerText = `${playerLap + 1} / ${maxLaps}`;
        } else {
            isFinished = true;
            showSummaryModal();
        }
    }

    if (isRaining) {
        const positions = rainPoints.geometry.attributes.position.array;
        for (let i = 1; i < rainCount * 3; i += 3) {
            positions[i] -= 2.5;
            if (positions[i] < 0) positions[i] = 100;
        }
        rainPoints.geometry.attributes.position.needsUpdate = true;
    }

    aiCars.forEach(ai => {
        ai.progress = (ai.progress + ai.speed * 0.0004) % 1;
        const pt = trackCurve.getPointAt(ai.progress);
        const nextPt = trackCurve.getPointAt((ai.progress + 0.005) % 1);
        const dir = new THREE.Vector3().subVectors(nextPt, pt).normalize();
        const norm = new THREE.Vector3(-dir.z, 0, dir.x).normalize();
        
        ai.obj.group.position.copy(pt.clone().add(norm.multiplyScalar(ai.offset)));
        ai.obj.group.rotation.y = Math.atan2(dir.x, dir.z);
        ai.obj.wheels.forEach(w => w.rotation.x += ai.speed * 0.4);
    });

    calculateStandings(currentProgress);
    const speedKmh = Math.round(Math.abs(speed) * 310);
    updateHUDTelemetry(speedKmh, isAccel, isBrake);
    updateAudioEngine(speedKmh);
}

function updateHUDTelemetry(speedKmh, isAccel, isBrake) {
    document.getElementById('speedVal').innerText = speedKmh;

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

    const rpmPercent = (speedKmh % 45) / 45;
    const activeLeds = Math.floor(rpmPercent * 10);
    for (let i = 0; i < 10; i++) {
        const led = document.getElementById(`led${i}`);
        if (i < activeLeds) led.classList.add('active');
        else led.classList.remove('active');
    }

    document.getElementById('thrBar').style.width = isAccel ? '100%' : '0%';
    document.getElementById('brkBar').style.width = isBrake ? '100%' : '0%';
    document.getElementById('ersBar').style.width = `${ersBattery}%`;
    document.getElementById('wearVal').innerText = `${Math.round(tireWear)}%`;
}

function changeTire(newCompound) {
    if (isPitChanging) return;
    isPitChanging = true;

    currentTire = newCompound;
    tireWear = 100.0;
    updateTireUI();

    document.getElementById('pitModal').style.display = 'none';
    playTeamRadio("Good pit stop! Push hard on out-lap!");

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

                    speed = 0.55;
                    carPos.x += 12;
                    inPit = false;
                    isPitChanging = false;
                    pitCooldown = true;
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
