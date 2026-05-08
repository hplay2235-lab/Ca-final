import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="CA Final Nov 2026 Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    div[data-testid="metric-container"] {
        background-color: #f5f5f5;
        border: 1px solid #dddddd;
        padding: 15px;
        border-radius: 12px;
    }

    section.main > div {
        background-color: #fafafa;
    }

    h1, h2, h3 {
        color: #1f4e79;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect(
    "tracker.db",
    check_same_thread=False
)

# ==========================================
# SUBJECTS
# ==========================================

subjects = {
    "FR": 200,
    "AFM": 200,
    "Audit": 110,
    "DT": 200,
    "IDT": 110
}

# ==========================================
# PREFILLED COMPLETED HOURS
# ==========================================

prefilled_progress = {
    "FR": 0,
    "AFM": 0,
    "Audit": 0,
    "DT": 10,
    "IDT": 65
}

# ==========================================
# LOAD DATA
# ==========================================

try:
    study_df = pd.read_sql_query(
        "SELECT * FROM study_log",
        conn
    )

except:
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
# SAVE FUNCTION
# ==========================================

def save_data(df):

    df.to_sql(
        "study_log",
        conn,
        if_exists="replace",
        index=False
    )

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

    # EXAM COUNTDOWN

    exam_date = datetime(2026, 11, 1)

    days_left = (
        exam_date - datetime.today()
    ).days

    st.metric(
        "Days Left For Exam",
        days_left
    )

    total_target_hours = sum(
        subjects.values()
    )

    subject_summary = []

    for subject, target in subjects.items():

        subject_data = study_df[
            study_df["Subject"] == subject
        ]

        completed = (
            subject_data[
                "Actual Hours"
            ].sum()
            + prefilled_progress.get(subject, 0)
        )

        pending = max(
            target - completed,
            0
        )

        percentage = min(
            round(
                (completed / target) * 100,
                2
            ),
            100
        )

        if percentage >= 100:
            status = "Completed"

        elif percentage > 0:
            status = "In Progress"

        else:
            status = "Not Started"

        subject_summary.append({
            "Subject": subject,
            "Lecture Hours": target,
            "Completed Hours": round(
                completed,
                2
            ),
            "Pending Hours": round(
                pending,
                2
            ),
            "% Complete": percentage,
            "Status": status
        })

    summary_df = pd.DataFrame(
        subject_summary
    )

    # METRICS

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Lecture Hours",
        total_target_hours
    )

    col2.metric(
        "Completed Hours",
        round(
            summary_df[
                "Completed Hours"
            ].sum(),
            2
        )
    )

    overall_percentage = round(
        (
            summary_df[
                "Completed Hours"
            ].sum()
            / total_target_hours
        ) * 100,
        2
    )

    col3.metric(
        "Overall Completion",
        f"{overall_percentage}%"
    )

    st.divider()

    # SUBJECT TABLE

    st.subheader("Subject Progress")

    st.dataframe(
        summary_df,
        use_container_width=True
    )

    st.divider()

    # PROGRESS BARS

    st.subheader("Progress Bars")

    for _, row in summary_df.iterrows():

        st.write(
            f"### {row['Subject']}"
        )

        st.progress(
            min(
                row["% Complete"] / 100,
                1.0
            )
        )

        st.write(
            f"""
            Completed:
            {row['Completed Hours']} hrs
            | Pending:
            {row['Pending Hours']} hrs
            """
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

        if chapter.strip() == "":

            st.error(
                "Please enter chapter name."
            )

        else:

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

            save_data(study_df)

            st.success(
                "Study entry added successfully!"
            )

# ==========================================
# STUDY LOG
# ==========================================

elif page == "Study Log":

    st.title("Study Log")

    if not study_df.empty:

        selected_subject = st.selectbox(
            "Filter by Subject",
            ["All"] + list(subjects.keys())
        )

        if selected_subject != "All":

            filtered_df = study_df[
                study_df["Subject"]
                == selected_subject
            ]

        else:
            filtered_df = study_df

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        st.divider()

        st.subheader("Edit/Delete Entry")

        row_to_edit = st.number_input(
            "Enter Row Number",
            min_value=0,
            max_value=len(filtered_df)-1,
            step=1
        )

        selected_row = filtered_df.iloc[
            row_to_edit
        ]

        with st.form("edit_form"):

            updated_actual = st.number_input(
                "Actual Hours",
                value=float(
                    selected_row[
                        "Actual Hours"
                    ]
                )
            )

            updated_questions = st.number_input(
                "Questions Solved",
                value=int(
                    selected_row[
                        "Questions Solved"
                    ]
                )
            )

            updated_remarks = st.text_area(
                "Remarks",
                value=str(
                    selected_row[
                        "Remarks"
                    ]
                )
            )

            update_btn = st.form_submit_button(
                "Update Entry"
            )

        if update_btn:

            original_index = selected_row.name

            study_df.loc[
                original_index,
                "Actual Hours"
            ] = updated_actual

            study_df.loc[
                original_index,
                "Questions Solved"
            ] = updated_questions

            study_df.loc[
                original_index,
                "Remarks"
            ] = updated_remarks

            save_data(study_df)

            st.success(
                "Entry updated!"
            )

        if st.button("Delete Entry"):

            original_index = selected_row.name

            study_df = study_df.drop(
                original_index
            ).reset_index(drop=True)

            save_data(study_df)

            st.success(
                "Entry deleted!"
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
            "IDT"
        ],

        "Revision 1 Target": [
            "10 Sep 2026",
            "15 Sep 2026",
            "20 Sep 2026",
            "25 Sep 2026",
            "28 Sep 2026"
        ],

        "Revision 1 Status": [
            "Pending"
        ] * 5,

        "Revision 2 Target": [
            "05 Oct 2026",
            "10 Oct 2026",
            "12 Oct 2026",
            "15 Oct 2026",
            "18 Oct 2026"
        ],

        "Revision 2 Status": [
            "Pending"
        ] * 5,

        "Revision 3 Target": [
            "25 Oct 2026",
            "27 Oct 2026",
            "28 Oct 2026",
            "29 Oct 2026",
            "30 Oct 2026"
        ],

        "Revision 3 Status": [
            "Pending"
        ] * 5
    })

    st.dataframe(
        revision_df,
        use_container_width=True
    )

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
            "IDT"
        ],

        "Test 1": [
            "Pending"
        ] * 5,

        "Test 2": [
            "Pending"
        ] * 5,

        "Full Syllabus": [
            "Pending"
        ] * 5,

        "Weak Areas": [
            ""
        ] * 5
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
