"""LLM Monitoring Dashboard for ROAMFIT."""
import streamlit as st
from database import get_llm_stats, create_tables

# Page configuration
st.set_page_config(
    page_title="LLM Monitoring - ROAMFIT",
    page_icon="📊",
    layout="wide"
)

# Initialize database tables if needed
create_tables()

st.title("📊 LLM Usage Statistics")
st.markdown("Monitor token usage and costs for all LLM API calls")

# Get statistics
try:
    stats = get_llm_stats()
    
    # Overall statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total API Calls", stats["total_calls"])
    
    with col2:
        st.metric("Successful Calls", stats["successful_calls"])
    
    with col3:
        st.metric("Total Tokens", f"{stats['total_tokens']:,}")
    
    with col4:
        st.metric("Estimated Cost", f"${stats['estimated_cost']:.4f}")
    
    st.divider()
    
    # Breakdown by Agent
    st.subheader("📈 Breakdown by Agent")
    if stats["by_agent"]:
        # Create table data
        agent_data = []
        for agent in stats["by_agent"]:
            # Calculate cost for this agent
            # We'll use average pricing since we don't track model per agent
            tokens = agent["tokens_used"]
            estimated_cost = (tokens / 1000) * 0.008  # Average estimate
            
            agent_data.append({
                "Agent": agent["agent_name"],
                "Calls": agent["call_count"],
                "Tokens": f"{agent['tokens_used']:,}",
                "Avg Time (ms)": f"{agent['avg_time_ms']:.2f}",
                "Cost": f"${estimated_cost:.4f}"
            })
        
        st.dataframe(
            agent_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No agent statistics available yet. Make some LLM calls first!")
    
    st.divider()
    
    # Breakdown by Model
    st.subheader("🤖 Breakdown by Model")
    if stats["by_model"]:
        model_data = []
        for model in stats["by_model"]:
            # Calculate cost based on model
            model_name = model["model"]
            tokens_in = model["tokens_in"]
            tokens_out = model["tokens_out"]
            
            if "gpt-4o" in model_name.lower():
                cost = (tokens_in / 1000) * 0.0025 + (tokens_out / 1000) * 0.01
            elif "gpt-4" in model_name.lower():
                cost = (tokens_in / 1000) * 0.03 + (tokens_out / 1000) * 0.06
            else:
                cost = ((tokens_in + tokens_out) / 1000) * 0.008
            
            model_data.append({
                "Model": model_name,
                "Calls": model["call_count"],
                "Tokens In": f"{model['tokens_in']:,}",
                "Tokens Out": f"{model['tokens_out']:,}",
                "Total Tokens": f"{model['tokens_used']:,}",
                "Cost": f"${cost:.4f}"
            })
        
        st.dataframe(
            model_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No model statistics available yet. Make some LLM calls first!")
    
    st.divider()
    
    # Pricing information
    with st.expander("ℹ️ Pricing Information"):
        st.markdown("""
        **OpenAI Model Pricing (as of 2024):**
        
        - **GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
        - **GPT-4o**: $0.0025 per 1K input tokens, $0.01 per 1K output tokens
        
        Costs are estimated based on token usage and may vary slightly from actual billing.
        """)
    
except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")
    st.info("Make sure the database is initialized and contains LLM log data.")

