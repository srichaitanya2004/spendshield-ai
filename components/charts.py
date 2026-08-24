"""
Plotly chart generation functions
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_category_chart(df):
    """Create a bar chart of spending by category"""
    category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=category_data.index,
        y=category_data.values,
        title="Spending by Category",
        labels={'x': 'Category', 'y': 'Amount (₹)'},
        color=category_data.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def create_essential_vs_discretionary(df):
    """Create a pie chart comparing essential vs discretionary spending"""
    type_data = df.groupby('type')['amount'].sum()
    
    fig = px.pie(
        values=type_data.values,
        names=type_data.index,
        title="Essential vs Discretionary",
        color=type_data.index,
        color_discrete_map={
            'Essential': '#2ecc71',
            'Discretionary': '#e74c3c'
        }
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_top_categories_chart(df):
    """Create a horizontal bar chart of top spending categories"""
    top_data = df.groupby('category')['amount'].sum().sort_values(ascending=True).tail(10)
    
    fig = px.bar(
        x=top_data.values,
        y=top_data.index,
        orientation='h',
        title="Top 10 Spending Categories",
        labels={'x': 'Amount (₹)', 'y': 'Category'},
        color=top_data.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def create_trend_chart(df):
    """Create a line chart showing spending trends over time"""
    df['date'] = pd.to_datetime(df['date'])
    trend_data = df.groupby(df['date'].dt.to_period('D'))['amount'].sum().reset_index()
    trend_data['date'] = trend_data['date'].dt.to_timestamp()
    
    fig = px.line(
        trend_data,
        x='date',
        y='amount',
        title="Spending Trend",
        labels={'date': 'Date', 'amount': 'Amount (₹)'}
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    fig.add_scatter(
        x=trend_data['date'],
        y=trend_data['amount'],
        mode='lines+markers',
        name='Daily Spending',
        line=dict(color='#667eea', width=2)
    )
    
    return fig

def create_savings_simulation(current_df, adjusted_df):
    """Create a comparison chart for budget simulation"""
    current = current_df.groupby('category')['amount'].sum()
    adjusted = adjusted_df.groupby('category')['amount'].sum()
    
    comparison = pd.DataFrame({
        'Current': current,
        'Projected': adjusted
    }).fillna(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=comparison.index,
        y=comparison['Current'],
        name='Current',
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        x=comparison.index,
        y=comparison['Projected'],
        name='Projected',
        marker_color='#2ecc71'
    ))
    
    fig.update_layout(
        title="Current vs Projected Spending",
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        barmode='group',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig