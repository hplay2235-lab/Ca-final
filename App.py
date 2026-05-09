import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="CA Final Tracker",
    layout="wide"
)

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

def get_topic_status(subject, topic):
    result = conn.execute(
        "SELECT status FROM syllabus_progress WHERE subject=? AND topic=?",
        (subject, topic)
    ).fetchone()
    return result[0] if result else 0


def update_topic_status(subject, topic, status):
    conn.execute(
        "INSERT OR REPLACE INTO syllabus_progress VALUES (?, ?, ?)",
        (subject, topic, int(status))
    )
    conn.commit()

# ==========================================
# SYLLABUS DATA
# ==========================================
syllabus = {

    # ==========================================
    # FR
    # ==========================================
"FR": [

    # Basics
    "Introduction to Ind AS",
    "Conceptual Framework",

    # Presentation
    "Ind AS 1 – Presentation of Financial Statements",
    "Ind AS 34 – Interim Financial Reporting",
    "Ind AS 7 – Cash Flow Statement",

    # Accounting Policies
    "Ind AS 8 – Accounting Policies",
    "Ind AS 10 – Events after Reporting Period",
    "Ind AS 113 – Fair Value Measurement",

    # Revenue
    "Ind AS 115 – Revenue",

    # Assets
    "Ind AS 2 – Inventories",
    "Ind AS 16 – PPE",
    "Ind AS 23 – Borrowing Costs",
    "Ind AS 36 – Impairment",
    "Ind AS 38 – Intangible Assets",
    "Ind AS 40 – Investment Property",
    "Ind AS 105 – Assets Held for Sale",
    "Ind AS 116 – Leases",

    # Other Standards
    "Ind AS 41 – Agriculture",
    "Ind AS 20 – Government Grants",
    "Ind AS 102 – Share-based Payment",

    # Liabilities
    "Ind AS 19 – Employee Benefits",
    "Ind AS 37 – Provisions",

    # Impact Items
    "Ind AS 12 – Income Taxes",
    "Ind AS 21 – Forex",

    # Disclosures
    "Ind AS 24 – Related Party",
    "Ind AS 33 – EPS",
    "Ind AS 108 – Segments",

    # Financial Instruments (kept grouped intentionally)
    "Financial Instruments – Scope",
    "Financial Instruments – Classification",
    "Financial Instruments – Equity vs Liability",
    "Financial Instruments – Derivatives",
    "Financial Instruments – Recognition",
    "Financial Instruments – Hedge Accounting",
    "Financial Instruments – Disclosures",

    # Advanced
    "Ind AS 103 – Business Combinations",
    "Consolidation",
    "Ind AS 101 – First-time Adoption",

    # Extras
    "Financial Statement Analysis",
    "Professional Ethics",
    "Accounting & Technology"
]

    # ==========================================
    # AFM
    # ==========================================

    "AFM": [

        "Financial Policy & Strategy",
        "Risk Management",

        "Capital Budgeting – Advanced",

        "Security Analysis & Valuation",

        "Portfolio Management",

        "Securitization & Mutual Funds",

        "Derivatives",

        "Forex Risk Management",

        "International Financial Management",

        "Interest Rate Risk",

        "Business Valuation",

        "Mergers & Acquisitions",

        "Startup Finance"
    ],

    # ==========================================
    # AUDIT
    # ==========================================

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

    # ==========================================
    # DT
    # ==========================================

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

    # ==========================================
    # IDT
    # ==========================================

    "IDT": [

        # GST Core
        "Supply under GST",
        "Charge of GST",
        "Place of Supply",

        "Exemptions",

        "Time & Value of Supply",

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

        completed = sum(
            get_topic_status(subject, t)
            for t in topics
        )

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
                    value=bool(get_topic_status(subject, topic)),
                    key=f"{subject}_{topic}"
                )

                update_topic_status(subject, topic, checked)

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
