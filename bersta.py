import fitz  # PyMuPDF
from dataclasses import dataclass
import re
import os

@dataclass(frozen=True)
class PositionInPdf:
    page: int
    y: float

    def __lt__(self, other):
        return self.page < other.page or (self.page == other.page and self.y < other.y)

    def __le__(self, other):
        return self < other or self == other

@dataclass(frozen=True)
class TextInPdf:
    position: PositionInPdf
    text: str

def is_below(a: TextInPdf, b: TextInPdf):
    return a.page > b.page or a.y > b.y

def is_in_any(x: str, ys: list[str]):
    for y in ys:
        if y in x:
            return True
        
    return False

interesting_section_names = ["Pfandausgaben", "Pfandretouren"]
section_names = interesting_section_names + ["Summe"]

def extract_text_with_positions(pdf_path):
    document = fitz.open(pdf_path)
    sections = []
    values = []

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        result = TextInPdf(position=PositionInPdf(page=page_num, y=span["bbox"][1]),text=text)
                        if is_in_any(text, section_names):
                            sections.append(result)
                        value_re = re.compile("-?[0-9]+,[0-9]+€")
                        if value_re.match(text):
                            values.append(result)

    sections = sorted(sections, key=lambda x: x.position)

    return sections, values

def get_values(start: PositionInPdf, end: PositionInPdf, values: list[TextInPdf]):
    if end is not None:
        return [value for value in values if start <= value.position and value.position <= end]
    else:
        return [value for value in values if start <= value.position]

def format_single(result):
    import locale
    locale.setlocale(locale.LC_NUMERIC, "de")

    values = [x.text for x in result["values"]]
    without_eur = [x[:-1] for x in values]
    numbers = [locale.atof(x) for x in without_eur]

    result = [result["section"].text, f'Zahlen: {numbers}', f'Summe: {sum(numbers)}']

    return os.linesep.join(result)
    
def format_results(results):
    return os.linesep.join([ format_single(result) for result in results])

def extract_pfand_from_bersta_rechnung(file):
    sections, values = extract_text_with_positions(file)
    results = []

    for i in range(0, len(sections)):
        section = sections[i]
        start = section.position

        if i < len(sections)-1:
            end = sections[i+1].position
        else:
            end = None

        results.append({"section": section, "values": get_values(start, end, values)})

    interesting_results = [result for result in results if is_in_any(result["section"].text, interesting_section_names)]
    return format_results(interesting_results)