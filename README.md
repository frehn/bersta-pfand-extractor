# BerSta Pfand Extractor

## Run Application

`python bersta/ui.py`

## Run Tests

Create the file `tests/resources/test_extract_pfand_spec.json`
([sample](tests/resources/test_extract_pfand_spec.json.sample))
to add test cases.

Then run `pytest`.

## Build Windows Executable

`pyinstaller --onefile bersta/ui.py`

## TODO

- [ ] Fix test rechnung_3, rechnung_7: may have multiple sections of each pfandretouren/pfandausgaben