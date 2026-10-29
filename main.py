import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="F1 Aerodynamics Simulator",
    page_icon="🏎️",
    layout="wide"
)

# --- 물리 상구 및 기초 데이터 ---
RHO = 1.225            # 공기 밀도 (kg/m^3)
G = 9.81               # 중력가속도 (m/s^2)
CAR_MASS = 798         # F1 차체 최소 중량 (kg)
FRONTAL_AREA = 1.6     # 전면 투영 면적 (m^2)
TIRE_GRIP = 1.6        # 타이어 마찰 계수 (mu)
ENGINE_POWER = 750000  # 엔진 출력 (W, 약 1000마력)

# --- 서킷별 데이터 ---
CIRCUITS = {
    "몬자 (Monza - 이탈리아)": {
        "desc": "초고속 서킷 (직선 비중 매우 높음)",
        "d_straight": 4800,  # 직선 총 거리 (m)
        "d_corner": 1000,    # 코너 총 거리 (m)
        "r_corner": 120,     # 평균 코너 곡률 반경 (m)
    },
    "스파 (Spa - 벨기에)": {
        "desc": "밸런스형 서킷 (고속 직선 + 중고속 코너)",
        "d_straight": 3800,
        "d_corner": 3200,
        "r_corner": 85,
    },
    "모나코 (Monaco - 모나코)": {
        "desc": "저속/시가지 서킷 (코너 비중 매우 높음)",
        "d_straight": 1200,
        "d_corner": 2137,
        "r_corner": 35,
    }
}

# --- 물리 연산 함수 ---
def calculate_physics(angle_deg, circuit_info):
    """
    날개 각도(0~40도)와 서킷 정보를 받아 
    직선 최고 속도(km/h), 코너 한계 속도(km/h), 예상 랩타임(s), 다운포스/항력 계수를 반환합니다.
    """
    try:
        rad = np.radians(angle_deg)
        
        # 날개 각도에 따른 다운포스(Cl) 및 항력(Cd) 계수 변화
        cl = 1.0 + 1.8 * np.sin(rad)
        cd = 0.6 + 1.2 * (np.sin(rad) ** 2)
        
        # 1. 직선 최고 속도 (m/s -> km/h)
        v_straight_ms = (2 * ENGINE_POWER / (RHO * FRONTAL_AREA * cd)) ** (1/3)
        v_straight_kmh = v_straight_ms * 3.6
        
        # 2. 코너링 한계 속도 (m/s -> km/h)
        r = circuit_info["r_corner"]
        denom = (CAR_MASS / r) - (0.5 * TIRE_GRIP * RHO * FRONTAL_AREA * cl)
        
        if denom <= 0:
            v_corner_ms = v_straight_ms * 0.9
        else:
            v_corner_ms = np.sqrt((TIRE_GRIP * CAR_MASS * G) / denom)
        
        v_corner_ms = min(v_corner_ms, v_straight_ms)
        v_corner_kmh = v_corner_ms * 3.6
        
        # 3. 랩타임 산출 (직선 평균속도는 최고속도의 85%로 계산)
        t_straight = circuit_info["d_straight"] / (v_straight_ms * 0.85)
        t_corner = circuit_info["d_corner"] / v_corner_ms
        total_lap_time = t_straight + t_corner
        
        return v_straight_kmh, v_corner_kmh, total_lap_time, cl, cd
        
    except Exception as e:
        st.error(f"계산 수행 중 오류가 발생했습니다: {e}")
        return 0, 0, 0, 0, 0

# --- UI 레이아웃 ---
st.title("🏎️ F1 에어로다이나믹스 날개 튜닝 시뮬레이터")
st.markdown("서킷 특성에 맞춰 스포일러 각도를 최적화하여 최단의 랩타임을 도출하세요.")

# 사이드바 패널
st.sidebar.header("🔧 튜닝 설정")
selected_circuit_name = st.sidebar.selectbox("1. 서킷 선택", list(CIRCUITS.keys()))
circuit = CIRCUITS[selected_circuit_name]
st.sidebar.info(f"**서킷 특성:** {circuit['desc']}")

wing_angle = st.sidebar.slider(
    "2. 리어 윙 각도 (°)",
    min_value=0,
    max_value=40,
    value=15,
    step=1
)

# 메인 지표 계산
v_straight, v_corner, lap_time, cl, cd = calculate_physics(wing_angle, circuit)

# 주요 지표 출력
col1, col2, col3 = st.columns(3)
col1.metric("직선 최고 속도", f"{v_straight:.1f} km/h")
col2.metric("코너링 한계 속도", f"{v_corner:.1f} km/h")
col3.metric("예상 랩타임", f"{lap_time:.2f} 초")

st.divider()

# 각도별 시뮬레이션 및 최적 각도 산출
st.subheader("📊 각도별 랩타임 그래프 및 최적 '황금 각도'")

angles = np.arange(0, 41, 1)
lap_times = [calculate_physics(a, circuit)[2] for a in angles]

best_angle = angles[np.argmin(lap_times)]
best_lap_time = min(lap_times)

# 그래프 시각화
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(angles, lap_times, color='#E63946', linewidth=2.5, label='Lap Time (s)')
ax.axvline(x=wing_angle, color='gray', linestyle='--', label=f'Current Angle ({wing_angle}°)')
ax.scatter([best_angle], [best_lap_time], color='#FFD166', s=150, zorder=5, label=f'Optimal Angle ({best_angle}°)')

ax.set_xlabel("Wing Angle (°)")
ax.set_ylabel("Lap Time (sec)")
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper right')

st.pyplot(fig)

# 결과 메시지
if wing_angle == best_angle:
    st.success(f"🎯 **최적의 셋업입니다!** {selected_circuit_name}의 황금 각도는 **{best_angle}°**이며, 최적 랩타임은 **{best_lap_time:.2f}초**입니다.")
elif wing_angle < best_angle:
    st.warning(f"⚠️ **다운포스 부족:** 현재 각도({wing_angle}°)는 코너링 속도가 떨어집니다. 각도를 높여 다운포스를 확보하세요. (추천: {best_angle}°)")
else:
    st.info(f"💡 **공기저항 과다:** 현재 각도({wing_angle}°)는 항력이 커 직선 속도가 손실됩니다. 각도를 낮추세요. (추천: {best_angle}°)")

# 원리 설명
with st.expander("🔬 적용된 기계공학 원리 보기"):
    st.markdown("""
    - **유체역학 (Aerodynamics):** 공기저항 항력($F_d = \\frac{1}{2}\\rho v^2 A C_d$)과 차체를 누르는 다운포스($F_l = \\frac{1}{2}\\rho v^2 A C_l$) 트레이드오프 계산
    - **동력학 (Dynamics):** 코너링 시 타이어 마찰력과 원심력의 평형 방정식($\\frac{mv^2}{R} \\le \\mu N$)을 활용한 한계 속도 도출
    """)
