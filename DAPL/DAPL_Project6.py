import streamlit as st
import pandas as pd
import plotly.express as px

# ===== PAGE SETTINGS =====
st.set_page_config(page_title="India Road Accident Dashboard", layout="wide")

# ===== CUSTOM CSS =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: white;
}
.box {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.1);
}
.box:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    background: rgba(255,255,255,0.12);
}
h1, h2, h3 {
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ===== DATA LOADING & CLEANING =====
@st.cache_data
def load_data():
    # 1. Load the file
    df = pd.read_csv('DAPL/road_accidents.csv')
    
    # 2. Clean the rows
    df = df.dropna(subset=['State'])
    df = df[~df['State'].isin(['All India', 'Total', 'Total (All India)'])]
    
    # 3. Clean the numbers (Remove commas and convert to numeric)
    cols_to_fix = ['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    # 4. Fill any remaining NaNs with 0 so math doesn't break
    df = df.fillna(0)
    
    # NOW return the cleaned dataframe
    return df

df = load_data()

# ===== MENU =====
menu = st.radio("", ["Home", "Data", "Visuals", "Analysis", "Insights"], horizontal=True)

# ===== HOME =====
if menu == "Home":
    st.title("Road Accident Analysis Dashboard")

    c1, c2, c3 = st.columns(3)
    total_2023 = int(df['2023 Accidents'].sum())
    avg_2023 = round(df['2023 Accidents'].mean(), 2)
    max_state = df.loc[df['2023 Accidents'].idxmax(), 'State']

    c1.markdown(f"<div class='box'><h3>Total Accidents (2023)</h3><h2>{total_2023:,}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='box'><h3>Avg per State</h3><h2>{avg_2023}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='box'><h3>Highest Risk State</h3><h2>{max_state}</h2></div>", unsafe_allow_html=True)

    st.subheader("National Accident Trend (2019 - 2023)")
    yearly_data = df[['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']].sum()
    
    years = ['2019', '2020', '2021', '2022', '2023']
    fig = px.area(x=years, y=yearly_data.values, 
                  labels={'x': 'Year', 'y': 'Total Accidents'},
                  color_discrete_sequence=['#f87171'])
    fig.update_xaxes(type='category')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ===== DATA =====
elif menu == "Data":
    st.title("The Dataset")
    st.dataframe(df, use_container_width=True)

# ===== VISUALS =====
elif menu == "Visuals":
    st.title("Visual Exploration")
    
    col_a, col_b = st.columns(2)
    with col_a:
        graph_type = st.selectbox("Select Graph Type", 
            ["Bar Chart", "Pie Chart", "Line Trend", "Box Plot", "Histogram", "Sunburst"])
    with col_b:
        year_col = st.selectbox("Select Year", 
            ['2023 Accidents', '2022 Accidents', '2021 Accidents', '2020 Accidents', '2019 Accidents'])

    if graph_type == "Bar Chart":
        # Shows the top 10 most dangerous states
        fig = px.bar(df.nlargest(10, year_col), x='State', y=year_col, 
                     color=year_col, color_continuous_scale='Reds',
                     template="plotly_dark")
    
    elif graph_type == "Pie Chart":
        # Shows market share of accidents
        fig = px.pie(df.nlargest(10, year_col), names='State', values=year_col,
                     hole=0.4, template="plotly_dark")
    
    elif graph_type == "Line Trend":
        # Multi-state comparison over time
        years_list = ['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']
        temp_df = df.melt(id_vars='State', value_vars=years_list, var_name='Year', value_name='Count')
        temp_df['Year'] = temp_df['Year'].str.extract('(\d+)') 
        
        selected = st.multiselect("Select States to Compare", df['State'].unique(), default=df['State'].unique()[:3])
        fig = px.line(temp_df[temp_df['State'].isin(selected)], x='Year', y='Count', 
                      color='State', markers=True, template="plotly_dark")
        fig.update_xaxes(type='category')

    elif graph_type == "Box Plot":
        # Great for showing distribution and outliers
        fig = px.box(df, y=year_col, points="all", hover_data=['State'],
                     color_discrete_sequence=['#f87171'], template="plotly_dark")
        st.info("**Insight:** Outliers (dots far above the box) represent states with disproportionately high accident rates.")

    elif graph_type == "Histogram":
        # Shows the frequency of accident counts
        fig = px.histogram(df, x=year_col, nbins=15, 
                           color_discrete_sequence=['#6366f1'], template="plotly_dark")
        fig.update_layout(bargap=0.1)

    # Final visual polish
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ===== ANALYSIS =====
elif menu == "Analysis":
    st.title("In-Depth Statistical Breakdown")
    
    # ADDED ALL 5 YEARS TO THE SUMMARY
    st.subheader("1. Five-Year Summary Statistics")
    st.dataframe(df[['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']].describe())

    st.subheader("2. State Risk Profiles (2023)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color: #ef4444;'>🔴 Top 3 Highest Risk States</h4>", unsafe_allow_html=True)
        st.dataframe(df.nlargest(3, '2023 Accidents')[['State', '2023 Accidents']].reset_index(drop=True))
    with c2:
        st.markdown("<h4 style='color: #22c55e;'>🟢 Top 3 Safest Regions</h4>", unsafe_allow_html=True)
        st.dataframe(df.nsmallest(3, '2023 Accidents')[['State', '2023 Accidents']].reset_index(drop=True))

    st.subheader("3. The Pandemic Impact & Recovery")
    # Calculating dynamic percentages
    total_2019 = df['2019 Accidents'].sum()
    total_2020 = df['2020 Accidents'].sum()
    total_2023 = df['2023 Accidents'].sum()
    
    drop_2020 = ((total_2019 - total_2020) / total_2019) * 100
    surge_2023 = ((total_2023 - total_2020) / total_2020) * 100
    
    st.write(f"""
    * **The Lockdown Drop:** From 2019 to 2020, national accidents decreased by **{drop_2020:.1f}%** due to restricted mobility.
    * **The Post-Pandemic Surge:** Since the 2020 low, road accidents have surged by **{surge_2023:.1f}%**, indicating a rapid return of traffic volume.
    * **Variance:** The large difference between the `min` and `max` values in the summary table above highlights massive regional inequality in road safety.
    """)

# ===== INSIGHTS =====
elif menu == "Insights":
    st.title("Strategic Safety Insights")
    
    st.warning("**Major Finding: The Concentration of Risk**")
    st.write("""
    A visual analysis of the dataset reveals that road accidents in India are not evenly distributed. 
    Just a handful of high-volume states (such as Tamil Nadu and Madhya Pradesh) account for a massive percentage of total national accidents. 
    **Insight:** National road safety budgets should not be distributed equally; they must be hyper-focused on these specific high-risk corridors.
    """)

    st.info("**The Mobility Correlation (The 2020 Anomaly)**")
    st.write("""
    The sharp decline in accidents during the 2020 COVID-19 lockdowns proves that accident rates are heavily tied to raw traffic volume rather than sudden improvements in road infrastructure. 
    **Insight:** As India's vehicle ownership continues to grow post-2023, accidents will inevitably rise unless structural changes are made to highway traffic management.
    """)

    st.success("**Recommendations for Policymakers**")
    st.write("""
    1. **Targeted Interventions:** Deploy advanced speed-tracking cameras and highway patrols primarily in the top 5 highest-risk states.
    2. **District-Level Data:** This state-level EDA should be expanded to district-level data to identify specific "Black Spots" (highly dangerous junctions).
    3. **Awareness Campaigns:** Since accident numbers have fully rebounded past pre-pandemic levels, standard safety campaigns need to be modernized to target current driver behavior.
    """)
