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
    status INTEGER,
    UNIQUE(plan_date, subject, topic)
)
""")

conn.commit()

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


def save_study_entry(data):
    conn.execute(
        "INSERT INTO study_log VALUES (?, ?, ?, ?, ?, ?, ?)",
        data
    )
    conn.commit()


def save_plan(data):
    try:
        conn.execute(
            "INSERT INTO study_plan VALUES (?, ?, ?, ?)",
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
# SYLLABUS (DETAILED)
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
    "Daily Planner",
    "Plan Ahead",
    "Add Study Entry",
    "Study Log",
    "Revision Tracker"
])

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("📊 Dashboard")

    exam_date = datetime(2026, 11, 1)
    days_left = (exam_date - datetime.today()).days

    st.metric("Days Left", days_left)

    st.divider()

    # TODAY PLAN
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
                    f"{row['subject']} → {row['topic']}",
                    key=f"today_{i}"
                )

                if done:
                    update_status(row["subject"], row["topic"], 1)

            with col2:
                if st.button("❌", key=f"del_today_{i}"):
                    delete_plan(row["plan_date"], row["subject"], row["topic"])
                    st.rerun()

    st.divider()

    # REVISION ALERTS
    st.subheader("🔁 Revision Alerts")

    alerts = get_revision_alerts()

    if not alerts:
        st.success("No revision today")
    else:
        for _, a in pd.DataFrame(alerts).iterrows():
            st.warning(f"{a['subject']} → {a['topic']}")

# ==========================================
# SYLLABUS TRACKER
# ==========================================

elif page == "Syllabus Tracker":

    st.title("📚 Syllabus Tracker")

    for subject, topics in syllabus.items():

        with st.expander(subject):

            done = 0

            for t in topics:

                checked = st.checkbox(
                    t,
                    value=bool(get_status(subject, t)),
                    key=f"{subject}_{t}"
                )

                update_status(subject, t, checked)

                if checked:
                    done += 1

            percent = round((done / len(topics)) * 100, 2)

            st.progress(percent / 100)
            st.write(f"{percent}% completed")

# ==========================================
# DAILY PLANNER
# ==========================================

elif page == "Daily Planner":

    st.title("📅 Daily Planner")

    exam_date = datetime(2026, 11, 1)
    days_left = max((exam_date - datetime.today()).days, 1)

    pending = []

    for s, topics in syllabus.items():
        for t in topics:
            if get_status(s, t) == 0:
                pending.append((s, t))

    per_day = max(round(len(pending) / days_left), 1)

    st.write(f"Topics/day: **{per_day}**")

    today_plan = pending[:per_day]

    for s, t in today_plan:
        done = st.checkbox(f"{s} → {t}", key=f"plan_{s}_{t}")
        if done:
            update_status(s, t, 1)

# ==========================================
# PLAN AHEAD
# ==========================================

elif page == "Plan Ahead":

    st.title("📅 Plan Ahead")

    plan_date = st.date_input("Select Date")

    subject = st.selectbox("Subject", list(syllabus.keys()))
    topic = st.selectbox("Topic", syllabus[subject])

    if st.button("Add to Plan"):

        success = save_plan((
            str(plan_date),
            subject,
            topic,
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
                st.write(f"{row['subject']} → {row['topic']}")

            with col2:
                if st.button("❌", key=f"del_{i}"):
                    delete_plan(row["plan_date"], row["subject"], row["topic"])
                    st.rerun()

# ==========================================
# ADD ENTRY
# ==========================================

elif page == "Add Study Entry":

    st.title("➕ Study Entry")

    subject = st.selectbox("Subject", list(syllabus.keys()))
    topic = st.selectbox("Topic", syllabus[subject])

    date = st.date_input("Date", datetime.today())

    hours = st.number_input("Hours", 0.0, 24.0, 2.0)
    questions = st.number_input("Questions", 0, 1000, 0)
    revision = st.checkbox("Revision")
    remarks = st.text_area("Remarks")

    if st.button("Save"):
        save_study_entry((
            str(date), subject, topic,
            hours, questions,
            int(revision), remarks
        ))
        st.success("Saved!")

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
