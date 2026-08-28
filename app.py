from datetime import date

import pandas as pd
import streamlit as st

from image_analyzer import analyze_routine_image

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
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Ethan School Record",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Database
# --------------------------------------------------

init_db()


# --------------------------------------------------
# General
# --------------------------------------------------

today = date.today()


# ==================================================
# PASSWORD
# ==================================================

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


# ==================================================
# STRUCTURED DAILY ROUTINE FORM
# ==================================================

def routine_data_form(prefix, existing_data=None):
    """
    Display editable structured Daily Routine fields.

    Used by both Add and Edit.

    Returns:
        dict containing the final user-confirmed values.
    """

    existing_data = existing_data or {}

    # --------------------------------------------------
    # Standard values from the school's routine form
    # --------------------------------------------------

    common_moods = [
        "Happy",
        "Talkative",
        "Curious",
        "Cried",
    ]

    common_activities = [
        "Constructive Play",
        "Outdoor Play",
        "Storytime",
        "Music & Movement",
        "Learning Centers",
        "Maths & Science",
        "Art & Craft",
        "Indoor Play",
    ]

    # --------------------------------------------------
    # Preserve future AI values even if they are not
    # part of the original fixed lists.
    # --------------------------------------------------

    existing_moods = existing_data.get("mood", []) or []

    existing_activities = (
        existing_data.get(
            "favorite_activities",
            [],
        )
        or []
    )

    mood_options = list(
        dict.fromkeys(
            common_moods + existing_moods
        )
    )

    activity_options = list(
        dict.fromkeys(
            common_activities
            + existing_activities
        )
    )

    # --------------------------------------------------
    # Mood
    # --------------------------------------------------

    mood = st.multiselect(
        "Mood",
        options=mood_options,
        default=existing_moods,
        key=f"{prefix}_mood",
        accept_new_options=True,
    )

    # --------------------------------------------------
    # Favourite Activities
    # --------------------------------------------------

    favorite_activities = st.multiselect(
        "Favourite Activities",
        options=activity_options,
        default=existing_activities,
        key=f"{prefix}_activities",
        accept_new_options=True,
    )

    # --------------------------------------------------
    # Standard text fields
    # --------------------------------------------------

    morning_snack = st.text_input(
        "Morning Snack",
        value=existing_data.get(
            "morning_snack",
            "",
        )
        or "",
        key=f"{prefix}_morning_snack",
    )

    lunch = st.text_input(
        "Lunch",
        value=existing_data.get(
            "lunch",
            "",
        )
        or "",
        key=f"{prefix}_lunch",
    )

    afternoon_snack = st.text_input(
        "Afternoon Snack",
        value=existing_data.get(
            "afternoon_snack",
            "",
        )
        or "",
        key=f"{prefix}_afternoon_snack",
    )

    nap = st.text_input(
        "Nap",
        value=existing_data.get(
            "nap",
            "",
        )
        or "",
        key=f"{prefix}_nap",
    )

    bowel_movement = st.text_input(
        "Bowel Movement",
        value=existing_data.get(
            "bowel_movement",
            "",
        )
        or "",
        key=f"{prefix}_bowel",
    )

    extra_diapers = st.text_input(
        "Extra Diapers",
        value=existing_data.get(
            "extra_diapers",
            "",
        )
        or "",
        key=f"{prefix}_diapers",
    )

    extra_clothes = st.text_input(
        "Extra Clothes",
        value=existing_data.get(
            "extra_clothes",
            "",
        )
        or "",
        key=f"{prefix}_clothes",
    )

    other = st.text_area(
        "Other",
        value=existing_data.get(
            "other",
            "",
        )
        or "",
        height=80,
        key=f"{prefix}_other",
    )

    # --------------------------------------------------
    # Additional Items
    # --------------------------------------------------

    st.markdown("##### ➕ Additional Items")

    st.caption(
        "Add anything the teacher mentioned "
        "that is not covered by the standard fields."
    )

    additional_items = (
        existing_data.get(
            "additional_items",
            [],
        )
        or []
    )

    if additional_items:

        additional_df = pd.DataFrame(
            additional_items
        )

    else:

        additional_df = pd.DataFrame(
            columns=[
                "field",
                "value",
            ]
        )

    edited_additional_df = st.data_editor(
        additional_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "field": "Item",
            "value": "Value",
        },
        key=f"{prefix}_additional_items",
    )

    cleaned_additional_items = []

    for row in edited_additional_df.to_dict(
        orient="records"
    ):

        raw_field = row.get("field", "")
        raw_value = row.get("value", "")

        field = (
            ""
            if pd.isna(raw_field)
            else str(raw_field).strip()
        )

        value = (
            ""
            if pd.isna(raw_value)
            else str(raw_value).strip()
        )

        if field or value:

            cleaned_additional_items.append(
                {
                    "field": field,
                    "value": value,
                }
            )

    # --------------------------------------------------
    # Final structured data
    # --------------------------------------------------

    return {
        "mood": mood,
        "favorite_activities": (
            favorite_activities
        ),
        "morning_snack": (
            morning_snack.strip()
        ),
        "lunch": lunch.strip(),
        "afternoon_snack": (
            afternoon_snack.strip()
        ),
        "nap": nap.strip(),
        "bowel_movement": (
            bowel_movement.strip()
        ),
        "extra_diapers": (
            extra_diapers.strip()
        ),
        "extra_clothes": (
            extra_clothes.strip()
        ),
        "other": other.strip(),
        "additional_items": (
            cleaned_additional_items
        ),
    }


def load_routine_data_into_form(prefix, routine_data):
    """
    Load analyzed routine data into Streamlit widget state.
    """

    st.session_state[f"{prefix}_mood"] = (
        routine_data.get("mood", [])
        or []
    )

    st.session_state[f"{prefix}_activities"] = (
        routine_data.get(
            "favorite_activities",
            [],
        )
        or []
    )

    st.session_state[f"{prefix}_morning_snack"] = (
        routine_data.get(
            "morning_snack",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_lunch"] = (
        routine_data.get(
            "lunch",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_afternoon_snack"] = (
        routine_data.get(
            "afternoon_snack",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_nap"] = (
        routine_data.get(
            "nap",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_bowel"] = (
        routine_data.get(
            "bowel_movement",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_diapers"] = (
        routine_data.get(
            "extra_diapers",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_clothes"] = (
        routine_data.get(
            "extra_clothes",
            "",
        )
        or ""
    )

    st.session_state[f"{prefix}_other"] = (
        routine_data.get(
            "other",
            "",
        )
        or ""
    )

    # data_editor is easier to refresh from existing_data,
    # so remove its previous widget state.
    st.session_state.pop(
        f"{prefix}_additional_items",
        None,
    )

# ==================================================
# DISPLAY STRUCTURED DAILY ROUTINE
# ==================================================

def display_routine_data(routine_data):
    """
    Display saved structured Daily Routine data.
    """

    if not routine_data:

        st.caption(
            "No structured Daily Routine details."
        )

        return

    # --------------------------------------------------
    # Mood
    # --------------------------------------------------

    mood = routine_data.get(
        "mood",
        [],
    ) or []

    if mood:

        st.write(
            "**Mood:** "
            + ", ".join(mood)
        )

    # --------------------------------------------------
    # Favourite Activities
    # --------------------------------------------------

    activities = routine_data.get(
        "favorite_activities",
        [],
    ) or []

    if activities:

        st.write(
            "**Favourite Activities:** "
            + ", ".join(activities)
        )

    # --------------------------------------------------
    # Standard fields
    # --------------------------------------------------

    fields = [
        (
            "Morning Snack",
            "morning_snack",
        ),
        (
            "Lunch",
            "lunch",
        ),
        (
            "Afternoon Snack",
            "afternoon_snack",
        ),
        (
            "Nap",
            "nap",
        ),
        (
            "Bowel Movement",
            "bowel_movement",
        ),
        (
            "Extra Diapers",
            "extra_diapers",
        ),
        (
            "Extra Clothes",
            "extra_clothes",
        ),
        (
            "Other",
            "other",
        ),
    ]

    for label, key in fields:

        value = routine_data.get(key)

        if value:

            st.write(
                f"**{label}:** {value}"
            )

    # --------------------------------------------------
    # Additional Items
    # --------------------------------------------------

    additional_items = (
        routine_data.get(
            "additional_items",
            [],
        )
        or []
    )

    if additional_items:

        st.markdown(
            "**Additional Items:**"
        )

        for item in additional_items:

            field = item.get(
                "field",
                "",
            )

            value = item.get(
                "value",
                "",
            )

            if field and value:

                st.write(
                    f"- **{field}:** {value}"
                )

            elif field:

                st.write(
                    f"- **{field}**"
                )

            elif value:

                st.write(
                    f"- {value}"
                )


# ==================================================
# DISPLAY ONE COMPLETE RECORD
# ==================================================

def display_record(record):
    """
    Display one complete school record.
    """

    if record is None:
        return

    st.markdown(
        f"### 📖 {record['record_date']}"
    )

    # --------------------------------------------------
    # Daily Routine Image
    # --------------------------------------------------

    st.markdown(
        "#### 📷 Daily Routine"
    )

    image_path = record.get(
        "routine_image"
    )

    if image_path:

        try:

            image_bytes = (
                download_routine_image(
                    image_path
                )
            )

            st.image(
                image_bytes,
                use_container_width=True,
            )

        except Exception as error:

            st.warning(
                "The saved image could not "
                f"be loaded: {error}"
            )

    else:

        st.caption(
            "No Daily Routine image."
        )

    # --------------------------------------------------
    # Structured Daily Routine
    # --------------------------------------------------

    st.markdown(
        "#### 🧾 Daily Routine Details"
    )

    display_routine_data(
        record.get("routine_data")
    )

    # --------------------------------------------------
    # Daily Summary
    # --------------------------------------------------

    st.markdown(
        "#### 💬 Daily Summary"
    )

    if record.get("daily_summary"):

        st.write(
            record["daily_summary"]
        )

    else:

        st.caption(
            "No Daily Summary."
        )

    # --------------------------------------------------
    # Chinese Course
    # --------------------------------------------------

    st.markdown(
        "#### 🇨🇳 Chinese Course"
    )

    if record.get("chinese_course"):

        st.write(
            record["chinese_course"]
        )

    else:

        st.caption(
            "No Chinese Course record."
        )

    # --------------------------------------------------
    # English Course
    # --------------------------------------------------

    st.markdown(
        "#### 🇬🇧 English Course"
    )

    if record.get("english_course"):

        st.write(
            record["english_course"]
        )

    else:

        st.caption(
            "No English Course record."
        )


# ==================================================
# MOBILE-FRIENDLY STYLE
# ==================================================

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


# ==================================================
# AUTHENTICATION
# ==================================================

if not check_password():
    st.stop()


# ==================================================
# HEADER
# ==================================================

st.title(
    "👶 Ethan School Record"
)

page = st.radio(
    "Navigation",
    [
        "➕ Add",
        "📅 Records",
        "📤 Export",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

st.divider()


# ==================================================
# ADD RECORD
# ==================================================

if page == "➕ Add":

    st.subheader(
        "➕ Add Record"
    )

    # --------------------------------------------------
    # Date
    # --------------------------------------------------

    record_date = st.date_input(
        "Date",
        value=today,
        format="YYYY-MM-DD",
    )

    # --------------------------------------------------
    # Daily Routine Image
    # --------------------------------------------------

    st.markdown(
        "#### 📷 Daily Routine"
    )

    routine_image = st.file_uploader(
        "Upload the daily routine image",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
        label_visibility="collapsed",
        key="add_routine_image",
    )

    if routine_image is not None:

        st.image(
            routine_image,
            caption="Daily Routine",
            use_container_width=True,
        )

    if st.button(
        "✨ Analyze Image",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "Analyzing Daily Routine image..."
            ):

                analyzed_data = (
                    analyze_routine_image(
                        routine_image
                    )
                )

            st.session_state[
                "add_analyzed_routine_data"
            ] = analyzed_data

            load_routine_data_into_form(
                "add",
                analyzed_data,
            )

            st.success(
                "✅ Image analyzed successfully. "
                "Please review the fields below."
            )

            st.rerun()

        except Exception as error:

            error_message = str(error)

            if (
                "User location is not supported"
                in error_message
            ):

                st.error(
                    "Gemini API is not available "
                    "from the current network location. "
                    "We will test this again after "
                    "deploying to Streamlit Cloud."
                )

            else:

                st.error(
                    "Image analysis failed:\n\n"
                    f"{error}"
                )

    # --------------------------------------------------
    # Structured Daily Routine
    # --------------------------------------------------

    st.markdown(
        "#### 🧾 Daily Routine Details"
    )

    routine_data = routine_data_form(
        prefix="add",
        existing_data=(
            st.session_state.get(
                "add_analyzed_routine_data",
                {},
            )
        ),
    )

    st.divider()

    # --------------------------------------------------
    # Daily Summary
    # --------------------------------------------------

    st.markdown(
        "#### 💬 Daily Summary"
    )

    daily_summary = st.text_area(
        "Daily Summary",
        placeholder=(
            "Example:\n"
            "Today Ethan is doing better. "
            "He still likes to walk around, "
            "but he ate more today!"
        ),
        height=130,
        label_visibility="collapsed",
        key="add_daily_summary",
    )

    # --------------------------------------------------
    # Chinese Course
    # --------------------------------------------------

    st.markdown(
        "#### 🇨🇳 Chinese Course"
    )

    chinese_course = st.text_area(
        "Chinese Course",
        placeholder=(
            "Paste today's Chinese "
            "course content here..."
        ),
        height=220,
        label_visibility="collapsed",
        key="add_chinese_course",
    )

    # --------------------------------------------------
    # English Course
    # --------------------------------------------------

    st.markdown(
        "#### 🇬🇧 English Course"
    )

    english_course = st.text_area(
        "English Course",
        placeholder=(
            "Paste today's English "
            "course content here..."
        ),
        height=260,
        label_visibility="collapsed",
        key="add_english_course",
    )

    st.write("")

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    if st.button(
        "💾 Save Record",
        type="primary",
        use_container_width=True,
    ):

        record_date_string = (
            record_date.isoformat()
        )

        existing_record = (
            get_record_by_date(
                record_date_string
            )
        )

        if existing_record is not None:

            st.warning(
                "A record already exists for "
                f"{record_date_string}. "
                "Please edit the existing "
                "record instead."
            )

        else:

            image_path = None

            # ------------------------------------------
            # Upload image to Supabase Storage
            # ------------------------------------------

            if routine_image is not None:

                image_path = (
                    upload_routine_image(
                        record_date_string,
                        routine_image,
                    )
                )

            # ------------------------------------------
            # Save database record
            # ------------------------------------------

            saved = create_record(
                record_date=(
                    record_date_string
                ),
                routine_image=image_path,
                daily_summary=(
                    daily_summary.strip()
                ),
                chinese_course=(
                    chinese_course.strip()
                ),
                english_course=(
                    english_course.strip()
                ),
                routine_data=routine_data,
            )

            if saved:

                st.success(
                    "✅ Record for "
                    f"{record_date_string} "
                    "saved successfully!"
                )

            else:

                st.error(
                    "The record could not "
                    "be saved."
                )


# ==================================================
# RECORDS
# ==================================================

elif page == "📅 Records":

    st.subheader(
        "📅 Records"
    )

    # --------------------------------------------------
    # Find record
    # --------------------------------------------------

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

        st.session_state[
            "view_record_date"
        ] = selected_date.isoformat()

        st.session_state[
            "edit_mode"
        ] = False

        st.session_state[
            "delete_mode"
        ] = False

    # --------------------------------------------------
    # Display selected record
    # --------------------------------------------------

    if (
        "view_record_date"
        in st.session_state
    ):

        record_date_string = (
            st.session_state[
                "view_record_date"
            ]
        )

        selected_record = (
            get_record_by_date(
                record_date_string
            )
        )

        st.divider()

        if selected_record is None:

            st.info(
                "No record found for "
                f"{record_date_string}."
            )

        else:

            # ==========================================
            # NORMAL VIEW
            # ==========================================

            if not st.session_state.get(
                "edit_mode",
                False,
            ):

                display_record(
                    selected_record
                )

                st.write("")

                edit_col, delete_col = (
                    st.columns(2)
                )

                with edit_col:

                    if st.button(
                        "✏️ Edit",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "edit_mode"
                        ] = True

                        st.session_state[
                            "delete_mode"
                        ] = False

                        st.rerun()

                with delete_col:

                    if st.button(
                        "🗑️ Delete",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "delete_mode"
                        ] = True

                        st.session_state[
                            "edit_mode"
                        ] = False

                        st.rerun()

            # ==========================================
            # EDIT MODE
            # ==========================================

            if st.session_state.get(
                "edit_mode",
                False,
            ):

                st.markdown(
                    "### ✏️ Edit "
                    f"{record_date_string}"
                )

                # --------------------------------------
                # Current image
                # --------------------------------------

                current_image_path = (
                    selected_record.get(
                        "routine_image"
                    )
                )

                st.markdown(
                    "#### 📷 Daily Routine"
                )

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
                            "The current image "
                            "could not be loaded: "
                            f"{error}"
                        )

                else:

                    st.caption(
                        "No current Daily "
                        "Routine image."
                    )

                replacement_image = (
                    st.file_uploader(
                        (
                            "Upload a new image "
                            "only if you want to "
                            "replace the current one"
                        ),
                        type=[
                            "png",
                            "jpg",
                            "jpeg",
                        ],
                        key=(
                            "edit_image_"
                            f"{record_date_string}"
                        ),
                    )
                )

                # --------------------------------------
                # Structured Daily Routine
                # --------------------------------------

                st.markdown(
                    "#### 🧾 Daily Routine Details"
                )

                edited_routine_data = (
                    routine_data_form(
                        prefix=(
                            "edit_"
                            f"{record_date_string}"
                        ),
                        existing_data=(
                            selected_record.get(
                                "routine_data"
                            )
                            or {}
                        ),
                    )
                )

                st.divider()

                # --------------------------------------
                # Daily Summary
                # --------------------------------------

                edited_daily_summary = (
                    st.text_area(
                        "💬 Daily Summary",
                        value=(
                            selected_record.get(
                                "daily_summary",
                                "",
                            )
                            or ""
                        ),
                        height=130,
                        key=(
                            "edit_summary_"
                            f"{record_date_string}"
                        ),
                    )
                )

                # --------------------------------------
                # Chinese Course
                # --------------------------------------

                edited_chinese_course = (
                    st.text_area(
                        "🇨🇳 Chinese Course",
                        value=(
                            selected_record.get(
                                "chinese_course",
                                "",
                            )
                            or ""
                        ),
                        height=220,
                        key=(
                            "edit_chinese_"
                            f"{record_date_string}"
                        ),
                    )
                )

                # --------------------------------------
                # English Course
                # --------------------------------------

                edited_english_course = (
                    st.text_area(
                        "🇬🇧 English Course",
                        value=(
                            selected_record.get(
                                "english_course",
                                "",
                            )
                            or ""
                        ),
                        height=260,
                        key=(
                            "edit_english_"
                            f"{record_date_string}"
                        ),
                    )
                )

                save_col, cancel_col = (
                    st.columns(2)
                )

                # --------------------------------------
                # Save Changes
                # --------------------------------------

                with save_col:

                    if st.button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True,
                    ):

                        image_path = (
                            current_image_path
                        )

                        # ----------------------------------
                        # Replace image if requested
                        # ----------------------------------

                        if (
                            replacement_image
                            is not None
                        ):

                            new_image_path = (
                                upload_routine_image(
                                    record_date_string,
                                    replacement_image,
                                )
                            )

                            # If extension changed,
                            # delete old Storage object.
                            if (
                                current_image_path
                                and
                                current_image_path
                                != new_image_path
                            ):

                                delete_routine_image(
                                    current_image_path
                                )

                            image_path = (
                                new_image_path
                            )

                        # ----------------------------------
                        # Update Supabase record
                        # ----------------------------------

                        updated = update_record(
                            record_date=(
                                record_date_string
                            ),
                            routine_image=(
                                image_path
                            ),
                            daily_summary=(
                                edited_daily_summary
                                .strip()
                            ),
                            chinese_course=(
                                edited_chinese_course
                                .strip()
                            ),
                            english_course=(
                                edited_english_course
                                .strip()
                            ),
                            routine_data=(
                                edited_routine_data
                            ),
                        )

                        if updated:

                            st.session_state[
                                "edit_mode"
                            ] = False

                            st.success(
                                "✅ Record updated "
                                "successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "The record could "
                                "not be updated."
                            )

                # --------------------------------------
                # Cancel Edit
                # --------------------------------------

                with cancel_col:

                    if st.button(
                        "Cancel",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "edit_mode"
                        ] = False

                        st.rerun()

            # ==========================================
            # DELETE MODE
            # ==========================================

            if st.session_state.get(
                "delete_mode",
                False,
            ):

                st.warning(
                    "Delete the record for "
                    f"{record_date_string}?"
                )

                confirm_delete = (
                    st.checkbox(
                        (
                            "I confirm that I want "
                            "to permanently delete "
                            "this record."
                        )
                    )
                )

                (
                    delete_confirm_col,
                    cancel_delete_col,
                ) = st.columns(2)

                # --------------------------------------
                # Confirm Delete
                # --------------------------------------

                with delete_confirm_col:

                    if st.button(
                        "🗑️ Delete Permanently",
                        type="primary",
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True,
                    ):

                        image_path = (
                            selected_record.get(
                                "routine_image"
                            )
                        )

                        deleted = (
                            delete_record(
                                record_date_string
                            )
                        )

                        if deleted:

                            # Delete image from
                            # Supabase Storage.
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
                                "✅ Record deleted "
                                "successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "The record could "
                                "not be deleted."
                            )

                # --------------------------------------
                # Cancel Delete
                # --------------------------------------

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

    st.subheader(
        "📤 Export Records"
    )

    start_date = st.date_input(
        "Start Date",
        value=date(
            today.year,
            1,
            1,
        ),
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
            "Start Date cannot be "
            "later than End Date."
        )

    else:

        start_date_string = (
            start_date.isoformat()
        )

        end_date_string = (
            end_date.isoformat()
        )

        records = (
            get_records_by_date_range(
                start_date_string,
                end_date_string,
            )
        )

        st.caption(
            f"{start_date_string} to "
            f"{end_date_string}"
        )

        if not records:

            st.info(
                "No records found in "
                "this date range."
            )

        else:

            record_count = len(
                records
            )

            st.success(
                f"Found {record_count} record"
                f"{'s' if record_count != 1 else ''}."
            )

            excel_file = (
                create_excel(
                    records
                )
            )

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
                    "application/"
                    "vnd.openxmlformats-"
                    "officedocument."
                    "spreadsheetml.sheet"
                ),
                type="primary",
                use_container_width=True,
            )