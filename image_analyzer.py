from io import BytesIO
from typing import List

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field


MODEL_NAME = "gemini-3.5-flash-lite"


# ==================================================
# STRUCTURED OUTPUT SCHEMA
# ==================================================

class AdditionalItem(BaseModel):
    field: str = Field(
        description="Name of an additional field visible on the form."
    )

    value: str = Field(
        description="Value associated with the additional field."
    )


class RoutineData(BaseModel):
    mood: List[str] = Field(
        default_factory=list,
        description=(
            "Every mood label visibly appearing in the Mood section. "
            "All visible mood labels represent the child's mood for that day."
        ),
    )

    favorite_activities: List[str] = Field(
        default_factory=list,
        description=(
            "Every activity label visibly appearing in the Favourite "
            "Activities section. All visible activity labels represent "
            "activities for that day."
        ),
    )

    morning_snack: str = ""
    lunch: str = ""
    afternoon_snack: str = ""
    nap: str = ""
    bowel_movement: str = ""
    extra_diapers: str = ""
    extra_clothes: str = ""
    other: str = ""

    additional_items: List[AdditionalItem] = Field(
        default_factory=list
    )


# ==================================================
# GEMINI CLIENT
# ==================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ==================================================
# IMAGE LOADING
# ==================================================

def _load_image(uploaded_file):
    """
    Convert a Streamlit UploadedFile into a PIL Image.
    """

    image_bytes = uploaded_file.getvalue()

    image = Image.open(
        BytesIO(image_bytes)
    )

    # Make sure the image is fully loaded before the
    # BytesIO object disappears.
    image.load()

    return image


# ==================================================
# EMPTY RESULT
# ==================================================

def _empty_routine_data():
    """
    Return the standard empty Daily Routine structure.
    """

    return {
        "mood": [],
        "favorite_activities": [],
        "morning_snack": "",
        "lunch": "",
        "afternoon_snack": "",
        "nap": "",
        "bowel_movement": "",
        "extra_diapers": "",
        "extra_clothes": "",
        "other": "",
        "additional_items": [],
    }


# ==================================================
# ANALYZE IMAGE
# ==================================================

def analyze_routine_image(uploaded_file):
    """
    Analyze a kindergarten Daily Routine image
    using Gemini Vision.

    Returns:
        dict containing structured Daily Routine data.
    """

    if uploaded_file is None:
        return _empty_routine_data()

    image = _load_image(
        uploaded_file
    )

    prompt = """
You are reading a kindergarten Daily Routine Record form.

Your task is to accurately extract the information that
is visibly present in the image.

IMPORTANT FORM INTERPRETATION:

MOOD
- Every label visibly appearing inside the Mood section
  represents the child's mood for that day.
- Do NOT search for checkmarks.
- Do NOT try to decide whether a mood is selected.
- If a mood label appears in that section, include it.
- Preserve the visible bilingual wording when possible.

FAVOURITE ACTIVITIES
- Every activity label visibly appearing inside the
  Favourite Activities / The Activities I Enjoyed Today
  section represents an activity for that day.
- Do NOT search for checkmarks.
- If an activity label appears in that section, include it.
- Read the COMPLETE label. Do not abbreviate or truncate it.
- Preserve the visible bilingual wording when possible.

OTHER STANDARD FIELDS
Read the visible value associated with:
- Morning Snack
- Lunch
- Afternoon Snack
- Nap
- Bowel Movement
- Extra Diapers / Please bring extra diapers
- Extra Clothes / Please bring extra clothes
- Other

If one of these fields is blank, return an empty string.

ADDITIONAL INFORMATION
If there is visible information that does not belong to
one of the standard fields, put it in additional_items.

ACCURACY RULES
- Read only information visible in the image.
- Do not invent missing information.
- Do not guess based on typical kindergarten routines.
- Preserve wording from the image whenever possible.
- Pay attention to both Chinese and English text.
- Read full labels instead of partial OCR fragments.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            image,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RoutineData,
            temperature=0,
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    # Pydantic validates both field names and field types.
    routine_data = RoutineData.model_validate_json(
        response.text
    )

    return routine_data.model_dump()
