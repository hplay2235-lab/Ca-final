import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
                (today, row["subject"], row["topic"], 0, 0, 0, "Auto Planned")
            )

    conn.commit()


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
# FULL SYLLABUS
# ==========================================

syllabus = {
    "FR": [
        "Introduction to Ind AS","Conceptual Framework",
        "Ind AS 1","Ind AS 34","Ind AS 7",
        "Ind AS 8","Ind AS 10","Ind AS 113",
        "Ind AS 115",
        "Ind AS 2","Ind AS 16","Ind AS 23","Ind AS 36",
        "Ind AS 38","Ind AS 40","Ind AS 105","Ind AS 116",
        "Ind AS 41","Ind AS 20","Ind AS 102",
        "Ind AS 19","Ind AS 37",
        "Ind AS 12","Ind AS 21",
        "Ind AS 24","Ind AS 33","Ind AS 108",
        "FI Scope","FI Classification","FI Equity vs Liability",
        "FI Derivatives","FI Recognition","FI Hedge","FI Disclosure",
        "Ind AS 103","Consolidation","Ind AS 101",
        "Analysis","Ethics","Technology"
    ],
    "AFM": [
        "Financial Policy","Risk Management","Capital Budgeting",
        "Security Analysis","Valuation","Portfolio",
        "Securitization","Mutual Funds","Derivatives",
        "Forex Risk","International Finance","Interest Rate Risk",
        "Business Valuation","M&A","Startup Finance"
    ],
    "Audit": [
        "Quality Control","Audit Principles","Planning","Risk",
        "Evidence","Review","Reporting","Special Areas",
        "Audit Services","Assurance","Digital Audit",
        "Group Audit","Bank Audit","PSU Audit","Internal Audit",
        "Forensic","ESG","Ethics"
    ],
    "DT": [
        "Basic Concepts","Exempt Income","PGBP","Capital Gains",
        "Other Sources","Clubbing","Set-off","Deductions",
        "Entities","Trusts","Tax Planning","Digital Tax",
        "TDS","Authorities","Assessment","Appeals",
        "Disputes","Anti Avoidance","Tax Audit",
        "Non Resident","DTAA","Advance Ruling",
        "Transfer Pricing","BEPS","Treaties"
    ],
    "IDT": [
        "Supply","Charge","Place of Supply","Exemptions",
        "Time","Value","ITC","Registration",
        "Invoice","E-way Bill","Payment",
        "E-commerce","Returns","Import Export",
        "Refunds","Job Work","Assessment","Inspection",
        "Demand","Liability","Penalties","Appeals",
        "Advance Ruling","Misc GST",
        "Customs","Duty Types","Classification",
        "Valuation","Import Procedures","Warehousing",
        "Refunds Customs","FTP"
    ]
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
            done = st.checkbox(
                f"{row['subject']} → {row['topic']}",
                key=f"today_{i}"
            )
            if done:
                update_status(row["subject"], row["topic"], 1)

    st.divider()

    st.subheader("🔁 Revision Alerts")

    alerts = get_revision_alerts()

    if not alerts:
        st.success("No revision today")
    else:
        for a in alerts:
            st.warning(f"{a['subject']} → {a['topic']}")

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
