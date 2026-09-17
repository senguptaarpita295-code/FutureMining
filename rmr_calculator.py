"""🪨 Bieniawski Rock Mass Rating (RMR) Geotechnical Calculator
Native module engineered for FutureMining.
"""

from __future__ import annotations

import streamlit as st


# ============================================================
# CALCULATION FUNCTIONS
# ============================================================

def calc_r1(test_type: str, strength: float) -> int:
    """Parameter 1: Strength of Intact Rock (Max 15)"""
    if "Point Load" in test_type:
        if strength > 10:
            return 15
        elif 4 <= strength <= 10:
            return 12
        elif 2 <= strength < 4:
            return 7
        elif 1 <= strength < 2:
            return 4
        else:
            return 0
    else:  # UCS
        if strength > 250:
            return 15
        elif 100 <= strength <= 250:
            return 12
        elif 50 <= strength < 100:
            return 7
        elif 25 <= strength < 50:
            return 4
        elif 5 <= strength < 25:
            return 2
        elif 1 <= strength < 5:
            return 1
        else:
            return 0


def calc_r2(rqd: float) -> int:
    """Parameter 2: Rock Quality Designation (Max 20)"""
    if rqd >= 90:
        return 20
    elif rqd >= 75:
        return 17
    elif rqd >= 50:
        return 13
    elif rqd >= 25:
        return 8
    else:
        return 5


def calc_r3(spacing_mm: float) -> int:
    """Parameter 3: Spacing of Discontinuities (Max 20)"""
    if spacing_mm > 2000:
        return 20
    elif spacing_mm >= 600:
        return 15
    elif spacing_mm >= 200:
        return 10
    elif spacing_mm >= 60:
        return 8
    else:
        return 5


def calc_r4_length(length_m: float) -> int:
    if length_m < 1:
        return 6
    elif length_m < 3:
        return 4
    elif length_m < 10:
        return 2
    elif length_m <= 20:
        return 1
    else:
        return 0


def calc_r4_separation(sep_mm: float) -> int:
    if sep_mm <= 0:
        return 6
    elif sep_mm < 0.1:
        return 5
    elif sep_mm <= 1.0:
        return 4
    elif sep_mm <= 5.0:
        return 1
    else:
        return 0


def calc_r4_infill(infill_type: str, thick: float) -> int:
    if infill_type == "None":
        return 6
    elif "Hard" in infill_type:
        return 4 if thick < 5 else 2
    elif "Soft" in infill_type:
        return 2 if thick < 5 else 0
    return 6


ROUGHNESS_SCORES = {
    "Very rough": 6,
    "Rough": 5,
    "Slightly rough": 3,
    "Smooth": 1,
    "Slickensided": 0,
}

WEATHERING_SCORES = {
    "Unweathered": 6,
    "Slightly weathered": 5,
    "Moderately weathered": 3,
    "Highly weathered": 1,
    "Decomposed": 0,
}

ORIENTATION_ADJUSTMENTS = {
    "Tunnels": {
        "Very favorable": 0,
        "Favorable": -2,
        "Fair": -5,
        "Unfavorable": -10,
        "Very unfavorable": -12,
    },
    "Foundations": {
        "Very favorable": 0,
        "Favorable": -2,
        "Fair": -7,
        "Unfavorable": -15,
        "Very unfavorable": -25,
    },
    "Slopes": {
        "Very favorable": 0,
        "Favorable": -5,
        "Fair": -25,
        "Unfavorable": -50,
        "Very unfavorable": -60,
    },
}


def get_rock_class(score: float) -> tuple[str, str, str, str]:
    if score >= 81:
        return "Class I", "Very Good Rock", "#22c55e", "20 yr for 15m span · Cohesion > 400 kPa · Friction > 45°"
    elif score >= 61:
        return "Class II", "Good Rock", "#38bdf8", "1 yr for 10m span · Cohesion 300–400 kPa · Friction 35°–45°"
    elif score >= 41:
        return "Class III", "Fair Rock", "#f59e0b", "1 week for 5m span · Cohesion 200–300 kPa · Friction 25°–35°"
    elif score >= 21:
        return "Class IV", "Poor Rock", "#f97316", "10 hr for 2.5m span · Cohesion 100–200 kPa · Friction 15°–25°"
    else:
        return "Class V", "Very Poor Rock", "#ef4444", "30 min for 1m span · Cohesion < 100 kPa · Friction < 15°"


# ============================================================
# RENDER PAGE
# ============================================================

def render_rmr_calculator(light: bool = False):
    """Render full-featured RMR Geotechnical Calculator."""

    card_bg = "#ffffff" if light else "rgba(15, 23, 42, 0.75)"
    card_border = "#e2e8f0" if light else "rgba(51, 65, 85, 0.7)"
    text_muted = "#64748b" if light else "#94a3b8"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {'#f8fafc, #e2e8f0' if light else '#1e293b, #0f172a'}); padding: 1.25rem 1.5rem; border-radius: 14px; margin-bottom: 1.25rem; border: 1px solid {card_border};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="color: {'#0f172a' if light else '#38bdf8'}; margin: 0 0 0.35rem 0; font-size: 1.55rem;">🪨 Bieniawski Rock Mass Rating (RMR) Calculator</h2>
                    <p style="color: {text_muted}; margin: 0; font-size: 0.92rem;">
                        Standardized Rock Mass Classification System (Bieniawski 1973/1989) for tunnels, slopes, and foundations.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_calc, tab_replit, tab_theory = st.tabs([
        "🧮 Native Interactive Calculator",
        "🌐 Sagar Pal's RMR Web App",
        "📖 GATE Mining Theory & Reference",
    ])

    # ========================================================
    # TAB 1: NATIVE CALCULATOR
    # ========================================================
    with tab_calc:
        col_inputs, col_results = st.columns([1.75, 1.25], gap="large")

        with col_inputs:
            st.markdown("##### 1️⃣ Strength of Intact Rock")
            s_type = st.radio("Strength Test Type", ["Uniaxial Compressive Strength (UCS)", "Point Load Index Is(50)"], horizontal=True)
            if "Point Load" in s_type:
                s_val = st.number_input("Point Load Index Is(50) (MPa)", min_value=0.0, max_value=50.0, value=6.0, step=0.5)
            else:
                s_val = st.number_input("Uniaxial Compressive Strength (MPa)", min_value=0.0, max_value=500.0, value=120.0, step=5.0)
            r1 = calc_r1(s_type, s_val)
            st.caption(f"Rating R1 = **{r1} / 15** points")

            st.divider()

            st.markdown("##### 2️⃣ Rock Quality Designation (RQD)")
            rqd_val = st.slider("RQD Percentage (%)", min_value=0, max_value=100, value=80, step=1)
            r2 = calc_r2(rqd_val)
            st.caption(f"Rating R2 = **{r2} / 20** points")

            st.divider()

            st.markdown("##### 3️⃣ Spacing of Discontinuities")
            sp_val = st.number_input("Discontinuity Spacing (mm)", min_value=1.0, max_value=5000.0, value=450.0, step=25.0)
            r3 = calc_r3(sp_val)
            st.caption(f"Rating R3 = **{r3} / 20** points")

            st.divider()

            st.markdown("##### 4️⃣ Condition of Discontinuities (Max 30)")
            c_len = st.number_input("Discontinuity Length / Persistence (m)", min_value=0.1, max_value=50.0, value=3.5, step=0.5)
            r4_l = calc_r4_length(c_len)

            c_sep = st.number_input("Separation / Aperture (mm)", min_value=0.0, max_value=20.0, value=0.5, step=0.1)
            r4_s = calc_r4_separation(c_sep)

            c_rough = st.selectbox("Joint Roughness", list(ROUGHNESS_SCORES.keys()), index=1)
            r4_r = ROUGHNESS_SCORES[c_rough]

            c_infill = st.selectbox("Infilling / Gouge", ["None", "Hard filling (<5 mm)", "Hard filling (>=5 mm)", "Soft filling (<5 mm)", "Soft filling (>=5 mm)"], index=0)
            c_thick = 0.0
            if c_infill != "None":
                c_thick = st.number_input("Filling Thickness (mm)", min_value=0.1, max_value=50.0, value=3.0, step=0.5)
            r4_i = calc_r4_infill(c_infill, c_thick)

            c_weather = st.selectbox("Joint Weathering", list(WEATHERING_SCORES.keys()), index=1)
            r4_w = WEATHERING_SCORES[c_weather]

            r4 = r4_l + r4_s + r4_r + r4_i + r4_w
            st.caption(f"Rating R4 = **{r4} / 30** (Length: {r4_l}, Sep: {r4_s}, Rough: {r4_r}, Infill: {r4_i}, Weathering: {r4_w})")

            st.divider()

            st.markdown("##### 5️⃣ Groundwater Condition (Max 15)")
            gw_type = st.radio("Groundwater Evaluation Type", ["General Inflow Conditions", "Inflow Rate (L/min per 10m tunnel)", "Joint Water Pressure Ratio (pw / σ1)"])
            if gw_type == "General Inflow Conditions":
                gw_cond = st.selectbox("Condition", ["Completely dry", "Damp", "Wet", "Dripping", "Flowing"], index=0)
                gw_val = 0.0
            elif "Inflow" in gw_type:
                gw_val = st.number_input("Inflow (L/min per 10m)", min_value=0.0, max_value=500.0, value=5.0, step=1.0)
                gw_cond = ""
            else:
                gw_val = st.number_input("pw / σ1 Ratio", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
                gw_cond = ""

            if gw_type == "General Inflow Conditions":
                r5 = {"Completely dry": 15, "Damp": 10, "Wet": 7, "Dripping": 4, "Flowing": 0}.get(gw_cond, 15)
            elif "Inflow" in gw_type:
                r5 = 15 if gw_val == 0 else (10 if gw_val < 10 else (7 if gw_val <= 25 else (4 if gw_val <= 125 else 0)))
            else:
                r5 = 15 if gw_val == 0 else (10 if gw_val <= 0.1 else (7 if gw_val <= 0.2 else (4 if gw_val <= 0.5 else 0)))

            st.caption(f"Rating R5 = **{r5} / 15** points")

            st.divider()

            st.markdown("##### 6️⃣ Discontinuity Orientation Adjustment")
            st_col1, st_col2 = st.columns(2)
            with st_col1:
                structure = st.selectbox("Structure Application", ["Tunnels", "Foundations", "Slopes"])
            with st_col2:
                favorability = st.selectbox("Strike & Dip Orientation", ["Very favorable", "Favorable", "Fair", "Unfavorable", "Very unfavorable"])

            adj = ORIENTATION_ADJUSTMENTS[structure][favorability]
            st.caption(f"Adjustment = **{adj:+d}** points")

        with col_results:
            basic_rmr = r1 + r2 + r3 + r4 + r5
            final_rmr = max(0, basic_rmr + adj)
            cls_code, cls_title, cls_color, cls_desc = get_rock_class(final_rmr)

            st.markdown(
                f"""
                <div style="background: {card_bg}; border: 2px solid {cls_color}; border-radius: 14px; padding: 1.5rem; text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.12em; color: {text_muted};">Final Adjusted RMR</div>
                    <div style="font-size: 3.5rem; font-weight: 800; color: {cls_color}; line-height: 1.1; margin: 0.35rem 0;">{final_rmr}</div>
                    <div style="font-size: 0.88rem; color: {text_muted}; margin-bottom: 0.85rem;">out of 100</div>
                    <div style="display: inline-block; background: {cls_color}22; border: 1px solid {cls_color}; padding: 0.35rem 1rem; border-radius: 20px; font-weight: 700; color: {cls_color}; font-size: 1.05rem;">
                        {cls_code} · {cls_title}
                    </div>
                    <div style="margin-top: 1rem; font-size: 0.8rem; color: {text_muted}; line-height: 1.4;">
                        {cls_desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                st.markdown("##### 📊 Rating Ledger Breakdown")
                st.write(f"• **R1 (Intact Strength):** `{r1} / 15`")
                st.write(f"• **R2 (RQD):** `{r2} / 20`")
                st.write(f"• **R3 (Joint Spacing):** `{r3} / 20`")
                st.write(f"• **R4 (Joint Condition):** `{r4} / 30`")
                st.write(f"• **R5 (Groundwater):** `{r5} / 15`")
                st.markdown("---")
                st.write(f"**Basic RMR:** `{basic_rmr} / 100`")
                st.write(f"**Orientation Adjustment:** `{adj:+d}`")
                st.markdown(f"### **Final RMR:** `{final_rmr}`")

            st.link_button(
                "🌐 Open Sagar Pal's Web App in New Tab ↗",
                url="https://rmr-calculator-website--munna44sagarpal.replit.app/",
                use_container_width=True,
                type="primary",
            )

    # ========================================================
    # TAB 2: REPLIT EMBED
    # ========================================================
    with tab_replit:
        st.markdown("""
            <div style="margin-bottom: 0.75rem;">
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">
                    Interactive live view of the standalone React deployment created by Sagar Pal.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.link_button(
            "🌐 Open Standalone Website (Full Screen) ↗",
            url="https://rmr-calculator-website--munna44sagarpal.replit.app/",
            use_container_width=True,
        )

        st.components.v1.iframe(
            "https://rmr-calculator-website--munna44sagarpal.replit.app/",
            height=850,
            scrolling=True,
        )

    # ========================================================
    # TAB 3: GATE THEORY & FORMULAS
    # ========================================================
    with tab_theory:
        st.markdown(r"""
        ### 📚 GATE Mining Engineering — Bieniawski RMR Cheat Sheet

        #### 1. The 5 Basic Parameters
        $$\text{Basic RMR} = R_1 + R_2 + R_3 + R_4 + R_5$$

        * **$R_1$**: Uniaxial Compressive Strength ($\sigma_c$) or Point Load Index ($I_s(50)$) — Max 15
        * **$R_2$**: Rock Quality Designation ($RQD\%$) — Max 20
        * **$R_3$**: Discontinuity Spacing — Max 20
        * **$R_4$**: Discontinuity Condition (Length + Separation + Roughness + Infill + Weathering) — Max 30
        * **$R_5$**: Groundwater Inflow / Joint Water Pressure — Max 15

        #### 2. Adjusted RMR
        $$\text{RMR}_{\text{adjusted}} = \text{Basic RMR} + \text{Adjustment for Discontinuity Orientation}$$

        #### 3. Rock Mass Classes & Stand-Up Times
        | Class | Rating | Description | Stand-Up Time | Cohesion (kPa) | Friction Angle (°) |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **Class I** | 81 – 100 | Very Good Rock | 20 yr for 15m span | > 400 | > 45° |
        | **Class II** | 61 – 80 | Good Rock | 1 yr for 10m span | 300 – 400 | 35° – 45° |
        | **Class III** | 41 – 60 | Fair Rock | 1 week for 5m span | 200 – 300 | 25° – 35° |
        | **Class IV** | 21 – 40 | Poor Rock | 10 hours for 2.5m span | 100 – 200 | 15° – 25° |
        | **Class V** | < 21 | Very Poor Rock | 30 minutes for 1m span | < 100 | < 15° |
        """)
