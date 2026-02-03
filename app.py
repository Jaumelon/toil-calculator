import streamlit as st
import calendar
from datetime import date, datetime
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
    st.session_state.current_year = datetime.now().year
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().month

# Colors for calendar
COLORS = {
    "worked": "#90EE90",  # lightgreen
    "national": "#FFB6C1",  # pink
    "day_off": "#D3D3D3",  # lightgray
    "toil_day": "#FFD700",  # gold
    "worked_national": "#FFA500",  # orange
    "toil_national": "#F08080",  # lightcoral
    "default": "#ADD8E6"  # lightblue
}

def main():
    st.title("💰 TOIL Calculator")
    st.markdown("Track your work days and calculate TOIL balance")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to:", ["📅 Calendar", "📊 Monthly Results", "💰 TOIL Balance", "💾 Data Management"])
        
        st.header("Month Selection")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Year", min_value=2020, max_value=2030, 
                                 value=st.session_state.current_year, key="year_input")
        with col2:
            month = st.selectbox("Month", list(range(1, 13)), 
                               index=st.session_state.current_month-1, format_func=lambda x: calendar.month_name[x])
        
        if year != st.session_state.current_year or month != st.session_state.current_month:
            st.session_state.current_year = year
            st.session_state.current_month = month
            st.rerun()
        
        st.header("Quick Actions")
        if st.button("Calculate Current Month"):
            st.session_state.show_results = True
            st.rerun()
    
    # Page routing
    if page == "📅 Calendar":
        show_calendar()
    elif page == "📊 Monthly Results":
        show_results()
    elif page == "💰 TOIL Balance":
        show_balance()
    else:  # Data Management
        show_data_management()

def show_calendar():
    """Display interactive calendar"""
    st.header(f"{calendar.month_name[st.session_state.current_month]} {st.session_state.current_year}")
    
    # Legend
    cols = st.columns(7)
    legend_items = [
        ("Worked", COLORS["worked"], "✓"),
        ("National", COLORS["national"], "🎆"),
        ("Day Off", COLORS["day_off"], "🌴"),
        ("TOIL Day", COLORS["toil_day"], "💰"),
        ("Worked+National", COLORS["worked_national"], "✓🎆"),
        ("TOIL+National", COLORS["toil_national"], "💰🎆"),
        ("Not marked", COLORS["default"], "📅")
    ]
    
    for col, (label, color, symbol) in zip(cols, legend_items):
        with col:
            st.markdown(f"""
            <div style="background-color:{color}; padding:5px; border-radius:5px; text-align:center;">
                <b>{symbol}</b><br>
                <small>{label}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Calendar grid
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(st.session_state.current_year, st.session_state.current_month)
    
    # Day headers
    headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**", unsafe_allow_html=True)
    
    # Create calendar
    for week in month_days:
        cols = st.columns(7)
        for col_idx, day in enumerate(week):
            with cols[col_idx]:
                if day == 0:
                    st.write("")
                else:
                    display_day(day)

def display_day(day):
    """Display a single day in calendar"""
    day_data = st.session_state.data[st.session_state.current_year][st.session_state.current_month][day]
    
    # Determine color and symbol
    if day_data["worked"] and day_data["national"]:
        color = COLORS["worked_national"]
        symbol = "✓🎆"
    elif day_data["toil_day"] and day_data["national"]:
        color = COLORS["toil_national"]
        symbol = "💰🎆"
    elif day_data["worked"]:
        color = COLORS["worked"]
        symbol = "✓"
    elif day_data["national"]:
        color = COLORS["national"]
        symbol = "🎆"
    elif day_data["day_off"]:
        color = COLORS["day_off"]
        symbol = "🌴"
    elif day_data["toil_day"]:
        color = COLORS["toil_day"]
        symbol = "💰"
    else:
        color = COLORS["default"]
        symbol = "📅"
    
    # Get day name
    date_obj = date(st.session_state.current_year, st.session_state.current_month, day)
    day_name = date_obj.strftime("%a")
    
    # Create day button
    day_key = f"day_{st.session_state.current_year}_{st.session_state.current_month}_{day}"
    
    if st.button(f"{day}\n{symbol}", key=day_key, 
                use_container_width=True,
                help=f"{day_name}, {day}/{st.session_state.current_month}"):
        edit_day(day)

def edit_day(day):
    """Edit day flags"""
    st.session_state.editing_day = day
    st.rerun()

def show_day_editor():
    """Show day editing interface"""
    if 'editing_day' not in st.session_state:
        return
    
    day = st.session_state.editing_day
    day_data = st.session_state.data[st.session_state.current_year][st.session_state.current_month][day]
    
    st.subheader(f"Editing {day}/{st.session_state.current_month}/{st.session_state.current_year}")
    
    # Get day name
    date_obj = date(st.session_state.current_year, st.session_state.current_month, day)
    day_name = date_obj.strftime("%A")
    st.write(f"**{day_name}**")
    
    # Toggle buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        worked = st.toggle("Worked", value=day_data["worked"], 
                          help="You worked this day")
    with col2:
        national = st.toggle("National Holiday", value=day_data["national"],
                           help="Public holiday")
    with col3:
        day_off = st.toggle("Day Off", value=day_data["day_off"],
                          help="Your day off (weekend, PTO, etc.)")
    with col4:
        toil_day = st.toggle("TOIL Day", value=day_data["toil_day"],
                           help="Day off using TOIL credit")
    
    # Special handling for TOIL days
    if toil_day and not day_off:
        day_off = True
    
    # Save button
    if st.button("Save", type="primary"):
        st.session_state.data[st.session_state.current_year][st.session_state.current_month][day] = {
            "worked": worked,
            "national": national,
            "day_off": day_off,
            "toil_day": toil_day
        }
        del st.session_state.editing_day
        st.success(f"Day {day} updated!")
        st.rerun()
    
    # Cancel button
    if st.button("Cancel"):
        del st.session_state.editing_day
        st.rerun()

def show_results():
    """Show monthly TOIL calculation"""
    st.header("Monthly TOIL Calculation")
    
    if st.button("Calculate for Current Month", type="primary"):
        result = calculate_month(st.session_state.current_year, st.session_state.current_month)
        st.markdown(result)
    
    # Show editor if needed
    if 'editing_day' in st.session_state:
        show_day_editor()

def calculate_month(year, month):
    """Calculate TOIL for a month"""
    month_name = calendar.month_name[month]
    month_data = st.session_state.data[year][month]
    
    # Get total days
    cal = calendar.Calendar()
    total_days = sum(1 for week in cal.monthdayscalendar(year, month) for day in week if day != 0)
    
    # Count days
    worked_count = sum(1 for day_data in month_data.values() if day_data["worked"])
    national_count = sum(1 for day_data in month_data.values() if day_data["national"])
    day_off_count = sum(1 for day_data in month_data.values() if day_data["day_off"])
    toil_count = sum(1 for day_data in month_data.values() if day_data["toil_day"])
    
    total_day_off = day_off_count + toil_count
    expected_workdays = total_days - national_count - total_day_off
    new_toil = worked_count - expected_workdays
    toil_used = toil_count
    
    # Format result
    result = f"""
    ## {month_name} {year}
    
    ### 📊 Summary
    - **Total days in month:** {total_days}
    - **Days worked:** {worked_count}
    - **National holidays:** {national_count}
    - **Your days off:** {total_day_off} ({day_off_count} regular + {toil_count} TOIL)
    
    ### 🧮 Calculation
    - **Expected work days:** {total_days} - {national_count} - {total_day_off} = **{expected_workdays}**
    - **Actual days worked:** **{worked_count}**
    - **Difference:** {worked_count} - {expected_workdays} = **{new_toil:+.0f}**
    
    ### 💰 TOIL This Month
    - **New TOIL earned:** {new_toil:+.0f} day(s)
    - **TOIL days used:** {toil_used} day(s)
    - **Net change:** {new_toil - toil_used:+.0f} day(s)
    """
    
    if new_toil > 0:
        result += f"\n### 🎉 Result: You earned **{new_toil} TOIL day(s)** this month!"
    elif new_toil < 0:
        result += f"\n### ⚠️ Result: You worked **{-new_toil} day(s) less** than expected"
    else:
        result += f"\n### ✅ Result: Perfect balance this month"
    
    return result

def show_balance():
    """Show TOIL balance"""
    st.header("TOIL Balance Tracker")
    
    # Calculate balance
    total_toil_earned = 0
    total_toil_used = 0
    monthly_data = []
    
    for year in sorted(st.session_state.data.keys()):
        for month in sorted(st.session_state.data[year].keys()):
            month_data = st.session_state.data[year][month]
            if not any(day_data.values() for day_data in month_data.values()):
                continue
            
            # Calculate for this month
            cal = calendar.Calendar()
            total_days = sum(1 for week in cal.monthdayscalendar(year, month) for day in week if day != 0)
            
            worked_count = sum(1 for day_data in month_data.values() if day_data["worked"])
            national_count = sum(1 for day_data in month_data.values() if day_data["national"])
            day_off_count = sum(1 for day_data in month_data.values() if day_data["day_off"])
            toil_count = sum(1 for day_data in month_data.values() if day_data["toil_day"])
            
            total_day_off = day_off_count + toil_count
            expected_workdays = total_days - national_count - total_day_off
            new_toil = worked_count - expected_workdays
            toil_used = toil_count
            
            if new_toil > 0:
                total_toil_earned += new_toil
            total_toil_used += toil_used
            
            monthly_data.append({
                "Year": year,
                "Month": calendar.month_name[month],
                "Earned": max(new_toil, 0),
                "Used": toil_used,
                "Net": new_toil - toil_used
            })
    
    current_balance = total_toil_earned - total_toil_used
    st.session_state.toil_balance = current_balance
    
    # Display balance
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total TOIL Earned", f"{total_toil_earned} days")
    with col2:
        st.metric("Total TOIL Used", f"{total_toil_used} days")
    with col3:
        st.metric("Current Balance", f"{current_balance} days", 
                 delta=f"{current_balance:+d}" if current_balance != 0 else None)
    
    if current_balance > 0:
        st.success(f"💰 Your employer owes you **{current_balance} TOIL day(s)**!")
    elif current_balance < 0:
        st.warning(f"⚠️ You've used **{-current_balance} more TOIL days** than earned")
    else:
        st.info("✅ Your TOIL account is balanced")
    
    # Monthly breakdown
    if monthly_data:
        st.subheader("Monthly Breakdown")
        df = pd.DataFrame(monthly_data)
        st.dataframe(df, use_container_width=True)
    
    # Manual balance adjustment
    st.subheader("Adjust Balance")
    col1, col2 = st.columns(2)
    with col1:
        new_balance = st.number_input("Set balance to:", value=current_balance, step=1)
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("Update Balance"):
            st.session_state.toil_balance = new_balance
            st.success("Balance updated!")
            st.rerun()

def show_data_management():
    """Data management page"""
    st.header("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Save Data")
        if st.button("Download Data", type="primary"):
            # Prepare data for download
            download_data = {}
            for year in st.session_state.data:
                download_data[str(year)] = {}
                for month in st.session_state.data[year]:
                    download_data[str(year)][str(month)] = {}
                    for day, day_data in st.session_state.data[year][month].items():
                        download_data[str(year)][str(month)][str(day)] = day_data
            
            download_data["_toil_balance"] = st.session_state.toil_balance
            
            # Create download link
            json_str = json.dumps(download_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="toil_data.json",
                mime="application/json"
            )
    
    with col2:
        st.subheader("Load Data")
        uploaded_file = st.file_uploader("Upload JSON file", type="json")
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                
                # Clear current data
                st.session_state.data.clear()
                
                # Load data
                for key in loaded_data:
                    if key == "_toil_balance":
                        st.session_state.toil_balance = loaded_data[key]
                    else:
                        year = int(key)
                        for month_str in loaded_data[key]:
                            month = int(month_str)
                            for day_str, day_data in loaded_data[key][month_str].items():
                                day = int(day_str)
                                st.session_state.data[year][month][day] = day_data
                
                st.success("Data loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    # Clear data
    st.subheader("Clear Data")
    if st.button("Clear All Data", type="secondary"):
        if st.checkbox("I'm sure I want to delete all data"):
            st.session_state.data.clear()
            st.session_state.toil_balance = 0
            st.success("All data cleared!")
            st.rerun()

if __name__ == "__main__":
    main()
