import streamlit as st
import calendar
from datetime import date
import json
import pandas as pd
from collections import defaultdict

# Page setup
st.set_page_config(page_title="TOIL Calculator", layout="wide")

# Initialize data
if 'data' not in st.session_state:
    st.session_state.data = defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {"worked": False, "national": False, "day_off": False, "toil_day": False}
    )))
if 'toil_balance' not in st.session_state:
    st.session_state.toil_balance = 0

# Colors
COLORS = {
    "worked": "#90EE90",
    "national": "#FFB6C1",
    "day_off": "#D3D3D3",
    "toil_day": "#FFD700",
    "default": "#ADD8E6"
}

def main():
    st.title("💰 TOIL Calculator")
    
    # Sidebar
    with st.sidebar:
        st.header("Month Selection")
        year = st.number_input("Year", 2024, 2030, 2024)
        month = st.selectbox("Month", range(1, 13), format_func=lambda x: calendar.month_name[x])
        
        if st.button("Calculate Current Month", type="primary"):
            calculate_month(year, month)
    
    # Calendar display
    st.header(f"{calendar.month_name[month]} {year}")
    
    # Day editing
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    for week in month_days:
        cols = st.columns(7)
        for col_idx, day in enumerate(week):
            with cols[col_idx]:
                if day != 0:
                    display_day(year, month, day)

def display_day(year, month, day):
    """Show a single day"""
    day_data = st.session_state.data[year][month][day]
    
    # Determine color
    if day_data["worked"] and day_data["national"]:
        color = "#FFA500"
        symbol = "✓🎆"
    elif day_data["worked"]:
        color = COLORS["worked"]
        symbol = "✓"
    elif day_data["national"]:
        color = COLORS["national"]
        symbol = "🎆"
    elif day_data["toil_day"]:
        color = COLORS["toil_day"]
        symbol = "💰"
    elif day_data["day_off"]:
        color = COLORS["day_off"]
        symbol = "🌴"
    else:
        color = COLORS["default"]
        symbol = "📅"
    
    # Day button
    if st.button(f"{day}\n{symbol}", key=f"{year}{month}{day}", use_container_width=True):
        edit_day(year, month, day)

def edit_day(year, month, day):
    """Edit day flags"""
    day_data = st.session_state.data[year][month][day]
    
    with st.expander(f"Edit {day}/{month}/{year}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            day_data["worked"] = st.toggle("Worked", day_data["worked"])
        with col2:
            day_data["national"] = st.toggle("National", day_data["national"])
        with col3:
            day_data["day_off"] = st.toggle("Day Off", day_data["day_off"])
        with col4:
            day_data["toil_day"] = st.toggle("TOIL Day", day_data["toil_day"])
        
        if st.button("Save", type="primary"):
            st.success("Saved!")
            st.rerun()

def calculate_month(year, month):
    """Calculate TOIL for month"""
    month_data = st.session_state.data[year][month]
    
    # Count days
    worked = sum(1 for d in month_data.values() if d["worked"])
    national = sum(1 for d in month_data.values() if d["national"])
    day_off = sum(1 for d in month_data.values() if d["day_off"])
    toil = sum(1 for d in month_data.values() if d["toil_day"])
    
    # Calculate
    total_days = sum(1 for week in calendar.monthdayscalendar(year, month) for d in week if d != 0)
    expected = total_days - national - day_off - toil
    new_toil = worked - expected
    
    # Display results
    st.subheader("Results")
    st.write(f"**Worked:** {worked} days")
    st.write(f"**Expected:** {expected} days")
    st.write(f"**New TOIL:** {new_toil} days")
    st.write(f"**TOIL used:** {toil} days")
    
    if new_toil > 0:
        st.success(f"🎉 You earned {new_toil} TOIL days!")
    elif new_toil < 0:
        st.warning(f"⚠️ You worked {-new_toil} days less than expected")

if __name__ == "__main__":
    main()
