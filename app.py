"""
FPGA Traffic Light Controller — Streamlit Visualization Dashboard
-------------------------------------------------------------------
This is a SOFTWARE VISUALIZATION of the FSM implemented in Verilog
(rtl/traffic_light_controller.v). It mirrors the same state machine,
state names, and timing (10s GREEN / 2s YELLOW) so the behavior shown
here matches the RTL waveform exactly.

Extra logic not in the base RTL (clearly separated):
 - Pedestrian request -> forces an all-red safety state + WALK signal
 - Emergency override  -> forces the FSM to flash red on both directions

NOTE: This dashboard is a real-time *behavioral* model in Python for
demo/portfolio purposes. The authoritative, hardware-verified design
is the Verilog RTL + testbench in /rtl and /tb.
"""

import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="FPGA Traffic Light Controller", page_icon="🚦", layout="centered")

# ----------------------------------------------------------------
# FSM CONSTANTS — must match rtl/traffic_light_controller.v exactly
# ----------------------------------------------------------------
GREEN_TIME = 10   # seconds, matches localparam GREEN_TIME
YELLOW_TIME = 2    # seconds, matches localparam YELLOW_TIME
PED_TIME = 6     # seconds, extra state not in base RTL
EMERGENCY_FLASH_PERIOD = 0.5  # seconds, flash rate during emergency

STATES = ["S0_NS_GREEN", "S1_NS_YELLOW", "S2_EW_GREEN", "S3_EW_YELLOW"]
STATE_DURATIONS = {
    "S0_NS_GREEN": GREEN_TIME,
    "S1_NS_YELLOW": YELLOW_TIME,
    "S2_EW_GREEN": GREEN_TIME,
    "S3_EW_YELLOW": YELLOW_TIME,
}
NEXT_STATE = {
    "S0_NS_GREEN": "S1_NS_YELLOW",
    "S1_NS_YELLOW": "S2_EW_GREEN",
    "S2_EW_GREEN": "S3_EW_YELLOW",
    "S3_EW_YELLOW": "S0_NS_GREEN",
}

# ----------------------------------------------------------------
# SESSION STATE INIT (acts as our "registers")
# ----------------------------------------------------------------
def init_state():
    if "current_state" not in st.session_state:
        st.session_state.current_state = "S0_NS_GREEN"
        st.session_state.sec_in_state = 0
        st.session_state.last_tick = time.time()
        st.session_state.mode = "NORMAL"          # NORMAL | PEDESTRIAN | EMERGENCY
        st.session_state.ped_requested = False
        st.session_state.emergency_active = False
        st.session_state.flash_on = True
        st.session_state.log = []
        st.session_state.running = True

init_state()

def log_event(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.insert(0, f"[{ts}] {msg}")
    st.session_state.log = st.session_state.log[:12]  # keep last 12

# ----------------------------------------------------------------
# OUTPUT DECODE (mirrors the Verilog output-decode always block)
# ----------------------------------------------------------------
def get_outputs(state, mode, flash_on):
    out = {"ns_red": 0, "ns_yellow": 0, "ns_green": 0,
           "ew_red": 0, "ew_yellow": 0, "ew_green": 0, "ped_walk": 0}

    if mode == "EMERGENCY":
        # Flashing red both directions, no green ever
        if flash_on:
            out["ns_red"] = 1
            out["ew_red"] = 1
        return out

    if mode == "PEDESTRIAN":
        out["ns_red"] = 1
        out["ew_red"] = 1
        out["ped_walk"] = 1
        return out

    # NORMAL mode — matches RTL exactly
    if state == "S0_NS_GREEN":
        out["ns_green"] = 1; out["ew_red"] = 1
    elif state == "S1_NS_YELLOW":
        out["ns_yellow"] = 1; out["ew_red"] = 1
    elif state == "S2_EW_GREEN":
        out["ns_red"] = 1; out["ew_green"] = 1
    elif state == "S3_EW_YELLOW":
        out["ns_red"] = 1; out["ew_yellow"] = 1

    return out

# ----------------------------------------------------------------
# FSM TICK LOGIC (runs once per rerun, simulates one "clock tick")
# ----------------------------------------------------------------
def fsm_tick():
    now = time.time()
    elapsed = now - st.session_state.last_tick

    if elapsed < 1.0:
        return  # only advance once per simulated second

    st.session_state.last_tick = now

    # ---- EMERGENCY mode: just flash, ignore normal FSM ----
    if st.session_state.mode == "EMERGENCY":
        st.session_state.flash_on = not st.session_state.flash_on
        return

    # ---- PEDESTRIAN mode: count down walk timer ----
    if st.session_state.mode == "PEDESTRIAN":
        st.session_state.sec_in_state += 1
        if st.session_state.sec_in_state >= PED_TIME:
            st.session_state.mode = "NORMAL"
            st.session_state.sec_in_state = 0
            st.session_state.ped_requested = False
            log_event("Pedestrian phase ended -> resuming NORMAL")
        return

    # ---- NORMAL mode: standard FSM progression ----
    st.session_state.sec_in_state += 1
    duration = STATE_DURATIONS[st.session_state.current_state]

    if st.session_state.sec_in_state >= duration:
        # Check pedestrian request only at a safe boundary (end of a state)
        if st.session_state.ped_requested:
            st.session_state.mode = "PEDESTRIAN"
            st.session_state.sec_in_state = 0
            log_event("Pedestrian request granted -> all-red WALK phase")
            return

        old = st.session_state.current_state
        st.session_state.current_state = NEXT_STATE[old]
        st.session_state.sec_in_state = 0
        log_event(f"State transition: {old} -> {st.session_state.current_state}")

# ----------------------------------------------------------------
# UI
# ----------------------------------------------------------------
st.title("🚦 FPGA Traffic Light Controller")
st.caption("Real-time behavioral visualization of the Verilog FSM (rtl/traffic_light_controller.v)")

with st.expander("ℹ️ About this dashboard", expanded=False):
    st.markdown("""
    This is a **software visualization** of the hardware FSM — built to demo the
    exact same state machine, state names, and timing as the Verilog RTL.

    - **Base FSM (NORMAL mode):** 4 states, 10s GREEN / 2s YELLOW — identical to RTL
    - **Pedestrian mode:** extra logic not in the base RTL — forces all-red + WALK
    - **Emergency mode:** extra logic not in the base RTL — flashing red override

    The authoritative, hardware-verified design lives in `/rtl` and `/tb` (Verilog).
    This Streamlit app is the demo/interaction layer for the GitHub portfolio.
    """)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🚶 Request Pedestrian Crossing", disabled=(st.session_state.mode != "NORMAL")):
        st.session_state.ped_requested = True
        log_event("Pedestrian button pressed (will trigger at next safe state boundary)")
with col2:
    if st.session_state.mode != "EMERGENCY":
        if st.button("🚨 Trigger Emergency Override"):
            st.session_state.mode = "EMERGENCY"
            st.session_state.emergency_active = True
            log_event("EMERGENCY override activated — flashing red")
    else:
        if st.button("✅ Clear Emergency"):
            st.session_state.mode = "NORMAL"
            st.session_state.emergency_active = False
            st.session_state.sec_in_state = 0
            log_event("Emergency cleared -> resuming NORMAL FSM")
with col3:
    if st.button("🔄 Reset FSM"):
        st.session_state.current_state = "S0_NS_GREEN"
        st.session_state.sec_in_state = 0
        st.session_state.mode = "NORMAL"
        st.session_state.ped_requested = False
        st.session_state.emergency_active = False
        st.session_state.log = []
        log_event("FSM reset -> S0_NS_GREEN")

st.divider()

# Run one FSM tick per rerun
fsm_tick()
outputs = get_outputs(st.session_state.current_state, st.session_state.mode, st.session_state.flash_on)

# ---------------- Status bar ----------------
mode_label = {"NORMAL": "🟢 NORMAL", "PEDESTRIAN": "🚶 PEDESTRIAN PHASE", "EMERGENCY": "🚨 EMERGENCY OVERRIDE"}
st.subheader(f"Mode: {mode_label[st.session_state.mode]}")

if st.session_state.mode == "NORMAL":
    duration = STATE_DURATIONS[st.session_state.current_state]
    remaining = max(duration - st.session_state.sec_in_state, 0)
    st.write(f"**Current state:** `{st.session_state.current_state}`  |  **Time remaining:** {remaining}s")
    st.progress(min(st.session_state.sec_in_state / duration, 1.0))
elif st.session_state.mode == "PEDESTRIAN":
    remaining = max(PED_TIME - st.session_state.sec_in_state, 0)
    st.write(f"**WALK signal active**  |  **Time remaining:** {remaining}s")
    st.progress(min(st.session_state.sec_in_state / PED_TIME, 1.0))
else:
    st.write("All directions flashing **RED**. Emergency vehicle has right of way.")

# ---------------- Light rendering ----------------
def light_html(red, yellow, green, label):
    def circle(on, color):
        bg = color if on else "#222"
        glow = f"box-shadow: 0 0 20px {color};" if on else ""
        return f"<div style='width:50px;height:50px;border-radius:50%;background:{bg};{glow}margin:4px auto;'></div>"

    return f"""
    <div style='text-align:center;'>
        <div style='font-weight:600;margin-bottom:6px;'>{label}</div>
        <div style='background:#111;padding:10px;border-radius:12px;display:inline-block;'>
            {circle(red, '#ff3b30')}
            {circle(yellow, '#ffcc00')}
            {circle(green, '#34c759')}
        </div>
    </div>
    """

lc1, lc2 = st.columns(2)
with lc1:
    st.markdown(light_html(outputs["ns_red"], outputs["ns_yellow"], outputs["ns_green"], "North–South"),
                unsafe_allow_html=True)
with lc2:
    st.markdown(light_html(outputs["ew_red"], outputs["ew_yellow"], outputs["ew_green"], "East–West"),
                unsafe_allow_html=True)

if outputs["ped_walk"]:
    st.success("🚶 WALK signal: ON")

st.divider()

# ---------------- Output table (mirrors RTL output table) ----------------
with st.expander("📋 Raw output signals (mirrors RTL port values)"):
    st.code(
        "\n".join([f"{k:10s} = {v}" for k, v in outputs.items()]),
        language="text"
    )

# ---------------- Event log ----------------
st.subheader("Event Log")
if st.session_state.log:
    st.code("\n".join(st.session_state.log), language="text")
else:
    st.caption("No events yet.")

st.divider()
st.caption("This dashboard mirrors rtl/traffic_light_controller.v. "
           "See /tb for the testbench and /waveforms for simulation proof.")

# ---------------- Auto-refresh loop ----------------
time.sleep(1)
st.rerun()