from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


def create_excel(records):
    """
    Create an Excel workbook from school records.

    Returns:
        BytesIO object containing the Excel file.
    """

    rows = []

    for record in records:

        image_path = record.get("routine_image")

        if image_path:
            image_name = Path(image_path).name
        else:
            image_name = ""

        rows.append(
            {
                "Date": record.get("record_date", ""),
                "Daily Summary": record.get("daily_summary", ""),
                "Chinese Course": record.get("chinese_course", ""),
                "English Course": record.get("english_course", ""),
                "Daily Routine Image": image_name,
            }
        )

    dataframe = pd.DataFrame(rows)

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        dataframe.to_excel(
            writer,
            sheet_name="School Records",
            index=False,
        )

        worksheet = writer.book["School Records"]

        # Header formatting
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

        # Wrap text and align cells
        for row in worksheet.iter_rows(
            min_row=2,
            max_row=worksheet.max_row,
        ):
            for cell in row:
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

        # Column widths
        column_widths = {
            1: 14,   # Date
            2: 45,   # Daily Summary
            3: 60,   # Chinese Course
            4: 60,   # English Course
            5: 28,   # Image
        }

        for column_number, width in column_widths.items():
            column_letter = get_column_letter(
                column_number
            )

            worksheet.column_dimensions[
                column_letter
            ].width = width

        # Freeze header row
        worksheet.freeze_panes = "A2"

    output.seek(0)

    return output