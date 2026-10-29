import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F1 2D Racing & Spoiler Simulator",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 2D 키보드 레이싱 게임 & 에어로다이나믹스")
st.markdown("""
**[조작 방법]**
- **방향키 위(↑) / 아래(↓):** 가속 / 브레이크 및 후진
- **방향키 좌(←) / 우(→):** 조향 (핸들링)
- **리어 윙 각도 조절:** 아래 슬라이더로 윙 각도를 조절하면 **최고 속도**와 **코너링 접지력**이 실시간으로 변합니다!
""")

# HTML5 Canvas + JS F1 Game Code
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background-color: #1a1a1a;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #gameContainer {
            position: relative;
            margin-top: 10px;
        }
        canvas {
            border: 3px solid #444;
            border-radius: 8px;
            background-color: #2e7d32; /* Track Grass */
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        .ui-panel {
            display: flex;
            gap: 20px;
            background: #2b2b2b;
            padding: 12px 25px;
            border-radius: 10px;
            margin-bottom: 10px;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .ui-item {
            font-size: 16px;
            font-weight: bold;
        }
        .ui-value {
            color: #ffcc00;
        }
        /* Summary Modal Overlay */
        #summaryModal {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(20, 20, 20, 0.95);
            border: 2px solid #ffcc00;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            width: 320px;
            box-shadow: 0 0 30px rgba(255, 204, 0, 0.4);
            z-index: 10;
        }
        #summaryModal h2 { color: #ffcc00; margin-top: 0; }
        .stat-box {
            background: #333;
            margin: 8px 0;
            padding: 10px;
            border-radius: 8px;
            text-align: left;
        }
        .btn-restart {
            background: #ffcc00;
            color: black;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 15px;
        }
        .btn-restart:hover {
            background: #e6b800;
        }
    </style>
</head>
<body>

    <div class="ui-panel">
        <div class="ui-item">🔧 리어 윙 각도: <input type="range" id="wingSlider" min="0" max="40" value="15" oninput="updateWing(this.value)"> <span id="wingVal" class="ui-value">15°</span></div>
        <div class="ui-item">⚡ 속도: <span id="speedVal" class="ui-value">0</span> km/h</div>
        <div class="ui-item">🚩 Current Lap: <span id="lapVal" class="ui-value">1 / 3</span></div>
        <div class="ui-item">⏱️ Time: <span id="timeVal" class="ui-value">0.00s</span></div>
    </div>

    <div id="gameContainer">
        <canvas id="raceCanvas" width="800" height="500"></canvas>
        
        <div id="summaryModal">
            <h2>🏁 레이스 종료!</h2>
            <div class="stat-box">🏆 <b>최단 랩타임 (Best):</b> <span id="bestLap" style="color:#4caf50;">-</span></div>
            <div class="stat-box">🐢 <b>최장 랩타임 (Worst):</b> <span id="worstLap" style="color:#f44336;">-</span></div>
            <div class="stat-box">📊 <b>랩별 기록:</b><div id="lapHistory" style="font-size:13px; margin-top:5px; color:#aaa;"></div></div>
            <button class="btn-restart" onclick="resetGame()">다시 도전하기</button>
        </div>
    </div>

<script>
const canvas = document.getElementById('raceCanvas');
const ctx = canvas.getContext('2d');

// --- Game Variables ---
let wingAngle = 15;
let keys = {};

// Car State
let car = {
    x: 400,
    y: 430,
    angle: 0, // Radians
    speed: 0,
    accel: 0.15,
    friction: 0.97
};

// Track Parameters (Oval with chicanes)
const outerTrack = [
    {x: 150, y: 470}, {x: 650, y: 470}, {x: 750, y: 370}, 
    {x: 750, y: 130}, {x: 650, y: 30}, {x: 150, y: 30}, 
    {x: 50, y: 130}, {x: 50, y: 370}
];

const innerTrack = [
    {x: 180, y: 390}, {x: 620, y: 390}, {x: 670, y: 320}, 
    {x: 670, y: 180}, {x: 620, y: 110}, {x: 180, y: 110}, 
    {x: 130, y: 180}, {x: 130, y: 320}
];

// Lap & Time Logic
let currentLap = 1;
const maxLaps = 3;
let startTime = Date.now();
let lapStartTime = Date.now();
let lapTimes = [];
let checkpointPassed = false;
let isFinished = false;

// Event Listeners for Keys
window.addEventListener('keydown', e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) {
        e.preventDefault();
    }
    keys[e.key] = true;
});
window.addEventListener('keyup', e => keys[e.key] = false);

function updateWing(val) {
    wingAngle = parseInt(val);
    document.getElementById('wingVal').innerText = val + '°';
}

// Check if point inside polygon
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

function checkTrackBounds(x, y) {
    const inOuter = isPointInPoly(outerTrack, {x, y});
    const inInner = isPointInPoly(innerTrack, {x, y});
    return inOuter && !inInner; // Valid on track if inside outer but outside inner
}

function updatePhysics() {
    if (isFinished) return;

    // Aerodynamics Mechanics: Wing Angle Tradeoff
    // Higher wing angle = Lower top speed (high drag), but higher grip & turning speed
    const maxSpeed = 10 - (wingAngle / 40) * 3.5; // Top Speed: 10 (0°) -> 6.5 (40°)
    const grip = 0.02 + (wingAngle / 40) * 0.035;   // Steering Responsiveness/Grip

    // Acceleration & Braking
    if (keys['ArrowUp']) {
        car.speed += car.accel;
    } else if (keys['ArrowDown']) {
        car.speed -= car.accel * 0.8;
    } else {
        car.speed *= car.friction;
    }

    // Clamp speed based on wing angle
    if (car.speed > maxSpeed) car.speed = maxSpeed;
    if (car.speed < -maxSpeed * 0.3) car.speed = -maxSpeed * 0.3;

    // Off-track penalty (Grass)
    const onTrack = checkTrackBounds(car.x, car.y);
    if (!onTrack) {
        car.speed *= 0.85; // Heavy drag on grass
    }

    // Steering
    if (Math.abs(car.speed) > 0.1) {
        const dir = car.speed > 0 ? 1 : -1;
        if (keys['ArrowLeft']) car.angle -= grip * dir;
        if (keys['ArrowRight']) car.angle += grip * dir;
    }

    // Movement
    car.x += Math.cos(car.angle) * car.speed;
    car.y += Math.sin(car.angle) * car.speed;

    // Checkpoint & Finish Line Logic
    // Halfway Checkpoint (x ~ 400, y ~ 70 top straight)
    if (car.y < 120 && car.x > 300 && car.x < 500) {
        checkpointPassed = true;
    }

    // Finish Line crossing (bottom straight: x ~ 400, y between 390 and 470)
    if (checkpointPassed && car.x > 390 && car.x < 410 && car.y > 390 && car.y < 470) {
        const now = Date.now();
        const lapTime = (now - lapStartTime) / 1000;
        lapTimes.push(lapTime);
        
        checkpointPassed = false;
        lapStartTime = now;
        
        if (currentLap < maxLaps) {
            currentLap++;
            document.getElementById('lapVal').innerText = `${currentLap} / ${maxLaps}`;
        } else {
            // Race Finish
            isFinished = true;
            showSummary();
        }
    }

    // UI Updates
    document.getElementById('speedVal').innerText = Math.round(Math.abs(car.speed) * 32);
    if (!isFinished) {
        const currentLapTimer = ((Date.now() - lapStartTime) / 1000).toFixed(2);
        document.getElementById('timeVal').innerText = `${currentLapTimer}s`;
    }
}

function showSummary() {
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
    car.x = 400;
    car.y = 430;
    car.angle = 0;
    car.speed = 0;
    
    document.getElementById('lapVal').innerText = `1 / ${maxLaps}`;
    document.getElementById('summaryModal').style.display = 'none';
    lapStartTime = Date.now();
}

function drawTrack() {
    // Clear Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Asphalt Track
    ctx.beginPath();
    ctx.moveTo(outerTrack[0].x, outerTrack[0].y);
    for (let i = 1; i < outerTrack.length; i++) ctx.lineTo(outerTrack[i].x, outerTrack[i].y);
    ctx.closePath();
    ctx.fillStyle = '#333';
    ctx.fill();

    // Cut out inner island (Grass)
    ctx.beginPath();
    ctx.moveTo(innerTrack[0].x, innerTrack[0].y);
    for (let i = 1; i < innerTrack.length; i++) ctx.lineTo(innerTrack[i].x, innerTrack[i].y);
    ctx.closePath();
    ctx.fillStyle = '#2e7d32';
    ctx.fill();

    // Start/Finish Line
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 6;
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.moveTo(400, 390);
    ctx.lineTo(400, 470);
    ctx.stroke();
    ctx.setLineDash([]); // Reset dash
}

function drawCar() {
    ctx.save();
    ctx.translate(car.x, car.y);
    ctx.rotate(car.angle);

    // Car Shadow
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(-12, -7, 26, 16);

    // F1 Car Body (Red)
    ctx.fillStyle = '#e63946';
    ctx.fillRect(-12, -5, 24, 10);

    // Front Wing
    ctx.fillStyle = '#111';
    ctx.fillRect(10, -8, 4, 16);

    // Rear Wing (Changes size/style based on wing angle)
    const wingVisualWidth = 2 + (wingAngle / 40) * 4;
    ctx.fillStyle = '#ffcc00';
    ctx.fillRect(-14, -7, wingVisualWidth, 14);

    // Wheels
    ctx.fillStyle = '#000';
    ctx.fillRect(4, -8, 6, 3);
    ctx.fillRect(4, 5, 6, 3);
    ctx.fillRect(-10, -8, 6, 3);
    ctx.fillRect(-10, 5, 6, 3);

    ctx.restore();
}

function gameLoop() {
    updatePhysics();
    drawTrack();
    drawCar();
    requestAnimationFrame(gameLoop);
}

// Start Game Loop
lapStartTime = Date.now();
gameLoop();

</script>
</body>
</html>
"""

# Render Component
components.html(game_html, height=620)
