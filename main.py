import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F1 Championship & Aerodynamics Simulator",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 챔피언십: 리얼 서킷 & 타이어 피트인 시뮬레이터")
st.markdown("""
**[게임 조작 및 튜닝 전략]**
- **방향키 (↑ / ↓ / ← / →) 또는 WASD:** 가속 / 브레이크 / **부드러운 조향**
- **스페이스바 (Space):** 리어 윙 4단계 전환 (**0° ➔ 15° ➔ 30° ➔ 40°**)
- **피트인 (Pit Stop):** 타이어 마모 시 **피트 레이인(주황색 피트 박스)**으로 진입하면 3초 간 정지 후 타이어 교체!
- **타이어 전략:**
  - 🔴 **Soft:** 압도적 속도 & 접지력, 빠른 마모
  - 🟡 **Medium:** 균형 잡힌 주행 성능
  - ⚪ **Hard:** 느린 속도, 뛰어난 내구성
""")

# HTML5 Canvas 기반 F1 챔피언십 엔진 (AI 경쟁, 타이어 마모, 피트스탑 포함)
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #0b0f19;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            user-select: none;
        }
        #gameContainer {
            position: relative;
            margin-top: 5px;
        }
        canvas {
            border: 3px solid #1e293b;
            border-radius: 12px;
            background-color: #0f172a;
            box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        }
        
        /* F1 Telemetry HUD Overlay */
        .hud-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(8px);
            padding: 10px 18px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            z-index: 5;
        }
        .hud-item {
            font-size: 13px;
            font-weight: 600;
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

        /* Start Setup Overlay */
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

        /* Pit Stop Overlay */
        #pitModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(220, 38, 38, 0.95);
            border: 3px solid #ffffff;
            padding: 20px 30px;
            border-radius: 14px;
            text-align: center;
            z-index: 60;
        }
        #pitModal h3 { margin: 0 0 10px 0; color: white; }
        .btn-compound {
            padding: 8px 15px;
            margin: 4px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
        }

        /* Finish Summary Modal */
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
</head>
<body>

    <div id="gameContainer">
        <!-- Telemetry HUD -->
        <div class="hud-panel">
            <div class="hud-item">🏎️ 순위: <span id="posVal" class="hud-value" style="color:#38bdf8;">1st / 4</span></div>
            <div class="hud-item">🔧 윙 [Space]: <span id="wingBadge" class="badge badge-wing">15°</span></div>
            <div class="hud-item">🛞 타이어: <span id="tireBadge" class="badge badge-medium">MEDIUM</span> <span id="wearVal" class="hud-value">100%</span></div>
            <div class="hud-item">⚡ 속도: <span id="speedVal" class="hud-value">0</span> km/h</div>
            <div class="hud-item">🚩 Lap: <span id="lapVal" class="hud-value">1 / 5</span></div>
            <div class="hud-item">⏱️ 타임: <span id="timeVal" class="hud-value">0.00s</span></div>
        </div>

        <canvas id="raceCanvas" width="880" height="560"></canvas>
        
        <!-- Game Setup Modal -->
        <div id="startModal">
            <h2>🏆 F1 챔피언십 설정</h2>
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
            <button class="btn-start" onclick="initGame()">레이스 스타트!</button>
        </div>

        <!-- Pit Stop Interactive Modal -->
        <div id="pitModal">
            <h3>⛽ PIT STOP! 타이어 교체 선택</h3>
            <p style="font-size:13px; margin-bottom:10px;">교체할 컴파운드를 선택하세요 (3초 소요):</p>
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
const canvas = document.getElementById('raceCanvas');
const ctx = canvas.getContext('2d');

// --- Aerodynamics Tuning Presets ---
const wingPresetAngles = [0, 15, 30, 40];
let wingPresetIndex = 1;
let wingAngle = 15;

// Tire Compounds Specs
const TIRE_SPECS = {
    'SOFT': { speedMult: 1.08, gripMult: 1.25, wearRate: 0.28, color: '#e63946', badgeClass: 'badge-soft' },
    'MEDIUM': { speedMult: 1.00, gripMult: 1.00, wearRate: 0.14, color: '#eab308', badgeClass: 'badge-medium' },
    'HARD': { speedMult: 0.94, gripMult: 0.82, wearRate: 0.06, color: '#94a3b8', badgeClass: 'badge-hard' }
};

let currentTire = 'MEDIUM';
let tireWear = 100.0; // 0~100%

let keys = {};

// Player Car State
let player = {
    x: 440,
    y: 495,
    angle: 0,
    speed: 0,
    steerAngle: 0,
    lapsCompleted: 0,
    progress: 0,
    inPit: false,
    pitTimer: 0
};

// 3 AI Competitors Setup
let aiCars = [
    { id: 1, name: "Red Bull", color: "#1e3a8a", wingColor: "#f59e0b", x: 440, y: 460, angle: 0, speed: 0, progress: 0, lap: 0, targetIndex: 0, baseSpeed: 7.2 },
    { id: 2, name: "Mercedes", color: "#64748b", wingColor: "#06b6d4", x: 400, y: 460, angle: 0, speed: 0, progress: 0, lap: 0, targetIndex: 0, baseSpeed: 7.0 },
    { id: 3, name: "McLaren", color: "#f97316", wingColor: "#111827", x: 400, y: 495, angle: 0, speed: 0, progress: 0, lap: 0, targetIndex: 0, baseSpeed: 6.8 }
];

// Detailed Circuit Waypoint Way
const outerTrack = [
    {x: 100, y: 460}, {x: 440, y: 460}, {x: 760, y: 460}, {x: 820, y: 390},
    {x: 820, y: 170}, {x: 710, y: 70},  {x: 520, y: 70},  {x: 440, y: 150},
    {x: 360, y: 70},  {x: 160, y: 70},  {x: 60, y: 170},  {x: 60, y: 390}
];

const innerTrack = [
    {x: 140, y: 390}, {x: 440, y: 390}, {x: 720, y: 390}, {x: 750, y: 340},
    {x: 750, y: 200}, {x: 670, y: 130}, {x: 520, y: 130}, {x: 440, y: 210},
    {x: 360, y: 130}, {x: 180, y: 130}, {x: 120, y: 200}, {x: 120, y: 340}
];

// Race Waypoints for AI Pathfinding
const aiWaypoints = [
    {x: 440, y: 480}, {x: 740, y: 480}, {x: 790, y: 430}, {x: 790, y: 200},
    {x: 690, y: 100}, {x: 520, y: 100}, {x: 440, y: 180}, {x: 360, y: 100},
    {x: 170, y: 100}, {x: 90, y: 200},  {x: 90, y: 410},  {x: 150, y: 480}
];

// Race Timing & State
let maxLaps = 5;
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isGameStarted = false;
let isFinished = false;

// Event Listeners
window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," ","KeyW","KeyS","KeyA","KeyD"].includes(e.code)) {
        e.preventDefault();
    }
    if (e.code === 'Space' && !e.repeat && isGameStarted && !isFinished) {
        wingPresetIndex = (wingPresetIndex + 1) % wingPresetAngles.length;
        wingAngle = wingPresetAngles[wingPresetIndex];
        document.getElementById('wingBadge').innerText = wingAngle + '°';
    }
    keys[e.code] = true;
});
window.addEventListener('keyup', e => keys[e.code] = false);

function initGame() {
    maxLaps = parseInt(document.getElementById('selectLaps').value);
    currentTire = document.getElementById('selectTire').value;
    updateTireUI();

    document.getElementById('startModal').style.display = 'none';
    document.getElementById('lapVal').innerText = `1 / ${maxLaps}`;

    isGameStarted = true;
    lapStartTime = Date.now();
}

function updateTireUI() {
    const spec = TIRE_SPECS[currentTire];
    const badge = document.getElementById('tireBadge');
    badge.innerText = currentTire;
    badge.className = `badge ${spec.badgeClass}`;
}

function isPointInPoly(poly, pt) {
    let c = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        if (((poly[i].y > pt.y) !== (poly[j].y > pt.y)) &&
            (pt.x < (poly[j].x - poly[i].x) * (pt.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)) {
            c = !c;
        }
    }
    return c;
}

function checkOnTrack(x, y) {
    const inOuter = isPointInPoly(outerTrack, {x, y});
    const inInner = isPointInPoly(innerTrack, {x, y});
    return inOuter && !inInner;
}

function updatePhysics() {
    if (!isGameStarted || isFinished) return;

    // Pit Stop Frozen Logic
    if (player.inPit) {
        player.speed *= 0.8;
        return;
    }

    const spec = TIRE_SPECS[currentTire];
    
    // Tire wear penalty (Below 30% wear degrades performance)
    const wearGripPenalty = tireWear < 30 ? (tireWear / 30) : 1.0;
    
    // Aerodynamics + Tire Trade-Off
    const baseMaxSpeed = (9.4 - (wingAngle / 40) * 3.2) * spec.speedMult * wearGripPenalty;
    const gripFactor = (0.022 + (wingAngle / 40) * 0.028) * spec.gripMult * wearGripPenalty;

    // Throttle & Braking Controls
    if (keys['ArrowUp'] || keys['KeyW']) {
        player.speed += 0.12;
    } else if (keys['ArrowDown'] || keys['KeyS']) {
        player.speed -= 0.18;
    } else {
        player.speed *= 0.985;
    }

    // Speed Limits
    if (player.speed > baseMaxSpeed) player.speed = baseMaxSpeed;
    if (player.speed < -baseMaxSpeed * 0.3) player.speed = -baseMaxSpeed * 0.3;

    // Steering Smooth Inertia
    const steerTarget = (keys['ArrowLeft'] || keys['KeyA']) ? -1 : ((keys['ArrowRight'] || keys['KeyD']) ? 1 : 0);
    player.steerAngle += (steerTarget - player.steerAngle) * 0.15;

    if (Math.abs(player.speed) > 0.2) {
        const dir = player.speed > 0 ? 1 : -1;
        player.angle += player.steerAngle * gripFactor * dir;
    }

    // Tire Wear Reduction calculation
    if (Math.abs(player.speed) > 0.5) {
        tireWear -= spec.wearRate * (1 + Math.abs(player.steerAngle) * 0.5) * 0.1;
        if (tireWear < 0) tireWear = 0;
    }

    // Off-Track Grass Drag Penalty
    const onTrack = checkOnTrack(player.x, player.y);
    if (!onTrack) {
        player.speed *= 0.88;
    }

    // Movement Translation
    player.x += Math.cos(player.angle) * player.speed;
    player.y += Math.sin(player.angle) * player.speed;

    // Check Pit Stop Area Entrance (Pit Lane Box: x ~ 400-500, y ~ 500-530)
    if (player.x > 380 && player.x < 480 && player.y > 500 && player.y < 535 && !player.inPit) {
        player.inPit = true;
        document.getElementById('pitModal').style.display = 'block';
    }

    // Checkpoint & Lap Logic
    if (player.y < 150 && player.x > 380 && player.x < 520) {
        checkpointPassed = true;
    }

    // Crossing Finish Line (x ~ 440, y ~ 460~530)
    if (checkpointPassed && player.x > 430 && player.x < 450 && player.y > 450 && player.y < 535) {
        const now = Date.now();
        const lapTime = (now - lapStartTime) / 1000;
        lapTimes.push(lapTime);
        
        checkpointPassed = false;
        lapStartTime = now;
        player.lapsCompleted++;

        if (player.lapsCompleted < maxLaps) {
            document.getElementById('lapVal').innerText = `${player.lapsCompleted + 1} / ${maxLaps}`;
        } else {
            isFinished = true;
            showSummaryModal();
        }
    }

    // --- AI Competitors Movement Logic ---
    aiCars.forEach(ai => {
        const target = aiWaypoints[ai.targetIndex];
        const dx = target.x - ai.x;
        const dy = target.y - ai.y;
        const targetAngle = Math.atan2(dy, dx);
        
        // AI Steering toward waypoint
        let angleDiff = targetAngle - ai.angle;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        
        ai.angle += angleDiff * 0.1;
        ai.speed = ai.baseSpeed;
        
        ai.x += Math.cos(ai.angle) * ai.speed;
        ai.y += Math.sin(ai.angle) * ai.speed;

        const dist = Math.hypot(dx, dy);
        if (dist < 40) {
            ai.targetIndex = (ai.targetIndex + 1) % aiWaypoints.length;
            if (ai.targetIndex === 0) ai.lap++;
        }
    });

    // Rank Calculation (Standings)
    calculateStandings();

    // Telemetry UI Updates
    document.getElementById('speedVal').innerText = Math.round(Math.abs(player.speed) * 35);
    document.getElementById('wearVal').innerText = `${Math.round(tireWear)}%`;
    if (!isFinished) {
        const currentLapTimer = ((Date.now() - lapStartTime) / 1000).toFixed(2);
        document.getElementById('timeVal').innerText = `${currentLapTimer}s`;
    }
}

function calculateStandings() {
    const allCars = [
        { name: "Player", lap: player.lapsCompleted, progress: getTrackProgress(player), isPlayer: true },
        ...aiCars.map(ai => ({ name: ai.name, lap: ai.lap, progress: ai.targetIndex, isPlayer: false }))
    ];

    allCars.sort((a, b) => (b.lap * 100 + b.progress) - (a.lap * 100 + a.progress));
    
    const rank = allCars.findIndex(c => c.isPlayer) + 1;
    const rankSuffix = rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th';
    document.getElementById('posVal').innerText = `${rank}${rankSuffix} / 4`;
}

function getTrackProgress(pt) {
    let minDist = Infinity;
    let closestIdx = 0;
    aiWaypoints.forEach((wp, idx) => {
        const d = Math.hypot(wp.x - pt.x, wp.y - pt.y);
        if (d < minDist) {
            minDist = d;
            closestIdx = idx;
        }
    });
    return closestIdx;
}

function changeTire(newCompound) {
    currentTire = newCompound;
    tireWear = 100.0;
    updateTireUI();

    setTimeout(() => {
        player.inPit = false;
        document.getElementById('pitModal').style.display = 'none';
    }, 1500); // 1.5sec Pit stop delay
}

function drawTrack() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Gravel Runoff Areas (Sand Traps)
    ctx.fillStyle = '#c29b62';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 2. Red/White Kerb Border Line
    ctx.beginPath();
    ctx.moveTo(outerTrack[0].x, outerTrack[0].y);
    for (let i = 1; i < outerTrack.length; i++) ctx.lineTo(outerTrack[i].x, outerTrack[i].y);
    ctx.closePath();
    ctx.fillStyle = '#dc2626';
    ctx.fill();

    // 3. Dark Asphalt Track Surface
    ctx.beginPath();
    ctx.moveTo(outerTrack[0].x, outerTrack[0].y);
    for (let i = 1; i < outerTrack.length; i++) ctx.lineTo(outerTrack[i].x, outerTrack[i].y);
    ctx.closePath();
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();

    ctx.fillStyle = '#1e293b';
    ctx.fill();

    // 4. Inner Grass Island
    ctx.beginPath();
    ctx.moveTo(innerTrack[0].x, innerTrack[0].y);
    for (let i = 1; i < innerTrack.length; i++) ctx.lineTo(innerTrack[i].x, innerTrack[i].y);
    ctx.closePath();
    ctx.fillStyle = '#15803d';
    ctx.fill();
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#dc2626';
    ctx.stroke();

    // 5. Pit Lane & Pit Box Surface (Orange Line)
    ctx.fillStyle = '#ea580c';
    ctx.fillRect(380, 505, 100, 30);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px sans-serif';
    ctx.fillText('PIT BOX', 405, 525);

    // 6. Start/Finish Line Stripe
    ctx.save();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 8;
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(440, 390);
    ctx.lineTo(440, 460);
    ctx.stroke();
    ctx.restore();
}

function drawCars() {
    // Draw AI Competitors
    aiCars.forEach(ai => {
        ctx.save();
        ctx.translate(ai.x, ai.y);
        ctx.rotate(ai.angle);

        ctx.fillStyle = ai.color;
        ctx.fillRect(-13, -6, 26, 12);

        // AI Rear Wing
        ctx.fillStyle = ai.wingColor;
        ctx.fillRect(-15, -7, 4, 14);

        // Wheels
        ctx.fillStyle = '#000';
        ctx.fillRect(4, -8, 6, 3);
        ctx.fillRect(4, 5, 6, 3);
        ctx.fillRect(-10, -8, 6, 3);
        ctx.fillRect(-10, 5, 6, 3);

        ctx.restore();
    });

    // Draw Player Car
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.rotate(player.angle);

    // Shadow
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(-15, -9, 32, 18);

    // Player F1 Chassis (Red Bull Red)
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-14, -6, 28, 12);

    // Cockpit
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(-2, -4, 10, 8);

    // Front Wing
    ctx.fillStyle = '#111';
    ctx.fillRect(12, -9, 4, 18);

    // Adjustable Rear Wing
    const wingWidth = 3 + (wingAngle / 40) * 5;
    ctx.fillStyle = '#f59e0b';
    ctx.fillRect(-16, -8, wingWidth, 16);

    // Wheels (Color matches Tire Compound)
    ctx.fillStyle = TIRE_SPECS[currentTire].color;
    ctx.fillRect(4, -9, 7, 3);
    ctx.fillRect(4, 6, 7, 3);
    ctx.fillRect(-11, -9, 7, 3);
    ctx.fillRect(-11, 6, 7, 3);

    ctx.restore();
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

function gameLoop() {
    updatePhysics();
    drawTrack();
    drawCars();
    requestAnimationFrame(gameLoop);
}

// Start Engine Loop
gameLoop();

</script>
</body>
</html>
"""

# Streamlit Component Render
components.html(game_html, height=620)
