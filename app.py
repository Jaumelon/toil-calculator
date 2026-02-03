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
    st.session_state.data = {}
if 'toil_balance' not in st.session_state:
    st.session_state.toil_balance = 0.0
if 'current_year' not in st.session_state:
    st.session_state.current_year = date.today().year
if 'current_month' not in st.session_state:
    st.session_state.current_month = date.today().month
if 'edit_day' not in st.session_state:
    st.session_state.edit_day = None

# Colors for calendar
COLORS = {
    "worked": "#90EE90",  # lightgreen
    "national": "#FFB6C1",  # pink
    "day_off": "#D3D3D3",  # lightgray
    "toil_day": "#FFD700",  # gold
    "worked_national": "#FFA500",  # orange
    "default": "#ADD8E6"  # lightblue
}

def get_day_data(year, month, day):
    """Get data for a specific day"""
    key = f"{year}-{month}-{day}"
    if key not in st.session_state.data:
        # Default values
        st.session_state.data[key] = {
            "worked": False,
            "national": False,
            "day_off": False,
            "toil_day": False
        }
    return st.session_state.data[key]

def save_day_data(year, month, day, data):
    """Save data for a specific day"""
    key = f"{year}-{month}-{day}"
    st.session_state.data[key] = data

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
        
        # Data management
        st.header("Data Management")
        
        # Export data
        if st.button("📤 Export Data"):
            data_str = json.dumps(st.session_state.data)
            st.download_button(
                label="Download JSON",
                data=data_str,
                file_name=f"toil_data_{date.today().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        # Import data
        uploaded_file = st.file_uploader("📥 Import Data", type=['json'])
        if uploaded_file:
            try:
                imported_data = json.load(uploaded_file)
                st.session_state.data.update(imported_data)
                st.success("Data imported successfully!")
            except:
                st.error("Failed to import data. Invalid format.")
        
        if st.button("🗑️ Clear All Data"):
            if st.checkbox("I'm sure I want to delete all data"):
                st.session_state.data = {}
                st.session_state.toil_balance = 0.0
                st.success("All data cleared!")
                st.rerun()
    
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
    
    # Legend with better formatting
    legend_html = """
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <strong>Legend:</strong><br>
        <span style="color: #90EE90;">✓</span> Worked | 
        <span style="color: #FFB6C1;">🎆</span> National Holiday | 
        <span style="color: #D3D3D3;">🌴</span> Day Off | 
        <span style="color: #FFD700;">💰</span> TOIL Day | 
        <span style="color: #ADD8E6;">📅</span> Not marked
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)
    
    # Display edit modal if needed
    if st.session_state.edit_day:
        edit_day_modal(st.session_state.edit_day)
    
    # Calendar grid
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    # Day headers with better styling
    cols = st.columns(7)
    headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for col, header in zip(cols, headers):
        col.markdown(f"<div style='text-align: center; font-weight: bold;'>{header}</div>", 
                    unsafe_allow_html=True)
    
    # Create calendar
    for week_idx, week in enumerate(month_days):
        cols = st.columns(7)
        for col_idx, day in enumerate(week):
            with cols[col_idx]:
                if day != 0:
                    display_day(day)
                else:
                    # Empty day
                    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

def display_day(day):
    """Display a single day"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    day_data = get_day_data(year, month, day)
    
    # Determine color and symbol
    if day_data["worked"] and day_data["national"]:
        bg_color = COLORS["worked_national"]
        symbol = "✓🎆"
        tooltip = "Worked on National Holiday"
    elif day_data["worked"]:
        bg_color = COLORS["worked"]
        symbol = "✓"
        tooltip = "Worked"
    elif day_data["national"]:
        bg_color = COLORS["national"]
        symbol = "🎆"
        tooltip = "National Holiday"
    elif day_data["toil_day"]:
        bg_color = COLORS["toil_day"]
        symbol = "💰"
        tooltip = "TOIL Day"
    elif day_data["day_off"]:
        bg_color = COLORS["day_off"]
        symbol = "🌴"
        tooltip = "Day Off"
    else:
        bg_color = COLORS["default"]
        symbol = "📅"
        tooltip = "Not marked"
    
    # Create styled button
    button_html = f"""
    <div style="
        background-color: {bg_color};
        border-radius: 5px;
        padding: 8px;
        text-align: center;
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        border: 1px solid #ccc;
        margin: 2px;
    ">
        <div style="font-size: 18px; font-weight: bold;">{day}</div>
        <div style="font-size: 14px;">{symbol}</div>
    </div>
    """
    
    # Use markdown with onclick to trigger edit
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Add invisible button for interaction
    if st.button(f"Edit {day}", key=f"edit_{year}_{month}_{day}", 
                help=tooltip, use_container_width=True):
        st.session_state.edit_day = day
        st.rerun()

def edit_day_modal(day):
    """Show edit modal for a day"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    day_data = get_day_data(year, month, day)
    
    st.subheader(f"Edit {calendar.month_name[month]} {day}, {year}")
    
    # Create a form for editing
    with st.form(key=f"edit_form_{day}"):
        col1, col2 = st.columns(2)
        
        with col1:
            worked = st.checkbox("Worked", value=day_data["worked"])
            national = st.checkbox("National Holiday", value=day_data["national"])
        
        with col2:
            day_off = st.checkbox("Day Off", value=day_data["day_off"])
            toil_day = st.checkbox("TOIL Day", value=day_data["toil_day"])
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            save_button = st.form_submit_button("💾 Save", type="primary")
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel")
        
        if save_button:
            # Validate inputs
            if sum([worked, national, day_off, toil_day]) > 2:
                st.error("Cannot select more than 2 options!")
            else:
                new_data = {
                    "worked": worked,
                    "national": national,
                    "day_off": day_off,
                    "toil_day": toil_day
                }
                save_day_data(year, month, day, new_data)
                st.session_state.edit_day = None
                st.success("Changes saved!")
                st.rerun()
        
        if cancel_button:
            st.session_state.edit_day = None
            st.rerun()

def show_calculation():
    """Calculate TOIL for current month"""
    year = st.session_state.current_year
    month = st.session_state.current_month
    
    st.header(f"TOIL Calculation for {calendar.month_name[month]} {year}")
    
    # Get month data
    cal = calendar.Calendar()
    month_days_list = [d for week in cal.monthdayscalendar(year, month) for d in week if d != 0]
    
    # Initialize counters
    worked = 0
    national = 0
    day_off = 0
    toil_used = 0
    
    for day in month_days_list:
        day_data = get_day_data(year, month, day)
        if day_data["worked"]:
            worked += 1
        if day_data["national"]:
            national += 1
        if day_data["day_off"]:
            day_off += 1
        if day_data["toil_day"]:
            toil_used += 1
    
    total_days = len(month_days_list)
    total_off = day_off + toil_used
    expected = total_days - national - total_off
    new_toil = worked - expected
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Worked Days", f"{worked}")
    with col2:
        st.metric("Expected Days", f"{expected}")
    with col3:
        st.metric("TOIL Earned", f"{max(0, new_toil)}", delta=f"{new_toil:+d}")
    with col4:
        st.metric("TOIL Used", f"{toil_used}")
    
    # Calculation details
    with st.expander("📝 Calculation Details"):
        st.write(f"**Total days in month:** {total_days}")
        st.write(f"**National holidays:** {national}")
        st.write(f"**Days off:** {day_off}")
        st.write(f"**TOIL days used:** {toil_used}")
        st.write(f"**Expected work days:** {total_days} - {national} - {total_off} = {expected}")
        st.write(f"**TOIL calculation:** {worked} - {expected} = {new_toil:+d}")
    
    # Update balance
    if st.button("Update Balance", type="primary"):
        if new_toil > 0:
            st.session_state.toil_balance += new_toil
        st.session_state.toil_balance -= toil_used
        st.success(f"Balance updated! Current balance: {st.session_state.toil_balance:.1f} days")
        st.rerun()

def show_balance():
    """Show TOIL balance"""
    st.header("TOIL Balance")
    
    # Current balance with better styling
    balance_color = "green" if st.session_state.toil_balance >= 0 else "red"
    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    ">
        <h2 style="margin: 0; color: #666;">Current TOIL Balance</h2>
        <h1 style="margin: 10px 0; color: {balance_color};">{st.session_state.toil_balance:.1f} days</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Balance adjustment
    st.subheader("Adjust Balance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        adjustment = st.number_input("Adjustment (+/- days)", 
                                    value=0.0,
                                    step=0.5,
                                    format="%.1f")
    
    with col2:
        if st.button("➕ Add Days"):
            st.session_state.toil_balance += adjustment
            st.success(f"Added {adjustment} days!")
            st.rerun()
    
    with col3:
        if st.button("➖ Subtract Days"):
            st.session_state.toil_balance -= adjustment
            st.success(f"Subtracted {adjustment} days!")
            st.rerun()
    
    # Set to specific value
    st.subheader("Set Specific Balance")
    col1, col2 = st.columns([2, 1])
    with col1:
        new_balance = st.number_input("Set balance to:", 
                                     value=st.session_state.toil_balance,
                                     step=0.5,
                                     format="%.1f")
    with col2:
        if st.button("Update Balance"):
            st.session_state.toil_balance = new_balance
            st.success(f"Balance set to {new_balance} days!")
            st.rerun()
    
    # View all data
    with st.expander("📊 View All Data"):
        if st.session_state.data:
            df_data = []
            for key, value in st.session_state.data.items():
                year, month, day = map(int, key.split('-'))
                df_data.append({
                    "Date": f"{day:02d}/{month:02d}/{year}",
                    "Worked": "✓" if value["worked"] else "",
                    "National Holiday": "✓" if value["national"] else "",
                    "Day Off": "✓" if value["day_off"] else "",
                    "TOIL Day": "✓" if value["toil_day"] else ""
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data recorded yet.")

if __name__ == "__main__":
    main()
