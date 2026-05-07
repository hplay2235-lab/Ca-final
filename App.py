# ==========================================
# CA FINAL NOV 2026 TRACKER APP
# ==========================================
# Run using:
# pip install streamlit pandas plotly openpyxl
# streamlit run app.py
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="CA Final Nov 2026 Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATA FILES
# ==========================================

DATA_FILE = "study_log.csv"

# ==========================================
# SUBJECTS DATA
# ==========================================

subjects = {
    "FR": 220,
    "AFM": 180,
    "Audit": 140,
    "DT": 220,
    "IDT": 120,
    "IBS": 80
}

# ==========================================
# LOAD DATA
# ==========================================

if os.path.exists(DATA_FILE):
    study_df = pd.read_csv(DATA_FILE)
else:
    study_df = pd.DataFrame(columns=[
        "Date",
        "Subject",
        "Chapter",
        "Planned Hours",
        "Actual Hours",
        "Questions Solved",
        "Revision Done",
        "Remarks"
    ])

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("CA Final Tracker")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Study Entry",
        "Study Log",
        "Revision Tracker",
        "Mock Tests"
    ]
)

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("CA Final Nov 2026 Dashboard")

    # TOTAL HOURS
    total_target_hours = sum(subjects.values())

    subject_summary = []

    for subject, target in subjects.items():

        subject_data = study_df[study_df["Subject"] == subject]

        completed = subject_data["Actual Hours"].sum()

        percentage = round((completed / target) * 100, 2)

        if percentage >= 100:
            status = "Completed"
        elif percentage > 0:
            status = "In Progress"
        else:
            status = "Not Started"

        subject_summary.append({
            "Subject": subject,
            "Target Hours": target,
            "Completed Hours": round(completed, 2),
            "% Complete": percentage,
            "Status": status
        })

    summary_df = pd.DataFrame(subject_summary)

    # METRICS
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Target Hours",
        total_target_hours
    )

    col2.metric(
        "Completed Hours",
        round(summary_df["Completed Hours"].sum(), 2)
    )

    overall_percentage = round(
        (
            summary_df["Completed Hours"].sum()
            / total_target_hours
        ) * 100,
        2
    )

    col3.metric(
        "Overall Completion",
        f"{overall_percentage}%"
    )

    st.divider()

    # TABLE
    st.subheader("Subject Progress")

    st.dataframe(
        summary_df,
        use_container_width=True
    )

    # PROGRESS BARS
    st.subheader("Progress Bars")

    for _, row in summary_df.iterrows():

        st.write(f"### {row['Subject']}")

        st.progress(
            min(row["% Complete"] / 100, 1.0)
        )

        st.write(f"{row['% Complete']}% completed")

    st.divider()

    # CHART
    st.subheader("Completion Chart")

    fig = px.bar(
        summary_df,
        x="Subject",
        y="% Complete",
        color="% Complete",
        text="% Complete",
        title="Subject-wise Completion"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# ADD STUDY ENTRY
# ==========================================

elif page == "Add Study Entry":

    st.title("Add Study Entry")

    with st.form("study_form"):

        date = st.date_input(
            "Date",
            datetime.today()
        )

        subject = st.selectbox(
            "Subject",
            list(subjects.keys())
        )

        chapter = st.text_input(
            "Lecture / Chapter"
        )

        planned_hours = st.number_input(
            "Planned Hours",
            min_value=0.0,
            max_value=24.0,
            value=2.0
        )

        actual_hours = st.number_input(
            "Actual Hours",
            min_value=0.0,
            max_value=24.0,
            value=0.0
        )

        questions = st.number_input(
            "Questions Solved",
            min_value=0,
            max_value=1000,
            value=0
        )

        revision_done = st.checkbox(
            "Revision Done"
        )

        remarks = st.text_area(
            "Remarks"
        )

        submit = st.form_submit_button(
            "Save Entry"
        )

    if submit:

        new_row = {
            "Date": str(date),
            "Subject": subject,
            "Chapter": chapter,
            "Planned Hours": planned_hours,
            "Actual Hours": actual_hours,
            "Questions Solved": questions,
            "Revision Done": revision_done,
            "Remarks": remarks
        }

        study_df = pd.concat(
            [
                study_df,
                pd.DataFrame([new_row])
            ],
            ignore_index=True
        )

        study_df.to_csv(
            DATA_FILE,
            index=False
        )

        st.success("Study entry added successfully!")

# ==========================================
# STUDY LOG
# ==========================================

elif page == "Study Log":

    st.title("Study Log")

    if not study_df.empty:

        st.dataframe(
            study_df,
            use_container_width=True
        )

        st.download_button(
            "Download CSV",
            study_df.to_csv(index=False),
            file_name="study_log.csv",
            mime="text/csv"
        )

    else:
        st.info("No entries yet.")

# ==========================================
# REVISION TRACKER
# ==========================================

elif page == "Revision Tracker":

    st.title("Revision Tracker")

    revision_df = pd.DataFrame({
        "Subject": [
            "FR",
            "AFM",
            "Audit",
            "DT",
            "IDT",
            "IBS"
        ],
        "Revision 1 Target": [
            "10 Sep 2026",
            "15 Sep 2026",
            "20 Sep 2026",
            "25 Sep 2026",
            "28 Sep 2026",
            "30 Sep 2026"
        ],
        "Revision 2 Target": [
            "05 Oct 2026",
            "10 Oct 2026",
            "12 Oct 2026",
            "15 Oct 2026",
            "18 Oct 2026",
            "20 Oct 2026"
        ],
        "Revision 3 Target": [
            "25 Oct 2026",
            "27 Oct 2026",
            "28 Oct 2026",
            "29 Oct 2026",
            "30 Oct 2026",
            "31 Oct 2026"
        ]
    })

    st.table(revision_df)

# ==========================================
# MOCK TEST TRACKER
# ==========================================

elif page == "Mock Tests":

    st.title("Mock Test Tracker")

    mock_df = pd.DataFrame({
        "Subject": [
            "FR",
            "AFM",
            "Audit",
            "DT",
            "IDT",
            "IBS"
        ],
        "Test 1": [
            "Pending"
        ] * 6,
        "Test 2": [
            "Pending"
        ] * 6,
        "Full Syllabus": [
            "Pending"
        ] * 6,
        "Weak Areas": [
            ""
        ] * 6
    })

    st.dataframe(
        mock_df,
        use_container_width=True
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "CA Final Nov 2026 Preparation Tracker"
)
