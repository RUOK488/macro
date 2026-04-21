import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import base64

# Page configuration
st.set_page_config(
    page_title="Advanced India Power Plant Planner", 
    layout="wide",
    page_icon="⚡"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
    }
    .highlight {
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">⚡ Advanced India Power Plant Planning System</h1>', unsafe_allow_html=True)
st.markdown("### Professional Grade Cost-Benefit Analysis with GIS Integration")

# Sidebar
st.sidebar.markdown("## 🎛️ Control Panel")
st.sidebar.markdown("---")

# Currency selection
currency = st.sidebar.selectbox("💰 Currency", ["INR (₹)", "USD ($)"])
usd_to_inr = 83.5

# Advanced India dataset with district-level data
india_data = pd.DataFrame({
    'State': ['Rajasthan', 'Rajasthan', 'Rajasthan', 'Gujarat', 'Gujarat', 'Tamil Nadu', 'Tamil Nadu', 
              'Maharashtra', 'Karnataka', 'Madhya Pradesh', 'Uttar Pradesh', 'Andhra Pradesh', 
              'Telangana', 'Punjab', 'Kerala', 'West Bengal', 'Odisha', 'Bihar', 'Haryana'],
    'District': ['Jodhpur', 'Jaisalmer', 'Bikaner', 'Kutch', 'Patan', 'Ramanathapuram', 'Tirunelveli',
                 'Solapur', 'Kolar', 'Neemuch', 'Jhansi', 'Anantapur', 'Mahabubnagar', 'Fazilka',
                 'Palakkad', 'Purulia', 'Sundargarh', 'Bhagalpur', 'Sirsa'],
    'Latitude': [26.28, 26.91, 28.02, 23.65, 23.85, 9.38, 8.73, 17.68, 13.13, 24.47, 25.45, 14.68, 16.73, 30.40, 10.77, 23.33, 22.12, 25.25, 29.53],
    'Longitude': [73.02, 70.92, 73.31, 69.65, 71.88, 78.76, 77.70, 75.92, 78.13, 74.86, 78.56, 77.58, 78.00, 74.02, 76.65, 86.39, 84.08, 86.97, 75.03],
    'Solar_Irradiance_kWh_m2': [2100, 2300, 2200, 2150, 2050, 1950, 2000, 1850, 1900, 2050, 1800, 1950, 1850, 1750, 1700, 1650, 1750, 1650, 1800],
    'Wind_Speed_ms': [6.5, 7.2, 6.8, 8.5, 7.5, 7.8, 8.2, 5.8, 6.2, 5.5, 4.8, 6.5, 5.5, 5.0, 4.5, 4.2, 5.2, 4.0, 5.5],
    'Land_Cost_per_Acre_INR': [800000, 600000, 700000, 500000, 650000, 1200000, 1100000, 1500000, 1800000, 900000, 1200000, 1000000, 1300000, 1800000, 2000000, 1500000, 950000, 1100000, 1700000],
    'Grid_Connectivity': ['High', 'Medium', 'High', 'High', 'Medium', 'High', 'Medium', 'High', 'High', 'Medium', 'Medium', 'High', 'High', 'High', 'Medium', 'Low', 'Medium', 'Low', 'High'],
    'Evacuation_Infrastructure': ['Good', 'Average', 'Good', 'Excellent', 'Average', 'Good', 'Average', 'Good', 'Good', 'Average', 'Average', 'Good', 'Good', 'Good', 'Average', 'Poor', 'Average', 'Poor', 'Good']
})

# Create advanced map
m = folium.Map(location=[22.5, 78.5], zoom_start=5, tiles="OpenStreetMap")

# Add different marker colors based on solar potential
for idx, row in india_data.iterrows():
    solar_potential = row['Solar_Irradiance_kWh_m2']
    if solar_potential > 2100:
        color = 'darkgreen'
    elif solar_potential > 1900:
        color = 'green'
    elif solar_potential > 1700:
        color = 'orange'
    else:
        color = 'red'
    
    # Create detailed popup HTML
    popup_html = f"""
    <div style="font-family: Arial; width: 250px;">
        <b>📍 {row['District']}, {row['State']}</b><br>
        <hr style="margin: 5px 0;">
        ☀️ Solar Irradiance: {row['Solar_Irradiance_kWh_m2']} kWh/m²/year<br>
        💨 Wind Speed: {row['Wind_Speed_ms']} m/s<br>
        🏔️ Land Cost: ₹{row['Land_Cost_per_Acre_INR']:,}/acre<br>
        ⚡ Grid Connectivity: {row['Grid_Connectivity']}<br>
        🛣️ Evacuation: {row['Evacuation_Infrastructure']}
    </div>
    """
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['District']}, {row['State']} - {solar_potential} kWh/m²",
        color=color,
        fill=True,
        fill_opacity=0.7,
        icon=folium.Icon(color=color, icon='bolt', prefix='fa')
    ).add_to(m)

# Add heat map layer for solar intensity
from folium.plugins import HeatMap
heat_data = [[row['Latitude'], row['Longitude'], row['Solar_Irradiance_kWh_m2']/1000] for idx, row in india_data.iterrows()]
HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)

# Add fullscreen button
folium.plugins.Fullscreen().add_to(m)

# Display map
st.subheader("🗺️ Interactive GIS Map of India - Click on Any Location")
col1, col2 = st.columns([2, 1])

with col1:
    map_data = st_folium(m, width=700, height=500, key="india_map")

with col2:
    st.markdown("### 📌 Map Legend")
    st.markdown("🟢 **Green** - Excellent Solar Potential (>2100 kWh/m²)")
    st.markdown("🟠 **Orange** - Good Solar Potential (1700-1900 kWh/m²)")
    st.markdown("🔴 **Red** - Moderate Solar Potential (<1700 kWh/m²)")
    st.markdown("---")
    st.markdown("### 📊 Data Source")
    st.markdown("- Solar data: NREL/TERI")
    st.markdown("- Wind data: NIWE")
    st.markdown("- Land costs: Industry survey 2025")

# Advanced calculation function
def advanced_calculation(plant_type, capacity_mw, district_data, include_carbon_credits=True):
    """Advanced economic calculation with carbon credits and sensitivity"""
    
    # Base parameters
    solar_irradiance = district_data['Solar_Irradiance_kWh_m2']
    wind_speed = district_data['Wind_Speed_ms']
    land_cost = district_data['Land_Cost_per_Acre_INR']
    grid_score = 1.0 if district_data['Grid_Connectivity'] == 'High' else (0.7 if district_data['Grid_Connectivity'] == 'Medium' else 0.4)
    
    # Plant-specific calculations
    if plant_type == "Solar PV":
        capital_cost_per_mw_usd = 650000 - (solar_irradiance - 1700) * 50
        capital_cost_per_mw_usd = max(550000, min(750000, capital_cost_per_mw_usd))
        
        efficiency = 0.18 + (solar_irradiance - 1700) * 0.00005
        efficiency = min(0.22, efficiency)
        
        capacity_factor = 0.16 + (solar_irradiance - 1700) * 0.0001
        capacity_factor = min(0.23, capacity_factor)
        
        degradation = 0.005  # 0.5% per year
        
    elif plant_type == "Wind":
        capital_cost_per_mw_usd = 900000 - (wind_speed - 5) * 30000
        capital_cost_per_mw_usd = max(750000, min(1050000, capital_cost_per_mw_usd))
        
        efficiency = 0.35 + (wind_speed - 5) * 0.02
        efficiency = min(0.45, efficiency)
        
        capacity_factor = 0.25 + (wind_speed - 5) * 0.03
        capacity_factor = min(0.40, capacity_factor)
        
        degradation = 0.002  # 0.2% per year
        
    else:  # Hybrid
        capital_cost_per_mw_usd = 800000
        efficiency = 0.30
        capacity_factor = 0.30
        degradation = 0.003
    
    # Land requirement (approx 5 acres per MW for solar, 2 for wind)
    if plant_type == "Solar PV":
        land_required_acres = capacity_mw * 4
    elif plant_type == "Wind":
        land_required_acres = capacity_mw * 1.5
    else:
        land_required_acres = capacity_mw * 2.5
    
    land_cost_total_inr = land_required_acres * land_cost
    land_cost_total_usd = land_cost_total_inr / usd_to_inr
    
    # Capital cost calculation
    capital_cost_usd = capacity_mw * capital_cost_per_mw_usd + land_cost_total_usd
    capital_cost_inr = capital_cost_usd * usd_to_inr
    
    # Annual O&M (2% of capital cost for solar, 3% for wind)
    om_percent = 0.02 if plant_type == "Solar PV" else 0.03
    annual_om_usd = capital_cost_usd * om_percent
    annual_om_inr = annual_om_usd * usd_to_inr
    
    # Energy generation
    hours_per_year = 8760
    annual_energy_mwh = capacity_mw * capacity_factor * hours_per_year
    annual_energy_kwh = annual_energy_mwh * 1000
    
    # Revenue calculations
    electricity_price_usd = 0.085  # $/kWh
    annual_revenue_usd = annual_energy_kwh * electricity_price_usd
    annual_revenue_inr = annual_revenue_usd * usd_to_inr
    
    # Carbon credits (if enabled)
    carbon_credit_usd_per_ton = 50  # Market price
    co2_avoided_tons = annual_energy_mwh * 0.4  # 0.4 tons CO2/MWh avoided
    
    if include_carbon_credits:
        carbon_revenue_usd = co2_avoided_tons * carbon_credit_usd_per_ton
        carbon_revenue_inr = carbon_revenue_usd * usd_to_inr
    else:
        carbon_revenue_usd = 0
        carbon_revenue_inr = 0
    
    total_annual_revenue_usd = annual_revenue_usd + carbon_revenue_usd
    total_annual_revenue_inr = annual_revenue_inr + carbon_revenue_inr
    
    # Profit and payback
    annual_profit_usd = total_annual_revenue_usd - annual_om_usd
    annual_profit_inr = annual_profit_usd * usd_to_inr
    
    payback_years = capital_cost_usd / annual_profit_usd if annual_profit_usd > 0 else 999
    
    # Lifetime analysis (25 years with degradation)
    lifetime_years = 25
    total_revenue_usd = 0
    total_om_usd = 0
    
    for year in range(lifetime_years):
        current_efficiency = (1 - degradation) ** year
        current_energy = annual_energy_kwh * current_efficiency
        current_revenue = current_energy * electricity_price_usd
        if include_carbon_credits:
            current_revenue += co2_avoided_tons * carbon_credit_usd_per_ton * current_efficiency
        
        total_revenue_usd += current_revenue
        total_om_usd += annual_om_usd * (1 + 0.02) ** year  # 2% annual increase in O&M
    
    total_profit_usd = total_revenue_usd - total_om_usd - capital_cost_usd
    total_profit_inr = total_profit_usd * usd_to_inr
    roi_percent = (total_profit_usd / capital_cost_usd) * 100
    
    # Levelized Cost of Energy (LCOE)
    lcoe_usd = (capital_cost_usd + total_om_usd) / (annual_energy_kwh * lifetime_years)
    lcoe_inr = lcoe_usd * usd_to_inr
    
    # Grid connectivity impact
    grid_adjustment = (grid_score - 0.7) * 0.2
    final_roi = roi_percent * (1 + grid_adjustment)
    
    return {
        'Capital Cost (USD)': f"${capital_cost_usd:,.0f}",
        'Capital Cost (INR)': f"₹{capital_cost_inr:,.0f}",
        'Land Cost (INR)': f"₹{land_cost_total_inr:,.0f}",
        'Land Required': f"{land_required_acres:.1f} acres",
        'Annual O&M (USD)': f"${annual_om_usd:,.0f}",
        'Annual Energy': f"{annual_energy_mwh:,.0f} MWh",
        'Annual Revenue (USD)': f"${annual_revenue_usd:,.0f}",
        'Carbon Credit Revenue': f"${carbon_revenue_usd:,.0f}",
        'Total Annual Revenue': f"${total_annual_revenue_usd:,.0f}",
        'Annual Profit (USD)': f"${annual_profit_usd:,.0f}",
        'Payback Period': f"{payback_years:.1f} years",
        'ROI (25 years)': f"{final_roi:.0f}%",
        'Total Profit (25 yrs)': f"${total_profit_usd:,.0f}",
        'LCOE': f"${lcoe_usd:.03f}/kWh",
        'CO2 Avoided/year': f"{co2_avoided_tons:,.0f} tons",
        'Capacity Factor': f"{capacity_factor * 100:.1f}%",
        'System Efficiency': f"{efficiency * 100:.1f}%",
        'Grid Score': f"{grid_score * 100:.0f}%"
    }

# Main input section
col1, col2, col3 = st.columns(3)

with col1:
    plant_type = st.selectbox("🏭 Power Plant Type", ["Solar PV", "Wind", "Hybrid (Solar+Wind)"])
    
with col2:
    capacity_mw = st.slider("⚡ Plant Capacity (MW)", 1, 1000, 100, 10)
    
with col3:
    include_carbon = st.checkbox("🌿 Include Carbon Credits", value=True)

# District selection
st.subheader("📍 Select Location for Analysis")
district_list = [f"{row['District']}, {row['State']}" for idx, row in india_data.iterrows()]
selected_location = st.selectbox("Choose District", district_list)

# Get selected district data
selected_row = india_data[district_list.index(selected_location)]
district_name = selected_row['District']
state_name = selected_row['State']

# Advanced analysis tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Economic Analysis", "📈 Sensitivity Analysis", "🌍 Environmental Impact", "📑 Export Report"])

with tab1:
    # Run calculation
    results = advanced_calculation(plant_type, capacity_mw, selected_row, include_carbon)
    
    st.markdown(f"## 📍 Analysis for {district_name}, {state_name}")
    st.markdown(f"### 🏭 {capacity_mw} MW {plant_type} Power Plant")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Capital Investment", results['Capital Cost (INR)'])
        st.metric("⏱️ Payback Period", results['Payback Period'])
    
    with col2:
        st.metric("📈 Annual Profit", results['Annual Profit (USD)'])
        st.metric("🎯 ROI", results['ROI (25 years)'])
    
    with col3:
        st.metric("⚡ Annual Energy", results['Annual Energy'])
        st.metric("💵 LCOE", results['LCOE'])
    
    with col4:
        st.metric("🌿 CO2 Avoided", results['CO2 Avoided/year'])
        st.metric("🏔️ Land Required", results['Land Required'])
    
    # Detailed results table
    st.markdown("### 📋 Detailed Breakdown")
    results_df = pd.DataFrame(list(results.items()), columns=['Parameter', 'Value'])
    st.dataframe(results_df, use_container_width=True)

with tab2:
    st.markdown("### 📈 Sensitivity Analysis - How Parameters Affect ROI")
    
    # Sensitivity sliders
    col1, col2 = st.columns(2)
    
    with col1:
        elec_price_var = st.slider("Electricity Price Variation (%)", 50, 150, 100, 10)
        capex_var = st.slider("Capital Cost Variation (%)", 70, 130, 100, 10)
    
    with col2:
        opex_var = st.slider("O&M Cost Variation (%)", 70, 130, 100, 10)
        degradation_var = st.slider("Degradation Rate Variation (%)", 50, 200, 100, 10)
    
    # Calculate sensitivity scenarios
    scenarios = []
    base_roi = float(results['ROI (25 years)'].replace('%', ''))
    
    for elec in [80, 100, 120]:
        for capex in [80, 100, 120]:
            adjusted_roi = base_roi * (elec/100) / (capex/100)
            scenarios.append({
                'Electricity Price': f"{elec}%",
                'Capital Cost': f"{capex}%",
                'ROI': f"{adjusted_roi:.0f}%"
            })
    
    sensitivity_df = pd.DataFrame(scenarios)
    st.dataframe(sensitivity_df, use_container_width=True)
    
    # Create heatmap
    st.markdown("#### ROI Heat Map")
    heatmap_data = []
    for elec in [80, 100, 120]:
        row = []
        for capex in [80, 100, 120]:
            adjusted_roi = base_roi * (elec/100) / (capex/100)
            row.append(adjusted_roi)
        heatmap_data.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=['80% Capex', '100% Capex', '120% Capex'],
        y=['80% Price', '100% Price', '120% Price'],
        colorscale='RdYlGn',
        text=[[f"{val:.0f}%" for val in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 12}
    ))
    fig.update_layout(title="ROI Sensitivity Heat Map", height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🌍 Environmental Impact Assessment")
    
    co2_tons = float(results['CO2 Avoided/year'].replace(' tons', '').replace(',', ''))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🌿 CO2 Avoided per Year", f"{co2_tons:,.0f} tons")
        st.metric("🌳 Equivalent Trees Planted", f"{co2_tons * 45:,.0f}")
        st.metric("🚗 Cars Off Road", f"{co2_tons // 4.6:,.0f}")
    
    with col2:
        st.metric("💡 Homes Powered", f"{int(capacity_mw * 1000):,.0f}")
        st.metric("🏭 Coal Plants Replaced", f"{capacity_mw / 500:.1f}")
        st.metric("🛢️ Oil Saved (barrels/year)", f"{co2_tons // 0.43:,.0f}")
    
    # Environmental timeline
    years = list(range(1, 26))
    cumulative_co2 = [co2_tons * y for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=cumulative_co2, mode='lines+markers', 
                              name='Cumulative CO2 Savings', fill='tozeroy'))
    fig.update_layout(title="Cumulative CO2 Savings Over Plant Lifetime",
                      xaxis_title="Years", yaxis_title="CO2 Avoided (tons)")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 📑 Generate Project Report")
    
    report_data = {
        'Project Name': f"{capacity_mw} MW {plant_type} Plant at {district_name}, {state_name}",
        'Analysis Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Capital Investment (INR)': results['Capital Cost (INR)'],
        'Annual Energy Generation': results['Annual Energy'],
        'Annual Profit': results['Annual Profit (USD)'],
        'Payback Period': results['Payback Period'],
        'ROI': results['ROI (25 years)'],
        'CO2 Avoided per Year': results['CO2 Avoided/year'],
        'LCOE': results['LCOE']
    }
    
    st.json(report_data)
    
    # Download button
    report_json = json.dumps(report_data, indent=2)
    b64 = base64.b64encode(report_json.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="power_plant_report.json">📥 Download Report (JSON)</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    st.info("📌 Recommendation based on analysis:\n" + 
            ("✅ Highly viable - Consider immediate investment" if float(results['ROI (25 years)'].replace('%', '')) > 100
             else "📌 Moderately viable - Consider with incentives" if float(results['ROI (25 years)'].replace('%', '')) > 50
             else "⚠️ Not recommended - Consider alternative location/technology"))

# Comparison chart across top locations
st.markdown("---")
st.subheader("🏆 Top 5 Locations for Your Plant Type")

# Calculate top locations
top_locations = []
for idx, row in india_data.iterrows():
    temp_result = advanced_calculation(plant_type, capacity_mw, row, include_carbon)
    top_locations.append({
        'Location': f"{row['District']}, {row['State']}",
        'ROI': float(temp_result['ROI (25 years)'].replace('%', '')),
        'Payback': float(temp_result['Payback Period'].replace(' years', ''))
    })

top_df = pd.DataFrame(top_locations).sort_values('ROI', ascending=False).head(5)

fig = px.bar(top_df, x='Location', y='ROI', title="Top 5 Locations by ROI",
             color='ROI', color_continuous_scale='Viridis')
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("⚡ **Advanced Power Plant Planning System v2.0** | Data sources: NREL, TERI, MNRE, NIWE | For educational purposes")