import fitz  # PyMuPDF
from dataclasses import dataclass
import re
import os
import decimal

decimal.getcontext().prec = 7
decimal.getcontext().traps[decimal.FloatOperation] = True

PFANDAUSGABEN_SECTION_HEADLINE = "Pfandausgaben"
PFANDRETOUREN_SECTION_HEADLINE = "Pfandretouren"
SUMME_SECTION_HEADLINE = "Summe"
LIEFERUNG_SECTION_HEADLINE = "LS.Nr."

# Abschnitte, die für Pfand relevant sind
INTERESTING_SECTION_HEADLINES = [PFANDAUSGABEN_SECTION_HEADLINE, PFANDRETOUREN_SECTION_HEADLINE]

# Alle Abschnitte (um das Ende der Pfand-Abschnitte zu erkennen)
ALL_SECTION_HEADLINES = INTERESTING_SECTION_HEADLINES + [SUMME_SECTION_HEADLINE, LIEFERUNG_SECTION_HEADLINE]

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
class PfandExtractionSection:
    headline: str
    values: list[float]

@dataclass(frozen=True)
class PfandExtractionResult:
    ausgaben_values: list[float]
    ausgaben: float
    retouren_values: list[float]
    retouren: float




def extract_text_with_positions(pdf_path, section_headlines) -> tuple[list[TextInPdf], list[TextInPdf]]:
    document = fitz.open(pdf_path)
    headlines = []
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
                        if is_in_any(text, section_headlines):
                            headlines.append(result)
                        value_re = re.compile("-?[0-9]+,[0-9]+€")
                        if value_re.match(text):
                            values.append(result)

    headlines = sorted(headlines, key=lambda x: x.position)

    return headlines, values

def get_values(start: PositionInPdf, end: PositionInPdf, values: list[TextInPdf]) -> list[str]:
    if end is not None:
        return [value.text for value in values if start <= value.position and value.position <= end]
    else:
        return [value.text for value in values if start <= value.position]
   
def parse_value(value: str) -> decimal.Decimal:
    without_eur = value[:-1]
    with_dot_comma = without_eur.replace(",", ".")
    return decimal.Decimal(with_dot_comma)

def _result_to_string_array(headline: str, values: list[decimal.Decimal], sum: decimal.Decimal) -> list[str]:
  return [f'{headline} Positionen:', os.linesep.join([f'{x}€' for x in values]), f'{headline} Summe: {sum}€']

def result_to_string(result: PfandExtractionResult):
    ausgaben = _result_to_string_array(PFANDAUSGABEN_SECTION_HEADLINE, result.ausgaben_values, result.ausgaben)
    retouren = _result_to_string_array(PFANDRETOUREN_SECTION_HEADLINE, result.retouren_values, result.retouren)

    return os.linesep.join(ausgaben + [''] + retouren)

def datas_to_result(sections: list[PfandExtractionSection]) -> PfandExtractionResult:
    interesting_sections = [section for section in sections if is_in_any(section.headline, INTERESTING_SECTION_HEADLINES)]
    ausgaben_values = []
    ausgaben = decimal.Decimal('0')
    retouren_values = []
    retouren = decimal.Decimal('0')

    for data in interesting_sections:
        s = sum(data.values)
        if PFANDAUSGABEN_SECTION_HEADLINE in data.headline:
            ausgaben += s
            ausgaben_values += data.values
        elif PFANDRETOUREN_SECTION_HEADLINE in data.headline:
            retouren += -1 * s
            retouren_values += [-1 * v for v in data.values]
        else:
            raise f"Abschnitt '{data.headline}' unbekannt"

    return PfandExtractionResult(ausgaben_values, ausgaben, retouren_values, retouren)

def extract_pfand_from_bersta_rechnung(file) -> PfandExtractionResult:
    sections_in_pdf, values = extract_text_with_positions(file, ALL_SECTION_HEADLINES)
    section_datas = []

    for i in range(0, len(sections_in_pdf)):
        section = sections_in_pdf[i]
        start = section.position

        if i < len(sections_in_pdf)-1:
            end = sections_in_pdf[i+1].position
        else:
            end = None
        str_values = get_values(start, end, values)
        section_datas.append(PfandExtractionSection(headline=section.text, values=[parse_value(v) for v in str_values]))

    return datas_to_result(section_datas)


def extract_pfand_from_bersta_rechnung_as_string(file) -> str:
    return result_to_string(extract_pfand_from_bersta_rechnung(file))