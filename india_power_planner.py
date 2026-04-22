import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import datetime
import json
import base64
import math

# Page config
st.set_page_config(
    page_title="India Power Plant Planner", 
    layout="wide",
    page_icon="⚡"
)

# Title
st.markdown("""
<h1 style='text-align: center; color: #1E88E5;'>⚡ India Power Plant Planning System</h1>
<p style='text-align: center;'>Click anywhere on the map → Compare Solar, Wind & Gas Turbine</p>
<hr>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## ⚙️ Settings")
st.sidebar.markdown("---")

usd_to_inr = 83.5
capacity_mw = st.sidebar.slider("Plant Capacity (MW)", 1, 500, 100, 10)
include_carbon = st.sidebar.checkbox("🌿 Include Carbon Credits", value=True)
electricity_price = st.sidebar.number_input("Electricity Price ($/kWh)", 0.05, 0.20, 0.085, 0.005)

# India district data
india_data = pd.DataFrame({
    'State': ['Rajasthan', 'Rajasthan', 'Rajasthan', 'Gujarat', 'Gujarat', 'Gujarat', 
              'Tamil Nadu', 'Tamil Nadu', 'Maharashtra', 'Karnataka', 'Madhya Pradesh', 
              'Uttar Pradesh', 'Andhra Pradesh', 'Telangana', 'Punjab', 'Kerala', 
              'West Bengal', 'Odisha', 'Bihar', 'Haryana', 'Ladakh', 'Himachal Pradesh',
              'Uttarakhand', 'Assam', 'Jharkhand', 'Chhattisgarh', 'Delhi', 'Goa'],
    'District': ['Jaisalmer', 'Jodhpur', 'Bikaner', 'Kutch', 'Patan', 'Banaskantha',
                 'Ramanathapuram', 'Tirunelveli', 'Solapur', 'Kolar', 'Neemuch',
                 'Jhansi', 'Anantapur', 'Mahabubnagar', 'Fazilka', 'Palakkad',
                 'Purulia', 'Sundargarh', 'Bhagalpur', 'Sirsa', 'Leh', 'Kullu',
                 'Dehradun', 'Kamrup', 'Ranchi', 'Bilaspur', 'Central Delhi', 'North Goa'],
    'Latitude': [26.91, 26.28, 28.02, 23.65, 23.85, 24.15, 9.38, 8.73, 17.68, 13.13, 24.47,
                 25.45, 14.68, 16.73, 30.40, 10.77, 23.33, 22.12, 25.25, 29.53, 34.15, 31.96,
                 30.32, 26.14, 23.34, 22.08, 28.61, 15.50],
    'Longitude': [70.92, 73.02, 73.31, 69.65, 71.88, 72.95, 78.76, 77.70, 75.92, 78.13, 74.86,
                  78.56, 77.58, 78.00, 74.02, 76.65, 86.39, 84.08, 86.97, 75.03, 77.58, 77.17,
                  78.03, 91.79, 85.33, 82.15, 77.23, 73.83],
    'Solar_GHI': [6.2, 5.8, 5.9, 5.8, 5.5, 5.4, 5.2, 5.3, 5.0, 5.1, 5.5,
                  4.8, 5.2, 5.0, 4.7, 4.5, 4.3, 4.8, 4.5, 4.8, 5.5, 4.8,
                  4.6, 4.4, 4.9, 5.2, 5.0, 5.3],
    'Wind_Speed': [6.8, 6.2, 6.5, 8.5, 7.2, 7.0, 7.8, 8.2, 5.8, 6.2, 5.5,
                   4.8, 6.5, 5.5, 5.0, 4.5, 4.2, 5.2, 4.0, 5.5, 5.5, 4.8,
                   4.5, 4.2, 5.0, 5.2, 4.5, 4.8],
    'Land_Cost': [400000, 600000, 500000, 350000, 500000, 450000, 1200000, 1100000,
                  1500000, 1800000, 800000, 1200000, 1000000, 1300000, 1800000,
                  2000000, 1500000, 950000, 1100000, 1700000, 300000, 800000,
                  1000000, 900000, 1000000, 850000, 25000000, 2500000],
    'Grid_Score': [0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.85, 0.75, 0.80, 0.85, 0.70,
                   0.65, 0.75, 0.70, 0.80, 0.70, 0.55, 0.60, 0.50, 0.75, 0.40, 0.55,
                   0.65, 0.50, 0.60, 0.55, 0.95, 0.85]
})

def calculate_plant(plant_type, capacity, solar, wind, grid_score, land_cost):
    """Calculate economics for all plant types"""
    
    if plant_type == "Solar":
        cf = min(0.24, max(0.11, 0.12 + (solar - 4.0) * 0.035))
        capex_per_mw = min(800000, max(550000, 700000 - (solar - 4.5) * 40000))
        land_per_mw = 4.5
        om_pct = 0.018
        co2_factor = 0.4
    elif plant_type == "Wind":
        cf = min(0.42, max(0.12, 0.12 + (wind - 4.0) * 0.055))
        capex_per_mw = min(1050000, max(800000, 950000 - (wind - 5.0) * 25000))
        land_per_mw = 1.8
        om_pct = 0.025
        co2_factor = 0.4
    else:  # Gas Turbine
        cf = 0.85
        capex_per_mw = 800000
        land_per_mw = 0.5
        om_pct = 0.022
        co2_factor = 0.15
    
    grid_adj = 0.85 + grid_score * 0.15
    land_total = capacity * land_per_mw * land_cost / usd_to_inr
    total_capex = capacity * capex_per_mw * grid_adj + land_total
    total_capex_inr = total_capex * usd_to_inr
    
    annual_energy_mwh = capacity * cf * 8760
    annual_energy_kwh = annual_energy_mwh * 1000
    
    revenue_usd = annual_energy_kwh * electricity_price
    om_usd = total_capex * om_pct
    co2_tons = annual_energy_mwh * co2_factor
    carbon_usd = co2_tons * 50 if include_carbon and plant_type != "Gas" else 0
    
    profit_usd = revenue_usd + carbon_usd - om_usd
    payback = total_capex / profit_usd if profit_usd > 0 else 999
    total_profit_25 = profit_usd * 25
    roi = (total_profit_25 / total_capex) * 100
    lcoe_usd = total_capex / (annual_energy_kwh * 25)
    
    if plant_type == "Solar":
        suitability = min(100, max(0, (solar - 3.5) * 25))
    elif plant_type == "Wind":
        suitability = min(100, max(0, (wind - 3.5) * 20))
    else:
        suitability = 70
    
    return {
        'Plant Type': plant_type,
        'Capital Cost (USD)': f"${total_capex:,.0f}",
        'Capital Cost (INR)': f"₹{total_capex_inr/10000000:.1f} Cr",
        'Annual Energy': f"{annual_energy_mwh:,.0f} MWh",
        'Annual Revenue': f"${revenue_usd:,.0f}",
        'Carbon Credit': f"${carbon_usd:,.0f}",
        'Annual Profit': f"${profit_usd:,.0f}",
        'Payback Period': f"{payback:.1f} years",
        'ROI (25 years)': f"{roi:.0f}%",
        'CO2 Saved/year': f"{co2_tons:,.0f} tons",
        'LCOE': f"${lcoe_usd:.03f}/kWh",
        'Suitability': f"{suitability:.0f}%",
        'Land Required': f"{capacity * land_per_mw:.1f} acres"
    }

# Map creation - FIXED with proper tile sources that don't require attribution
st.subheader("🗺️ Click anywhere on the map")

# Map style selector - Using only map types that work without attribution issues
map_style = st.radio("Map Style", ["Standard", "OpenStreetMap"], horizontal=True)

# Create map - Simple OpenStreetMap (always works)
m = folium.Map(location=[22.5, 78.5], zoom_start=5, control_scale=True)

# Add markers
for idx, row in india_data.iterrows():
    solar = row['Solar_GHI']
    if solar > 5.8:
        color = 'darkgreen'
    elif solar > 5.2:
        color = 'green'
    elif solar > 4.6:
        color = 'orange'
    else:
        color = 'red'
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8,
        popup=f"""
        <b>{row['District']}, {row['State']}</b><br>
        ☀️ Solar: {row['Solar_GHI']} kWh/m²/day<br>
        💨 Wind: {row['Wind_Speed']} m/s<br>
        🏔️ Land: ₹{row['Land_Cost']:,.0f}/acre
        """,
        tooltip=f"{row['District']} - Solar: {row['Solar_GHI']}",
        color=color,
        fill=True,
        fill_opacity=0.7
    ).add_to(m)

# Instruction marker
folium.Marker(
    location=[28.61, 77.23],
    popup="👆 Click anywhere on this map!",
    icon=folium.Icon(color='blue', icon='info-sign')
).add_to(m)

# Display map
col1, col2 = st.columns([2, 1])

with col1:
    map_data = st_folium(m, width=700, height=500, key="map")

with col2:
    st.markdown("### 📌 Map Legend")
    st.markdown("🟢 **Dark Green** - Excellent Solar (>5.8)")
    st.markdown("🟢 **Green** - Good Solar (5.2-5.8)")
    st.markdown("🟠 **Orange** - Moderate (4.6-5.2)")
    st.markdown("🔴 **Red** - Lower (<4.6)")
    st.markdown("---")
    st.markdown(f"**Capacity:** {capacity_mw} MW")
    st.markdown(f"**Carbon Credits:** {'✅ On' if include_carbon else '❌ Off'}")
    st.markdown(f"**Electricity Price:** ${electricity_price}/kWh")

# Location selection
st.markdown("---")
st.subheader("📍 Select Location")

# Initialize variables
selected_location = None
selected_row = None
solar_est = None
wind_est = None

# Check if map was clicked
if map_data and map_data.get('last_clicked'):
    lat = map_data['last_clicked']['lat']
    lng = map_data['last_clicked']['lng']
    st.success(f"📍 Selected coordinates: {lat:.4f}°N, {lng:.4f}°E")
    
    # Find nearest district
    min_dist = float('inf')
    nearest_idx = 0
    for idx, row in india_data.iterrows():
        dist = math.sqrt((lat - row['Latitude'])**2 + (lng - row['Longitude'])**2)
        if dist < min_dist:
            min_dist = dist
            nearest_idx = idx
    
    selected_row = india_data.iloc[nearest_idx]
    selected_location = f"{selected_row['District']}, {selected_row['State']}"
    st.info(f"🏠 Nearest district: {selected_location} ({min_dist * 111:.1f} km away)")
    
    # Estimate resources
    solar_est = selected_row['Solar_GHI'] * (1.0 - abs(lat - 23.5) * 0.02)
    wind_est = selected_row['Wind_Speed'] * (1.2 if abs(lat - 21) < 3 else 1.0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("☀️ Estimated Solar GHI", f"{solar_est:.2f} kWh/m²/day")
    with col2:
        st.metric("💨 Estimated Wind Speed", f"{wind_est:.1f} m/s")
else:
    # Dropdown selection
    location_list = india_data['District'] + ", " + india_data['State']
    selected_location = st.selectbox("Choose a district", location_list.tolist())
    
    # Find the selected row
    for idx, row in india_data.iterrows():
        if f"{row['District']}, {row['State']}" == selected_location:
            selected_row = row
            solar_est = row['Solar_GHI']
            wind_est = row['Wind_Speed']
            break

# Plant type selection
if selected_row is not None:
    st.subheader("🏭 Select Plant Types to Compare")
    plant_options = st.multiselect(
        "Choose plant types",
        ["Solar", "Wind", "Gas Turbine"],
        default=["Solar", "Wind", "Gas Turbine"]
    )
    
    # Calculate results
    if plant_options:
        results = []
        for plant in plant_options:
            result = calculate_plant(
                plant, capacity_mw, solar_est, wind_est, 
                selected_row['Grid_Score'], selected_row['Land_Cost']
            )
            result['Location'] = selected_location
            results.append(result)
        
        # Display results
        st.subheader("📊 Comparison Results")
        results_df = pd.DataFrame(results)
        display_cols = ['Plant Type', 'Capital Cost (INR)', 'Annual Energy', 'Annual Profit', 
                        'Payback Period', 'ROI (25 years)', 'CO2 Saved/year', 'Suitability']
        st.dataframe(results_df[display_cols], use_container_width=True)
        
        # ROI Chart
        fig1 = px.bar(results_df, x='Plant Type', y='ROI (25 years)', 
                      title="Return on Investment (ROI) by Plant Type",
                      color='ROI (25 years)', color_continuous_scale='Viridis',
                      text='ROI (25 years)')
        fig1.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Payback Chart
        fig2 = px.bar(results_df, x='Plant Type', y='Payback Period',
                      title="Payback Period (Years) - Lower is Better",
                      color='Payback Period', color_continuous_scale='Reds_r',
                      text='Payback Period')
        fig2.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
        
        # CO2 Chart
        fig3 = px.bar(results_df, x='Plant Type', y='CO2 Saved/year',
                      title="CO2 Saved per Year (Tons)",
                      color='CO2 Saved/year', color_continuous_scale='Greens',
                      text='CO2 Saved/year')
        fig3.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Capital Cost Chart
        fig4 = px.bar(results_df, x='Plant Type', y='Capital Cost (INR)',
                      title="Capital Investment Required",
                      color='Capital Cost (INR)', color_continuous_scale='Blues',
                      text='Capital Cost (INR)')
        fig4.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)
        
        # Recommendation
        st.subheader("🏆 Recommendation")
        
        roi_values = [float(r['ROI (25 years)'].replace('%', '')) for r in results]
        best_idx = roi_values.index(max(roi_values))
        best = results[best_idx]
        
        if max(roi_values) > 100:
            st.success(f"""
            ### ✅ STRONGLY RECOMMENDED: {best['Plant Type']}
            
            | Metric | Value |
            |--------|-------|
            | **Location** | {best['Location']} |
            | **ROI** | {best['ROI (25 years)']} |
            | **Payback** | {best['Payback Period']} |
            | **CO2 Saved** | {best['CO2 Saved/year']} |
            | **Capital Cost** | {best['Capital Cost (INR)']} |
            
            This is an excellent investment opportunity with strong returns.
            """)
        elif max(roi_values) > 50:
            st.info(f"""
            ### 📌 RECOMMENDED: {best['Plant Type']}
            
            | Metric | Value |
            |--------|-------|
            | **Location** | {best['Location']} |
            | **ROI** | {best['ROI (25 years)']} |
            | **Payback** | {best['Payback Period']} |
            | **CO2 Saved** | {best['CO2 Saved/year']} |
            
            This project offers good returns. Consider government incentives.
            """)
        else:
            st.warning(f"""
            ### ⚠️ CAUTION: {best['Plant Type']}
            
            | Metric | Value |
            |--------|-------|
            | **Location** | {best['Location']} |
            | **ROI** | {best['ROI (25 years)']} |
            | **Payback** | {best['Payback Period']} |
            
            Returns are below target. Consider alternative locations or technologies.
            """)
        
        # Download report
        st.subheader("📑 Export Report")
        
        csv = results_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="power_plant_report.csv">📥 Download CSV Report</a>'
        st.markdown(href, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>📍 Click anywhere on the map → Compare Solar, Wind & Gas Turbine</p>
    <p>Data: Solar GHI (kWh/m²/day), Wind Speed (m/s), Land Cost (₹/acre)</p>
    <p><strong>Best Locations:</strong> Rajasthan (Solar), Gujarat/Kutch (Wind), Anywhere (Gas Turbine)</p>
</div>
""", unsafe_allow_html=True)
