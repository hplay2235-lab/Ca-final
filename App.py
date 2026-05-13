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
    next_revision TEXT,
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
# SUBJECT HOURS
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


# ✅ OPTION 1: UPDATE INSTEAD OF DUPLICATE
def save_plan(data):
    try:
        conn.execute("""
            INSERT INTO study_plan (plan_date, subject, topic, hours, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(plan_date, subject, topic)
            DO UPDATE SET hours=excluded.hours
        """, data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
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
    today = datetime.today()
    today_str = str(today.date())

    df = get_plan(today_str)

    for _, row in df.iterrows():

        exists = conn.execute(
            "SELECT * FROM study_log WHERE date=? AND subject=? AND topic=?",
            (today_str, row["subject"], row["topic"])
        ).fetchone()

        if not exists:
            next_rev = today + timedelta(days=1)

            conn.execute(
                "INSERT INTO study_log VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    today_str,
                    row["subject"],
                    row["topic"],
                    row["hours"],
                    0,
                    0,
                    str(next_rev.date()),
                    "Auto Planned"
                )
            )

    conn.commit()


def get_completed_hours(subject):
    df = pd.read_sql_query(
        f"SELECT hours FROM study_log WHERE subject='{subject}'",
        conn
    )
    return df["hours"].sum() if not df.empty else 0


def get_revision_alerts():
    df = pd.read_sql_query("SELECT * FROM study_log", conn)
    today = str(datetime.today().date())
    return df[df["next_revision"] == today] if not df.empty else pd.DataFrame()

def delete_log(date, subject, topic):
    conn.execute(
        "DELETE FROM study_log WHERE date=? AND subject=? AND topic=?",
        (date, subject, topic)
    )
    conn.commit()

# ==========================================
# AUTO LOG
# ==========================================

auto_log_plan()

# ==========================================
# FULL DETAILED SYLLABUS
# ==========================================

syllabus = {

# ==========================================
# PAPER 1: FINANCIAL REPORTING (FR)
# ==========================================

"FR": {

"Introduction & Framework": [
"Introduction to Indian Accounting Standards (Ind AS)",
"Conceptual Framework for Financial Reporting"
],

"Presentation of Financial Statements": [
"Ind AS 1 – Presentation of Financial Statements",
"Ind AS 34 – Interim Financial Reporting",
"Ind AS 7 – Statement of Cash Flows"
],

"Measurement & Accounting Policies": [
"Ind AS 8 – Accounting Policies, Changes in Estimates & Errors",
"Ind AS 10 – Events after the Reporting Period",
"Ind AS 113 – Fair Value Measurement"
],

"Revenue Recognition": [
"Ind AS 115 – Revenue from Contracts with Customers"
],

"Assets of Financial Statements": [
"Ind AS 2 – Inventories",
"Ind AS 16 – Property, Plant & Equipment",
"Ind AS 23 – Borrowing Costs",
"Ind AS 36 – Impairment of Assets",
"Ind AS 38 – Intangible Assets",
"Ind AS 40 – Investment Property",
"Ind AS 105 – Non-current Assets Held for Sale",
"Ind AS 116 – Leases"
],

"Other Indian Accounting Standards": [
"Ind AS 41 – Agriculture",
"Ind AS 20 – Government Grants",
"Ind AS 102 – Share-Based Payment"
],

"Liabilities of Financial Statements": [
"Ind AS 19 – Employee Benefits",
"Ind AS 37 – Provisions, Contingent Liabilities & Contingent Assets"
],

"Items Impacting Financial Statements": [
"Ind AS 12 – Income Taxes",
"Ind AS 21 – Effects of Changes in Foreign Exchange Rates"
],

"Disclosures in Financial Statements": [
"Ind AS 24 – Related Party Disclosures",
"Ind AS 33 – Earnings per Share",
"Ind AS 108 – Operating Segments"
],

"Financial Instruments": [
"Scope & Definitions",
"Classification & Measurement",
"Equity vs Financial Liabilities",
"Derivatives & Embedded Derivatives",
"Recognition & Derecognition",
"Hedge Accounting",
"Disclosures"
],

"Advanced Accounting Standards": [
"Ind AS 103 – Business Combinations",
"Consolidated & Separate Financial Statements",
"Ind AS 101 – First-time Adoption of Ind AS"
],

"Other Areas": [
"Analysis of Financial Statements",
"Professional & Ethical Duties of Chartered Accountant",
"Accounting & Technology"
]

},

# ==========================================
# PAPER 2: AFM
# ==========================================

"AFM": {

"Financial Policy & Strategy": [
"Financial Policy",
"Corporate Strategy"
],

"Risk Management": [
"Risk Management Techniques",
"Derivatives – Futures, Options, Swaps"
],

"Capital Budgeting": [
"Advanced Capital Budgeting Decisions"
],

"Markets & Investments": [
"Security Analysis",
"Security Valuation",
"Portfolio Management",
"Mutual Funds",
"Securitization"
],

"Foreign Exchange & International Finance": [
"Foreign Exchange Exposure",
"Forex Risk Management",
"International Financial Management",
"Interest Rate Risk Management"
],

"Valuation & Restructuring": [
"Business Valuation",
"Mergers & Acquisitions",
"Corporate Restructuring",
"Startup Finance"
]

},

# ==========================================
# PAPER 3: AUDIT
# ==========================================

"Audit": {

"Core Principles": [
"Quality Control",
"Auditing Principles",
"Auditor Responsibilities"
],

"Audit Planning & Execution": [
"Audit Planning",
"Audit Strategy",
"Materiality",
"Risk Assessment",
"Internal Control",
"Audit Evidence",
"Completion & Review"
],

"Audit Reporting": [
"Audit Reports"
],

"Specialised Areas": [
"Specialised Audits",
"Audit-related Services",
"Review of Financial Information",
"Assurance Engagements"
],

"Advanced Audits": [
"Digital Auditing",
"Group Audits",
"Bank Audit",
"NBFC Audit",
"PSU Audit",
"Internal Audit"
],

"Forensic & Emerging Areas": [
"Due Diligence",
"Forensic Audit",
"ESG & Sustainability Assurance"
],

"Ethics & Liabilities": [
"Professional Ethics",
"Auditor Liabilities"
]

},

# ==========================================
# PAPER 4: DT
# ==========================================

"DT": {

"Basic Concepts": [
"Basic Concepts of Income Tax",
"Exempt Income"
],

"Heads of Income": [
"Profits & Gains of Business or Profession",
"Capital Gains",
"Income from Other Sources"
],

"Adjustments": [
"Clubbing of Income",
"Set-off & Carry Forward of Losses",
"Deductions from Gross Total Income"
],

"Entities": [
"Assessment of Various Entities",
"Assessment of Trusts & Special Entities"
],

"Procedural Aspects": [
"TDS/TCS",
"Income Tax Authorities",
"Assessment Procedure",
"Appeals & Revision",
"Dispute Resolution"
],

"Advanced Taxation": [
"Tax Planning",
"Tax Avoidance vs Evasion",
"Taxation of Digital Transactions",
"Anti-Avoidance Measures",
"Tax Audit & Ethical Compliance"
],

"International Taxation": [
"Non-Resident Taxation",
"Double Taxation Relief",
"Transfer Pricing",
"BEPS",
"Tax Treaties",
"Model Tax Conventions"
],

"Other": [
"Advance Rulings",
"Latest Developments"
]

},

# ==========================================
# PAPER 5: IDT
# ==========================================

"IDT": {

"GST Basics": [
"Supply under GST",
"Charge of GST",
"Place of Supply",
"Exemptions"
],

"GST Core Concepts": [
"Time of Supply",
"Value of Supply",
"Input Tax Credit",
"Registration"
],

"GST Compliance": [
"Tax Invoice",
"Credit & Debit Notes",
"Accounts & Records",
"E-way Bill",
"Returns",
"Payment of Tax"
],

"GST Advanced": [
"Import & Export under GST",
"Refunds",
"Job Work",
"Assessment & Audit",
"Inspection, Search & Seizure",
"Demand & Recovery",
"Liability in Special Cases",
"Offences, Penalties & Ethics"
],

"GST Litigation": [
"Appeals & Revision",
"Advance Ruling"
],

"Customs": [
"Customs Duty – Levy & Exemptions",
"Types of Duty",
"Classification of Goods",
"Valuation under Customs",
"Import & Export Procedures",
"Warehousing",
"Refunds (Customs)"
],

"Foreign Trade Policy": [
"Foreign Trade Policy"
]

}

}

# ==========================================
# SIDEBAR
# ==========================================

page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Syllabus Tracker",
    "Plan Ahead",
    "Study Log"
])

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("📊 Dashboard")

    today = str(datetime.today().date())
    df = get_plan(today)

    st.subheader("📌 Today's Plan")

    if df.empty:
        st.info("No plan today")
    else:
        for i, row in df.iterrows():
            done = st.checkbox(
                f"{row['subject']} → {row['topic']} ({row['hours']} hrs)",
                key=f"plan_{i}"
            )
            if done:
                update_status(row["subject"], row["topic"], 1)

    st.divider()

    st.subheader("🔁 Revision Alerts")

    alerts = get_revision_alerts()

    if alerts.empty:
        st.success("No revision today")
    else:
        for _, row in alerts.iterrows():
            st.warning(f"{row['subject']} → {row['topic']}")

    st.divider()

    st.subheader("📊 Progress")

    total_target = sum(subject_hours.values())
    total_done = 0

    for sub in subject_hours:
        target = subject_hours[sub]
        done = get_completed_hours(sub)

        total_done += done
        percent = min((done / target) * 100, 100)

        st.write(sub)
        st.progress(percent / 100)
        st.write(f"{done:.1f}/{target} hrs ({round(percent,2)}%)")

    overall = (total_done / total_target) * 100

    st.subheader("Overall")
    st.progress(overall / 100)
    st.write(f"{round(overall,2)}%")

# ==========================================
# SYLLABUS TRACKER
# ==========================================

elif page == "Syllabus Tracker":

    st.title("📚 Syllabus Tracker")

    for subject, chapters in syllabus.items():

        st.header(subject)

        for chapter, topics in chapters.items():

            with st.expander(chapter):

                for t in topics:

                    checked = st.checkbox(
                        t,
                        value=bool(get_status(subject, t)),
                        key=f"{subject}_{chapter}_{t}"
                    )

                    update_status(subject, t, checked)

# ==========================================
# PLAN AHEAD
# ==========================================

elif page == "Plan Ahead":

    st.title("📅 Plan Ahead")

    date = st.date_input("Date")

    subject = st.selectbox("Subject", list(syllabus.keys()))
    chapter = st.selectbox("Chapter", list(syllabus[subject].keys()))
    topic = st.selectbox("Topic", syllabus[subject][chapter])

    hours = st.number_input("Hours", 0.5, 12.0, 2.0)

    if st.button("Add / Update Plan"):

        success = save_plan((str(date), subject, topic, hours, 0))

        if success:
            st.success("Added / Updated ✅")

    st.divider()

    df = get_plan(str(date))

    if not df.empty:
        for i, row in df.iterrows():

            col1, col2 = st.columns([5,1])

            with col1:
                st.write(f"{row['subject']} → {row['topic']} ({row['hours']} hrs)")

            with col2:
                if st.button("❌", key=i):
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
        for i, row in df.iterrows():

            col1, col2, col3, col4 = st.columns([4,2,2,1])

            with col1:
                st.write(f"{row['subject']} → {row['topic']}")

            with col2:
                st.write(f"Next Rev: {row['next_revision']}")

            with col3:
                done = st.checkbox("Revision Done", key=f"rev_{i}")

                if done:
                    conn.execute(
                        "UPDATE study_log SET revision=1 WHERE date=? AND subject=? AND topic=?",
                        (row["date"], row["subject"], row["topic"])
                    )
                    conn.commit()

            with col4:
                if st.button("❌", key=f"del_{i}"):
                    delete_log(row["date"], row["subject"], row["topic"])
                    st.rerun()

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("CA Final Tracker 🚀")
