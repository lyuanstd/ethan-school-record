from datetime import date

import streamlit as st

from database import (
    create_record,
    delete_record,
    delete_routine_image,
    download_routine_image,
    get_record_by_date,
    get_records_by_date_range,
    init_db,
    update_record,
    upload_routine_image,
)

from export import create_excel


# --------------------------------------------------
# Database
# --------------------------------------------------

init_db()


# --------------------------------------------------
# Date
# --------------------------------------------------

today = date.today()

def check_password():
    """
    Show a simple password login screen.

    Returns:
        True if the user is authenticated.
        False otherwise.
    """

    if st.session_state.get("authenticated", False):
        return True

    st.title("👶 Ethan School Record")

    st.write("Please enter the password to continue.")

    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button(
        "Enter",
        type="primary",
        use_container_width=True,
    ):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Incorrect password.")

    return False


def display_record(record):
    """
    Display one complete school record.
    """

    if record is None:
        return

    st.markdown(
        f"### 📖 {record['record_date']}"
    )

    # ------------------------------------------
    # Daily Routine Image
    # ------------------------------------------

    st.markdown("#### 📷 Daily Routine")

    image_path = record.get("routine_image")

    if image_path:
        try:
            image_bytes = download_routine_image(
                image_path
            )

            st.image(
                image_bytes,
                use_container_width=True,
            )

        except Exception as error:
            st.warning(
                f"The saved image could not be loaded: {error}"
            )
    else:
        st.caption("No Daily Routine image.")


    # ------------------------------------------
    # Daily Summary
    # ------------------------------------------

    st.markdown("#### 💬 Daily Summary")

    if record.get("daily_summary"):
        st.write(record["daily_summary"])
    else:
        st.caption("No Daily Summary.")

    # ------------------------------------------
    # Chinese Course
    # ------------------------------------------

    st.markdown("#### 🇨🇳 Chinese Course")

    if record.get("chinese_course"):
        st.write(record["chinese_course"])
    else:
        st.caption("No Chinese Course record.")

    # ------------------------------------------
    # English Course
    # ------------------------------------------

    st.markdown("#### 🇬🇧 English Course")

    if record.get("english_course"):
        st.write(record["english_course"])
    else:
        st.caption("No English Course record.")


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Ethan School Record",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Mobile-friendly style
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 700px;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        div[data-testid="stButton"] > button {
            min-height: 3rem;
            font-size: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Authentication
# --------------------------------------------------

if not check_password():
    st.stop()

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("👶 Ethan School Record")

page = st.radio(
    "Navigation",
    ["➕ Add", "📅 Records", "📤 Export"],
    horizontal=True,
    label_visibility="collapsed",
)

st.divider()


# ==================================================
# ADD RECORD
# ==================================================

if page == "➕ Add":

    st.subheader("➕ Add Record")

    record_date = st.date_input(
        "Date",
        value=today,
        format="YYYY-MM-DD",
    )

    st.markdown("#### 📷 Daily Routine")

    routine_image = st.file_uploader(
        "Upload the daily routine image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if routine_image is not None:
        st.image(
            routine_image,
            caption="Daily Routine",
            use_container_width=True,
        )

    st.markdown("#### 💬 Daily Summary")

    daily_summary = st.text_area(
        "Daily Summary",
        placeholder=(
            "Example:\n"
            "Today Ethan is doing better. He still likes to walk around, "
            "but he ate more today!"
        ),
        height=130,
        label_visibility="collapsed",
    )

    st.markdown("#### 🇨🇳 Chinese Course")

    chinese_course = st.text_area(
        "Chinese Course",
        placeholder="Paste today's Chinese course content here...",
        height=220,
        label_visibility="collapsed",
    )

    st.markdown("#### 🇬🇧 English Course")

    english_course = st.text_area(
        "English Course",
        placeholder="Paste today's English course content here...",
        height=260,
        label_visibility="collapsed",
    )

    st.write("")

    if st.button(
        "💾 Save Record",
        type="primary",
        use_container_width=True,
    ):

        record_date_string = record_date.isoformat()

        # ------------------------------------------
        # Check whether this date already exists
        # ------------------------------------------

        existing_record = get_record_by_date(record_date_string)

        if existing_record is not None:

            st.warning(
                f"A record already exists for {record_date_string}. "
                "Please edit the existing record instead."
            )

        else:

            # --------------------------------------
            # Save uploaded image
            # --------------------------------------

            image_path = None

            if routine_image is not None:
                image_path = upload_routine_image(
                    record_date_string,
                    routine_image,
                )

            # --------------------------------------
            # Save database record
            # --------------------------------------

            saved = create_record(
                record_date=record_date_string,
                routine_image=image_path,
                daily_summary=daily_summary.strip(),
                chinese_course=chinese_course.strip(),
                english_course=english_course.strip(),
            )

            if saved:

                st.success(
                    f"✅ Record for {record_date_string} saved successfully!"
                )

            else:

                st.error(
                    "The record could not be saved."
                )


# ==================================================
# RECORDS
# ==================================================

elif page == "📅 Records":

    st.subheader("📅 Records")

    # ==================================================
    # FIND A RECORD
    # ==================================================

    selected_date = st.date_input(
        "Date",
        value=today,
        format="YYYY-MM-DD",
        key="record_search_date",
    )

    if st.button(
        "🔍 View Record",
        use_container_width=True,
    ):
        st.session_state["view_record_date"] = (
            selected_date.isoformat()
        )
        st.session_state["edit_mode"] = False
        st.session_state["delete_mode"] = False

    # ==================================================
    # DISPLAY SELECTED RECORD
    # ==================================================

    if "view_record_date" in st.session_state:

        record_date_string = (
            st.session_state["view_record_date"]
        )

        selected_record = get_record_by_date(
            record_date_string
        )

        st.divider()

        if selected_record is None:

            st.info(
                f"No record found for {record_date_string}."
            )

        else:

            # ==========================================
            # NORMAL VIEW
            # ==========================================

            if not st.session_state.get("edit_mode", False):

                display_record(selected_record)

                st.write("")

                edit_col, delete_col = st.columns(2)

                with edit_col:

                    if st.button(
                        "✏️ Edit",
                        use_container_width=True,
                    ):
                        st.session_state["edit_mode"] = True
                        st.session_state["delete_mode"] = False
                        st.rerun()

                with delete_col:

                    if st.button(
                        "🗑️ Delete",
                        use_container_width=True,
                    ):
                        st.session_state["delete_mode"] = True
                        st.session_state["edit_mode"] = False
                        st.rerun()

            # ==========================================
            # EDIT MODE
            # ==========================================

            if st.session_state.get("edit_mode", False):

                st.markdown(
                    f"### ✏️ Edit {record_date_string}"
                )

                # --------------------------------------
                # Current image
                # --------------------------------------

                current_image_path = (
                    selected_record.get("routine_image")
                )

                st.markdown("#### 📷 Daily Routine")

                if current_image_path:

                    try:
                        current_image_bytes = (
                            download_routine_image(
                                current_image_path
                            )
                        )

                        st.image(
                            current_image_bytes,
                            caption="Current Image",
                            use_container_width=True,
                        )

                    except Exception as error:
                        st.warning(
                            f"The current image could not be loaded: {error}"
                        )

                replacement_image = st.file_uploader(
                    "Upload a new image only if you want to replace the current one",
                    type=["png", "jpg", "jpeg"],
                    key=f"edit_image_{record_date_string}",
                )

                # --------------------------------------
                # Text fields
                # --------------------------------------

                edited_daily_summary = st.text_area(
                    "💬 Daily Summary",
                    value=selected_record.get(
                        "daily_summary", ""
                    ),
                    height=130,
                )

                edited_chinese_course = st.text_area(
                    "🇨🇳 Chinese Course",
                    value=selected_record.get(
                        "chinese_course", ""
                    ),
                    height=220,
                )

                edited_english_course = st.text_area(
                    "🇬🇧 English Course",
                    value=selected_record.get(
                        "english_course", ""
                    ),
                    height=260,
                )

                save_col, cancel_col = st.columns(2)

                with save_col:

                    if st.button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True,
                    ):

                        image_path = current_image_path

                        # ----------------------------------
                        # Replace image if a new one exists
                        # ----------------------------------

                        if replacement_image is not None:

                            new_image_path = upload_routine_image(
                                record_date_string,
                                replacement_image,
                            )

                            # If the extension changed, remove the old object.
                            if (
                                    current_image_path
                                    and current_image_path != new_image_path
                            ):
                                delete_routine_image(
                                    current_image_path
                                )

                            image_path = new_image_path

                        updated = update_record(
                            record_date=record_date_string,
                            routine_image=image_path,
                            daily_summary=(
                                edited_daily_summary.strip()
                            ),
                            chinese_course=(
                                edited_chinese_course.strip()
                            ),
                            english_course=(
                                edited_english_course.strip()
                            ),
                        )

                        if updated:

                            st.session_state["edit_mode"] = False

                            st.success(
                                "✅ Record updated successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "The record could not be updated."
                            )

                with cancel_col:

                    if st.button(
                        "Cancel",
                        use_container_width=True,
                    ):
                        st.session_state["edit_mode"] = False
                        st.rerun()

            # ==========================================
            # DELETE MODE
            # ==========================================

            if st.session_state.get("delete_mode", False):

                st.warning(
                    f"Delete the record for "
                    f"{record_date_string}?"
                )

                confirm_delete = st.checkbox(
                    "I confirm that I want to permanently delete this record."
                )

                delete_confirm_col, cancel_delete_col = (
                    st.columns(2)
                )

                with delete_confirm_col:

                    if st.button(
                        "🗑️ Delete Permanently",
                        type="primary",
                        disabled=not confirm_delete,
                        use_container_width=True,
                    ):

                        image_path = (
                            selected_record.get(
                                "routine_image"
                            )
                        )

                        deleted = delete_record(
                            record_date_string
                        )

                        if deleted:

                            # Delete local image too
                            if image_path:
                                delete_routine_image(
                                    image_path
                                )

                            st.session_state.pop(
                                "view_record_date",
                                None,
                            )

                            st.session_state[
                                "delete_mode"
                            ] = False

                            st.success(
                                "✅ Record deleted successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "The record could not be deleted."
                            )

                with cancel_delete_col:

                    if st.button(
                        "Cancel Delete",
                        use_container_width=True,
                    ):
                        st.session_state[
                            "delete_mode"
                        ] = False

                        st.rerun()


# ==================================================
# EXPORT
# ==================================================

elif page == "📤 Export":

    st.subheader("📤 Export Records")

    start_date = st.date_input(
        "Start Date",
        value=date(today.year, 1, 1),
        format="YYYY-MM-DD",
        key="export_start_date",
    )

    end_date = st.date_input(
        "End Date",
        value=today,
        format="YYYY-MM-DD",
        key="export_end_date",
    )

    if start_date > end_date:

        st.error(
            "Start Date cannot be later than End Date."
        )

    else:

        start_date_string = start_date.isoformat()
        end_date_string = end_date.isoformat()

        records = get_records_by_date_range(
            start_date_string,
            end_date_string,
        )

        st.caption(
            f"{start_date_string} to "
            f"{end_date_string}"
        )

        if not records:

            st.info(
                "No records found in this date range."
            )

        else:

            record_count = len(records)

            st.success(
                f"Found {record_count} record"
                f"{'s' if record_count != 1 else ''}."
            )

            excel_file = create_excel(records)

            file_name = (
                "Ethan_School_Record_"
                f"{start_date_string}_to_"
                f"{end_date_string}.xlsx"
            )

            st.download_button(
                label="📥 Download Excel",
                data=excel_file,
                file_name=file_name,
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                type="primary",
                use_container_width=True,
            )