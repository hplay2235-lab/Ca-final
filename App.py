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

    "FR": [
        "Ind AS 1", "Ind AS 7", "Ind AS 115",
        "Ind AS 16", "Ind AS 36", "Ind AS 38",
        "Financial Instruments", "Consolidation"
    ],

    "AFM": [
        "Capital Budgeting", "Portfolio",
        "Derivatives", "Forex Risk",
        "Business Valuation", "M&A"
    ],

    "Audit": [
        "Planning", "Risk", "Evidence",
        "Reporting", "Bank Audit",
        "Forensic", "Ethics"
    ],

    "DT": [
        "PGBP", "Capital Gains", "Deductions",
        "Assessment", "TDS", "Intl Tax", "TP"
    ],

    "IDT": [
        "Supply", "ITC", "Returns",
        "Refunds", "Customs", "FTP"
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
