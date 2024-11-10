# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="OKR Dashboard", layout="wide")

# Add custom CSS
st.markdown("""
<style>
    .st-emotion-cache-1y4p8pa {padding-top: 2rem;}
    .st-emotion-cache-1wmy9hl {max-width: 100%;}
</style>
""", unsafe_allow_html=True)

@st.cache_data  # Cache the data loading
def load_data():
    """Load OKR data from CSV"""
    df = pd.read_csv('index_goals.csv')
    
    status_mapping = {
        0: 'Not Started',
        1: 'Planned',
        2: 'Ongoing',
        3: 'Optimizing',
        4: 'Completed'
    }
    df['status_label'] = df['status'].map(status_mapping)
    return df

def create_radar_plot(df, goal_number):
    """Create radar plot for a specific goal's objectives"""
    goal_data = df[df['goal'] == goal_number]
    objectives = goal_data['objective'].unique()
    
    # Calculate average status for each objective
    objective_stats = []
    labels = []
    hover_text = []
    
    for obj in objectives:
        obj_data = goal_data[goal_data['objective'] == obj]
        avg_status = obj_data['status'].mean() / 4  # Normalize to 0-1
        num_okrs = len(obj_data)
        
        objective_stats.append(avg_status)
        labels.append(f'Obj {obj}')
        hover_text.append(f'Objective {obj}<br>Progress: {avg_status*100:.1f}%<br>OKRs: {num_okrs}')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=objective_stats,
        theta=labels,
        fill='toself',
        name=f'Goal {goal_number}',
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickformat='.0%'
            )),
        showlegend=False,
        title=f'Goal {goal_number} Objective Progress',
        height=400
    )
    
    return fig

def create_okr_progress_chart(df, goal_number):
    """Create detailed OKR progress chart"""
    goal_data = df[df['goal'] == goal_number]
    
    fig = px.bar(
        goal_data,
        x='okr',
        y='status',
        color='objective',
        title=f'Individual OKR Progress - Goal {goal_number}',
        labels={'status': 'Progress', 'okr': 'OKR', 'objective': 'Objective'},
        range_y=[0, 4]
    )
    
    fig.update_layout(height=400)
    return fig

def main():
    st.title('OKR Progress Dashboard')
    
    try:
        df = load_data()
    except Exception as e:
        st.error("Error loading data. Please ensure 'index_goals.csv' is in the same directory.")
        st.stop()
    
    # Sidebar
    st.sidebar.title('Navigation')
    view_type = st.sidebar.radio(
        "Select View",
        ["Overview", "Goal Details"]
    )
    
    if view_type == "Overview":
        # Summary metrics
        total_items = len(df)
        total_goals = len(df['goal'].unique())
        avg_completion = (df['status'].mean() / 4) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Goals", total_goals)
        col2.metric("Total OKRs", total_items)
        col3.metric("Average Completion", f"{avg_completion:.1f}%")
        
        # Overall goals progress
        st.subheader("Goals Overview")
        goals_progress = df.groupby('goal')['status'].mean().reset_index()
        goals_progress['completion'] = goals_progress['status'] / 4 * 100
        
        fig = px.bar(
            goals_progress,
            x='goal',
            y='completion',
            title='Goals Progress Overview',
            labels={'completion': 'Completion %', 'goal': 'Goal'},
            range_y=[0, 100]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Status distribution
        st.subheader("Status Distribution")
        status_dist = px.pie(
            df, 
            names='status_label',
            title='Overall Status Distribution'
        )
        st.plotly_chart(status_dist, use_container_width=True)
        
    else:  # Goal Details view
        selected_goal = st.sidebar.selectbox(
            'Select Goal',
            options=sorted(df['goal'].unique()),
            format_func=lambda x: f'Goal {x}'
        )
        
        # Goal specific metrics
        goal_data = df[df['goal'] == selected_goal]
        total_okrs = len(goal_data)
        goal_completion = (goal_data['status'].mean() / 4) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_radar_plot(df, selected_goal), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_okr_progress_chart(df, selected_goal), use_container_width=True)
        
        # Detailed OKR table
        st.subheader(f'Goal {selected_goal} Details')
        goal_details = goal_data[['objective', 'okr', 'status_label']].sort_values(['objective', 'okr'])
        st.dataframe(
            goal_details,
            column_config={
                "objective": "Objective",
                "okr": "OKR",
                "status_label": "Status"
            },
            use_container_width=True
        )

if __name__ == "__main__":
    main()