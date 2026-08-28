import streamlit as st
from supabase import create_client


# --------------------------------------------------
# Supabase client
# --------------------------------------------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_SECRET_KEY"],
)

STORAGE_BUCKET = "routine-images"


def upload_routine_image(record_date, uploaded_file):
    """
    Upload a routine image to Supabase Storage.

    Returns:
        Storage path saved in the database.
    """
    if uploaded_file is None:
        return None

    file_extension = uploaded_file.name.split(".")[-1].lower()
    storage_path = f"{record_date}.{file_extension}"

    file_bytes = uploaded_file.getvalue()

    supabase.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": uploaded_file.type,
            "upsert": "true",
        },
    )

    return storage_path


def download_routine_image(storage_path):
    """
    Download an image from the private Storage bucket.

    Returns:
        Raw image bytes.
    """
    if not storage_path:
        return None

    return (
        supabase.storage
        .from_(STORAGE_BUCKET)
        .download(storage_path)
    )


def delete_routine_image(storage_path):
    """
    Delete an image from Supabase Storage.
    """
    if not storage_path:
        return

    supabase.storage.from_(STORAGE_BUCKET).remove(
        [storage_path]
    )


# --------------------------------------------------
# Database initialization
# --------------------------------------------------

def init_db():
    """
    Supabase table is already created in the dashboard.

    This function is kept so app.py does not need
    to change when switching from SQLite to Supabase.
    """
    pass


# --------------------------------------------------
# Create
# --------------------------------------------------

def create_record(
    record_date,
    routine_image=None,
    daily_summary="",
    chinese_course="",
    english_course="",
    routine_data=None,
):
    """
    Create one daily school record.

    Returns:
        True if saved successfully.
        False if a record already exists for that date.
    """

    existing_record = get_record_by_date(record_date)

    if existing_record is not None:
        return False

    data = {
        "record_date": record_date,
        "routine_image": routine_image,
        "daily_summary": daily_summary,
        "chinese_course": chinese_course,
        "english_course": english_course,
        "routine_data": routine_data,
    }

    response = (
        supabase
        .table("daily_records")
        .insert(data)
        .execute()
    )

    return bool(response.data)


# --------------------------------------------------
# Read one record
# --------------------------------------------------

def get_record_by_date(record_date):
    """
    Get one record by date.
    """

    response = (
        supabase
        .table("daily_records")
        .select("*")
        .eq("record_date", record_date)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# --------------------------------------------------
# Update
# --------------------------------------------------

def update_record(
    record_date,
    routine_image=None,
    daily_summary="",
    chinese_course="",
    english_course="",
    routine_data=None,
):
    """
    Update an existing daily school record.
    """

    data = {
        "routine_image": routine_image,
        "daily_summary": daily_summary,
        "chinese_course": chinese_course,
        "english_course": english_course,
        "routine_data": routine_data,
    }

    response = (
        supabase
        .table("daily_records")
        .update(data)
        .eq("record_date", record_date)
        .select("record_date")
        .execute()
    )

    return bool(response.data)


# --------------------------------------------------
# Delete
# --------------------------------------------------

def delete_record(record_date):
    """
    Delete one daily school record.
    """

    response = (
        supabase
        .table("daily_records")
        .delete()
        .eq("record_date", record_date)
        .select("record_date")
        .execute()
    )

    return bool(response.data)


# --------------------------------------------------
# Date range
# --------------------------------------------------

def get_records_by_date_range(start_date, end_date):
    """
    Get all records within a date range, inclusive.

    Records are sorted from oldest to newest.
    """

    response = (
        supabase
        .table("daily_records")
        .select("*")
        .gte("record_date", start_date)
        .lte("record_date", end_date)
        .order("record_date")
        .execute()
    )

    return response.data
