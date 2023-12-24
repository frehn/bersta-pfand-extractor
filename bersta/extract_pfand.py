import fitz  # PyMuPDF
from dataclasses import dataclass
import re
import os

PFANDAUSGABEN_SECTION_NAME = "Pfandausgaben"
PFANDRETOUREN_SECTION_NAME = "Pfandretouren"
SUMME_SECTION_NAME = "Summe" # Teil der Rechnung nach Pfandretouren

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

@dataclass(frozen=True)
class PfandExtractionData:
    section: str
    values: list[float]

@dataclass(frozen=True)
class PfandExtractionResult:
    ausgaben_values: list[float]
    ausgaben: float
    retouren_values: list[float]
    retouren: float




def extract_text_with_positions(pdf_path, section_names) -> tuple[list[TextInPdf], list[TextInPdf]]:
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

def get_values(start: PositionInPdf, end: PositionInPdf, values: list[TextInPdf]) -> list[str]:
    if end is not None:
        return [value.text for value in values if start <= value.position and value.position <= end]
    else:
        return [value.text for value in values if start <= value.position]
   
def format_value(value: str):
    import locale
    locale.setlocale(locale.LC_NUMERIC, "de")
    without_eur = value[:-1]
    return locale.atof(without_eur)

def result_to_string(result: PfandExtractionResult):
    ausgaben = [PFANDAUSGABEN_SECTION_NAME, f'Zahlen: {result.ausgaben_values}', f'Summe: {result.ausgaben}']
    retouren = [PFANDRETOUREN_SECTION_NAME, f'Zahlen: {result.retouren_values}', f'Summe: {result.retouren}']

    return os.linesep.join(ausgaben + retouren)

def datas_to_result(datas: list[PfandExtractionData]) -> PfandExtractionResult:
    interesting_section_names = [PFANDAUSGABEN_SECTION_NAME, PFANDRETOUREN_SECTION_NAME]
    interesting_datas = [data for data in datas if is_in_any(data.section, interesting_section_names)]
    ausgaben_values = []
    ausgaben = None
    retouren = None
    retouren_values = []

    for data in interesting_datas:
        s = sum(data.values)
        if PFANDAUSGABEN_SECTION_NAME in data.section:
            ausgaben = s
            ausgaben_values = data.values
        elif PFANDRETOUREN_SECTION_NAME in data.section:
            retouren = -1 * s
            retouren_values = [-1 * v for v in data.values]
        else:
            raise f"Abschnitt '{data.section}' unbekannt"

    return PfandExtractionResult(ausgaben_values, ausgaben, retouren_values, retouren)

def extract_pfand_from_bersta_rechnung(file) -> PfandExtractionResult:
    section_names = [PFANDAUSGABEN_SECTION_NAME, PFANDRETOUREN_SECTION_NAME, SUMME_SECTION_NAME]
    sections, values = extract_text_with_positions(file, section_names)
    section_datas = []

    for i in range(0, len(sections)):
        section = sections[i]
        start = section.position

        if i < len(sections)-1:
            end = sections[i+1].position
        else:
            end = None
        str_values = get_values(start, end, values)
        section_datas.append(PfandExtractionData(section=section.text, values=[format_value(v) for v in str_values]))

    return datas_to_result(section_datas)


def extract_pfand_from_bersta_rechnung_as_string(file) -> str:
    return result_to_string(extract_pfand_from_bersta_rechnung(file))