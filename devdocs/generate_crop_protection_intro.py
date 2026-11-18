from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "CropProtection_Introduction.pptx"

NAVY = RGBColor(24, 52, 65)
TEAL = RGBColor(30, 117, 109)
MINT = RGBColor(222, 241, 236)
BLUE = RGBColor(54, 111, 147)
SKY = RGBColor(226, 239, 246)
GOLD = RGBColor(215, 158, 53)
CREAM = RGBColor(248, 246, 238)
WHITE = RGBColor(255, 255, 255)
INK = RGBColor(31, 44, 51)
MUTED = RGBColor(92, 108, 116)
LINE = RGBColor(204, 216, 220)
RED = RGBColor(174, 68, 62)


def make_deck() -> Presentation:
    deck = Presentation()
    deck.slide_width = Inches(13.333)
    deck.slide_height = Inches(7.5)
    return deck


def add_text(
    slide,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 20,
    color: RGBColor = INK,
    bold: bool = False,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    font: str = "Aptos",
    margin: float = 0.08,
) -> None:
    box = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(width), Inches(height)
    )
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    paragraph.font.name = font
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.color.rgb = color


def add_rich_text(
    slide,
    runs: list[tuple[str, bool, RGBColor]],
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 19,
) -> None:
    box = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(width), Inches(height)
    )
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    for text, bold, color in runs:
        run = paragraph.add_run()
        run.text = text
        run.font.name = "Aptos"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color


def add_header(slide, title: str, kicker: str, number: int) -> None:
    add_text(slide, kicker.upper(), 0.65, 0.28, 8.5, 0.35, size=10, color=TEAL, bold=True)
    add_text(slide, title, 0.65, 0.68, 11.7, 0.6, size=28, color=NAVY, bold=True)
    slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(1.32), Inches(1.05), Inches(0.05)
    ).fill.solid()
    accent = slide.shapes[-1]
    accent.fill.fore_color.rgb = GOLD
    accent.line.fill.background()
    add_text(
        slide,
        f"{number:02d}",
        12.1,
        0.35,
        0.55,
        0.4,
        size=11,
        color=MUTED,
        bold=True,
        align=PP_ALIGN.RIGHT,
    )


def add_footer(slide, source: str) -> None:
    slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(7.12), Inches(12.0), Inches(0.015)
    ).fill.solid()
    line = slide.shapes[-1]
    line.fill.fore_color.rgb = LINE
    line.line.fill.background()
    add_text(slide, source, 0.65, 7.17, 12.0, 0.2, size=8, color=MUTED)


def add_card(
    slide,
    title: str,
    body: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: RGBColor = WHITE,
    accent: RGBColor = TEAL,
    title_size: float = 17,
) -> None:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = LINE
    add_text(slide, title, x + 0.25, y + 0.18, width - 0.5, 0.45, size=title_size, color=accent, bold=True)
    add_text(slide, body, x + 0.25, y + 0.72, width - 0.5, height - 0.92, size=13, color=INK)


def add_bullet_list(
    slide,
    items: list[str],
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 18,
    color: RGBColor = INK,
) -> None:
    box = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(width), Inches(height)
    )
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.12)
    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = item
        paragraph.level = 0
        paragraph.font.name = "Aptos"
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = color
        paragraph.space_after = Pt(9)
        paragraph.text = f"•  {paragraph.text}"


def add_arrow(slide, x1: float, y1: float, x2: float, y2: float, color=TEAL) -> None:
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    connector.line.color.rgb = color
    connector.line.width = Pt(2.2)
    connector.line.end_arrowhead = True


def add_picture_fit(slide, path: Path, x: float, y: float, width: float, height: float) -> None:
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(width), height=Inches(height))


def build() -> None:
    deck = make_deck()

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = NAVY
    add_text(slide, "xCropProtection", 0.75, 0.85, 9.8, 0.8, size=38, color=WHITE, bold=True)
    add_text(
        slide,
        "Introduction to a spatiotemporal component for crop-protection simulations",
        0.75,
        1.75,
        9.9,
        1.3,
        size=24,
        color=MINT,
    )
    accent = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.78), Inches(3.35), Inches(2.15), Inches(0.08)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = GOLD
    accent.line.fill.background()
    add_card(
        slide,
        "Modelled unit",
        "An application to a field at a sampled date, rate, and treatment area.",
        8.85,
        4.05,
        3.75,
        2.05,
        fill=MINT,
        accent=TEAL,
        title_size=16,
    )
    add_text(
        slide,
        "xCropProtectionDemo  •  developer introduction",
        0.78,
        6.72,
        8.0,
        0.3,
        size=11,
        color=WHITE,
    )

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Why the component exists", "Purpose", 2)
    add_rich_text(
        slide,
        [
            ("xCropProtection simulates ", True, NAVY),
            ("who/what is treated, where, when, at what rate, and with which mitigation", False, INK),
            (".", True, NAVY),
        ],
        0.75,
        1.62,
        11.6,
        0.8,
        size=22,
    )
    add_card(slide, "Realistic use patterns", "Represent products, active substances, tank mixes, spray sequences, choices, and alternatives.", 0.75, 2.7, 3.75, 2.55)
    add_card(slide, "Landscape scale", "Operate on actual field identifiers, LULC types, geometries, and scenario time extents.", 4.78, 2.7, 3.75, 2.55, fill=SKY, accent=BLUE)
    add_card(slide, "Transparent uncertainty", "Sample dates, sequences, and numeric parameters from explicitly defined distributions.", 8.82, 2.7, 3.75, 2.55, fill=CREAM, accent=GOLD)
    add_text(slide, "Designed as a reusable xLandscape component, while the demo provides a complete host model.", 0.85, 5.72, 11.7, 0.58, size=17, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: README.md; docs/index.md")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Input → simulated applications", "Model boundary", 3)
    add_card(slide, "Landscape scenario", "Field geometry • feature ID • LULC type • valid time range", 0.75, 2.0, 3.2, 1.55)
    add_card(slide, "Crop protection calendar", "Target crop • indication • alternatives • treatment sequence", 0.75, 4.05, 3.2, 1.55, fill=MINT)
    add_card(slide, "Global experiment", "Dates • Monte Carlo runs • parallelism • output type", 4.55, 4.05, 3.2, 1.55, fill=SKY, accent=BLUE)
    add_card(slide, "xCropProtection", "Matches calendars to fields, samples choices, and creates applications.", 8.35, 2.95, 4.05, 2.05, fill=NAVY, accent=GOLD)
    add_text(slide, "xCropProtection", 8.78, 3.28, 3.2, 0.55, size=21, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Date • field • PPP • rate • applied area • technology", 8.83, 4.12, 3.1, 0.8, size=13, color=MINT, align=PP_ALIGN.CENTER)
    add_arrow(slide, 3.98, 2.78, 8.3, 3.45)
    add_arrow(slide, 3.98, 4.83, 8.3, 4.03)
    add_arrow(slide, 7.78, 4.83, 8.3, 4.4, BLUE)
    add_text(slide, "Output is persisted in the xLandscape multidimensional store (arr.dat / HDF5).", 4.95, 6.35, 6.85, 0.42, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: model/variant/mc.xml; docs/index.md")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "One model step", "Runtime flow", 4)
    stages = [
        ("1", "Match", "Field LULC / feature ID meets calendar scope."),
        ("2", "Check", "Calendar validity and application window include the day."),
        ("3", "Sample", "Choose sequence, date, and distributed numeric values."),
        ("4", "Apply", "Calculate treated geometry after buffer and margin."),
        ("5", "Record", "Write date, field, PPP, rate, area, and technology."),
    ]
    for index, (number, title, body) in enumerate(stages):
        x = 0.75 + index * 2.45
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x), Inches(2.08), Inches(0.62), Inches(0.62)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = TEAL if index < 4 else GOLD
        circle.line.fill.background()
        add_text(slide, number, x, 2.18, 0.62, 0.3, size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, title, x - 0.25, 2.93, 1.1, 0.42, size=17, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, body, x - 0.52, 3.55, 1.65, 1.45, size=12, color=INK, align=PP_ALIGN.CENTER)
        if index < len(stages) - 1:
            add_arrow(slide, x + 0.75, 2.39, x + 2.24, 2.39, LINE)
    add_bullet_list(slide, [
        "Sampling occurs at the declared scale (for example: year × base geometry).",
        "MinimumAppliedArea suppresses applications whose remaining treated area is too small.",
    ], 1.1, 5.5, 10.9, 1.15, size=15, color=MUTED)
    add_footer(slide, "Sources: docs/reference/distributions.md; docs/tutorials/training-intro.md")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Files that define a run", "Repository contract", 5)
    add_card(slide, ".xrun", "User-level run controls\nProject • CP scenario • dates • output type • MC • SimID", 0.75, 1.75, 2.8, 3.95, fill=CREAM, accent=GOLD)
    add_card(slide, "xCropProtection.xml", "Scenario composition\nPPM Calendar includes • Technology definitions or include", 3.78, 1.75, 2.8, 3.95)
    add_card(slide, "PPMCalendar.xml", "Treatment logic\nTemporal validity • target crops • sequences • applications", 6.82, 1.75, 2.8, 3.95, fill=SKY, accent=BLUE)
    add_card(slide, "mc.xml", "Component wiring\nInputs from LandscapeScenario • component parameters • HDF store", 9.85, 1.75, 2.72, 3.95, fill=MINT, accent=TEAL)
    add_arrow(slide, 3.58, 3.7, 3.76, 3.7)
    add_arrow(slide, 6.62, 3.7, 6.8, 3.7)
    add_arrow(slide, 9.65, 3.7, 9.83, 3.7)
    add_text(slide, "Stable boundary: the UI exports the first three without editing mc.xml.", 0.85, 6.15, 11.8, 0.45, size=16, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: SingleField_Lindan_5feb.xrun; model/variant/mc.xml; CropProtection/")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "The treatment hierarchy", "PPM calendar", 6)
    levels = [
        ("PPM calendar", "Valid period + target crop/field scope", NAVY),
        ("Indication", "A pest-control purpose; its sequences may be selected", BLUE),
        ("Application sequence", "Alternative treatment programmes with probabilities", TEAL),
        ("Application", "Tank contents, rate, date window, technology, buffer, margin", GOLD),
    ]
    for index, (title, body, color) in enumerate(levels):
        width = 10.7 - index * 0.7
        x = 1.3 + index * 0.35
        y = 1.75 + index * 1.12
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(y),
            Inches(width),
            Inches(0.9),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        add_text(slide, title, x + 0.3, y + 0.14, 2.5, 0.45, size=17, color=WHITE, bold=True)
        add_text(slide, body, x + 2.75, y + 0.14, width - 3.08, 0.5, size=13, color=WHITE)
    add_card(slide, "AND / OR mental model", "Applications within a sampled sequence all occur.\nSequences within an indication are alternatives.", 2.0, 6.1, 9.4, 0.72, fill=CREAM, accent=GOLD, title_size=13)
    add_footer(slide, "Sources: docs/reference/ppm-calendar.md; docs/xCropProtection-templates/")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Where variability enters", "Distributions", 7)
    add_card(slide, "Choice", "Choose one indication or application sequence. Probabilities must sum to 1.", 0.75, 1.75, 3.7, 1.75, fill=MINT)
    add_card(slide, "Constant", "A fixed rate, buffer, margin, or minimum applied area.", 4.8, 1.75, 3.7, 1.75, fill=SKY, accent=BLUE)
    add_card(slide, "Uniform", "Sample continuously between Lower and Upper.", 8.85, 1.75, 3.7, 1.75, fill=CREAM, accent=GOLD)
    add_card(slide, "Normal", "Sample from Mean and SD.", 0.75, 4.05, 3.7, 1.75, fill=CREAM, accent=GOLD)
    add_card(slide, "Scale", "The declaration controls when values change: global, per year, per field, or a combination.", 4.8, 4.05, 3.7, 1.75, fill=MINT)
    add_card(slide, "Monte Carlo", "NumberMC repeats the parameterised process; ParallelProcesses controls concurrency.", 8.85, 4.05, 3.7, 1.75, fill=SKY, accent=BLUE)
    add_text(slide, "The demo UI exposes constant, uniform, and normal rates without hiding the XML scales.", 1.2, 6.33, 10.9, 0.38, size=15, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: docs/reference/distributions.md; template.xrun")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Products and active substances", "Conversion rules", 8)
    add_card(slide, "Product → product", "Names and application rates pass through unchanged.", 0.85, 2.0, 3.2, 1.65, fill=MINT)
    add_card(slide, "Active substance → active substance", "Names and rates pass through unchanged.", 0.85, 4.25, 3.2, 1.65, fill=SKY, accent=BLUE)
    add_card(slide, "Product → active substance", "Query the SQLite formulation database, then calculate inclusion-based active-substance rates.", 4.55, 2.75, 4.0, 2.05, fill=CREAM, accent=GOLD)
    add_card(slide, "Invalid direction", "Active substance → product cannot be inferred unambiguously.", 9.05, 2.75, 3.45, 2.05, fill=RGBColor(250, 231, 229), accent=RED)
    add_arrow(slide, 4.05, 2.83, 4.48, 3.28)
    add_arrow(slide, 4.05, 5.08, 4.48, 4.23)
    add_text(slide, "Input scale is attached to Products and ApplicationRates; output scale is global in the .xrun.", 1.2, 6.28, 10.9, 0.45, size=15, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: docs/reference/product-active-substance.md; CropProtection/product-active-substance.db")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Treatment geometry", "Spatial semantics", 9)
    field = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(1.9), Inches(5.9), Inches(3.8)
    )
    field.fill.solid()
    field.fill.fore_color.rgb = RGBColor(185, 216, 159)
    field.line.color.rgb = TEAL
    field.line.width = Pt(2)
    inner = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(1.85), Inches(2.8), Inches(4.1), Inches(2.0)
    )
    inner.fill.solid()
    inner.fill.fore_color.rgb = GOLD
    inner.line.fill.background()
    add_text(slide, "Field geometry", 2.38, 2.17, 2.9, 0.4, size=17, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Applied area", 2.72, 3.48, 2.25, 0.45, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "In-field margin + in-crop buffer", 1.38, 5.1, 4.9, 0.45, size=13, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_card(slide, "MinimumAppliedArea", "After geometry adjustment, skip the application when remaining area is below the global threshold.", 7.5, 1.95, 4.8, 1.55, fill=CREAM, accent=GOLD)
    add_card(slide, "Output meaning", "AppliedMass can be derived from application rate × applied area.", 7.5, 4.05, 4.8, 1.55, fill=SKY, accent=BLUE)
    add_text(slide, "The model receives fields, LULC types, and geometries from LandscapeScenario.", 7.65, 6.05, 4.55, 0.48, size=14, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: model/variant/mc.xml; docs/reference/ppm-calendar.md")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "How the demo model is wired", "Architecture", 10)
    components = [
        ("LandscapeScenario", "FeatureIds\nFeatureTypeIds\nGeometries", 0.8, 2.2, BLUE),
        ("xCropProtection", ".xrun parameters\nPPM calendars\nTechnologies", 4.85, 2.2, TEAL),
        ("X3dfStore", "Application datasets\nMonte Carlo output", 8.9, 2.2, NAVY),
    ]
    for title, body, x, y, color in components:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(3.55), Inches(2.2)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        add_text(slide, title, x + 0.25, y + 0.3, 3.05, 0.5, size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, body, x + 0.35, y + 1.12, 2.85, 0.92, size=14, color=WHITE, align=PP_ALIGN.CENTER)
    add_arrow(slide, 4.38, 3.3, 4.8, 3.3)
    add_arrow(slide, 8.43, 3.3, 8.85, 3.3)
    add_card(slide, "Execution", "experiment.xml controls Monte Carlo orchestration; mc.xml composes LandscapeScenario and xCropProtection.", 1.1, 5.2, 11.1, 0.92, fill=CREAM, accent=GOLD, title_size=13)
    add_footer(slide, "Sources: model/variant/experiment.xml; model/variant/mc.xml")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "What is already in the demo", "Present assets", 11)
    rows = [
        ("SingleField_100x100_dev", "1 schematic field", "LULC target type 2", "Lindan demonstration"),
        ("Demo-scenario", "1,000 features", "LULC target types 222 / 444", "Choice + normal + uniform"),
        ("Rummen", "Real catchment", "Apple fields and reaches", "Multi-application examples"),
        ("Templates", "Parameter examples", "Multiple crops and patterns", "Tank mixes and choices"),
    ]
    x_positions = [0.75, 3.9, 6.15, 9.1]
    widths = [3.0, 2.1, 2.8, 3.45]
    headers = ["Scenario / set", "Spatial extent", "Parameter focus", "Suggested use"]
    for x, width, header in zip(x_positions, widths, headers):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.75), Inches(width), Inches(0.55))
        shape.fill.solid()
        shape.fill.fore_color.rgb = NAVY
        shape.line.fill.background()
        add_text(slide, header, x + 0.12, 1.88, width - 0.24, 0.28, size=11, color=WHITE, bold=True)
    for row_index, row in enumerate(rows):
        y = 2.36 + row_index * 0.92
        for column, (x, width, value) in enumerate(zip(x_positions, widths, row)):
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(width), Inches(0.8))
            shape.fill.solid()
            shape.fill.fore_color.rgb = WHITE if row_index % 2 == 0 else SKY
            shape.line.color.rgb = LINE
            add_text(slide, value, x + 0.12, y + 0.14, width - 0.24, 0.48, size=12, color=NAVY if column == 0 else INK, bold=column == 0)
    add_text(slide, "A new UI starts with SingleField_Lindan_5feb.xrun for the shortest edit–run loop.", 0.9, 6.35, 11.5, 0.38, size=15, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: scenario/; CropProtection/; README.md")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Browser parameterisation workflow", "Simulation studio", 12)
    steps = [
        ("01", "Select", "Choose an .xrun template, landscape scenario, and XML CP scenario."),
        ("02", "Configure", "Set dates, output type, MC count, concurrency, and minimum area."),
        ("03", "Edit", "Change applications, tank items, rates, windows, buffers, and technologies."),
        ("04", "Validate", "Check file existence, ranges, sequence probabilities, and conversion rules."),
        ("05", "Export / run", "Create a unique bundle; launch only when the runtime is available."),
    ]
    for index, (number, title, body) in enumerate(steps):
        x = 0.72 + index * 2.52
        add_text(slide, number, x, 1.72, 0.75, 0.6, size=26, color=GOLD, bold=True)
        add_text(slide, title, x, 2.43, 2.15, 0.43, size=18, color=NAVY, bold=True)
        add_text(slide, body, x, 3.05, 2.1, 1.5, size=12, color=INK)
        if index < 4:
            add_arrow(slide, x + 2.12, 2.1, x + 2.45, 2.1, LINE)
    add_card(slide, "Non-destructive output", "simulation_ui/generated/<SimID>/<SimID>.xrun\nCropProtection/generated/<SimID>/xCropProtection.xml", 1.15, 5.25, 11.0, 1.05, fill=MINT, title_size=14)
    add_footer(slide, "Source: simulation_ui/app.py; simulation_ui/model_io.py")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    add_header(slide, "Reading the result", "Outputs", 13)
    output_items = [
        ("ApplicationDates", "Simulation day"),
        ("AppliedFields", "Feature ID"),
        ("ApplicationRates", "g/ha"),
        ("AppliedAreas", "Treated area"),
        ("AppliedPPP", "Product or substance"),
        ("TechnologyDriftReductions", "Configured fraction"),
    ]
    for index, (name, meaning) in enumerate(output_items):
        x = 0.85 + (index % 2) * 6.05
        y = 1.78 + (index // 2) * 1.25
        add_card(slide, name, meaning, x, y, 5.55, 0.95, fill=WHITE if index % 2 == 0 else SKY, accent=TEAL if index % 2 == 0 else BLUE, title_size=14)
    add_text(slide, "Analysis notebooks export the HDF store to CSV, plot rates and cumulative loading, and map applications.", 1.15, 5.85, 11.0, 0.55, size=16, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: docs/xToxicLoad/xToxicLoad-output.md; analysis/")

    slide = deck.slides.add_slide(deck.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = NAVY
    add_text(slide, "From concept to first run", 0.8, 0.7, 10.8, 0.75, size=30, color=WHITE, bold=True)
    add_bullet_list(
        slide,
        [
            "Start the Streamlit UI: python -m streamlit run simulation_ui\\app.py",
            "Choose SingleField_Lindan_5feb.xrun and keep the one-field scenario.",
            "Change rate, date window, buffer, margin, or Monte Carlo count.",
            "Export a unique SimID bundle, then launch when model/core is initialised.",
            "Inspect run/<SimID>/mcs/.../store/arr.dat or use the analysis notebooks.",
        ],
        1.0,
        1.8,
        10.9,
        3.85,
        size=20,
        color=WHITE,
    )
    add_text(slide, "Key idea", 1.0, 5.8, 1.5, 0.35, size=11, color=GOLD, bold=True)
    add_text(slide, "Explicit landscape units + explicit treatment logic + controlled variability", 1.0, 6.18, 11.2, 0.65, size=23, color=MINT, bold=True)
    add_text(slide, "Generated for xCropProtectionDemo", 0.98, 7.15, 4.0, 0.2, size=8, color=WHITE)

    deck.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
