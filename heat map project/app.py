import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import difflib
import os
from datetime import datetime
import openpyxl
import json

HISTORY_FILE = "history.json"

# Load chat history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        try:
            all_histories = json.load(f)
            if isinstance(all_histories, list):
                all_histories = {}  # reset if old format
        except:
            all_histories = {}
else:
    all_histories = {}


if "messages" not in st.session_state:
    st.session_state.messages = []

if "username" not in st.session_state:
    st.session_state.username = ""

# Page config
st.set_page_config(page_title="Chennai Risk Chatbot", page_icon="🌆")
st.markdown("""
    <style>
        .big-font { font-size:24px !important; }
        .highlight { color: #FF4B4B; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Chennai AI Risk Chatbot")
st.markdown("<p class='big-font'>Ask about <span class='highlight'>accidents, pollution, crime, heat, flood, population, or risk factors</span>.</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📜 Chat History by User")
    for user, history in all_histories.items():
        with st.expander(f"🧑 {user}"):
            for msg in history:
                if msg["role"] == "user":
                    st.markdown(f"- {msg['content']}")


# Load data
accident_df = pd.read_excel("accident.xlsx")
flood_df = pd.read_excel("flood.xlsx")
crime_df = pd.read_excel("crime_details.xlsx")
air_df = pd.read_excel("air_pollution.xlsx")
heat_df = pd.read_excel("heat.xlsx")
population_df = pd.read_excel("population.xlsx")
risk_df = pd.read_excel("riskanalysis.xlsx")

# Clean column headers
for df in [accident_df, flood_df, crime_df, air_df, heat_df, population_df, risk_df]:
    df.columns = df.columns.str.strip()

# Initialize session state
# Ask for user's name only once
if not st.session_state.username:
    name = st.text_input("👤 Enter your name to begin:", key="username_input")
    if name:
        st.session_state.username = name
        if name in all_histories:
            st.session_state.messages = all_histories[name]
        else:
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Hi {name}, welcome to Chennai AI Assistant Chatbot! 😊",
                "time": datetime.now().strftime("%I:%M %p")
            }]
        st.rerun()
    st.stop()



# Fuzzy zone matcher
def find_zone(query_text, zone_list):
    query_text = query_text.lower()
    for zone in zone_list:
        if zone.lower() in query_text:
            return zone
    for word in query_text.split():
        match = difflib.get_close_matches(word, zone_list, n=1, cutoff=0.6)
        if match:
            return match[0]
    return difflib.get_close_matches(query_text, zone_list, n=1, cutoff=0.6)[0] if difflib.get_close_matches(query_text, zone_list, n=1, cutoff=0.6) else None

# Plotting
def plot_bar(df, xcol, ycol, title, color='blue'):
    df = df[[xcol, ycol]].dropna()
    df[ycol] = pd.to_numeric(df[ycol], errors='coerce')
    df = df.groupby(xcol).sum().sort_values(ycol, ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df.index, df[ycol], color=color)
    ax.set_title(title)
    ax.set_ylabel(ycol)
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        ax.annotate(f"{int(bar.get_height())}", xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                    ha='center', va='bottom', fontsize=8)
    st.pyplot(fig)

# Display previous messages with visual responses
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        timestamp = msg.get("time", "")
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        role_name = "You" if msg["role"] == "user" else "AI"
        st.markdown(f"{role_icon} {role_name} {timestamp}")
        st.markdown(msg["content"])

    if msg["role"] == "assistant":
        zone = msg.get("zone", "")
        mtype = msg.get("type", "")
        
        def show_precaution(title, tips):
            st.markdown(f"### ⚠️ Precaution for {title}")
            for tip in tips:
                st.markdown(f"- {tip}")

        if mtype == "flood":
            st.dataframe(flood_df[flood_df["Zone"] == zone])
            plot_bar(flood_df, "Zone", "People Affected", "Flood Impact", "blue")
            show_precaution("Flood", [
                "Avoid walking or driving through flood waters.",
                "Relocate to higher ground in case of warnings.",
                "Stay updated through official alerts.",
                "Boil drinking water to avoid infections.",
                "Keep emergency contacts and supplies ready."
            ])

        elif mtype == "accident":
            st.dataframe(accident_df[accident_df["Zone"] == zone])
            plot_bar(accident_df, "Zone", "No. of Cases", "Accident Cases", "red")
            show_precaution("Road Accidents", [
                f"Drive carefully near {zone}.",
                "Follow all traffic signals and speed limits.",
                "Wear helmet/seatbelt at all times.",
                "Avoid using mobile phones while driving.",
                "Stay alert in crowded intersections."
            ])

        elif mtype == "crime":
            st.dataframe(crime_df[crime_df["Zone"] == zone])
            plot_bar(crime_df, "Zone", "Total Crimes", "Crime by Zone", "orange")
            show_precaution("Crime", [
                f"Avoid isolated areas in {zone}, especially at night.",
                "Always lock your doors and windows.",
                "Report any suspicious activity to police.",
                "Avoid sharing personal info with strangers.",
                "Install safety apps or devices."
            ])

        elif mtype == "pollution":
            st.dataframe(air_df[air_df["Zone"] == zone])
            plot_bar(air_df, "Zone", "Avg. Value (µg/m³) or AQI", "Air Pollution", "grey")
            show_precaution("Air Pollution", [
                f"Wear a mask when outdoors in {zone}.",
                "Avoid outdoor exercise during peak hours.",
                "Use air purifiers at home.",
                "Stay indoors if you have respiratory issues.",
                "Check AQI levels before planning activities."
            ])

        elif mtype == "heat":
            st.dataframe(heat_df[heat_df["Area"] == zone])
            plot_bar(heat_df, "Zone", "Heatstroke Cases", "Heatstroke Cases", "green")
            show_precaution("Heat", [
                f"Use an umbrella or cap in {zone}.",
                "Stay hydrated – drink plenty of water.",
                "Avoid outdoor activities during noon.",
                "Wear light and breathable clothes.",
                "Apply sunscreen to protect from sunburn."
            ])

        elif mtype == "population":
            st.dataframe(population_df[population_df["Zone"] == zone])
            plot_bar(population_df, "Zone", "Population", "Population by Zone", "purple")
            show_precaution("Crowded Areas", [
                f"Plan your commute to avoid traffic in {zone}.",
                "Stay aware of your surroundings in crowded places.",
                "Avoid peak hours when possible.",
                "Keep belongings safe to avoid theft.",
                "Use masks in crowded areas for hygiene."
            ])

        elif mtype == "risk":
            zone_data = risk_df[risk_df["Zone"] == zone]
            st.dataframe(zone_data)
            risk_cols = ["Accident", "Air Pollution", "Flood", "Heat", "Crime", "Population"]
            if not zone_data.empty and all(col in zone_data.columns for col in risk_cols):
                values = zone_data[risk_cols].iloc[0].values.astype(int)
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.bar(risk_cols, values, color='pink')
                ax.set_ylabel("Risk Level (1=Low, 2=Medium, 3=High)")
                plt.xticks(rotation=45)
                for bar in bars:
                    ax.annotate(f'{int(bar.get_height())}', 
                        xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), 
                        xytext=(0, 3), textcoords="offset points", ha='center')
                st.pyplot(fig)
                show_precaution("Overall Risk", [
                    f"Be aware of combined risk factors in {zone}.",
                    "Follow weather and safety alerts regularly.",
                    "Avoid unnecessary travel during risky times.",
                    "Practice good health and hygiene.",
                    "Stay informed using trusted government sources."
                ])
            else:
                st.warning("⚠ Risk data for this zone is incomplete or missing.")

            

# Chat input
query = st.chat_input("Type your query here...")
if query:
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({
        "role": "user", "content": query, "time": timestamp
    })
    
    q = query.lower()
    zone, reply_type, bot_reply = None, None, ""

    if "flood" in q or "rain" in q:
        zones = flood_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "flood"
        bot_reply = f"🌊 Flood Data for {zone}" if zone else "❗ Mention a valid area."

    elif "accident" in q:
        zones = accident_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "accident"
        bot_reply = f"🚧 Accidents in {zone}" if zone else "❗ Mention a valid area."

    elif "crime" in q:
        zones = crime_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "crime"
        bot_reply = f"🚔 Crimes in {zone}" if zone else "❗ Mention a valid zone."

    elif "pollution" in q or "air" in q:
        zones = air_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "pollution"
        bot_reply = f"🌫 Air Quality in {zone}" if zone else "❗ Mention a valid zone."

    elif "heat" in q or "temperature" in q:
        zones = heat_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "heat"
        bot_reply = f"🥵 Heat Impact in {zone}" if zone else "❗ Mention a valid zone."

    elif "population" in q:
        zones = population_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "population"
        bot_reply = f"👥 Population in {zone}" if zone else "❗ Mention a valid zone."

    elif "risk" in q or "riskfactor" in q or "risk factor" in q:
        zones = risk_df["Zone"].dropna().unique()
        zone = find_zone(q, zones)
        reply_type = "risk"
        bot_reply = f"🚨 Risk Factors in {zone}" if zone else "❗ Mention a valid zone."

    else:
        bot_reply = "❓ Try asking about accidents, air pollution, crime, heat, flood, population, or risk."

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "time": timestamp,
        "type": reply_type,
        "zone": zone
    })
    all_histories[st.session_state.username] = st.session_state.messages
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_histories, f, indent=2)


    st.rerun()
