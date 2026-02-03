import streamlit as st
import calendar
from datetime import date
import json
import pandas as pd
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="TOIL Calculator",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {"worked": False, "national": False, "day_off": False, "toil_day": False}
    )))
if 'toil_balance' not in st.session_state:
    st.session_state.toil_balance = 0
if 'current_year' not in st.session_state:
    st.session_state.current_year = 2024
if 'current_month' not in st.session_state:
    st.session_state.current_month = 1

# Colors for calendar
COLORS = {
    "worked": "#90EE90",  # lightgreen
    "national": "#FFB6C1",  # pink
    "day_off": "#D3D3D3",  # lightgray
    "toil_day": "#FFD700",  # gold
    "worked_national": "#FFA500",  # orange
    "default": "#ADD8E6"  # lightblue
}

def main():
    st.title("💰 TOIL Calculator")
    st.markdown("Track work days and calculate TOIL balance")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to:", ["📅 Calendar", "📊 Calculate", "💰 Balance"])
        
        st.header("Month Selection")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Year", 2020, 2030, st.session_state.current_year)
        with col2:
            month = st.selectbox("Month", range(1, 13), 
                               index=st.session_state.current_month-1,
                               format_func=lambda x: calendar.month_name[x])
        
        st.session_state.current_year = year
        st.session_state.current_month = month
        
        if st.button("Calculate This Month", type="primary"):
            st.session_state.calculate = True
    
    # Page routing
    if page == "📅 Calendar":
        show_calendar()
    elif page == "📊 Calculate":
        show_calculation()
    else:
        show_balance()

def show_calendar():
    """Show interactive calendar"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    
    st.header(f"{calendar.month_name[month]} {year}")
    
    # Legend
    st.markdown("""
    **Legend:** ✓ Worked | 🎆 National | 🌴 Day Off | 💰 TOIL Day | 📅 Not marked
    """)
    
    # Calendar grid
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    # Day headers
    cols = st.columns(7)
    headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")
    
    # Create calendar
    for week in month_days:
        cols = st.columns(7)
        for col_idx, day in enumerate(week):
            with cols[col_idx]:
                if day != 0:
                    display_day(day)

def display_day(day):
    """Display a single day"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    day_data = st.session_state.data[year][month][day]
    
    # Determine color and symbol
    if day_data["worked"] and day_data["national"]:
        color = COLORS["worked_national"]
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
    if st.button(f"{day}\n{symbol}", key=f"day_{year}_{month}_{day}",
                help=f"Click to edit day {day}",
                use_container_width=True):
        edit_day(day)

def edit_day(day):
    """Edit a day's flags"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    day_data = st.session_state.data[year][month][day]
    
    st.subheader(f"Edit {day}/{month}/{year}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        worked = st.toggle("Worked", day_data["worked"])
    with col2:
        national = st.toggle("National Holiday", day_data["national"])
    with col3:
        day_off = st.toggle("Day Off", day_data["day_off"])
    with col4:
        toil_day = st.toggle("TOIL Day", day_data["toil_day"])
    
    if st.button("Save Changes", type="primary"):
        day_data["worked"] = worked
        day_data["national"] = national
        day_data["day_off"] = day_off
        day_data["toil_day"] = toil_day
        st.success("Saved!")
        st.rerun()

def show_calculation():
    """Calculate TOIL for current month"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    
    st.header(f"TOIL Calculation for {calendar.month_name[month]} {year}")
    
    if st.button("Calculate Now", type="primary") or st.session_state.get('calculate', False):
        # Get month data
        month_data = st.session_state.data[year][month]
        
        # Count days
        worked = sum(1 for d in month_data.values() if d["worked"])
        national = sum(1 for d in month_data.values() if d["national"])
        day_off = sum(1 for d in month_data.values() if d["day_off"])
        toil = sum(1 for d in month_data.values() if d["toil_day"])
        
        # Calculate
        cal = calendar.Calendar()
        total_days = sum(1 for week in cal.monthdayscalendar(year, month) for d in week if d != 0)
        
        total_off = day_off + toil
        expected = total_days - national - total_off
        new_toil = worked - expected
        
        # Display
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Worked", f"{worked} days")
        with col2:
            st.metric("Expected", f"{expected} days")
        with col3:
            st.metric("New TOIL", f"{new_toil:+d} days")
        with col4:
            st.metric("TOIL Used", f"{toil} days")
        
        # Result
        st.subheader("Result")
        if new_toil > 0:
            st.success(f"🎉 You earned {new_toil} TOIL day(s) this month!")
        elif new_toil < 0:
            st.warning(f"⚠️ You worked {-new_toil} day(s) less than expected")
        else:
            st.info("✅ Perfect balance this month")
        
        # Update balance
        if new_toil > 0:
            st.session_state.toil_balance += new_toil
        st.session_state.toil_balance -= toil
        
        # Reset flag
        if 'calculate' in st.session_state:
            st.session_state.calculate = False

def show_balance():
    """Show TOIL balance"""
    st.header("TOIL Balance")
    
    # Current balance
    st.metric("Current TOIL Balance", f"{st.session_state.toil_balance} days",
             delta=None, delta_color="normal")
    
    # Manual adjustment
    st.subheader("Adjust Balance")
    col1, col2 = st.columns(2)
    with col1:
        new_balance = st.number_input("Set balance to:", 
                                     value=st.session_state.toil_balance)
    with col2:
        if st.button("Update Balance"):
            st.session_state.toil_balance = new_balance
            st.success("Balance updated!")
            st.rerun()
    
    # Data management
    st.subheader("Data Management")
    if st.button("Clear All Data"):
        if st.checkbox("I'm sure I want to delete all data"):
            st.session_state.data.clear()
            st.session_state.toil_balance = 0
            st.success("All data cleared!")
            st.rerun()

if __name__ == "__main__":
    main()
