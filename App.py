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

# ==========================================
# SYLLABUS (FINAL CORRECT)
# ==========================================

syllabus = {

    # ======================================
    # FR
    # ======================================
    "FR": [

        "Introduction to Ind AS",
        "Conceptual Framework",

        "Ind AS 1 – Presentation",
        "Ind AS 34 – Interim",
        "Ind AS 7 – Cash Flow",

        "Ind AS 8 – Accounting Policies",
        "Ind AS 10 – Events",
        "Ind AS 113 – Fair Value",

        "Ind AS 115 – Revenue",

        "Ind AS 2 – Inventories",
        "Ind AS 16 – PPE",
        "Ind AS 23 – Borrowing Costs",
        "Ind AS 36 – Impairment",
        "Ind AS 38 – Intangible",
        "Ind AS 40 – Investment Property",
        "Ind AS 105 – Held for Sale",
        "Ind AS 116 – Leases",

        "Ind AS 41 – Agriculture",
        "Ind AS 20 – Govt Grants",
        "Ind AS 102 – Share-based",

        "Ind AS 19 – Employee Benefits",
        "Ind AS 37 – Provisions",

        "Ind AS 12 – Taxes",
        "Ind AS 21 – Forex",

        "Ind AS 24 – Related Party",
        "Ind AS 33 – EPS",
        "Ind AS 108 – Segments",

        "Financial Instruments – Scope",
        "Financial Instruments – Classification",
        "Financial Instruments – Equity vs Liability",
        "Financial Instruments – Derivatives",
        "Financial Instruments – Recognition",
        "Financial Instruments – Hedge",
        "Financial Instruments – Disclosure",

        "Ind AS 103 – Business Comb",
        "Consolidation",
        "Ind AS 101 – First-time",

        "Financial Analysis",
        "Ethics",
        "Accounting Tech"
    ],

    # ======================================
    # AFM
    # ======================================
    "AFM": [
        "Financial Policy",
        "Risk Management",
        "Capital Budgeting",
        "Security Valuation",
        "Portfolio",
        "Securitization",
        "Mutual Funds",
        "Derivatives",
        "Forex Risk",
        "International Finance",
        "Interest Rate Risk",
        "Business Valuation",
        "M&A",
        "Startup Finance"
    ],

    # ======================================
    # AUDIT
    # ======================================
    "Audit": [
        "Quality Control",
        "Audit Principles",
        "Planning",
        "Risk Assessment",
        "Evidence",
        "Review",
        "Reporting",
        "Special Areas",
        "Audit Services",
        "Assurance",
        "Digital Audit",
        "Group Audit",
        "Bank Audit",
        "PSU Audit",
        "Internal Audit",
        "Forensic Audit",
        "ESG",
        "Ethics"
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
        "Clubbing",
        "Set-off",
        "Deductions",
        "Entities",
        "Trusts",
        "Tax Planning",
        "Digital Tax",
        "TDS",
        "Authorities",
        "Assessment",
        "Appeals",
        "Disputes",
        "Anti Avoidance",
        "Tax Audit",
        "Non Resident",
        "DTAA",
        "Advance Ruling",
        "Transfer Pricing",
        "BEPS",
        "Tax Treaties"
    ],

    # ======================================
    # IDT
    # ======================================
    "IDT": [
        "Supply",
        "Charge",
        "Place of Supply",
        "Exemptions",
        "Time & Value",
        "ITC",
        "Registration",
        "Invoice",
        "E-way Bill",
        "Payment",
        "E-commerce",
        "Returns",
        "Import Export",
        "Refunds",
        "Job Work",
        "Assessment Audit",
        "Inspection",
        "Demand",
        "Liability Cases",
        "Penalties",
        "Appeals",
        "Advance Ruling",
        "Misc GST",

        "Customs Levy",
        "Types of Duty",
        "Classification",
        "Valuation",
        "Import Export Procedures",
        "Warehousing",
        "Customs Refund",

        "Foreign Trade Policy"
    ]
}

# ==========================================
# SIDEBAR
# ==========================================

page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Syllabus Tracker",
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

        summary.append({
            "Subject": subject,
            "Completed": completed,
            "Total": total,
            "%": percent
        })

    df = pd.DataFrame(summary)

    st.dataframe(df, use_container_width=True)

    st.subheader("Progress")

    for _, row in df.iterrows():
        st.write(f"### {row['Subject']}")
        st.progress(row["%"] / 100)

# ==========================================
# SYLLABUS TRACKER
# ==========================================

elif page == "Syllabus Tracker":

    st.title("📚 Syllabus Tracker")

    for subject, topics in syllabus.items():

        with st.expander(subject):

            completed = 0

            for topic in topics:

                checked = st.checkbox(
                    topic,
                    value=bool(get_status(subject, topic)),
                    key=f"{subject}_{topic}"
                )

                update_status(subject, topic, checked)

                if checked:
                    completed += 1

            percent = round((completed / len(topics)) * 100, 2)

            st.progress(percent / 100)
            st.write(f"{percent}% completed")

# ==========================================
# REVISION TRACKER
# ==========================================

elif page == "Revision Tracker":

    st.title("🔁 Revision Tracker")

    st.table(pd.DataFrame({
        "Subject": ["FR","AFM","Audit","DT","IDT"],
        "Rev 1": ["10 Sep","15 Sep","20 Sep","25 Sep","28 Sep"],
        "Rev 2": ["05 Oct","10 Oct","12 Oct","15 Oct","18 Oct"],
        "Rev 3": ["25 Oct","27 Oct","28 Oct","29 Oct","30 Oct"]
    }))

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("CA Final Tracker 🚀")
