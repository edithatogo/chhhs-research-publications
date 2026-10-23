import io
import zipfile
import unittest

from scripts.grants_nhmrc_download import _dataset_metadata, _workbook_inventory


def workbook_bytes():
    strings = [
        "Title", "NHMRC outcomes", "Access rights", "Open", "Data custodian",
        "NHMRC", "Publish date (yyyy-mm-dd)", "46289", "Grant ID", "Application ID",
    ]
    shared = """<?xml version="1.0" encoding="UTF-8"?>
    <sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="10" uniqueCount="10">{}</sst>""".format(
        "".join(f"<si><t>{value}</t></si>" for value in strings)
    )
    workbook = """<?xml version="1.0" encoding="UTF-8"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <sheets><sheet name="METADATA" sheetId="1" r:id="rId1"/>
      <sheet name="GRANTS DATA" sheetId="2" r:id="rId2"/></sheets></workbook>"""
    relationships = """<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Target="worksheets/sheet1.xml"/>
      <Relationship Id="rId2" Target="worksheets/sheet2.xml"/>
    </Relationships>"""
    metadata = """<?xml version="1.0" encoding="UTF-8"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <dimension ref="A1:B4"/><sheetData>
      <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>
      <row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>
      <row r="3"><c r="A3" t="s"><v>4</v></c><c r="B3" t="s"><v>5</v></c></row>
      <row r="4"><c r="A4" t="s"><v>6</v></c><c r="B4" t="s"><v>7</v></c></row>
      </sheetData></worksheet>"""
    data = """<?xml version="1.0" encoding="UTF-8"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <dimension ref="A1:B2"/><sheetData>
      <row r="1"><c r="A1" t="s"><v>8</v></c><c r="B1" t="s"><v>9</v></c></row>
      <row r="2"><c r="A2"><v>G-1</v></c><c r="B2"><v>A-1</v></c></row>
      </sheetData></worksheet>"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/sharedStrings.xml", shared)
        archive.writestr("xl/worksheets/sheet1.xml", metadata)
        archive.writestr("xl/worksheets/sheet2.xml", data)
    return buffer.getvalue()


class NhMrcWorkbookInspectionTests(unittest.TestCase):
    def test_inventory_reads_sheet_names_bounds_and_shared_headers(self):
        inventory = _workbook_inventory(workbook_bytes())
        self.assertEqual(
            inventory,
            [
                {"sheet": "METADATA", "dimension": "A1:B4", "first_row_cells": "Title, NHMRC outcomes"},
                {"sheet": "GRANTS DATA", "dimension": "A1:B2", "first_row_cells": "Grant ID, Application ID"},
            ],
        )

    def test_metadata_is_allowlisted_and_excel_dates_are_normalized(self):
        result = _dataset_metadata(workbook_bytes())
        self.assertEqual(result["Title"], "NHMRC outcomes")
        self.assertEqual(result["Access rights"], "Open")
        self.assertEqual(result["Data custodian"], "NHMRC")
        self.assertEqual(result["Publish date (yyyy-mm-dd)"], "2026-09-24")
        self.assertNotIn("G-1", result.values())


if __name__ == "__main__":
    unittest.main()
