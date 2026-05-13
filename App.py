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

"FR": {

"Introduction": [
"Introduction to Ind AS",
"Conceptual Framework"
],

"Presentation": [
"Ind AS 1 – Presentation of Financial Statements",
"Ind AS 34 – Interim Financial Reporting",
"Ind AS 7 – Statement of Cash Flows"
],

"Measurement": [
"Ind AS 8 – Accounting Policies",
"Ind AS 10 – Events after Reporting Period",
"Ind AS 113 – Fair Value Measurement"
],

"Revenue": [
"Ind AS 115 – Revenue from Contracts"
],

"Assets": [
"Ind AS 2 – Inventories",
"Ind AS 16 – PPE",
"Ind AS 23 – Borrowing Costs",
"Ind AS 36 – Impairment",
"Ind AS 38 – Intangible",
"Ind AS 40 – Investment Property",
"Ind AS 105 – Held for Sale",
"Ind AS 116 – Leases"
],

"Financial Instruments": [
"FI – Scope",
"FI – Classification",
"FI – Equity vs Liability",
"FI – Derivatives",
"FI – Recognition",
"FI – Hedge",
"FI – Disclosure"
],

"Advanced": [
"Ind AS 103 – Business Combinations",
"Consolidation",
"Ind AS 101 – First-time Adoption"
],

"Other": [
"Analysis",
"Ethics",
"Technology"
]

},

"AFM": {
"Core": [
"Financial Policy","Risk Management","Capital Budgeting"
],
"Markets": [
"Security Analysis","Valuation","Portfolio","Mutual Funds"
],
"Advanced": [
"Derivatives","Forex Risk","International Finance","Interest Rate Risk"
],
"Strategic": [
"Business Valuation","M&A","Startup Finance"
]
},

"Audit": {
"Core": [
"Quality Control","Audit Principles","Planning","Risk"
],
"Execution": [
"Evidence","Review","Reporting"
],
"Special": [
"Bank Audit","PSU Audit","Internal Audit"
],
"Advanced": [
"Forensic","ESG","Digital Audit","Group Audit"
],
"Ethics": [
"Professional Ethics"
]
},

"DT": {
"Core": [
"Basic Concepts","PGBP","Capital Gains","Other Sources"
],
"Adjustments": [
"Clubbing","Set-off","Deductions"
],
"Entities": [
"Entities","Trusts"
],
"Procedures": [
"TDS","Authorities","Assessment","Appeals"
],
"International": [
"Non Resident","DTAA","Transfer Pricing","BEPS"
],
"Advanced": [
"Anti Avoidance","Tax Audit","Digital Tax"
]
},

"IDT": {

"GST Basics": [
"Supply","Charge","Place of Supply","Exemptions"
],

"GST Core": [
"Time","Value","ITC","Registration"
],

"GST Compliance": [
"Invoice","Returns","Payment","E-way Bill"
],

"GST Advanced": [
"Refunds","Job Work","Assessment","Inspection","Demand"
],

"Customs": [
"Levy","Classification","Valuation","Procedures","Warehousing"
],

"FTP": [
"Foreign Trade Policy"
]

}

}
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

    st.title("📚 Syllabus Tracker (Notion Style)")

    for subject, chapters in syllabus.items():

        st.header(f"📘 {subject}")

        subject_total = 0
        subject_done = 0

        for chapter, topics in chapters.items():

            with st.expander(f"📂 {chapter}"):

                chapter_done = 0

                for topic in topics:

                    checked = st.checkbox(
                        topic,
                        value=bool(get_status(subject, topic)),
                        key=f"{subject}_{chapter}_{topic}"
                    )

                    update_status(subject, topic, checked)

                    subject_total += 1

                    if checked:
                        chapter_done += 1
                        subject_done += 1

                # CHAPTER PROGRESS
                percent = round((chapter_done / len(topics)) * 100, 2)

                st.progress(percent / 100)
                st.write(f"{percent}% completed")

        # SUBJECT PROGRESS
        if subject_total > 0:
            sub_percent = round((subject_done / subject_total) * 100, 2)

            st.subheader(f"{subject} Progress")
            st.progress(sub_percent / 100)
            st.write(f"{sub_percent}% completed")

        st.divider()

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
