import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(page_title="CA Final Tracker", layout="wide")

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect("tracker.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS syllabus_progress (
    subject TEXT,
    topic TEXT,
    status INTEGER,
    UNIQUE(subject, topic)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS study_log (
    date TEXT,
    subject TEXT,
    topic TEXT,
    hours REAL,
    questions INTEGER,
    revision INTEGER,
    remarks TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS study_plan (
    plan_date TEXT,
    subject TEXT,
    topic TEXT,
    hours REAL,
    status INTEGER,
    UNIQUE(plan_date, subject, topic)
)
""")

conn.commit()

# ==========================================
# SUBJECT HOURS (TARGET)
# ==========================================

subject_hours = {
    "FR": 200,
    "AFM": 200,
    "DT": 200,
    "IDT": 110,
    "Audit": 110
}

# ==========================================
# FUNCTIONS
# ==========================================

def get_status(subject, topic):
    res = conn.execute(
        "SELECT status FROM syllabus_progress WHERE subject=? AND topic=?",
        (subject, topic)
    ).fetchone()
    return res[0] if res else 0


def update_status(subject, topic, status):
    conn.execute(
        "INSERT OR REPLACE INTO syllabus_progress VALUES (?, ?, ?)",
        (subject, topic, int(status))
    )
    conn.commit()


def save_plan(data):
    try:
        conn.execute(
            "INSERT INTO study_plan VALUES (?, ?, ?, ?, ?)",
            data
        )
        conn.commit()
        return True
    except:
        return False


def delete_plan(plan_date, subject, topic):
    conn.execute(
        "DELETE FROM study_plan WHERE plan_date=? AND subject=? AND topic=?",
        (plan_date, subject, topic)
    )
    conn.commit()


def get_plan(date):
    return pd.read_sql_query(
        f"SELECT * FROM study_plan WHERE plan_date='{date}'",
        conn
    )


def auto_log_plan():
    today = str(datetime.today().date())

    df = get_plan(today)

    for _, row in df.iterrows():

        exists = conn.execute(
            "SELECT * FROM study_log WHERE date=? AND subject=? AND topic=?",
            (today, row["subject"], row["topic"])
        ).fetchone()

        if not exists:
            conn.execute(
                "INSERT INTO study_log VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    today,
                    row["subject"],
                    row["topic"],
                    row["hours"],
                    0,
                    0,
                    "Auto Planned"
                )
            )

    conn.commit()


def get_completed_hours(subject):
    df = pd.read_sql_query(
        f"SELECT hours FROM study_log WHERE subject='{subject}'",
        conn
    )

    if df.empty:
        return 0

    return df["hours"].sum()


def get_revision_alerts():
    df = pd.read_sql_query("SELECT subject, topic, date FROM study_log", conn)

    if df.empty:
        return []

    df["date"] = pd.to_datetime(df["date"])
    latest = df.sort_values("date").groupby(["subject", "topic"]).last().reset_index()

    today = pd.to_datetime(datetime.today())

    alerts = []

    for _, row in latest.iterrows():
        gap = (today - row["date"]).days
        if gap in [1, 3, 7]:
            alerts.append(row)

    return alerts


# ==========================================
# AUTO LOG TRIGGER
# ==========================================

auto_log_plan()

# ==========================================
# FULL SYLLABUS (CLEANED BUT STRUCTURED)
# ==========================================

syllabus = {
    "FR": ["Ind AS 1","Ind AS 7","Ind AS 115","Ind AS 16","Ind AS 36","Ind AS 38","FI Scope","Consolidation"],
    "AFM": ["Capital Budgeting","Portfolio","Derivatives","Forex Risk","Valuation","M&A"],
    "Audit": ["Planning","Risk","Evidence","Reporting","Bank Audit","Ethics"],
    "DT": ["PGBP","Capital Gains","Deductions","TDS","Transfer Pricing"],
    "IDT": ["Supply","ITC","Returns","Refunds","Customs","FTP"]
}

# ==========================================
# SIDEBAR
# ==========================================

page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Syllabus Tracker",
    "Plan Ahead",
    "Study Log",
    "Revision Tracker"
])

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("📊 Dashboard")

    st.subheader("📌 Today's Plan")

    today = str(datetime.today().date())
    df = get_plan(today)

    if df.empty:
        st.info("No plan for today")
    else:
        for i, row in df.iterrows():

            col1, col2 = st.columns([5,1])

            with col1:
                done = st.checkbox(
                    f"{row['subject']} → {row['topic']} ({row['hours']} hrs)",
                    key=f"today_{i}"
                )
                if done:
                    update_status(row["subject"], row["topic"], 1)

            with col2:
                if st.button("❌", key=f"del_today_{i}"):
                    delete_plan(row["plan_date"], row["subject"], row["topic"])
                    st.rerun()

    st.divider()

    st.subheader("🔁 Revision Alerts")

    alerts = get_revision_alerts()

    if not alerts:
        st.success("No revision today")
    else:
        for a in alerts:
            st.warning(f"{a['subject']} → {a['topic']}")

    # PROGRESS SECTION
    st.divider()
    st.subheader("📊 Subject Progress (Hours Based)")

    total_target = sum(subject_hours.values())
    total_done = 0

    for subject in subject_hours:

        target = subject_hours[subject]
        completed = get_completed_hours(subject)

        total_done += completed

        percent = min(round((completed / target) * 100, 2), 100)

        st.write(f"### {subject}")
        st.progress(percent / 100)
        st.write(f"{completed:.1f} / {target} hrs ({percent}%)")

    overall_percent = round((total_done / total_target) * 100, 2)

    st.divider()
    st.subheader("📈 Overall Completion")

    st.progress(min(overall_percent / 100, 1.0))
    st.write(f"{total_done:.1f} / {total_target} hrs ({overall_percent}%)")

# ==========================================
# SYLLABUS TRACKER
# ==========================================

elif page == "Syllabus Tracker":

    st.title("📚 Syllabus Tracker")

    for subject, topics in syllabus.items():

        with st.expander(subject):

            for t in topics:

                checked = st.checkbox(
                    t,
                    value=bool(get_status(subject, t)),
                    key=f"{subject}_{t}"
                )

                update_status(subject, t, checked)

# ==========================================
# PLAN AHEAD
# ==========================================

elif page == "Plan Ahead":

    st.title("📅 Plan Ahead")

    plan_date = st.date_input("Select Date")

    subject = st.selectbox("Subject", list(syllabus.keys()))
    topic = st.selectbox("Topic", syllabus[subject])

    hours = st.number_input("Planned Hours", 0.5, 12.0, 2.0)

    if st.button("Add to Plan"):

        success = save_plan((
            str(plan_date),
            subject,
            topic,
            hours,
            0
        ))

        if success:
            st.success("Added!")
        else:
            st.warning("Already exists!")

    st.divider()

    df = get_plan(str(plan_date))

    if df.empty:
        st.info("No plans")
    else:
        for i, row in df.iterrows():

            col1, col2 = st.columns([5,1])

            with col1:
                st.write(f"{row['subject']} → {row['topic']} ({row['hours']} hrs)")

            with col2:
                if st.button("❌", key=f"del_{i}"):
                    delete_plan(row["plan_date"], row["subject"], row["topic"])
                    st.rerun()

# ==========================================
# STUDY LOG
# ==========================================

elif page == "Study Log":

    st.title("📘 Study Log")

    df = pd.read_sql_query("SELECT * FROM study_log", conn)

    if df.empty:
        st.info("No entries")
    else:
        st.dataframe(df, use_container_width=True)

# ==========================================
# REVISION TRACKER
# ==========================================

elif page == "Revision Tracker":

    st.title("🔁 Revision Plan")

    st.table(pd.DataFrame({
        "Subject": ["FR","AFM","Audit","DT","IDT"],
        "Rev1": ["10 Sep","15 Sep","20 Sep","25 Sep","28 Sep"],
        "Rev2": ["05 Oct","10 Oct","12 Oct","15 Oct","18 Oct"],
        "Rev3": ["25 Oct","27 Oct","28 Oct","29 Oct","30 Oct"]
    }))

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("CA Final Tracker 🚀")
