import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIG ---
TEAM_PIN = "1234"  # Change this to your actual secret PIN
st.set_page_config(page_title="Team Press-Up Tracker", page_icon="💪")

st.title("💪 Team Press-Up Tracker")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch Data from both tabs (Reps and Members)
# Note: Ensure your 'spreadsheet' secret points to the main URL
df_reps = conn.read(worksheet="Sheet1", ttl="0s")
df_members = conn.read(worksheet="Members", ttl="0s")

# --- SIDEBAR: LOG DATA ---
with st.sidebar:
    st.header("Log Your Reps")
    
    # Dynamically get names from the 'Members' tab
    if not df_members.empty:
        member_list = df_members["Name"].tolist()
        name = st.selectbox("Select Your Name", member_list)
    else:
        name = st.text_input("Enter Name (Members list empty)")

    reps = st.number_input("Number of Press-Ups", min_value=1, max_value=500, step=1)
    
    # PIN Security
    input_pin = st.text_input("Enter Team PIN", type="password")
    
    submit_button = st.button("Submit Entry")

    if submit_button:
        if input_pin == TEAM_PIN:
            new_data = pd.DataFrame([{
                "Date": date.today().strftime("%Y-%m-%d"),
                "Name": name,
                "Reps": reps
            }])
            
            # Combine and update the 'Sheet1' (Reps) tab
            updated_df = pd.concat([df_reps, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"Nice work, {name}! Data saved.")
            st.balloons()
        else:
            st.error("Incorrect PIN. Try again!")

# --- MAIN DASHBOARD ---
if not df_reps.empty:
    # Today's Leaderboard
    st.subheader("🏆 Today's Leaderboard")
    today = date.today().strftime("%Y-%m-%d")
    today_df = df_reps[df_reps['Date'] == today]
    
    if not today_df.empty:
        # Group by name in case someone logs multiple sets in one day
        leaderboard = today_df.groupby("Name")["Reps"].sum().sort_values(ascending=False)
        st.bar_chart(leaderboard)
    else:
        st.info("No reps recorded yet today. Be the first!")

    # Total History
    st.subheader("📈 Team Consistency")
    history_df = df_reps.groupby(["Date", "Name"])['Reps'].sum().unstack().fillna(0)
    st.line_chart(history_df)
else:
    st.write("The log is empty. Start training!")