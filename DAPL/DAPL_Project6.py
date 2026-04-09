import streamlit as st
import pandas as pd
import plotly.express as px

# ===== 1. PAGE SETTINGS =====
st.set_page_config(page_title="India Road Accident Dashboard", layout="wide")

# ===== 2. CUSTOM CSS =====
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #020617, #0f172a);
        color: white;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .box {
        background: rgba(255,255,255,0.08);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===== 3. DATA LOADING & CLEANING =====
@st.cache_data
def load_data():
    # Load from the DAPL folder as identified earlier
    df = pd.read_csv('DAPL/road_accidents.csv')
    df = df.dropna(subset=['State'])
    df = df[~df['State'].isin(['All India', 'Total', 'Total (All India)'])]
    
    # Cleaning numbers
    cols_to_fix = ['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    return df.fillna(0)

df_raw = load_data()

# ===== 4. SIDEBAR MENU & INTERACTION =====
with st.sidebar:
    st.title("Dashboard Menu")
    menu = st.radio("Go to:", ["Home", "Data", "Visuals", "Analysis", "Insights"])
    
    st.divider()
    st.header("⚙️ Global Filters")
    # INTERACTIVE: Filter the whole dashboard by State
    selected_states = st.multiselect("Select States", 
                                     options=sorted(df_raw['State'].unique()), 
                                     default=sorted(df_raw['State'].unique()))

# Apply filters to the dataframe used in the app
df = df_raw[df_raw['State'].isin(selected_states)]

# ===== 5. HOME =====
if menu == "Home":
    st.title("Road Accident Analysis Dashboard")

    c1, c2, c3 = st.columns(3)
    
    if not df.empty:
        total_2023 = int(df['2023 Accidents'].sum())
        avg_2023 = round(df['2023 Accidents'].mean(), 2)
        max_state = df.loc[df['2023 Accidents'].idxmax(), 'State']

        c1.markdown(f"<div class='box'><h3>Total Accidents (2023)</h3><h2>{total_2023:,}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='box'><h3>Avg per State</h3><h2>{avg_2023}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='box'><h3>Highest Risk State</h3><h2>{max_state}</h2></div>", unsafe_allow_html=True)

        st.subheader("National Accident Trend (2019 - 2023)")
        yearly_data = df[['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']].sum()
        years = ['2019', '2020', '2021', '2022', '2023']
        fig = px.area(x=years, y=yearly_data.values, labels={'x': 'Year', 'y': 'Total Accidents'}, color_discrete_sequence=['#f87171'], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one state in the sidebar.")

# ===== 6. DATA =====
elif menu == "Data":
    st.title("The Dataset")
    st.dataframe(df, use_container_width=True)

# ===== 7. VISUALS =====
elif menu == "Visuals":
    st.title("Visual Exploration")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Simplified list: Bar, Pie, Line, Box, and Histogram
        graph_type = st.selectbox("Select Graph Type", 
            ["Bar Chart", "Pie Chart", "Line Trend", "Box Plot", "Histogram"])
    with col_b:
        year_col = st.selectbox("Select Year", 
            ['2023 Accidents', '2022 Accidents', '2021 Accidents', '2020 Accidents', '2019 Accidents'])

    if graph_type == "Bar Chart":
        fig = px.bar(df.nlargest(10, year_col), x='State', y=year_col, color=year_col, template="plotly_dark")
    
    elif graph_type == "Pie Chart":
        fig = px.pie(df.nlargest(10, year_col), names='State', values=year_col, template="plotly_dark")
    
    elif graph_type == "Line Trend":
        years_list = ['2019 Accidents', '2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents']
        temp_df = df.melt(id_vars='State', value_vars=years_list, var_name='Year', value_name='Count')
        temp_df['Year'] = temp_df['Year'].str.extract('(\d+)') 
        fig = px.line(temp_df, x='Year', y='Count', color='State', markers=True, template="plotly_dark")
    
    elif graph_type == "Box Plot":
        fig = px.box(df, y=year_col, points="all", hover_data=['State'], template="plotly_dark")
    
    elif graph_type == "Histogram":
        # Frequency distribution of accident counts
        fig = px.histogram(df, x=year_col, nbins=15, template="plotly_dark")
        fig.update_layout(bargap=0.1)
        st.info("**Histogram:** Shows how many states fall into different accident count ranges.")

    st.plotly_chart(fig, use_container_width=True)
# ===== 8. ANALYSIS =====
elif menu == "Analysis":
    st.title("In-Depth Statistical Breakdown")
    
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
    t19, t20, t23 = df['2019 Accidents'].sum(), df['2020 Accidents'].sum(), df['2023 Accidents'].sum()
    
    drop_20 = ((t19 - t20) / t19) * 100 if t19 != 0 else 0
    surge_23 = ((t23 - t20) / t20) * 100 if t20 != 0 else 0
    
    st.write(f"""
    * **The Lockdown Drop:** From 2019 to 2020, national accidents decreased by **{drop_20:.1f}%**.
    * **The Post-Pandemic Surge:** Since the 2020 low, road accidents have surged by **{surge_23:.1f}%**.
    * **Variance:** The large difference between the `min` and `max` values highlights massive regional inequality.
    """)

# ===== 9. INSIGHTS =====
elif menu == "Insights":
    st.title("Strategic Safety Insights")
    
    st.warning("**Major Finding: The Concentration of Risk**")
    st.write("""
    A visual analysis reveals accidents are not evenly distributed. Just a few high-volume states account for a massive percentage of total national accidents. 
    **Insight:** Budgets should be hyper-focused on these specific high-risk corridors.
    """)

    st.info("**The Mobility Correlation (The 2020 Anomaly)**")
    st.write("""
    The 2020 decline proves accident rates are heavily tied to traffic volume. As vehicle ownership grows, accidents will rise unless structural changes are made.
    """)

    st.success("**Recommendations for Policymakers**")
    st.write("""
    1. **Targeted Interventions:** Deploy advanced speed-tracking in the top 5 highest-risk states.
    2. **District-Level Data:** Expand this to identify specific "Black Spots" (dangerous junctions).
    3. **Awareness Campaigns:** Modernize campaigns to target current post-pandemic driver behavior.
    """)
