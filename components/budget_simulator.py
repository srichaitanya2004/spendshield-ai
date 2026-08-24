"""
Budget Simulator component for interactive savings projections
"""

import streamlit as st
import pandas as pd
from components import charts

def render_simulator(df):
    """Render the budget simulator interface"""
    st.subheader("💹 Budget Simulator")
    st.info("Adjust the reduction percentages for each category to see your potential savings.")
    
    # Get unique categories
    categories = df['category'].unique()
    
    # Create sliders for each category
    st.markdown("### Adjust Reduction Percentages")
    
    reductions = {}
    col1, col2 = st.columns(2)
    
    for idx, category in enumerate(sorted(categories)):
        col = col1 if idx % 2 == 0 else col2
        with col:
            default = 10 if category in ['Entertainment', 'Dining', 'Shopping'] else 5
            reductions[category] = col.slider(
                f"{category}",
                min_value=0,
                max_value=50,
                value=default,
                step=5,
                key=f"sim_{category}"
            ) / 100
    
    if st.button("🔄 Update Projections", use_container_width=True):
        # Calculate projected spending
        projected_df = df.copy()
        
        for category, reduction in reductions.items():
            mask = projected_df['category'] == category
            projected_df.loc[mask, 'amount'] = projected_df.loc[mask, 'amount'] * (1 - reduction)
        
        # Store in session state
        st.session_state.budget_sim = {
            'projected_df': projected_df,
            'reductions': reductions
        }
        st.success("✅ Projections updated!")
        st.rerun()
    
    # Display projections if available
    if 'projected_df' in st.session_state.budget_sim:
        projected_df = st.session_state.budget_sim['projected_df']
        reductions = st.session_state.budget_sim['reductions']
        
        st.markdown("---")
        st.subheader("📊 Projected Savings")
        
        # Calculate metrics
        current_total = df['amount'].sum()
        projected_total = projected_df['amount'].sum()
        monthly_savings = current_total - projected_total
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Spending",
                f"₹{current_total:,.0f}"
            )
        
        with col2:
            st.metric(
                "Projected Spending",
                f"₹{projected_total:,.0f}",
                delta=f"-₹{monthly_savings:,.0f}",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Annual Savings",
                f"₹{monthly_savings * 12:,.0f}",
                delta=f"{monthly_savings / current_total * 100:.1f}% reduction"
            )
        
        # Show comparison chart
        st.plotly_chart(
            charts.create_savings_simulation(df, projected_df),
            use_container_width=True
        )
        
        # Show detailed breakdown
        with st.expander("📋 Detailed Breakdown"):
            comparison_data = []
            for category in sorted(df['category'].unique()):
                current = df[df['category'] == category]['amount'].sum()
                projected = projected_df[projected_df['category'] == category]['amount'].sum()
                savings = current - projected
                reduction_pct = reductions.get(category, 0) * 100
                
                comparison_data.append({
                    'Category': category,
                    'Current': f"₹{current:,.0f}",
                    'Projected': f"₹{projected:,.0f}",
                    'Savings': f"₹{savings:,.0f}",
                    'Reduction': f"{reduction_pct:.0f}%"
                })
            
            st.dataframe(
                pd.DataFrame(comparison_data),
                use_container_width=True,
                hide_index=True
            )