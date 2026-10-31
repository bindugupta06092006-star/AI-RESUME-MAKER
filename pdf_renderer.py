# pdf_renderer.py
import textwrap
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.errors import FPDFException  # if this import fails, fallback to generic Exception in except

def _break_long_tokens(s, max_token_len=60):
    """
    Insert a zero-width-space (\u200b) into tokens longer than max_token_len so FPDF can break them.
    E.g. longfilebasenamewithnospaces -> longfilebase\u200bname...
    """
    def repl(m):
        tok = m.group(0)
        # insert zero-width-space every max_token_len chars
        return "\u200b".join([tok[i:i+max_token_len] for i in range(0, len(tok), max_token_len)])
    # tokens are sequences of non-whitespace characters
    return re.sub(r'\S{'+str(max_token_len+1)+r',}', repl, s)

def text_to_pdf(text, filename="resume.pdf", template="Classic", ttf_path=None, font_name="DejaVu", font_size=11):
    """
    Enhanced PDF writer with professional formatting based on template style.
    Templates: Classic, Modern, Elegant
    """
    pdf = FPDF()
    if not hasattr(pdf, "unifontsubset"):
        pdf.unifontsubset = False

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Template-specific color schemes (RGB)
    colors = {
        "Classic": {"header": (41, 128, 185), "accent": (52, 73, 94)},     # Blue/Dark
        "Modern": {"header": (46, 204, 113), "accent": (39, 174, 96)},     # Green
        "Elegant": {"header": (155, 89, 182), "accent": (142, 68, 173)}    # Purple
    }
    
    template_colors = colors.get(template, colors["Classic"])
    
    # Parse the resume text
    lines = text.split("\n")
    
    # Track if we're in the header section (first few lines)
    in_header = True
    name_found = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            pdf.ln(4)
            continue
        
        # Detect name (usually first non-empty line or contains "Name:")
        if in_header and not name_found and (i < 3 or "name:" in line.lower()):
            name_found = True
            # Extract name
            name_text = line.replace("Name:", "").replace("NAME:", "").strip()
            if name_text:
                # Name styling
                pdf.set_font("Arial", "B", 20)
                pdf.set_text_color(*template_colors["header"])
                pdf.cell(0, 12, name_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(2)
                # Add horizontal line
                pdf.set_draw_color(*template_colors["header"])
                pdf.set_line_width(0.5)
                pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                pdf.ln(5)
                pdf.set_text_color(0, 0, 0)
                continue
        
        # Detect section headers (all caps, ends with colon, or common headers)
        section_keywords = ["PROFESSIONAL SUMMARY", "SUMMARY", "SKILLS", "TECHNICAL SKILLS", 
                          "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE", "PROJECTS", 
                          "CERTIFICATIONS", "ACHIEVEMENTS", "OBJECTIVE"]
        
        is_section = False
        for keyword in section_keywords:
            if keyword in line.upper() and (line.endswith(":") or line.upper() == keyword):
                is_section = True
                break
        
        if is_section:
            in_header = False
            pdf.ln(3)
            pdf.set_font("Arial", "B", 13)
            pdf.set_text_color(*template_colors["accent"])
            display_text = line.rstrip(":")
            pdf.cell(0, 8, display_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Underline for section headers
            pdf.set_draw_color(*template_colors["accent"])
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 50, pdf.get_y())
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            continue
        
        # Detect bullet points
        if line.startswith("•") or line.startswith("-") or line.startswith("*"):
            in_header = False
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            # Remove bullet and clean
            clean_line = line[1:].strip()
            # Add simple bullet (use hyphen instead of bullet character)
            pdf.set_x(pdf.l_margin + 5)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(*template_colors["header"])
            pdf.cell(5, 5, "-", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            # Wrap text for bullet
            pdf.multi_cell(0, 5, clean_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue
        
        # Regular paragraph text
        if in_header and i < 5:
            # Contact info or summary in header area
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        else:
            in_header = False
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save
    pdf.output(filename)
    print(f"Saved professional PDF to {filename}")
