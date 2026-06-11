import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------------

sheet_id = "1p36E9e6tx97J1jZ1cx9-6BRmCNaHAxaUOye-uPdlseE"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{sheet_id}/export?format=csv"
)

df = pd.read_csv(csv_url)

# -----------------------------------
# DATA CLEANING
# -----------------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True
)

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.markdown(
    """
    <div style="
        text-align:center;
        padding:10px;
        border-radius:12px;
        background:linear-gradient(
        135deg,
        rgba(0,255,136,0.18),
        rgba(0,120,90,0.12)
        );
        border:1px solid rgba(255,255,255,0.08);
        margin-bottom:15px;
    ">
        <h2 style="
            margin:0;
            color:#00FF88;
            box-shadow:
            0 0 18px rgba(0,255,136,0.12);
        ">
        ⚙ CONTROL CENTER
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    <span style="
        color:#B388FF;
        font-weight:bold;
        font-size:18px;
    ">
    🎯 ASSET
    </span>
    """,
    unsafe_allow_html=True
)
selected_asset = st.sidebar.multiselect(
    "",
    options=df["Asset"].unique(),
    default=df["Asset"].unique()
)
st.sidebar.markdown(
    """
    <hr style="
    border:none;
    height:1px;
    background:rgba(255,255,255,0.08);
    margin-top:8px;
    margin-bottom:8px;
    ">
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    <span style="
        color:#B388FF;
        font-weight:bold;
        font-size:18px;
    ">
    📍 TRADE SETUP
    </span>
    """,
    unsafe_allow_html=True
)
selected_direction = st.sidebar.multiselect(
    "",
    options=df["Direction"].unique(),
    default=df["Direction"].unique()
)
selected_result = st.sidebar.multiselect(
    "",
    options=df["Result"].unique(),
    default=df["Result"].unique()
)
st.sidebar.markdown(
    """
    <hr style="
    border:none;
    height:1px;
    background:rgba(255,255,255,0.08);
    margin-top:8px;
    margin-bottom:8px;
    ">
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    <span style="
        color:#B388FF;
        font-weight:bold;
        font-size:18px;
    ">
    📅 DATE RANGE
    </span>
    """,
    unsafe_allow_html=True
)
date_range = st.sidebar.date_input(
    "",
    value=(
        df["Date"].min().date(),
        df["Date"].max().date()
    )
)
start_date = pd.to_datetime(date_range[0])

end_date = pd.to_datetime(date_range[1])

filtered_df = df[
    (df["Asset"].isin(selected_asset))
    &
    (df["Direction"].isin(selected_direction))
    &
    (df["Result"].isin(selected_result))
    &
    (df["Date"] >= start_date)
    &
    (df["Date"] <= end_date)
]

# -----------------------------------
# CORE ANALYTICS
# -----------------------------------

total_trades = len(filtered_df)

wins = len(filtered_df[filtered_df["Result"] == "Win"])

losses = len(filtered_df[filtered_df["Result"] == "Loss"])

breakevens = len(
    filtered_df[
        filtered_df["Result"]
        .astype(str)
        .str.strip()
        .isin(
            [
                "BE",
                "Breakeven",
                "BreakEven",
                "B/E"
            ]
        )
    ]
)

# WINRATE EXCLUDING BREAKEVENS

winrate_denominator = wins + losses

if winrate_denominator > 0:
    winrate = (wins / winrate_denominator) * 100
else:
    winrate = 0

# AVERAGES

average_risk = filtered_df["Risk %"].mean()

average_rrr = filtered_df["RRR"].mean()

# PERFORMANCE

total_fees = filtered_df["Fees"].sum()

total_net_pnl = filtered_df["Net PnL"].sum()
total_gross_pnl = filtered_df["PnL"].sum()

overall_return = (
    filtered_df["Overall Return%(compounded)"]
    .iloc[-1]
)
starting_capital = 2930

current_capital = filtered_df[
    "Trade Amount"
].iloc[-1]

peak_capital = filtered_df[
    "Trade Amount"
].max()

distance_from_peak = (
    (
        current_capital -
        peak_capital
    )
    /
    peak_capital
) * 100

# -----------------------------------
# TRADE INTERVAL ANALYSIS
# -----------------------------------

filtered_df = filtered_df.sort_values("Date")

filtered_df["Trade Gap"] = (
    filtered_df["Date"]
    .diff()
    .dt.days
)

average_trade_gap = (
    filtered_df["Trade Gap"]
    .mean()
)

# LONGEST GAP

longest_gap = filtered_df["Trade Gap"].max()

# SHORTEST GAP

shortest_gap = filtered_df["Trade Gap"].min()

# ACTIVE TRADING DAYS

active_trading_days = (
    filtered_df["Date"]
    .dt.date
    .nunique()
)

# -----------------------------------
# FREQUENCY STATE DETECTOR
# -----------------------------------

if average_trade_gap <= 2:
    frequency_state = "Aggressive"

elif average_trade_gap <= 7:
    frequency_state = "Balanced"

elif average_trade_gap <= 14:
    frequency_state = "Selective"

else:
    frequency_state = "Inactive"

# -----------------------------------
# WEEKLY ACTIVITY
# -----------------------------------

filtered_df["Week"] = (
    filtered_df["Date"]
    .dt.strftime("%Y-%U")
)

weekly_activity = (
    filtered_df
    .groupby("Week")
    .size()
    .reset_index(name="Trades")
)

# -----------------------------------
# MONTHLY PERFORMANCE
# -----------------------------------

filtered_df["Month"] = (
    filtered_df["Date"]
    .dt.strftime("%b %Y")
)

monthly_performance = (
    filtered_df
    .groupby("Month")
    .agg({
        "Return %(per trade)": "sum",
        "Net PnL": "sum"
    })
    .reset_index()
)

# -----------------------------------
# YEARLY ACTIVITY
# -----------------------------------

filtered_df["Year"] = (
    filtered_df["Date"]
    .dt.year
)

yearly_activity = (
    filtered_df
    .groupby("Year")
    .size()
    .reset_index(name="Trades")
)
# -----------------------------------
# DAY OF WEEK ANALYTICS
# -----------------------------------

filtered_df["Day"] = (
    filtered_df["Date"]
    .dt.day_name()
)

day_summary = (
    filtered_df
    .groupby("Day")
    .agg({
        "Trade No": "count",
        "Net PnL": "sum"
    })
    .reset_index()
)

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

day_summary["Day"] = pd.Categorical(
    day_summary["Day"],
    categories=day_order,
    ordered=True
)

day_summary = day_summary.sort_values("Day")
# -----------------------------------
# DRAWDOWN ENGINE
# -----------------------------------

# EQUITY CURVE

filtered_df["Equity"] = (
    filtered_df["Trade Amount"]
)

# RUNNING PEAK

filtered_df["Peak Equity"] = (
    filtered_df["Equity"]
    .cummax()
)

# DRAWDOWN %

filtered_df["Drawdown %"] = (
    (
        filtered_df["Equity"]
        - filtered_df["Peak Equity"]
    )
    / filtered_df["Peak Equity"]
) * 100

# MAX DRAWDOWN

max_drawdown = (
    filtered_df["Drawdown %"]
    .min()
)

# CURRENT DRAWDOWN

current_drawdown = (
    filtered_df["Drawdown %"]
    .iloc[-1]
)

# -----------------------------------
# RECOVERY DURATION
# -----------------------------------

recovery_counter = 0

recovery_periods = []

max_recovery_duration = 0

for dd in filtered_df["Drawdown %"]:

    if dd < 0:

        recovery_counter += 1

    else:

        if recovery_counter > 0:

            recovery_periods.append(
                recovery_counter
            )

            if recovery_counter > max_recovery_duration:

                max_recovery_duration = recovery_counter

        recovery_counter = 0

if recovery_counter > 0:

    recovery_periods.append(
        recovery_counter
    )

average_recovery_duration = (
    sum(recovery_periods)
    / len(recovery_periods)
    if len(recovery_periods) > 0
    else 0
)
        
# -----------------------------------
# STREAK ANALYTICS
# -----------------------------------

current_win_streak = 0
current_loss_streak = 0

best_win_streak = 0
worst_loss_streak = 0

temp_win = 0
temp_loss = 0

for result in filtered_df["Result"]:

    if result == "Win":

        temp_win += 1
        temp_loss = 0

        if temp_win > best_win_streak:
            best_win_streak = temp_win

    elif result == "Loss":

        temp_loss += 1
        temp_win = 0

        if temp_loss > worst_loss_streak:
            worst_loss_streak = temp_loss

for result in reversed(
    filtered_df["Result"].tolist()
):

    if result == "Win":
        current_win_streak += 1
    else:
        break

for result in reversed(
    filtered_df["Result"].tolist()
):

    if result == "Loss":
        current_loss_streak += 1
    else:
        break
with open("background.jpg", "rb") as image_file:
    encoded_bg = base64.b64encode(
        image_file.read()
    ).decode()
# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown(f"""
<style>

.block-container
{{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}}
.stApp
{{
    background:
    linear-gradient(
        rgba(5,8,15,0.7),
        rgba(5,8,15,0.7)
    ),
    url("data:image/jpg;base64,{encoded_bg}");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
h1
{{
    font-size: 2.8rem !important;
}}

h2
{{
    padding-top: 1rem;
    padding-bottom: 0.5rem;
}}

a[href^="#"],
h1 a,
h2 a,
h3 a
{{
    display:none !important;
}}
div[data-testid="stMetric"]
{{
    background: linear-gradient(
        135deg,
        rgba(35,35,35,0.35),
        rgba(15,15,15,0.55)
    );

    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 20px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.05);

    padding: 18px;
}}
div[data-testid="column"] {{
    padding-left: 8px;
    padding-right: 8px;
}}
section[data-testid="stSidebar"] {{
    background: rgba(10,10,10,0.75);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);

    border-right: 1px solid rgba(255,255,255,0.08);
}}
div[data-baseweb="tag"] {{
    background: linear-gradient(
        135deg,
        rgba(0,245,255,0.20),
        rgba(0,255,136,0.20)
    ) !important;

    border: 1px solid rgba(0,245,255,0.25) !important;

    color: white !important;

    border-radius: 8px !important;
}}
button[data-baseweb="tab"] {{
    background: rgba(20,20,20,0.45);

    border: 3px solid rgba(255,255,255,0.08);

    border-radius: 14px;

    margin-right: 50px;

    padding-left: 40px;

    padding-right: 40px;

    padding-top: 8px;

    padding-bottom: 8px;

    min-height: 42px;

    color: white;

    transition: all 0.25s ease;
}}

div[data-baseweb="tab-list"] {{
    gap: 8px;
}}
button[data-baseweb="tab"]:hover {{
    border-color: rgba(0,245,255,0.40);

    box-shadow:
        0 0 12px rgba(0,245,255,0.18);
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    background:
    linear-gradient(
        135deg,
        rgba(0,245,255,0.15),
        rgba(0,255,136,0.12)
    );

    border-color:
        rgba(0,245,255,0.35);

    box-shadow:
        0 0 16px rgba(0,245,255,0.15);
}}
span[data-baseweb="tag"] {{
    background: linear-gradient(
        135deg,
        rgba(0,255,136,0.25),
        rgba(0,180,120,0.25)
    ) !important;

    border: 1px solid rgba(0,255,136,0.50) !important;

    color: white !important;

    border-radius: 8px !important;

    box-shadow:
        0 0 10px rgba(0,255,136,0.15) !important;
}}

span[data-baseweb="tag"] * {{
    color: white !important;
}}
/* BLACK TEXT INSIDE SELECTED DATES */

div[aria-label*="Selected"] div {{
    color: black !important;
    font-weight: 700 !important;
}}
</style>
""", unsafe_allow_html=True)
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(20,20,20,0.45)",
    paper_bgcolor="rgba(20,20,20,0.25)",
    font=dict(
        color="white",
        size=12
    ),
    title_font=dict(
        size=18
    ),
    
    hovermode="x",

    hoverlabel=dict(
        bgcolor="#0B1220",
        bordercolor="#00F5FF",
        font_size=14,
        font_color="white"
    ),
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.03)",
        zeroline=False
    )

)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown("---")
st.markdown(
    """
    <h1 style="
        text-align:center;
        background:linear-gradient(
            90deg,
            #00F5FF,
            #00FF88
        );
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:5px;
    ">
    TRADING PERFORMANCE TERMINAL
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

overview_tab, behavior_tab, edge_tab, risk_tab, performance_tab = st.tabs(
    [
        "📊 Overview",
        "📅 Behavior",
        "🎯 Edge",
        "⚠️ Risk",
        "📈 Performance"
    ]
)
# =====================================
# OVERVIEW SECTION
# =====================================
if total_trades < 8:

    trading_status = "📊 EARLY DATA"
    status_color = "#7700FF"

elif distance_from_peak <= -15:

    trading_status = "🔄 UNDER RECOVERY"
    status_color = "#FFA500"

elif distance_from_peak >= -2:

    trading_status = "🔥 STRONG MOMENTUM"
    status_color = "#FFD700"

elif (
    overall_return > 0
    and winrate >= 55
):

    trading_status = "✅ CONSISTENTLY PROFITABLE"
    status_color = "#00FF88"

elif overall_return > 0:

    trading_status = "📈 BUILDING CONSISTENCY"
    status_color = "#00BFFF"

else:

    trading_status = "⚠ DEVELOPING EDGE"
    status_color = "#FF4B4B"
with overview_tab:
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    📊 Executive Summary
    </h2>

    """,
    unsafe_allow_html=True
    )
    st.markdown(
        "<div style='height:20px'></div>",
        unsafe_allow_html=True
    )
    overview_row = st.columns(5)
    with overview_row[0]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                    letter-spacing:1px;
                ">
                    TOTAL TRADES
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px currentColor;
                    color:#00F5FF;
                ">
                    {total_trades}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with overview_row[1]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    WIN RATE
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px currentColor;
                    color:#00FF88;
                ">
                    {winrate:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with overview_row[2]:

        gross_color = (
            "#00FF88"
            if total_gross_pnl >= 0
            else "#FF4B4B"
        )

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    GROSS PNL
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px currentColor;
                    color:{gross_color};
                ">
                    ₹{total_gross_pnl:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with overview_row[3]:

        pnl_color = (
            "#00FF88"
            if total_net_pnl >= 0
            else "#FF4B4B"
        )

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    NET PNL
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px currentColor;
                    color:{pnl_color};
                ">
                    ₹{total_net_pnl:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with overview_row[4]:

        return_color = (
            "#FFD700"
            if overall_return >= 0
            else "#FF4B4B"
        )

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    OVERALL RETURN
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px currentColor;
                    color:{return_color};
                ">
                    {overall_return:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown(
        "<div style='height:35px'></div>",
        unsafe_allow_html=True
    )
    record_row = st.columns(5)
    with record_row[0]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    WINS
                </div>
                <div style="
                    color:#00FF88;
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px rgba(0,255,136,0.45);
                    margin-left:0px;
                ">
                    {wins}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with record_row[1]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    LOSSES
                </div>
                <div style="
                    color:#FF4B4B;
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px rgba(0,255,136,0.45);
                    margin-left:0px;
                ">
                    {losses}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with record_row[2]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    BE
                </div>
                <div style="
                    color:#FFD700;
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px rgba(255,215,0,0.45);
                    margin-left:0px;
                ">
                    {breakevens}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    best_trade = filtered_df[
        "Net PnL"
    ].max()
    with record_row[3]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    BEST
                </div>
                <div style="
                    color:#00FF88;
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px rgba(0,255,136,0.45);
                    margin-left:0px;
                ">
                    ₹{best_trade:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    worst_trade = filtered_df[
        "Net PnL"
    ].min()
    with record_row[4]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    WORST
                </div>
                <div style="
                    color:#FF4B4B;
                    font-size:42px;
                    font-weight:800;
                    text-shadow:
                    0 0 5px rgba(255,75,75,0.45);
                    margin-left:0px;
                ">
                    ₹{worst_trade:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown(
        "<div style='height:40px'></div>",
        unsafe_allow_html=True
    )
    capital_row = st.columns(4)
    with capital_row[0]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    STARTING CAPITAL
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    color:#00F5FF;
                    text-shadow:
                    0 0 5px rgba(0,245,255,0.40);
                ">
                    ₹{starting_capital:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with capital_row[1]:
        
        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    CURRENT CAPITAL
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    color:#00FF88;
                    text-shadow:
                    0 0 5px rgba(0,245,255,0.40);
                ">
                    ₹{current_capital:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with capital_row[2]:
       
        st.markdown(
            f"""
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    PEAK CAPITAL
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    color:#FFD700;
                    text-shadow:
                    0 0 5px rgba(0,245,255,0.40);
                ">
                    ₹{peak_capital:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    distance_color = (
        "#00FF88"
        if distance_from_peak >= 0
        else "#FF4B4B"
    )
    with capital_row[3]:

        st.markdown(
            f"""
            
            <div style="
                text-align:center;
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    DISTANCE FROM PEAK
                </div>
                <div style="
                    font-size:42px;
                    font-weight:800;
                    color:{distance_color};
                    text-shadow:
                    0 0 5px {distance_color};
                ">
                    {distance_from_peak:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='height:50px'></div>",
            unsafe_allow_html=True
        )
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:30px 0;
        ">
            <div style="
                color:#AAAAAA;
                font-size:16px;
                letter-spacing:3px;
                margin-bottom:12px;
            ">
                TRADING STATUS
            </div>
            <div style="
                font-size:52px;
                font-weight:900;
                color:{status_color};
                text-shadow:
                0 0 5px {status_color};
            ">
                {trading_status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------
    # MAIN KPI CARDS
    # -----------------------------------

    
    
# =====================================
# BEHAVIOR SECTION
# =====================================
with behavior_tab:
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    📅 Behavioral Analytics
    </h2>
    """,
    unsafe_allow_html=True
)
    # -----------------------------------
    # TRADE FREQUENCY ANALYTICS
    # -----------------------------------
    
    max_gap_reference = max(
        longest_gap,
        1
    )

    avg_gap_pct = (
        average_trade_gap
        / max_gap_reference
    ) * 100

    short_gap_pct = (
        shortest_gap
        / max_gap_reference
    ) * 100
    st.markdown(
        """
        <div style="height:20px;"></div>
        """,
        unsafe_allow_html=True
    )
    freq_left, freq_right = st.columns([3,1])
    with freq_left:
        st.markdown(
            f"""
            
            <div style="
                color:#FFD700;
                font-weight:700;
                margin-bottom:10px;
                margin-top:20px;
            ">
                AVERAGE GAP
            </div>
            <div style="
                display:flex;
                align-items:center;
                gap:0px;
                width:100%;
            ">
                <div style="
                    width:80px;
                    height:80px;
                    border-radius:50%;
                    border:2px solid ##FFD700;
                    box-shadow:0 0 12px rgba(255,215,0,0.35);
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    flex-shrink:0;
                    z-index:2;
                    background:rgba(15,15,15,0.95);
                ">
                    <div style="
                        font-size:25px;
                        font-weight:700;
                        color:white;
                        line-height:1;
                    ">
                        {average_trade_gap:.1f}
                    </div>
                    <div style="
                        color:#AAAAAA;
                        font-size:12px;
                    ">
                        Days
                    </div>
                </div>
                <div style="
                    width:65%;
                    height:22px;
                    margin-left:-15px;
                    background:rgba(255,255,255,0.06);
                    overflow:hidden;
                    position:relative;
                ">
                    <div style="
                        width:{avg_gap_pct}%;
                        height:100%;
                        background:linear-gradient(
                            90deg,
                            #FF8A00,
                            #FFD700
                        );
                        border-radius:999px;
                    ">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='height:18px'></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            
            <div style="
                color:#C44DFF;
                font-weight:700;
                margin-bottom:10px;
                margin-top:20px;
            ">
                SHORTEST GAP
            </div>
            <div style="
                display:flex;
                align-items:center;
                gap:0px;
                width:100%;
            ">
                <div style="
                    width:80px;
                    height:80px;
                    border-radius:50%;
                    border:2px solid ##C44DFF;
                    box-shadow:0 0 12px rgba(0,255,136,0.35);
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    flex-shrink:0;
                    z-index:2;
                    background:rgba(15,15,15,0.95);
                ">
                    <div style="
                        font-size:25px;
                        font-weight:700;
                        color:white;
                        line-height:1;
                    ">
                        {shortest_gap:.0f}
                    </div>
                    <div style="
                        color:#AAAAAA;
                        font-size:12px;
                    ">
                        Days
                    </div>
                </div>
                <div style="
                    width:65%;
                    height:22px;
                    margin-left:-15px;
                    background:rgba(255,255,255,0.06);
                    overflow:hidden;
                    position:relative;
                ">
                    <div style="
                        width:{short_gap_pct}%;
                        height:100%;
                        background: linear-gradient(
                            90deg,
                            #7A5CFF,
                            #C44DFF
                        );
                        border-radius:999px;
                    ">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='height:18px'></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            
            <div style="
                color:#00F5FF;
                font-weight:700;
                margin-bottom:10px;
                margin-top:20px;
            ">
                LONGEST GAP
            </div>
            <div style="
                display:flex;
                align-items:center;
                gap:0px;
                width:100%;
            ">
                <div style="
                    width:80px;
                    height:80px;
                    border-radius:50%;
                    border:2px solid ##00F5FF;
                    box-shadow:0 0 12px rgba(0,245,255,0.35);
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    flex-shrink:0;
                    z-index:2;
                    background:rgba(15,15,15,0.95);
                ">
                    <div style="
                        font-size:25px;
                        font-weight:700;
                        color:white;
                        line-height:1;
                    ">
                        {longest_gap:.0f}
                    </div>
                    <div style="
                        color:#AAAAAA;
                        font-size:12px;
                    ">
                        Days
                    </div>
                </div>
                <div style="
                    width:65%;
                    height:22px;
                    margin-left:-15px;
                    background:rgba(255,255,255,0.06);
                    overflow:hidden;
                    position:relative;
                ">
                    <div style="
                        width:100%;
                        height:100%;
                        background:linear-gradient(
                            90deg,
                            #00A3FF,
                            #00F5FF
                        );
                        border-radius:999px;
                    ">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with freq_right:
        st.markdown(
            f"""
            <div style="
                height:100%;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                margin-top:160px;
                margin-left:-550px;
            ">
                <div style="
                    color:#B0B0B0;
                    font-size:16px;
                    letter-spacing:4px;
                    margin-bottom:20px;
                ">
                    TRADING RHYTHM
                </div>
                <div style="
                    color:#00FF88;
                    font-size:52px;
                    font-weight:800;
                    text-shadow:
                        0 0 8px rgba(0,255,136,0.35),
                        0 0 20px rgba(0,255,136,0.20);
                    text-align:center;
                ">
                    {frequency_state.upper()}
                </div>
                <div style="
                    width:220px;
                    height:2px;
                    background:linear-gradient(
                        90deg,
                        transparent,
                        rgba(0,255,136,0.7),
                        transparent
                    );
                    margin-top:20px;
                ">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
# -----------------------------------
# TRADING CONSISTENCY HEATMAP
# -----------------------------------
    profit_days = len(
        filtered_df[
            filtered_df["Result"] == "Win"
        ]
    )

    loss_days = len(
        filtered_df[
            filtered_df["Result"] == "Loss"
        ]
    )

    be_days = len(
        filtered_df[
            filtered_df["Result"]
            .astype(str)
            .str.strip()
            .isin([
                "BE",
                "Breakeven",
                "BreakEven",
                "B/E"
            ])
        ]
    )
    st.markdown(
        "<div style='height:60px'></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h2 style="
            color:#E5E7EB;
            border-bottom:2px solid rgba(0,245,255,0.30);
            padding-bottom:10px;
            margin-bottom:25px;
            font-weight:700;
        ">
        🗓 Trading Consistency Heatmap
        </h2>
        """,
        unsafe_allow_html=True
    )
    import calendar
    
    top_row = st.columns([0.5, 1, 1])

    with top_row[0]:

        selected_year = st.selectbox(
            "Calendar Year",
            [2026, 2027],
            index=0
        )

    with top_row[1]:

        active_days = len(
            pd.to_datetime(
                filtered_df["Date"],
                dayfirst=True
            ).dt.date.unique()
        )

        st.markdown(
            f"""
            <div style="
                margin-top:35px;
                text-align:center;
                font-size:15px;
                font-weight:600;
            ">
                <span style="
                    color:#BBBBBB;
                ">
                    ACTIVE DAYS
                </span>
                <span style="
                    color:#00FF88;
                    font-size:28px;
                    font-weight:800;
                    margin-left:10px;
                    text-shadow:0 0 10px rgba(0,255,136,0.35);
                ">
                    {active_days}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with top_row[2]:
        latest_trade_date = pd.to_datetime(
            filtered_df["Date"],
            dayfirst=True
        ).max()
        

        start_of_year = pd.Timestamp(
            year=selected_year,
            month=1,
            day=1
        )

        days_elapsed = (
            latest_trade_date -
            start_of_year
        ).days + 1

        inactive_days = max(
            0,
            days_elapsed - active_days
        )

        st.markdown(
            f"""
            <div style="
                margin-top:35px;
                text-align:center;
                font-size:15px;
                font-weight:600;
            ">
                <span style="
                    color:#BBBBBB;
                ">
                    INACTIVE DAYS
                </span>
                <span style="
                    color:#FF4B4B;
                    font-size:28px;
                    font-weight:800;
                    margin-left:10px;
                    text-shadow:0 0 10px rgba(255,75,75,0.30);
                ">
                    {inactive_days}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    summary1, summary2, summary3 = st.columns(3)

    heatmap_cols = st.columns([1])

    with heatmap_cols[0]:

        import plotly.graph_objects as go
        import numpy as np
        import calendar
        all_x = []
        all_y = []
        all_z = []
        hover_data = []

        month_tickvals = []
        month_ticktext = []

        current_x_offset = 0
        for month in range(1, 13):

            month_tickvals.append(current_x_offset + 2)
            month_ticktext.append(
                calendar.month_abbr[month]
            )
            calendar.setfirstweekday(
                calendar.SUNDAY
            )           

            month_cal = calendar.monthcalendar(
                selected_year,
                month
            )

            for week_idx, week in enumerate(month_cal):

                for weekday_idx, day_num in enumerate(week):

                    if day_num == 0:
                        continue

                    current_date = pd.Timestamp(
                        year=selected_year,
                        month=month,
                        day=day_num
                    )

                    matching_trade = filtered_df[
                        pd.to_datetime(
                            filtered_df["Date"],
                            dayfirst=True
                        ).dt.date
                        ==
                        current_date.date()
                    ]

                    value = 0
                    date_text = ""

                    asset_name = ""
                    net_pnl_text = ""
                    return_text = ""

                    if len(matching_trade) > 0:

                        result = str(
                            matching_trade.iloc[0]["Result"]
                        ).strip()
                        date_text = current_date.strftime(
                            "%d %B %Y"
                        )
                        asset_name = str(
                            matching_trade.iloc[0]["Asset"]
                        )

                        net_pnl = matching_trade.iloc[0][
                            "Net PnL"
                        ]

                        trade_return = matching_trade.iloc[0][
                            "Return %(per trade)"
                        ]

                        net_pnl_color = (
                            "#00FF88"
                            if net_pnl > 0
                            else "#FF4B4B"
                        )

                        return_color = (
                            "#00FF88"
                            if trade_return > 0
                            else "#FF4B4B"
                        )

                        net_pnl_text = (
                            f"<span style='color:{net_pnl_color}; font-weight:700;'>"
                            f"+₹{net_pnl:,.0f}"
                            "</span>"
                            if net_pnl > 0
                            else
                            f"<span style='color:{net_pnl_color}; font-weight:700;'>"
                            f"-₹{abs(net_pnl):,.0f}"
                            "</span>"
                        )

                        return_text = (
                            f"<span style='color:{return_color}; font-weight:700;'>"
                            f"+{trade_return:.0f}%"
                            "</span>"
                            if trade_return > 0
                            else
                            f"<span style='color:{return_color}; font-weight:700;'>"
                            f"{trade_return:.0f}%"
                            "</span>"
                        )

                        if result == "Win":
                            value = 3

                        elif result == "Loss":
                            value = 2

                        elif result in [
                            "BE",
                            "Breakeven",
                            "BreakEven",
                            "B/E"
                        ]:
                            value = 1

                    all_x.append(
                        current_x_offset + week_idx
                    )

                    all_y.append(
                        weekday_idx
                    )

                    all_z.append(
                        value
                    )
                    hover_data.append(

                        ""

                        if value == 0

                        else

                        [
                            date_text,
                            asset_name,
                            net_pnl_text,
                            return_text
                        ]
                    )

            current_x_offset += (
                len(month_cal) + 1
            )
            
        heatmap_fig = go.Figure()

        empty_x = []
        empty_y = []

        trade_x = []
        trade_y = []
        trade_colors = []
        trade_hover = []
        for x, y, z, h in zip(
            all_x,
            all_y,
            all_z,
            hover_data
        ):

            if z == 0:

                empty_x.append(x)
                empty_y.append(y)

            else:

                trade_x.append(x)
                trade_y.append(y)

                trade_colors.append(

                    "#FFD700"
                    if z == 1

                    else "#FF4B4B"
                    if z == 2

                    else "#00FF88"

                )

                trade_hover.append(h)
        heatmap_fig.add_trace(

            go.Scatter(

                x=empty_x,
                y=empty_y,
                showlegend=False,

                mode="markers",

                marker=dict(

                    symbol="square",

                    size=20,

                    color="#1A1A1A",

                    line=dict(
                        width=1,
                        color="#111111"
                    )

                ),

                hoverinfo="skip"

            )

        )
        heatmap_fig.add_trace(

            go.Scatter(

                x=trade_x,
                y=trade_y,
                showlegend=False,

                mode="markers",

                customdata=trade_hover,

                hovertemplate=
                "<b>%{customdata[0]}</b><br><br>"
                "%{customdata[1]}<br>"
                "%{customdata[2]}<br>"
                "%{customdata[3]}"
                "<extra></extra>",

                marker=dict(

                    symbol="square",

                    size=20,

                    color=trade_colors,

                    line=dict(
                        width=1,
                        color="rgba(255,255,255,0.25)"
                    )

                )

            )

        )
        heatmap_fig.update_layout(
            
            hoverlabel=dict(
                bgcolor="#111111",
                bordercolor="#00F5FF",
                font=dict(
                    size=16,
                    color="white"
                )
            ),
            showlegend=False,
            height=380,

            margin=dict(
                l=40,
                r=20,
                t=20,
                b=30
            ),

            paper_bgcolor="#111111",

            plot_bgcolor="#111111",

            xaxis=dict(

                tickmode="array",

                tickvals=month_tickvals,

                ticktext=month_ticktext,

                tickfont=dict(
                    color="#E5E7EB",
                    size=13
                ),

                showgrid=False,

                zeroline=False,

                fixedrange=True
            ),

            yaxis=dict(

                tickmode="array",

                tickvals=[
                    0,1,2,3,4,5,6
                ],

                ticktext=[
                    "Sun",
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat"
                ],

                autorange="reversed",

                tickfont=dict(
                    color="#E5E7EB",
                    size=12
                ),

                showgrid=False,

                zeroline=False,

                fixedrange=True
            )
        )
        st.plotly_chart(
            heatmap_fig,
            use_container_width=True
        )
    st.markdown(
        "<div style='height:40px'></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h2 style="
            color:#E5E7EB;
            border-bottom:2px solid rgba(0,245,255,0.30);
            padding-bottom:10px;
            margin-bottom:25px;
            font-weight:700;
        ">
        ⚡ Streak Analytics
        </h2>
        """,
        unsafe_allow_html=True
    )

    streak_cols = st.columns(3)
    with streak_cols[0]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding:20px;
            ">
                <div style="
                    font-size:15px;
                    color:#AAAAAA;
                    letter-spacing:1px;
                ">
                    BEST STREAK
                </div>
                <div style="
                    font-size:56px;
                    font-weight:800;
                    color:#00FF88;
                    text-shadow:
                    0 0 10px rgba(0,255,136,0.45);
                ">
                    {best_win_streak}
                </div>
                <div style="
                    color:#00FF88;
                    font-size:16px;
                    font-weight:600;
                ">
                    Consecutive Wins
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with streak_cols[1]:
        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding:20px;
            ">
                <div style="
                    font-size:15px;
                    color:#AAAAAA;
                    letter-spacing:1px;
                ">
                    WORST STREAK
                </div>
                <div style="
                    font-size:56px;
                    font-weight:800;
                    color:#FF4B4B;
                    text-shadow:
                    0 0 10px rgba(255,75,75,0.45);
                ">
                    {worst_loss_streak}
                </div>
                <div style="
                    color:#FF4B4B;
                    font-size:16px;
                    font-weight:600;
                ">
                    Consecutive Losses
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if current_win_streak > 0:
            current_value = current_win_streak
            current_label = "Current Wins"
            current_color = "#00F5FF"
        elif current_loss_streak > 0:
            current_value = current_loss_streak
            current_label = "Current Losses"
            current_color = "#FFA500"
        else:
            current_value = 0
            current_label = "Neutral"
            current_color = "#AAAAAA"
        with streak_cols[2]:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:20px;
                ">
                    <div style="
                        font-size:15px;
                        color:#AAAAAA;
                        letter-spacing:1px;
                    ">
                        CURRENT STREAK
                    </div>
                    <div style="
                        font-size:56px;
                        font-weight:800;
                        color:{current_color};
                        text-shadow:
                        0 0 7px {current_color};
                    ">
                        {current_value}
                    </div>
                    <div style="
                        color:{current_color};
                        font-size:16px;
                        font-weight:600;
                    ">
                        {current_label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.markdown(
        "<div style='height:25px'></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h2 style="
            color:#E5E7EB;
            border-bottom:2px solid rgba(0,245,255,0.30);
            padding-bottom:10px;
            margin-bottom:25px;
            font-weight:700;
        ">
        📈 Recent Trade Momentum
        </h2>
        """,
        unsafe_allow_html=True
    )

    import plotly.graph_objects as go

    recent_trades = filtered_df.tail(10).copy()
    x_vals = []
    y_vals = []
    colors = []
    texts = []
    hover_data = []
    for idx, (_, row) in enumerate(
        recent_trades.iterrows()
    ):

        result = str(
            row["Result"]
        ).strip()

        if result == "Win":

            color = "#00FF88"
            label = "W"

        elif result == "Loss":

            color = "#FF4B4B"
            label = "L"

        else:

            color = "#FFD700"
            label = "BE"

        date_text = pd.to_datetime(
            row["Date"],
            dayfirst=True
        ).strftime(
            "%d %b %Y"
        )

        x_vals.append(idx)

        y_vals.append(0)

        colors.append(color)

        texts.append(label)

        hover_data.append([
            date_text,
            row["Asset"],
            row["Net PnL"],
            row["Return %(per trade)"]
        ])
    momentum_fig = go.Figure()
    momentum_fig.add_trace(

        go.Scatter(

            x=x_vals,

            y=y_vals,

            mode="markers+text",

            text=texts,

            textposition="middle center",

            textfont=dict(
                size=14,
                color="black",
                family="Arial Black"
            ),

            customdata=hover_data,

            hovertemplate=
            "<b>%{customdata[0]}</b><br><br>"
            "%{customdata[1]}<br>"
            "₹%{customdata[2]:,.0f}<br>"
            "%{customdata[3]:.2f}%"
            "<extra></extra>",

            marker=dict(

                size=42,

                color=colors,

                symbol="square",

                line=dict(
                    width=2,
                    color="white"
                )

            )

        )

    )
    momentum_fig.update_layout(
        height=140,

        margin=dict(
            l=20,
            r=20,
            t=10,
            b=10
        ),

        paper_bgcolor="#111111",

        plot_bgcolor="#111111",

        xaxis=dict(
            visible=False
        ),

        yaxis=dict(
            visible=False
        ),

        showlegend=False
    )
    st.plotly_chart(
        momentum_fig,
        use_container_width=True
    )
    st.markdown(
        "<div style='height:20px'></div>",
        unsafe_allow_html=True
    )
    recent_8 = filtered_df.tail(8).copy()

    recent_results = []

    for result in recent_8["Result"]:

        result = str(result).strip()

        if result == "Win":
            recent_results.append("Win")

        elif result == "Loss":
            recent_results.append("Loss")
        recent_wins = recent_results.count(
            "Win"
        )

        recent_losses = recent_results.count(
            "Loss"
        )

        total_recent = (
            recent_wins +
            recent_losses
        )
        if total_recent > 0:

            recent_winrate = (
                recent_wins /
                total_recent
            ) * 100

        else:

            recent_winrate = 0
        if current_loss_streak >= 3:

            momentum_status = "⚠ UNDER PRESSURE"
            momentum_color = "#FF4B4B"

        elif current_win_streak >= 4:

            momentum_status = "🔥 HOT STREAK"
            momentum_color = "#00FF88"

        elif current_loss_streak >= 2:

            momentum_status = "↘ COOLING OFF"
            momentum_color = "#FFA500"

        elif current_win_streak >= 2 and recent_winrate < 50:

            momentum_status = "↗ RECOVERING"
            momentum_color = "#00BFFF"

        elif recent_winrate >= 70:

            momentum_status = "⚡ STRONG"
            momentum_color = "#00F5FF"

        else:

            momentum_status = "◉ BALANCED"
            momentum_color = "#FFD700"
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding-top:10px;
            padding-bottom:15px;
        ">
            <div style="
                color:#AAAAAA;
                font-size:14px;
                letter-spacing:2px;
                margin-bottom:10px;
            ">
                TRADING MOMENTUM
            </div>
            <div style="
                font-size:42px;
                font-weight:800;
                color:{momentum_color};
                text-shadow:
                0 0 4px {momentum_color};
            ">
                {momentum_status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================
# EDGE SECTION
# =====================================
with edge_tab:
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    🎯 Asset Edge Analytics
    </h2>
    """,
    unsafe_allow_html=True
)
    # -----------------------------------
    # ASSET EDGE ENGINE
    # -----------------------------------

    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)

    asset_summary = (
        filtered_df
        .groupby("Asset")
        .agg({
            "Trade No": "count",
            "Net PnL": "sum",
            "Return %(per trade)": "sum"
        })
        .reset_index()
    )

    # WINRATE CALCULATION PER ASSET

    asset_winrates = []

    for asset in asset_summary["Asset"]:

        asset_df = filtered_df[
            filtered_df["Asset"] == asset
        ]

        asset_wins = len(
            asset_df[asset_df["Result"] == "Win"]
        )

        asset_losses = len(
            asset_df[asset_df["Result"] == "Loss"]
        )

        denominator = asset_wins + asset_losses

        if denominator > 0:
            asset_winrate = (
                asset_wins / denominator
            ) * 100
        else:
            asset_winrate = 0

        asset_winrates.append(asset_winrate)

    asset_summary["Win Rate"] = asset_winrates
    asset_summary = asset_summary.sort_values(
        "Net PnL",
        ascending=False
    ).reset_index(drop=True)
    total_asset_profit = asset_summary["Net PnL"].sum()

    if total_asset_profit != 0:

        asset_summary["Contribution %"] = (
            asset_summary["Net PnL"]
            / total_asset_profit
        ) * 100

    else:

        asset_summary["Contribution %"] = 0
    best_asset = (
        asset_summary
        .sort_values("Net PnL", ascending=False)
        .iloc[0]["Asset"]
    )

    worst_asset = (
        asset_summary
        .sort_values("Net PnL", ascending=True)
        .iloc[0]["Asset"]
    )

    # DISPLAY CARDS

    asset_cols = st.columns(len(asset_summary))

    for i, row in asset_summary.iterrows():

        if row["Asset"] == best_asset:

            border_color = "#00FF88"
            glow = "0 0 12px rgba(0,255,136,0.35)"
            badge = "🏆 EDGE"

        elif row["Asset"] == worst_asset:

            border_color = "#FF4B4B"
            glow = "0 0 12px rgba(255,75,75,0.35)"
            badge = "⚠ WEAK"

        else:

            border_color = "rgba(0,245,255,0.25)"
            glow = "none"

            if row["Win Rate"] >= 50:
                badge = "STABLE"
            else:
                badge = "➖ NEUTRAL"

        with asset_cols[i]:
            if "EDGE" in badge:
                badge_bg = "rgba(0,255,136,0.15)"
                badge_glow = "0 0 8px rgba(0,255,136,0.25)"

            elif "WEAK" in badge:
                badge_bg = "rgba(255,75,75,0.15)"
                badge_glow = "0 0 8px rgba(255,75,75,0.20)"

            else:
                badge_bg = "rgba(53,18,161,0.18)"
                badge_glow = "none"

            pnl_color = (
                "#00FF88"
                if row["Net PnL"] >= 0
                else "#FF4B4B"
            )
            net_pnl_display = f"₹{row['Net PnL']:,.0f}"
            card_html = f"""
            <div style="
                border:2px solid {border_color};
                box-shadow:{glow};
                border-radius:20px;
                padding:24px 18px;
                background:
                linear-gradient(
                135deg,
                rgba(35,35,35,0.35),
                rgba(15,15,15,0.60)
                );
                text-align:center;
                transition:0.3s;
            ">
            <div style="
                text-align:center;
            ">
            <div style="
                font-size:24px;
                font-weight:800;
                letter-spacing:0.5px;
                margin-top:12px;
                margin-bottom:12px;
                text-align:center;
                width:100%;
                display:block;
            ">
                {row['Asset']}
            </div>

            <div style="
                background-color:{badge_bg};
                box-shadow:{badge_glow};
                padding:6px 14px;
                border-radius:999px;
                display:inline-block;
                font-size:12px;
                font-weight:bold;
                margin-bottom:12px;
            ">
                {badge}
            </div>
            </div>

            <div style="height:6px;"></div>

            <hr style="
                border:0;
                border-top:1px solid rgba(255,255,255,0.12);
                margin:12px 0 16px 0;
            ">

            <p><b>Trades</b><br>{int(row['Trade No'])}</p>
            <div style="height:4px;"></div>

            <p>
            <b>Net PnL</b><br>

            <span style="
                font-size:34px;
                font-weight:800;
                color:{pnl_color};
                text-shadow:0 0 4px {pnl_color};
            ">
                ₹{row['Net PnL']:,.0f}
            </span>

            </p>

            <p><b>Return</b><br>{row['Return %(per trade)']:.2f}%</p>
            <p>
            <b>Win Rate</b><br>

            <div style="
            width:100%;
            height:8px;
            background:rgba(255,255,255,0.08);
            border-radius:999px;
            margin-top:6px;
            margin-bottom:6px;
            ">

            <div style="
            width:{row['Win Rate']}%;
            height:100%;
            background:#249413;
            border-radius:999px;
            ">
            </div>

            </div>

            {row['Win Rate']:.2f}%
            </p>

            <p>
            <b>Contribution</b><br>

            <div style="
            width:100%;
            height:8px;
            background:rgba(255,255,255,0.08);
            border-radius:999px;
            margin-top:6px;
            margin-bottom:6px;
            ">

            <div style="
            width:{abs(row['Contribution %'])}%;
            height:100%;
            background:#3512a1;
            border-radius:999px;
            ">
            </div>

            </div>

            {row['Contribution %']:.1f}%
            </p>

            </div>
            """

            st.markdown(
                card_html,
                unsafe_allow_html=True
            )
    # -----------------------------------
    # ADVANCED ANALYTICS ENGINE
    # -----------------------------------

    # -----------------------------------
    # EXPECTANCY
    # -----------------------------------

    average_win = (
        filtered_df[filtered_df["Net PnL"] > 0]
        ["Net PnL"]
        .mean()
    )

    average_loss = abs(
        filtered_df[filtered_df["Net PnL"] < 0]
        ["Net PnL"]
        .mean()
    )
    actual_rrr = (
        average_win / average_loss
        if average_loss > 0
        else 0
    )
    # AVERAGE WINNER %

    average_winner_pct = (
        filtered_df[
            filtered_df["Return %(per trade)"] > 0
        ]["Return %(per trade)"]
        .mean()
    )

    # AVERAGE LOSER %

    average_loser_pct = abs(
        filtered_df[
            filtered_df["Return %(per trade)"] < 0
        ]["Return %(per trade)"]
        .mean()
    )

    loss_rate = 100 - winrate

    expectancy = (
        (winrate / 100) * average_win
    ) - (
        (loss_rate / 100) * average_loss
    )
    expectancy_pct = (
        (winrate / 100) * average_winner_pct
    ) - (
        (loss_rate / 100) * average_loser_pct
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    📍 Direction Analytics
    </h2>
    """,
    unsafe_allow_html=True
)
    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    direction_cols = st.columns(
        [1, 0.03, 1]
    )

    for i, direction in enumerate(["Long", "Short"]):

        direction_df = filtered_df[
            filtered_df["Direction"] == direction
        ]

        trades = len(direction_df)

        wins_dir = len(
            direction_df[
                direction_df["Result"] == "Win"
            ]
        )

        losses_dir = len(
            direction_df[
                direction_df["Result"] == "Loss"
            ]
        )

        if wins_dir + losses_dir > 0:
            winrate_dir = (
                wins_dir /
                (wins_dir + losses_dir)
            ) * 100
        else:
            winrate_dir = 0

        net_pnl_dir = direction_df["Net PnL"].sum()
        if total_net_pnl != 0:
            contribution_dir = (
                net_pnl_dir / total_net_pnl
            ) * 100
        else:
            contribution_dir = 0

        border_color = (
            "#00FF88"
            if net_pnl_dir >= 0
            else "#FF4B4B"
        )
        if i == 0:
            target_col = direction_cols[0]
        else:
            target_col = direction_cols[2]

        with target_col:

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:28px;
                    font-weight:700;
                    margin-bottom:30px;
                ">
                    {direction}
                </div>
                <p style='text-align:center;color:#AAAAAA;margin-bottom:12px;'>
                    Trades
                </p>

                <div style="
                    text-align:center;
                    font-size:34px;
                    font-weight:800;
                    margin-bottom:60px;
                ">
                    {trades}
                </div>
                """,
                unsafe_allow_html=True
            )
            import plotly.graph_objects as go

            donut_fig = go.Figure(
                go.Pie(
                    values=[
                        winrate_dir,
                        100 - winrate_dir
                    ],
                    hole=0.72,
                    sort=False,
                    textinfo="none",
                    marker=dict(
                        colors=[
                            "#CC00FFA7" if direction == "Long" else "#FFBB00B9",
                            "rgba(255,255,255,0.08)"
                        ],
                        line=dict(
                            color="rgba(0,0,0,0)",
                            width=0
                        )
                    )
                )
            )

            donut_fig.update_layout(
                showlegend=False,
                height=240,
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text=f"<b>{winrate_dir:.0f}%</b><br>Win Rate",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(
                            size=24,
                            color="white"
                        )
                    )
                ]
            )

            donut_fig.update_traces(
                hoverinfo="skip",
                hovertemplate=None
            )

            st.plotly_chart(
                donut_fig,
                use_container_width=True
            )

            st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
            
            pnl_color = (
                "#00FF88"
                if net_pnl_dir >= 0
                else "#FF4B4B"
            )

            st.markdown(
                "<p style='text-align:center;color:#AAAAAA;margin-bottom:12px;'>Net PnL</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<h2 style='text-align:center;color:{pnl_color};margin-bottom:18px;text-shadow:0 0 5px {pnl_color};'>₹{net_pnl_dir:,.0f}</h2>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='text-align:center;color:#AAAAAA;'>Contribution</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<h3 style='text-align:center;color:#00F5FF;text-shadow:0 0 5px #00F5FF;'>{contribution_dir:.1f}%</h3>",
                unsafe_allow_html=True
            )
        if len(direction_cols) == 3:

            with direction_cols[1]:

                st.markdown(
                    """
                    <div style="
                        height:260px;
                        width:1px;
                        margin:auto;
                        background:
                        rgba(255,255,255,0.08);
                        border-radius:999px;
                    ">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    🎯 Trade Quality
    </h2>
    """,
    unsafe_allow_html=True
)

    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
    quality_cols = st.columns(4)
    

    with quality_cols[0]:
        winner_pct = average_winner_pct

        if winner_pct < 30:
            winner_status = "WEAK"
            winner_color = "#FF4B4B"

        elif winner_pct < 60:
            winner_status = "GOOD"
            winner_color = "#FFD700"

        elif winner_pct < 80:
            winner_status = "STRONG"
            winner_color = "#00F5FF"

        else:
            winner_status = "ELITE"
            winner_color = "#00FF88"
        st.markdown(
            f"""
            <div style="
            border:1px solid rgba(255,255,255,0.12);
            border-radius:18px;
            padding:18px;
            text-align:center;
            background:rgba(20,20,20,0.45);
            box-shadow:0 0 12px rgba(0,245,255,0.12);
            ">

            <div style="
            color:#AAAAAA;
            font-size:13px;
            margin-bottom:8px;
            ">
            Average Winner %
            </div>

            <div style="
            font-size:34px;
            font-weight:800;
            color:{winner_color};
            ">
            {winner_pct:.1f}%
            </div>

            <div style="
            color:{winner_color};
            font-size:13px;
            font-weight:700;
            margin-top:4px;
            margin-bottom:12px;
            ">
            {winner_status}
            </div>

            <div style="
            width:100%;
            height:8px;
            background:rgba(255,255,255,0.08);
            border-radius:999px;
            overflow:hidden;
            ">

            <div style="
            width:{winner_pct}%;
            height:100%;
            background:{winner_color};
            ">
            </div>

            </div>

            <div style="
            margin-top:16px;
            color:#AAAAAA;
            font-size:12px;
            ">
            Average Win
            </div>

            <div style="
            color:#00FF88;
            font-size:28px;
            font-weight:800;
            text-shadow:0 0 8px rgba(255,107,107,0.35);
            ">
            ₹{average_win:,.0f}
            </div>

            </div>
            """,
                    unsafe_allow_html=True
                )

        
    with quality_cols[1]:

        loser_pct = average_loser_pct

        if loser_pct <= 10:
            loser_status = "ELITE"
            loser_color = "#00FF88"

        elif loser_pct <= 15:
            loser_status = "STABLE"
            loser_color = "#00F5FF"

        elif loser_pct <= 20:
            loser_status = "WEAK"
            loser_color = "#FFD700"

        else:
            loser_status = "FATAL"
            loser_color = "#FF4B4B"

        st.markdown(
    f"""
    <div style="
    border:1px solid rgba(255,255,255,0.12);
    border-radius:18px;
    padding:18px;
    text-align:center;
    background:rgba(20,20,20,0.45);
    box-shadow:0 0 12px rgba(0,245,255,0.12);
    ">

    <div style="
    color:#AAAAAA;
    font-size:13px;
    margin-bottom:8px;
    ">
    Average Loser %
    </div>

    <div style="
    font-size:34px;
    font-weight:800;
    color:{loser_color};
    ">
    {loser_pct:.1f}%
    </div>

    <div style="
    color:{loser_color};
    font-size:13px;
    font-weight:700;
    margin-top:4px;
    margin-bottom:12px;
    ">
    {loser_status}
    </div>

    <div style="
    width:100%;
    height:8px;
    background:rgba(255,255,255,0.08);
    border-radius:999px;
    overflow:hidden;
    ">

    <div style="
    width:{min(loser_pct*5,100)}%;
    height:100%;
    background:{loser_color};
    ">
    </div>

    </div>

    <div style="
    margin-top:16px;
    color:#AAAAAA;
    font-size:12px;
    ">
    Average Loss
    </div>

    <div style="
    color:#FF6B6B;
    font-size:28px;
    font-weight:800;
    text-shadow:0 0 8px rgba(255,107,107,0.35);
    ">
    ₹{average_loss:,.0f}
    </div>

    </div>
    """,
            unsafe_allow_html=True
        )

    
    with quality_cols[2]:

        actual_rrr = average_win / average_loss if average_loss > 0 else 0

        if actual_rrr < 3:
            rrr_status = "WEAK"
            rrr_color = "#FF4B4B"

        elif actual_rrr < 5:
            rrr_status = "GOOD"
            rrr_color = "#FFD700"

        elif actual_rrr < 7:
            rrr_status = "STRONG"
            rrr_color = "#00F5FF"

        else:
            rrr_status = "ELITE"
            rrr_color = "#00FF88"

        st.markdown(
        f"""
        <div style="
        border:1px solid rgba(255,255,255,0.12);
        border-radius:18px;
        padding:18px;
        text-align:center;
        background:rgba(20,20,20,0.45);
        box-shadow:0 0 12px rgba(0,245,255,0.12);
        ">

        <div style="
        color:#AAAAAA;
        font-size:13px;
        margin-bottom:8px;
        ">
        Actual RRR
        </div>

        <div style="
        font-size:34px;
        font-weight:800;
        color:{rrr_color};
        ">
        {actual_rrr:.2f}
        </div>

        <div style="
        color:{rrr_color};
        font-size:13px;
        font-weight:700;
        margin-top:4px;
        margin-bottom:12px;
        ">
        {rrr_status}
        </div>

        <div style="
        width:100%;
        height:8px;
        background:rgba(255,255,255,0.08);
        border-radius:999px;
        overflow:hidden;
        ">

        <div style="
        width:{min(actual_rrr*10,100)}%;
        height:100%;
        background:{rrr_color};
        ">
        </div>

        </div>

        <div style="
        margin-top:16px;
        color:#AAAAAA;
        font-size:12px;
        ">
        Risk Reward Ratio
        </div>

        </div>
        """,
        unsafe_allow_html=True
        )

    with quality_cols[3]:

        expectancy_pct = expectancy_pct

        if expectancy_pct < 10:
            expectancy_status = "WEAK"
            expectancy_color = "#FF4B4B"

        elif expectancy_pct < 20:
            expectancy_status = "GOOD"
            expectancy_color = "#FFD700"

        elif expectancy_pct < 30:
            expectancy_status = "STRONG"
            expectancy_color = "#00F5FF"

        else:
            expectancy_status = "ELITE"
            expectancy_color = "#00FF88"

        st.markdown(
            f"""
            <div style="
            border:1px solid rgba(255,255,255,0.12);
            border-radius:18px;
            padding:18px;
            text-align:center;
            background:rgba(20,20,20,0.45);
            box-shadow:0 0 12px rgba(0,245,255,0.12);
            ">

            <div style="
            color:#AAAAAA;
            font-size:13px;
            margin-bottom:8px;
            ">
            Expectancy %
            </div>

            <div style="
            font-size:34px;
            font-weight:800;
            color:{expectancy_color};
            ">
            {expectancy_pct:.1f}%
            </div>

            <div style="
            color:{expectancy_color};
            font-size:13px;
            font-weight:700;
            margin-top:4px;
            margin-bottom:12px;
            ">
            {expectancy_status}
            </div>

            <div style="
            width:100%;
            height:8px;
            background:rgba(255,255,255,0.08);
            border-radius:999px;
            overflow:hidden;
            ">

            <div style="
            width:{min(expectancy_pct*3,100)}%;
            height:100%;
            background:{expectancy_color};
            ">
            </div>

            </div>

            <div style="
            margin-top:16px;
            color:#AAAAAA;
            font-size:12px;
            ">
            Expected Return Per Trade
            </div>

            </div>
            """,
            unsafe_allow_html=True
            )
    
    st.markdown("---")
# =====================================
# RISK SECTION
# =====================================
with risk_tab:
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    ⚠️ Risk Analytics
    </h2>
    """,
    unsafe_allow_html=True
)
    risk_cols = st.columns([1.3, 1, 1])

    risk_cards = [
    ]

    with risk_cols[0]:

        import plotly.graph_objects as go

        if average_risk <= 5:
            risk_status = "CONSERVATIVE"

        elif average_risk <= 10:
            risk_status = "MODERATE"

        elif average_risk <= 20:
            risk_status = "AGGRESSIVE"

        else:
            risk_status = "EXTREME"

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=average_risk,

                number={
                    "suffix":"%",
                    "font":{"size":54}
                },

                gauge={
                    "axis":{
                        "range":[0,25],
                        "showticklabels":False
                    },

                    "bar":{
                        "color":"#000000",
                        "thickness":0.3
                    },

                    "steps":[

                        {
                            "range":[0,5],
                            "color":"#37EB1F"
                        },

                        {
                            "range":[5,10],
                            "color":"#1C87EB"
                        },

                        {
                            "range":[10,20],
                            "color":"#ECA31A"
                        },

                        {
                            "range":[20,25],
                            "color":"#F11818"
                        }

                    ]
                }
            )
        )

        fig.update_layout(
            height=340,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown(
            f"""
            <div style="
            text-align:center;
            color:#AAAAAA;
            margin-top:-25px;
            ">
            Average Risk Per Trade
            </div>

            <div style="
            text-align:center;
            font-weight:800;
            font-size:20px;
            color:#FFD700;
            text-shadow:0 0 3.5px #FFD700;
            margin-top:8px;
            ">
            {risk_status}
            </div>
            """,
            unsafe_allow_html=True
        )
    with risk_cols[1]:
        if average_rrr < 3:
            rrr_status = "WEAK"
            rrr_color = "#FF4B4B"

        elif average_rrr < 5:
            rrr_status = "GOOD"
            rrr_color = "#FFD700"

        elif average_rrr < 7:
            rrr_status = "STRONG"
            rrr_color = "#00F5FF"

        else:
            rrr_status = "ELITE"
            rrr_color = "#00FF88"
        st.markdown(
            """
            <div style="
            text-align:center;
            color:#AAAAAA;
            font-size:14px;
            margin-top:90px;
            margin-bottom:12px;
            ">
            Average RRR
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
            text-align:center;
            font-size:42px;
            font-weight:800;
            color:{rrr_color};
            text-shadow:0 0 4px {rrr_color};
            ">
            {average_rrr:.2f}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
            text-align:center;
            color:{rrr_color};
            font-size:16px;
            font-weight:700;
            margin-top:4px;
            ">
            {rrr_status}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
            margin-top:20px;
            width:90%;
            margin-left:auto;
            margin-right:auto;
            ">
                <div style="
                display:flex;
                justify-content:space-between;
                color:#888888;
                font-size:10px;
                margin-bottom:4px;
                ">
                    <span>WEAK</span>
                    <span>GOOD</span>
                    <span>STRONG</span>
                    <span>ELITE</span>
                </div>
                <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                ">
                    <div style="
                    width:12px;
                    height:12px;
                    border-radius:50%;
                    background:#FF4B4B;
                    ">
                    </div>
                    <div style="
                    flex:1;
                    height:3px;
                    background:rgba(255,255,255,0.12);
                    ">
                    </div>
                    <div style="
                    width:12px;
                    height:12px;
                    border-radius:50%;
                    background:#FFD700;
                    ">
                    </div>
                    <div style="
                    flex:1;
                    height:3px;
                    background:rgba(255,255,255,0.12);
                    ">
                    </div>
                    <div style="
                    width:18px;
                    height:18px;
                    border-radius:50%;
                    background:{rrr_color};
                    box-shadow:0 0 15px {rrr_color};
                    border:2px solid white;
                    ">
                    </div>
                    <div style="
                    flex:1;
                    height:3px;
                    background:rgba(255,255,255,0.12);
                    ">
                    </div>
                    <div style="
                    width:12px;
                    height:12px;
                    border-radius:50%;
                    background:#00FF88;
                    ">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    gross_profit = (
        filtered_df[
            filtered_df["Net PnL"] > 0
        ]["Net PnL"]
        .sum()
    )
    gross_loss = abs(
        filtered_df[
            filtered_df["Net PnL"] < 0
        ]["Net PnL"]
        .sum()
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0
    )

    fee_burn_pct = (
        (total_fees / gross_profit) * 100
        if gross_profit > 0
        else 0
    )

    cost_per_trade = (
        total_fees / total_trades
        if total_trades > 0
        else 0
    )
    with risk_cols[2]:

        st.markdown(
            f"""
            <div style="
            text-align:center;
            margin-top:60px;
            ">
                <div style="
                font-size:42px;
                ">
                💸
                </div>
                <div style="
                font-size:34px;
                font-weight:800;
                color:#FFD700;
                margin-top:10px;
                ">
                ₹{total_fees:,.0f}
                </div>
                <div style="
                color:#AAAAAA;
                font-size:12px;
                letter-spacing:1px;
                margin-top:4px;
                ">
                TOTAL FEES
                </div>
                <div style="
                height:16px;
                ">
                </div>
                <div style="
                color:#AAAAAA;
                font-size:12px;
                ">
                Fee Burn
                </div>
                <div style="
                color:#FF0000;
                font-size:24px;
                font-weight:800;
                text-shadow:0 0 5px rgba(255,0,255,0.9);
                ">
                {fee_burn_pct:.1f}%
                </div>
                <div style="
                height:10px;
                ">
                </div>
                <div style="
                color:#AAAAAA;
                font-size:12px;
                ">
                Cost / Trade
                </div>
                <div style="
                color:white;
                font-size:20px;
                font-weight:700;
                ">
                ₹{cost_per_trade:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    📉 Drawdown Analytics
    </h2>
    """,
    unsafe_allow_html=True
)
    st.markdown(
        "<div style='height:50px;'></div>",
        unsafe_allow_html=True
    )
    # -----------------------------------
    # DRAWDOWN ANALYTICS
    # -----------------------------------


    drawdown_cols = st.columns(3)
    with drawdown_cols[0]:

        dd_fill = min(abs(max_drawdown), 100)

        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="
                color:#AAAAAA;
                font-size:14px;
                ">
                Maximum Drawdown
                </div>
                <div style="
                color:#FF4B4B;
                font-size:42px;
                font-weight:800;
                margin-top:8px;
                text-shadow:0 0 6px rgba(255,75,75,0.7);
                ">
                {max_drawdown:.2f}%
                </div>
                <div style="
                width:90%;
                height:14px;
                margin:20px auto;
                background:#2A0808;
                border:1px solid #FF6B6B;
                border-radius:999px;
                overflow:hidden;
                box-shadow:0 0 4px rgba(255,107,107,0.35);
                ">
                    <div style="
                    width:{dd_fill}%;
                    height:100%;
                    background:#8B0000;
                    box-shadow:0 0 10px rgba(255,75,75,0.4);
                    ">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with drawdown_cols[1]:

        if current_drawdown < 0:
            dd_status = "ACTIVE"
            dd_color = "#FF4B4B"
            dd_dot = "🔴"
        else:
            dd_status = "RECOVERED"
            dd_color = "#00FF88"
            dd_dot = "🟢"
        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="
                color:#AAAAAA;
                font-size:14px;
                ">
                Current Drawdown
                </div>
                <div style="
                color:#FF4B4B;
                font-size:42px;
                font-weight:800;
                margin-top:8px;
                text-shadow:0 0 6px rgba(255,75,75,0.7);
                ">
                {current_drawdown:.2f}%
                </div>
                <div style="
                margin-top:20px;
                color:{dd_color};
                font-size:20px;
                font-weight:700;
                ">
                {dd_dot} {dd_status}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with drawdown_cols[2]:
        st.markdown(
            f"""
            <div style="
            text-align:center;
            ">
                <div style="
                color:#AAAAAA;
                font-size:14px;
                margin-bottom:24px;
                ">
                Recovery Metrics
                </div>
                <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                ">
                    <div style="
                    flex:1;
                    text-align:center;
                    ">
                        <div style="
                        color:#AAAAAA;
                        font-size:12px;
                        ">
                        Average Recovery
                        </div>
                        <div style="
                        color:#00F5FF;
                        font-size:34px;
                        font-weight:800;
                        margin-top:10px;
                        ">
                        {average_recovery_duration:.2f}
                        </div>
                        <div style="
                        color:#AAAAAA;
                        font-size:12px;
                        ">
                        Trades
                        </div>
                    </div>
                    <div style="
                    width:1px;
                    height:90px;
                    background:rgba(255,255,255,0.10);
                    margin-left:20px;
                    margin-right:20px;
                    ">
                    </div>
                    <div style="
                    flex:1;
                    text-align:center;
                    ">
                        <div style="
                        color:#AAAAAA;
                        font-size:12px;
                        ">
                        Worst Recovery
                        </div>
                        <div style="
                        color:#00F5FF;
                        font-size:34px;
                        font-weight:800;
                        margin-top:10px;
                        ">
                        {max_recovery_duration}
                        </div>
                        <div style="
                        color:#AAAAAA;
                        font-size:12px;
                        ">
                        Trades
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        

    # -----------------------------------
    # DRAWDOWN CURVE
    # -----------------------------------
    st.markdown(
        "<div style='height:50px;'></div>",
        unsafe_allow_html=True
    )
    drawdown_fig = px.area(
        filtered_df,
        x="Trade No",
        y="Drawdown %",
        title="Drawdown Curve",
        template="plotly_dark"
    )
    drawdown_fig.update_traces(
        fillcolor="rgba(139,0,0,0.15)",
        line=dict(
            color="#FF4B4B",
            width=3
        ),
        marker=dict(
            size=7,
            color="#FF4B4B",
            line=dict(
                color="white",
                width=1
            )
        ),
        mode="lines+markers"
    )
    drawdown_fig.update_layout(
        height=550,
        **CHART_LAYOUT
    )
    st.plotly_chart(
        drawdown_fig,
        use_container_width=True
    )
    st.markdown("---")
    
# =====================================
# PERFORMANCE SECTION
# =====================================
with performance_tab:
    
    st.markdown(
    """
    <h2 style="
        color:#E5E7EB;
        border-bottom:2px solid rgba(0,245,255,0.40);
        padding-bottom:10px;
        font-weight:700;
    ">
    📈 Performance Analytics
    </h2>
    """,
    unsafe_allow_html=True
    )
    top_left, top_right = st.columns(2)
    # -----------------------------------
    # TRADE BY TRADE PNL CURVE
    # -----------------------------------

    trade_pnl_fig = px.line(
        filtered_df,
        x="Trade No",
        y="PnL",
        title="📈 Trade-By-Trade PnL Curve",
        markers=True,
        template="plotly_dark"
    )

    trade_pnl_fig.update_layout(
        title_font=dict(
            size=20
        )
    )

    trade_pnl_fig.update_traces(
        line=dict(
            width=3,
            color="#00FF88"
        ),

        marker=dict(
            size=10,
            color=[
                "#22C55E" if x >= 0
                else "#EF4444"
                for x in filtered_df["PnL"]
            ],
            line=dict(
                width=2,
                color="white"
            )
        ),

        fill="tozeroy",
        fillcolor="rgba(0,255,136,0.08)"
    )

    trade_pnl_fig.update_layout(
        height=420,
        **CHART_LAYOUT
    )

    with top_left:

        st.plotly_chart(
            trade_pnl_fig,
            use_container_width=True
        )
    
    # -----------------------------------
    # RETURN PERCENTAGE GRAPH
    # -----------------------------------

    return_fig = px.line(
        filtered_df,
        x="Trade No",
        y="Return %(per trade)",
        title="⚡ Return % Per Trade",
        markers=True,
        template="plotly_dark"
    )
    return_fig.update_layout(
        title_font=dict(
            size=20
        )
    )
    return_fig.update_traces(
        line=dict(
            width=3,
            color="#FF8C00"
        ),
        marker=dict(
            size=10,
            line=dict(
                width=2,
                color="white"
            )
        ),
        fill="tozeroy",
        fillcolor="rgba(255,0,0,0.05)"
    )

    return_fig.update_layout(
        height=420,
        **CHART_LAYOUT
    )

    with top_right:

        st.plotly_chart(
            return_fig,
            use_container_width=True
        )
    # -----------------------------------
    # TRADE AMOUNT CURVE
    # -----------------------------------
    bottom_left, bottom_right = st.columns(2)
    amount_fig = px.line(
        filtered_df,
        x="Trade No",
        y="Trade Amount",
        title="💰 Account Growth Curve",
        markers=True,
        template="plotly_dark"
    )
    amount_fig.update_traces(
        customdata=filtered_df[
            ["Overall Return%(compounded)"]
        ],

        hovertemplate=
        "<b>Trade %{x}</b><br><br>"
        "Capital<br>"
        "₹%{y:,.0f}<br><br>"
        "Overall Return<br>"
        "%{customdata[0]:.2f}%"
        "<extra></extra>"
    )
    amount_fig.update_layout(
        title_font=dict(
            size=20
        )
    )

    amount_fig.update_traces(
        line=dict(
            width=3,
            color="#FFD700"
        ),
        marker=dict(
            size=10,
            line=dict(
                width=2,
                color="white"
            ),
            color="#FFD700"
        ),
        fill="tozeroy",
        fillcolor="rgba(255,215,0,0.10)"
    )

    amount_fig.update_layout(
        height=420,
        **CHART_LAYOUT
    )

    with bottom_left:

        st.plotly_chart(
            amount_fig,
            use_container_width=True
        )

    # -----------------------------------
    # FEES ANALYTICS
    # -----------------------------------

    fees_fig = px.bar(
        filtered_df,
        x="Trade No",
        y="Fees",
        title="💸 Fees Per Trade",
        template="plotly_dark"
    )
    fees_fig.add_hline(
        y=filtered_df["Fees"].mean(),
        line_dash="dash",
        line_color="#D3C013",
        annotation_text="Avg Fee"
    )
    fees_fig.update_layout(
        title_font=dict(
            size=20
        )
    )
    fees_colors = [
        "#B61C1C"
        if fee < filtered_df["Fees"].mean()
        else "#2738CF"
        for fee in filtered_df["Fees"]
    ]
    fees_fig.update_traces(
        text=[f"₹{x:.0f}" for x in filtered_df["Fees"]],
        textposition="outside"
    )

    fees_fig.update_traces(
        marker_color=fees_colors
    )
    fees_fig.update_traces(
        marker_line_width=0,
        opacity=0.95,
    )
    fees_fig.update_layout(
        height=360,
        **CHART_LAYOUT
    )
    with bottom_right:

        st.plotly_chart(
            fees_fig,
            use_container_width=True
        )
    st.markdown(
        "<div style='height:50px'></div>",
        unsafe_allow_html=True
    )

    st.subheader("📅 Monthly Performance Analytics")
    monthly_top = st.columns([2,8])

    with monthly_top[0]:

        monthly_year = st.selectbox(
            "",
            [2026, 2027],
            key="monthly_year",
            label_visibility="collapsed"
        )
    monthly_df = filtered_df.copy()

    monthly_df["Date"] = pd.to_datetime(
        monthly_df["Date"],
        dayfirst=True
    )
    monthly_df = monthly_df[
        monthly_df["Date"].dt.year
        == monthly_year
    ]

    monthly_df["Month"] = (
        monthly_df["Date"]
        .dt.strftime("%b")
    )
    month_order = [
        "Jan","Feb","Mar","Apr",
        "May","Jun","Jul","Aug",
        "Sep","Oct","Nov","Dec"
    ]


    monthly_stats = pd.DataFrame({
        "Month": month_order
    })

    monthly_grouped = (
        monthly_df
        .groupby("Month")
        .agg({
            "Net PnL":"sum",
            "Return %(per trade)":"sum"
        })
        .reset_index()
    )

    monthly_stats = monthly_stats.merge(
        monthly_grouped,
        on="Month",
        how="left"
    )

    monthly_stats = monthly_stats.fillna(0)
    
    monthly_stats["Month"] = pd.Categorical(
        monthly_stats["Month"],
        categories=month_order,
        ordered=True
    )

    monthly_stats = (
        monthly_stats
        .sort_values("Month")
    )
    monthly_colors = [

        "#00FF88"
        if pnl > 0

        else "#FF4B4B"
        if pnl < 0

        else "#FFD700"

        for pnl in monthly_stats["Net PnL"]
    ]

    monthly_fig = go.Figure()

    monthly_fig.add_trace(

        go.Bar(

            x=monthly_stats["Month"],

            y=monthly_stats["Net PnL"],
            hoverinfo="skip",
            marker=dict(
                color=monthly_colors,
                line=dict(
                    width=3,
                    color="white"
                ),
                opacity=0.95
            ),

            text=[
                f"₹{x:,.0f}"
                if x != 0
                else ""
                for x in monthly_stats["Net PnL"]
            ],

            textposition="outside",

            textfont=dict(
                size=16,
                color="white"
            )


        )

    )
    monthly_fig.add_trace(

        go.Scatter(

            x=monthly_stats["Month"],

            y=[-600] * len(monthly_stats),

            mode="text",

            text=[

                (
                    f"{x:.1f}%"
                    if x != 0
                    else ""
                )

                for x in monthly_stats[
                    "Return %(per trade)"
                ]
            ],

            textposition="bottom center",

            textfont=dict(
                size=14,
                color="#00F5FF"
            ),

            hoverinfo="skip"

        )

    )
    monthly_fig.update_layout(
        
        height=500,

        showlegend=False,

    )

    st.plotly_chart(
        monthly_fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )
    st.markdown(
        "<div style='height:30px'></div>",
        unsafe_allow_html=True
    )
    stats_row = st.columns(4)
    avg_monthly_pnl = (
        monthly_stats["Net PnL"]
        .replace(0, np.nan)
        .mean()
    )
    avg_monthly_return = (
        monthly_stats["Return %(per trade)"]
        .replace(0, np.nan)
        .mean()
    )
    traded_months = monthly_stats[
        monthly_stats["Net PnL"] != 0
    ]
    best_month_row = traded_months.loc[
        traded_months["Net PnL"].idxmax()
    ]

    worst_month_row = traded_months.loc[
        traded_months["Net PnL"].idxmin()
    ]
    with stats_row[0]:

        st.markdown(
            f"""
            <div style="
                height:130px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                background:rgba(15,15,15,0.45);
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    AVG MONTHLY PnL
                </div>
                <div style="
                    font-size:22px;
                    font-weight:800;
                    color:white;
                ">
                    ₹{avg_monthly_pnl:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with stats_row[1]:

        st.markdown(
            f"""
            <div style="
                height:130px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                background:rgba(15,15,15,0.45);
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    AVG MONTHLY RETURN
                </div>
                <div style="
                    font-size:22px;
                    font-weight:800;
                    color:white;
                ">
                    {avg_monthly_return:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with stats_row[2]:

        st.markdown(
            f"""
            <div style="
                height:130px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                background:rgba(15,15,15,0.45);
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    BEST MONTH
                </div>
                <div style="
                    font-size:26px;
                    font-weight:800;
                    color:white;
                ">
                    {best_month_row['Month']}
                </div>
                <div style="
                    font-size:18px;
                    font-weight:700;
                    color:#00FF88;
                ">
                    ₹{best_month_row['Net PnL']:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with stats_row[3]:

        st.markdown(
            f"""
            <div style="
                height:130px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                background:rgba(15,15,15,0.45);
            ">
                <div style="
                    color:#AAAAAA;
                    font-size:14px;
                ">
                    WORST MONTH
                </div>
                <div style="
                    font-size:26px;
                    font-weight:800;
                    color:white;
                ">
                    {worst_month_row['Month']}
                </div>
                <div style="
                    font-size:18px;
                    font-weight:700;
                    color:#FF4B4B;
                ">
                    ₹{worst_month_row['Net PnL']:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )