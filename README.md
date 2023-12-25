# BerSta Pfand Extractor

## Windows Download

Download the current version for Windows [here](https://github.com/frehn/bersta-pfand-extractor/releases/download/v1.0.0/bersta-pfand-extractor-1.0.0.zip).

## What is this?

_BerSta Pfand Extractor_ is a small application intended to help
users of [Foodsoft](https://github.com/foodcoops/foodsoft) with
the import of invoices from [Naturkost Grosshandel BerSta](https://www.bersta.at/).

When importing an invoice into Foodsoft, the billed deposits from the invoice 
need to be entered. BerSta Pfand Extractor facilitates this task by extracting 
this data from BerSta's PDF invoices:

![Screenshot](screenshot.png)

## Development

### Running the application

`python -m bersta`

### Running the tests

Create the file `tests/resources/test_extract_pfand_spec.json`
([sample](tests/resources/test_extract_pfand_spec.json.sample))
to add test cases.

Then run `pytest`.

### Building a Windows Executable

Running `pyinstaller bersta/__main__.py`
will package the application into the folder `dist/__main__`.
