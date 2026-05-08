"""
Bengaluru Heritage Guide — PDF Generator

Generates a comprehensive PDF document covering all 13 heritage sites
for ingestion by the RAG pipeline's vector store.
"""

import os
import json
from fpdf import FPDF


class HeritagePDF(FPDF):
    """Custom PDF with header/footer for the heritage guide."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Bengaluru Heritage Explorer - Architectural Guide", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def sanitize(text):
    """Replace problematic Unicode characters with ASCII equivalents."""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u00e9": "e",    # e-acute
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Final safety net: encode to latin-1 replacing anything unsupported
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def create_pdf():
    # Load master data for structured info
    with open("data/master_data.json", "r", encoding="utf-8") as f:
        master = json.load(f)

    landmarks = master.get("landmarks", [])
    styles = {s["name"]: s["description"] for s in master.get("styles", [])}
    eras = {e["name"]: e for e in master.get("eras", [])}

    pdf = HeritagePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Title Page ──
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 15, sanitize("Bengaluru Heritage"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.cell(0, 12, sanitize("Architectural Guide"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, sanitize("A comprehensive guide to 13 iconic heritage sites"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, sanitize("spanning over 1000 years of Bengaluru's history"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, sanitize("Covering: Chola Period (1085 CE) to Post-Independence (1956)"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, sanitize("Architectural Styles: Dravidian, Indo-Islamic, Neo-Classical, Tudor Revival, Gothic Revival & more"), align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Introduction Chapter ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, sanitize("Introduction"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)

    intro_text = sanitize(
        "Bengaluru, the capital of Karnataka, is a city where history and modernity coexist in remarkable "
        "harmony. While globally known as India's Silicon Valley, the city harbors a rich architectural "
        "heritage that stretches back nearly a millennium. From the Chola-period Someshwara Temple in "
        "Halasuru (circa 1085 CE) to the monumental Vidhana Soudha completed in 1956, Bengaluru's built "
        "heritage tells the story of successive dynasties, colonial encounters, and post-independence nation-building.\n\n"
        "The city was founded in 1537 by Kempe Gowda I, a chieftain under the Vijayanagara Empire, who "
        "built a mud fort and established the town's first markets. Under the rule of Hyder Ali and Tipu Sultan "
        "in the 18th century, Bengaluru was transformed into a fortified stronghold with grand palaces and "
        "botanical gardens. The British, after defeating Tipu Sultan in 1799, established a cantonment and "
        "introduced European architectural styles -- Neo-Classical civic buildings, Gothic Revival churches, "
        "and Indo-Saracenic institutional buildings that still define the city's central districts.\n\n"
        "This guide covers 13 landmark sites across Bengaluru, organized by their historical era and "
        "architectural style. Each entry provides detailed information about the site's history, architectural "
        "features, and significance within the broader context of Bengaluru's urban evolution."
    )
    pdf.multi_cell(0, 7, intro_text)

    # ── Architectural Styles Chapter ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, sanitize("Architectural Styles of Bengaluru"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    for style_name, style_desc in styles.items():
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, sanitize(style_name), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, sanitize(style_desc))
        # List landmarks with this style
        matching = [lm["name"] for lm in landmarks if lm.get("style") == style_name]
        if matching:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, sanitize(f"Examples in Bengaluru: {', '.join(matching)}"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # ── Historical Eras Chapter ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, sanitize("Historical Eras"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    for era_name, era_data in eras.items():
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, sanitize(f"{era_name} ({era_data.get('period', '')})"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, sanitize(era_data.get("description", "")))
        matching = [lm["name"] for lm in landmarks if lm.get("era") == era_name]
        if matching:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, sanitize(f"Sites from this era: {', '.join(matching)}"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # ── Individual Landmark Pages ──
    desc_dir = "data/descriptions"
    for lm in landmarks:
        pdf.add_page()
        # Landmark title
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, sanitize(lm["name"]), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Metadata table
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 240, 240)

        meta_fields = [
            ("Style", lm.get("style", "")),
            ("Era", lm.get("era", "")),
            ("Year Built", str(lm.get("year_built", ""))),
            ("Location", f"{lm.get('location', '')}, {lm.get('neighborhood', '')}"),
            ("Architect", lm.get("architect", "")),
        ]
        for label, value in meta_fields:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(35, 7, sanitize(f"{label}:"), border=0)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, sanitize(value), new_x="LMARGIN", new_y="NEXT")

        pdf.ln(5)

        # Short description
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 7, sanitize(lm.get("short_description", "")))
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        # Full description from text file
        desc_file = os.path.join(desc_dir, f"{lm['id']}.txt")
        if os.path.exists(desc_file):
            with open(desc_file, "r", encoding="utf-8") as f:
                full_text = f.read().strip()
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, sanitize(full_text))
        pdf.ln(5)

        # Nearby sites
        nearby = lm.get("nearby", [])
        if nearby:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, sanitize("Nearby Heritage Sites:"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for n in nearby:
                readable = n.replace("_", " ").title()
                pdf.cell(0, 7, sanitize(f"  - {readable}"), new_x="LMARGIN", new_y="NEXT")

    # ── Conclusion ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, sanitize("Bengaluru's Heritage Landscape"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    conclusion = sanitize(
        "Bengaluru's architectural heritage is a layered tapestry woven by Chola artisans, Vijayanagara "
        "founders, Mysorean rulers, British colonists, and post-independence visionaries. The 13 sites "
        "documented in this guide represent the full spectrum of the city's built history -- from the "
        "1000-year-old Someshwara Temple to the mid-20th-century Vidhana Soudha.\n\n"
        "What makes Bengaluru's heritage unique is its diversity. Within a few kilometers, one can walk "
        "from a Dravidian cave temple to a Tudor Revival palace, from an Indo-Islamic summer palace to a "
        "Gothic Revival cathedral. This coexistence of architectural traditions reflects the city's history "
        "as a crossroads of cultures, religions, and political powers.\n\n"
        "The Bengaluru Heritage Explorer project aims to make this heritage accessible through modern "
        "technology -- combining AI-powered natural language understanding, knowledge graph traversal, "
        "multi-modal search, and audio narration to create an intelligent digital tour guide for one of "
        "India's most historically rich cities."
    )
    pdf.multi_cell(0, 7, conclusion)

    # Save
    os.makedirs("data/docs", exist_ok=True)
    output_path = "data/docs/heritage_guide.pdf"
    pdf.output(output_path)
    print(f"Successfully generated {output_path} ({pdf.page_no()} pages)")


if __name__ == "__main__":
    create_pdf()
