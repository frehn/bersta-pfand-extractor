import json
import pytest
from bersta.extract_pfand import extract_pfand_from_bersta_rechnung

with open('tests/resources/test_extract_pfand_spec.json', 'r') as file:
    specs = json.load(file)

test_data = [(spec["file"], spec["ausgaben"], spec["retouren"]) for spec in specs]

@pytest.mark.parametrize("file_name, expected_ausgaben, expected_retouren", test_data)
def test_pfand_extraction(file_name, expected_ausgaben, expected_retouren):
    result = extract_pfand_from_bersta_rechnung(f'tests/resources/{file_name}')
    
    assert result.ausgaben == expected_ausgaben, f"Expected ausgaben {expected_ausgaben}, got {result.ausgaben}"
    assert result.retouren == expected_retouren, f"Expected retouren {expected_retouren}, got {result.retouren}"