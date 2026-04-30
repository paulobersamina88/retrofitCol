import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Column Retrofit Design App", layout="wide")

st.title("Column Retrofit Design and Repair by Added Jacket / Enlarged Section")
st.caption("Retrofit design for existing RC column carrying additional beam tributary load")

# --------------------------------------------------
# DESIGN CRITERIA
# --------------------------------------------------
st.header("DESIGN CRITERIA")

st.markdown("""
1. This retrofit method checks whether an existing reinforced concrete column can safely carry additional gravity load from a beam tributary length.
2. If the existing column is inadequate, an enlarged RC jacket section is designed to increase axial and bending capacity.
3. The design compares:
   - Existing column capacity
   - Required demand from existing load + added beam load
   - Retrofitted column capacity
4. This app is for preliminary engineering evaluation and teaching purposes only. Final design must be verified using applicable code provisions.
""")

# --------------------------------------------------
# INPUT DATA
# --------------------------------------------------
st.header("INPUT DATA")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Column Geometry")
    b = st.number_input("Existing column width b (mm)", value=300.0)
    h = st.number_input("Existing column depth h (mm)", value=300.0)
    height = st.number_input("Column unsupported height (m)", value=3.0)
    cover = st.number_input("Concrete cover (mm)", value=40.0)

with col2:
    st.subheader("Material Properties")
    fc = st.number_input("Concrete strength f'c (MPa)", value=21.0)
    fy = st.number_input("Steel yield strength fy (MPa)", value=415.0)
    Es = st.number_input("Steel modulus Es (MPa)", value=200000.0)
    phi = st.number_input("Strength reduction factor ϕ", value=0.65)

with col3:
    st.subheader("Existing Reinforcement")
    bar_dia = st.number_input("Existing main bar diameter (mm)", value=16.0)
    n_bars = st.number_input("Number of existing bars", value=8, step=1)
    tie_dia = st.number_input("Tie diameter (mm)", value=10.0)
    tie_spacing = st.number_input("Tie spacing (mm)", value=150.0)

st.divider()

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("Existing Load")
    Pu_existing = st.number_input("Existing axial load Pu existing (kN)", value=650.0)
    Mu_existing = st.number_input("Existing moment Mu existing (kN-m)", value=35.0)

with col5:
    st.subheader("Additional Beam Load")
    tributary_length = st.number_input("Beam tributary length carried by column (m)", value=4.0)
    beam_dead_load = st.number_input("Additional beam dead load wD (kN/m)", value=18.0)
    beam_live_load = st.number_input("Additional beam live load wL (kN/m)", value=8.0)

with col6:
    st.subheader("Load Combination")
    DL_factor = st.number_input("Dead load factor", value=1.2)
    LL_factor = st.number_input("Live load factor", value=1.6)
    eccentricity = st.number_input("Load eccentricity from column center (mm)", value=50.0)

# --------------------------------------------------
# RETROFIT INPUT
# --------------------------------------------------
st.header("RETROFIT SECTION INPUT")

col7, col8, col9 = st.columns(3)

with col7:
    jacket_thickness = st.number_input("RC jacket thickness each side (mm)", value=100.0)
    new_bar_dia = st.number_input("New jacket bar diameter (mm)", value=20.0)

with col8:
    new_bars = st.number_input("Number of added jacket bars", value=8, step=1)
    jacket_fc = st.number_input("Jacket concrete strength f'c jacket (MPa)", value=28.0)

with col9:
    jacket_fy = st.number_input("Jacket steel yield strength fy jacket (MPa)", value=415.0)
    confinement_factor = st.number_input("Confinement / composite action factor", value=0.85)

# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------
Ag_existing = b * h
As_existing = n_bars * (np.pi * bar_dia**2 / 4)

b_new = b + 2 * jacket_thickness
h_new = h + 2 * jacket_thickness

Ag_retrofit = b_new * h_new
As_added = new_bars * (np.pi * new_bar_dia**2 / 4)
As_total = As_existing + As_added

# Additional load from beam
P_add_service = (beam_dead_load + beam_live_load) * tributary_length
P_add_ultimate = (DL_factor * beam_dead_load + LL_factor * beam_live_load) * tributary_length

Pu_total = Pu_existing + P_add_ultimate

Mu_add = P_add_ultimate * (eccentricity / 1000)
Mu_total = Mu_existing + Mu_add

# Axial capacity approximation
Pn_existing = 0.85 * fc * (Ag_existing - As_existing) / 1000 + fy * As_existing / 1000
phiPn_existing = phi * Pn_existing

Pn_retrofit = (
    0.85 * jacket_fc * (Ag_retrofit - As_total) / 1000
    + jacket_fy * As_total / 1000
) * confinement_factor

phiPn_retrofit = phi * Pn_retrofit

# Simplified moment capacity estimate
d_existing = h - cover - tie_dia - bar_dia / 2
Mn_existing = As_existing * fy * (d_existing - h / 2) / 1_000_000
phiMn_existing = phi * Mn_existing

d_retrofit = h_new - cover - tie_dia - new_bar_dia / 2
Mn_retrofit = As_total * jacket_fy * (d_retrofit - h_new / 2) / 1_000_000
phiMn_retrofit = phi * Mn_retrofit

# Demand capacity ratio
DCR_P_existing = Pu_total / phiPn_existing if phiPn_existing > 0 else 999
DCR_M_existing = Mu_total / phiMn_existing if phiMn_existing > 0 else 999

DCR_P_retrofit = Pu_total / phiPn_retrofit if phiPn_retrofit > 0 else 999
DCR_M_retrofit = Mu_total / phiMn_retrofit if phiMn_retrofit > 0 else 999

status_existing = "PASS" if DCR_P_existing <= 1 and DCR_M_existing <= 1 else "FAIL"
status_retrofit = "PASS" if DCR_P_retrofit <= 1 and DCR_M_retrofit <= 1 else "FAIL"

# --------------------------------------------------
# DIAGRAM
# --------------------------------------------------
st.header("COLUMN RETROFIT SCHEMATIC")

fig, ax = plt.subplots(figsize=(6, 6))

# Existing column
rect1 = plt.Rectangle(
    (-b / 2, -h / 2),
    b,
    h,
    fill=False,
    linewidth=2,
    label="Existing Column"
)

# Retrofitted jacket
rect2 = plt.Rectangle(
    (-b_new / 2, -h_new / 2),
    b_new,
    h_new,
    fill=False,
    linestyle="--",
    linewidth=2,
    label="RC Jacket"
)

ax.add_patch(rect2)
ax.add_patch(rect1)

# bars existing
r = min(b, h) * 0.35
for i in range(int(n_bars)):
    angle = 2 * np.pi * i / int(n_bars)
    ax.plot(r * np.cos(angle), r * np.sin(angle), "o")

# added bars
r2 = min(b_new, h_new) * 0.40
for i in range(int(new_bars)):
    angle = 2 * np.pi * i / int(new_bars)
    ax.plot(r2 * np.cos(angle), r2 * np.sin(angle), "s")

ax.set_aspect("equal")
ax.set_title("Existing Column with Added RC Jacket")
ax.set_xlabel("Width direction, mm")
ax.set_ylabel("Depth direction, mm")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --------------------------------------------------
# DESIGN SUMMARY TABLES
# --------------------------------------------------
st.header("ANALYSIS & DESIGN SUMMARY")

st.subheader("Load Summary")

load_df = pd.DataFrame({
    "Item": [
        "Existing axial load",
        "Additional service load from beam",
        "Additional factored load from beam",
        "Total factored axial demand",
        "Additional moment from eccentricity",
        "Total factored moment demand"
    ],
    "Value": [
        Pu_existing,
        P_add_service,
        P_add_ultimate,
        Pu_total,
        Mu_add,
        Mu_total
    ],
    "Unit": [
        "kN",
        "kN",
        "kN",
        "kN",
        "kN-m",
        "kN-m"
    ]
})

st.dataframe(load_df, use_container_width=True)

st.subheader("Section Properties")

section_df = pd.DataFrame({
    "Section": ["Existing Column", "Retrofitted Column"],
    "b (mm)": [b, b_new],
    "h (mm)": [h, h_new],
    "Ag (mm²)": [Ag_existing, Ag_retrofit],
    "As total (mm²)": [As_existing, As_total],
    "Concrete f'c (MPa)": [fc, jacket_fc],
    "Steel fy (MPa)": [fy, jacket_fy]
})

st.dataframe(section_df, use_container_width=True)

st.subheader("Capacity Check")

capacity_df = pd.DataFrame({
    "Check": [
        "Existing axial capacity",
        "Existing moment capacity",
        "Retrofitted axial capacity",
        "Retrofitted moment capacity"
    ],
    "Demand": [
        Pu_total,
        Mu_total,
        Pu_total,
        Mu_total
    ],
    "Capacity": [
        phiPn_existing,
        phiMn_existing,
        phiPn_retrofit,
        phiMn_retrofit
    ],
    "DCR": [
        DCR_P_existing,
        DCR_M_existing,
        DCR_P_retrofit,
        DCR_M_retrofit
    ],
    "Status": [
        "PASS" if DCR_P_existing <= 1 else "FAIL",
        "PASS" if DCR_M_existing <= 1 else "FAIL",
        "PASS" if DCR_P_retrofit <= 1 else "FAIL",
        "PASS" if DCR_M_retrofit <= 1 else "FAIL"
    ]
})

st.dataframe(capacity_df, use_container_width=True)

# --------------------------------------------------
# FINAL DESIGN RESULT
# --------------------------------------------------
st.header("FINAL DESIGN RESULT")

colA, colB = st.columns(2)

with colA:
    st.subheader("Existing Column")
    if status_existing == "PASS":
        st.success("Existing column is adequate for the additional beam load.")
    else:
        st.error("Existing column is NOT adequate. Retrofit is required.")

with colB:
    st.subheader("Retrofitted Column")
    if status_retrofit == "PASS":
        st.success("Retrofitted column is adequate.")
    else:
        st.error("Retrofitted column is still not adequate. Increase jacket size, concrete strength, or added reinforcement.")

st.subheader("Recommended Retrofit Description")

st.markdown(f"""
Provide reinforced concrete jacketing around the existing column with a minimum jacket thickness of **{jacket_thickness:.0f} mm** on all sides, resulting in a final column size of **{b_new:.0f} mm × {h_new:.0f} mm**.  
Provide **{int(new_bars)} - {new_bar_dia:.0f} mm diameter** additional longitudinal bars with adequate ties, dowels, surface roughening, bonding agent, and shear connectors to ensure composite action between the existing column and the new jacket.
""")

# --------------------------------------------------
# EXPORTABLE REPORT TEXT
# --------------------------------------------------
st.header("REPORT FORMAT")

report = f"""
COLUMN RETROFIT DESIGN SUMMARY

1. Existing Column Size:
   b = {b:.0f} mm
   h = {h:.0f} mm

2. Retrofitted Column Size:
   b = {b_new:.0f} mm
   h = {h_new:.0f} mm

3. Load Demand:
   Existing axial load = {Pu_existing:.2f} kN
   Additional factored beam load = {P_add_ultimate:.2f} kN
   Total factored axial load = {Pu_total:.2f} kN
   Total factored moment = {Mu_total:.2f} kN-m

4. Existing Column Capacity:
   ϕPn = {phiPn_existing:.2f} kN
   ϕMn = {phiMn_existing:.2f} kN-m
   Status = {status_existing}

5. Retrofitted Column Capacity:
   ϕPn = {phiPn_retrofit:.2f} kN
   ϕMn = {phiMn_retrofit:.2f} kN-m
   Status = {status_retrofit}

6. Recommendation:
   Use RC jacketing with {jacket_thickness:.0f} mm thickness each side and provide {int(new_bars)} additional {new_bar_dia:.0f} mm diameter bars.
"""

st.text_area("Copy-ready design report", report, height=350)

st.download_button(
    label="Download Design Report",
    data=report,
    file_name="column_retrofit_design_summary.txt",
    mime="text/plain"
)
