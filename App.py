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
    status INTEGER
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_topic
ON syllabus_progress(subject, topic)
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
            alerts.append({
                "subject": row["subject"],
                "topic": row["topic"],
                "gap": gap
            })

    return alerts

# ==========================================
# SYLLABUS
# ==========================================

syllabus = {

    # ======================================
    # FR (DETAILED)
    # ======================================
    "FR": [

        "Introduction to Ind AS",
        "Conceptual Framework",

        "Ind AS 1 – Presentation of Financial Statements",
        "Ind AS 34 – Interim Financial Reporting",
        "Ind AS 7 – Cash Flow Statement",

        "Ind AS 8 – Accounting Policies",
        "Ind AS 10 – Events after Reporting Period",
        "Ind AS 113 – Fair Value Measurement",

        "Ind AS 115 – Revenue",

        "Ind AS 2 – Inventories",
        "Ind AS 16 – PPE",
        "Ind AS 23 – Borrowing Costs",
        "Ind AS 36 – Impairment",
        "Ind AS 38 – Intangible Assets",
        "Ind AS 40 – Investment Property",
        "Ind AS 105 – Assets Held for Sale",
        "Ind AS 116 – Leases",

        "Ind AS 41 – Agriculture",
        "Ind AS 20 – Government Grants",
        "Ind AS 102 – Share-based Payment",

        "Ind AS 19 – Employee Benefits",
        "Ind AS 37 – Provisions",

        "Ind AS 12 – Income Taxes",
        "Ind AS 21 – Forex",

        "Ind AS 24 – Related Party",
        "Ind AS 33 – EPS",
        "Ind AS 108 – Segments",

        "Financial Instruments – Scope",
        "Financial Instruments – Classification",
        "Financial Instruments – Equity vs Liability",
        "Financial Instruments – Derivatives",
        "Financial Instruments – Recognition",
        "Financial Instruments – Hedge Accounting",
        "Financial Instruments – Disclosures",

        "Ind AS 103 – Business Combinations",
        "Consolidation",
        "Ind AS 101 – First-time Adoption",

        "Financial Statement Analysis",
        "Professional Ethics",
        "Accounting & Technology"
    ],

    # ======================================
    # AFM
    # ======================================
    "AFM": [
        "Financial Policy & Strategy",
        "Risk Management",
        "Advanced Capital Budgeting",
        "Security Analysis",
        "Security Valuation",
        "Portfolio Management",
        "Securitization",
        "Mutual Funds",
        "Derivatives",
        "Forex Risk Management",
        "International Financial Management",
        "Interest Rate Risk",
        "Business Valuation",
        "Mergers & Acquisitions",
        "Startup Finance"
    ],

    # ======================================
    # AUDIT
    # ======================================
    "Audit": [
        "Quality Control",
        "Audit Principles & Responsibilities",
        "Audit Planning & Strategy",
        "Risk Assessment & Internal Control",
        "Audit Evidence",
        "Completion & Review",
        "Audit Reporting",
        "Specialised Areas",
        "Audit-related Services",
        "Review & Assurance Engagements",
        "Digital Auditing",
        "Group Audits",
        "Bank & NBFC Audit",
        "PSU Audit",
        "Internal Audit",
        "Forensic Audit & Due Diligence",
        "ESG & Sustainability",
        "Professional Ethics & Liabilities"
    ],

    # ======================================
    # DT
    # ======================================
    "DT": [
        "Basic Concepts",
        "Exempt Income",
        "PGBP",
        "Capital Gains",
        "Other Sources",
        "Clubbing of Income",
        "Set-off & Carry Forward",
        "Deductions",
        "Assessment of Entities",
        "Trusts & Special Entities",
        "Tax Planning vs Avoidance",
        "Digital Taxation",
        "TDS / TCS",
        "Tax Authorities",
        "Assessment Procedure",
        "Appeals & Revision",
        "Dispute Resolution",
        "Anti-Avoidance Measures",
        "Tax Audit & Ethics",
        "Non-Resident Taxation",
        "Double Taxation Relief",
        "Advance Ruling",
        "Transfer Pricing",
        "BEPS",
        "Tax Treaties"
    ],

    # ======================================
    # IDT
    # ======================================
    "IDT": [

        "Supply under GST",
        "Charge of GST",
        "Place of Supply",

        "Exemptions",

        "Time of Supply",
        "Value of Supply",

        "Input Tax Credit",

        "Registration",

        "Invoice & Documentation",

        "Accounts & E-way Bill",

        "Payment of Tax",

        "E-commerce",

        "Returns",

        "Import & Export",

        "Refunds",

        "Job Work",

        "Assessment & Audit",

        "Inspection & Search",

        "Demand & Recovery",

        "Liability in Special Cases",

        "Offences & Penalties",

        "Appeals & Revision",

        "Advance Ruling",

        "Miscellaneous GST",

        # Customs
        "Customs – Levy & Exemptions",
        "Types of Duty",
        "Classification",
        "Valuation",
        "Import & Export Procedures",
        "Warehousing",
        "Customs Refunds",

        # FTP
        "Foreign Trade Policy"
    ]
}

# ==========================================
# SIDEBAR
# ==========================================

page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Syllabus Tracker",
    "Daily Planner",
    "Add Study Entry",
    "Study Log",
    "Revision Tracker"
])

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("📊 CA Final Dashboard")

    exam_date = datetime(2026, 11, 1)
    days_left = (exam_date - datetime.today()).days

    st.metric("Days Left", days_left)

    summary = []

    for subject, topics in syllabus.items():

        completed = sum(get_status(subject, t) for t in topics)
        total = len(topics)

        percent = round((completed / total) * 100, 2)

        hours_df = pd.read_sql_query(
            f"SELECT SUM(hours) as h FROM study_log WHERE subject='{subject}'",
            conn
        )

        hours = hours_df["h"].iloc[0] if hours_df["h"].iloc[0] else 0

        summary.append({
            "Subject": subject,
            "Topics Done": completed,
            "Total": total,
            "% Completion": percent,
            "Hours": round(hours, 2)
        })

    df = pd.DataFrame(summary)

    st.dataframe(df, use_container_width=True)

    st.subheader("Progress")

    for _, row in df.iterrows():
        st.write(f"### {row['Subject']}")
        st.progress(row["% Completion"] / 100)

    st.divider()

    # REVISION ALERTS
    st.subheader("🔁 Revision Reminders")

    alerts = get_revision_alerts()

    if not alerts:
        st.success("No revisions today 👍")
    else:
        for a in alerts:
            st.warning(f"{a['subject']} → {a['topic']} (Revise)")

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

    if not pending:
        st.success("All topics done!")
        st.stop()

    per_day = max(round(len(pending) / days_left), 1)

    st.write(f"Topics/day: **{per_day}**")

    today_plan = pending[:per_day]

    for s, t in today_plan:
        done = st.checkbox(f"{s} → {t}", key=f"plan_{s}_{t}")
        if done:
            update_status(s, t, 1)

# ==========================================
# ADD ENTRY
# ==========================================

elif page == "Add Study Entry":

    st.title("➕ Add Study Entry")

    subject = st.selectbox("Subject", list(syllabus.keys()))
    topic = st.selectbox("Topic", syllabus[subject])

    date = st.date_input("Date", datetime.today())

    hours = st.number_input("Hours", 0.0, 24.0, 2.0)
    questions = st.number_input("Questions", 0, 1000, 0)
    revision = st.checkbox("Revision Done")
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
        st.info("No entries yet")
    else:
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "study_log.csv"
        )

# ==========================================
# REVISION TRACKER
# ==========================================

elif page == "Revision Tracker":

    st.title("🔁 Revision Tracker")

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
