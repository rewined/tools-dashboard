from dataclasses import dataclass
from typing import Tuple


@dataclass
class LabelFormat:
    name: str
    width: float  # in inches
    height: float  # in inches
    columns: int
    rows: int
    margin_top: float
    margin_left: float
    margin_right: float
    margin_bottom: float
    horizontal_spacing: float
    vertical_spacing: float


# Common label formats for 8.5x11 sheets
LABEL_FORMATS = {
    "avery_5160": LabelFormat(
        name="Avery 5160/5260 (1\" x 2-5/8\")",
        width=2.625,
        height=1.0,
        columns=3,
        rows=10,
        margin_top=0.5,
        margin_left=0.1875,
        margin_right=0.1875,
        margin_bottom=0.5,
        horizontal_spacing=0.125,
        vertical_spacing=0
    ),
    "avery_5163": LabelFormat(
        name="Avery 5163/5263 (2\" x 4\")",
        width=4.0,
        height=2.0,
        columns=2,
        rows=5,
        margin_top=0.5,
        margin_left=0.1875,
        margin_right=0.1875,
        margin_bottom=0.5,
        horizontal_spacing=0.125,
        vertical_spacing=0
    ),
    "avery_5167": LabelFormat(
        name="Avery 5167/5267 (1/2\" x 1-3/4\")",
        width=1.75,
        height=0.5,
        columns=4,
        rows=20,
        margin_top=0.5,
        margin_left=0.3125,
        margin_right=0.3125,
        margin_bottom=0.5,
        horizontal_spacing=0.3125,
        vertical_spacing=0
    ),
    "avery_8163": LabelFormat(
        name="Avery 8163 (2\" x 4\")",
        width=4.0,
        height=2.0,
        columns=2,
        rows=5,
        margin_top=0.5,
        margin_left=0.1875,
        margin_right=0.1875,
        margin_bottom=0.5,
        horizontal_spacing=0.125,
        vertical_spacing=0
    ),
    "custom_square": LabelFormat(
        name="Custom Square (2\" x 2\")",
        width=2.0,
        height=2.0,
        columns=4,
        rows=5,
        margin_top=0.5,
        margin_left=0.25,
        margin_right=0.25,
        margin_bottom=0.5,
        horizontal_spacing=0.125,
        vertical_spacing=0.125
    )
}