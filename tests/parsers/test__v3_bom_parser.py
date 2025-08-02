import os
import unittest
import pandas as pd

from src.parsers.interfaces import *
from src.models.interfaces import *

# noinspection PyProtectedMember
import src.parsers._v3_bom_parser as v3_parser


class TestIsV3Board(unittest.TestCase):

    def test_false_when_no_identifiers_present(self):
        """
        Should return False when none of the required headers are present.
        """
        df = pd.DataFrame([["Foo", "Bar", "Baz"], ["1", "2", "3"]])
        result = v3_parser._is_v3_board_sheet("Sheet3", df)
        self.assertFalse(result)

    def test_false_when_some_identifiers_missing(self):
        """
        Should return False when only a subset of BOARD_TABLE_IDENTIFIERS are present.
        """
        # Only include a partial set of required headers
        partial_headers = REQUIRED_V3_BOARD_TABLE_IDENTIFIERS[:-1] + ["Other"]
        data = [partial_headers] + [[None] * len(partial_headers)]
        df = pd.DataFrame(data)

        result = v3_parser._is_v3_board_sheet("Sheet2", df)
        self.assertFalse(result)

    def test_true_when_all_identifiers_present(self):
        """
        Should return True when all BOARD_TABLE_IDENTIFIERS are present in a row.
        """
        # Construct a DataFrame with all required headers in the first row
        headers = REQUIRED_V3_BOARD_TABLE_IDENTIFIERS + ["Extra Column"]
        data = [headers] + [[None] * len(headers)]
        df = pd.DataFrame(data)

        result = v3_parser._is_v3_board_sheet("Sheet1", df)
        self.assertTrue(result)


class TestIsV3Bom(unittest.TestCase):

    def test_false_when_no_identifiers_present(self):
        # Construct path relative to this test file
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsNotBomTemplate.xlsx')

        # Read excell file as pandas data frame
        df = pd.read_excel(file_path, sheet_name=None)

        # Check read is successful
        self.assertTrue(df)  # Checks that the dict is not empty

        # Run unit test
        with self.subTest("False"):
            sheets = list(df.items())
            self.assertFalse(is_v3_bom(sheets), "Failed to detect NOT a BOM template")

    def test_false_when_some_identifiers_missing(self):
        # Construct path relative to this test file
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsVersion2BomTemplate.xlsx')

        # Read excell file as pandas data frame
        df = pd.read_excel(file_path, sheet_name=None)

        # Check read is successful
        self.assertTrue(df)  # Checks that the dict is not empty

        # Run unit test
        with self.subTest("False"):
            sheets = list(df.items())
            self.assertFalse(is_v3_bom(sheets), "Failed to detect version 2 BOM template")

    def test_true_when_all_identifiers_present(self):
        # Construct path relative to this test file
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsVersion3BomTemplate.xlsx')

        # Read excell file as pandas data frame
        df = pd.read_excel(file_path, sheet_name=None)

        # Check read is successful
        self.assertTrue(df)  # Checks that the dict is not empty

        # Run unit test
        with self.subTest("True"):
            sheets = list(df.items())
            self.assertTrue(is_v3_bom(sheets), "Failed to detect version 3 BOM template")


class TestParseBoardHeader(unittest.TestCase):

    def test_true_when_full_header_match(self):
        """
        Test parsing board-level metadata from a real V3 BOM header section.
        """
        # Load Excel and extract the sheet
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "test_data", "IsVersion3BomTemplate.xlsx")
        df = pd.read_excel(file_path, dtype=str, header=None)

        # Extract the top 10 rows as the header block. Adjust as needed.
        header_df = df.iloc[:10]

        # Expected result based on actual cell contents in those rows
        expected = Header(
            model_no="FD100US",
            board_name="POWER PCBA",
            manufacturer="Kimball",
            build_stage="EB2",
            date="2020-08-10 00:00:00",
            material_cost="139.64",
            overhead_cost="2.34",
            total_cost="141.98"
        )

        # Parse and assert
        result = v3_parser._parse_board_header(header_df)
        self.assertEqual(result, expected)


class TestParseBoardTable(unittest.TestCase):

    def test_true_with_two_rows_and_messy_header(self):
        """
        Test parsing a BOM table with multiple rows into Item instances.
        """
        # Simulated BOM table with two rows and messy headers
        table_df = pd.DataFrame([
            {
                " Item ": 1,
                "Component\n": "Relay",
                "Device Package": "DIP",
                " Description ": "12VDC Relay",
                "Unit": "PCS",
                "Classification ": "A",
                "Manufacturer": "PANASONIC",
                "Manufacturer P/N": "SRG-S-112DM-F",
                "UL/VDE \tNumber": "VDE 40037165",
                "Validated at": "EB0",
                "Qty": 1,
                "Designator": "RY1",
                "U/P \n(RMB W/ VAT)": "1.000",
                "Sub-Total \n(RMB W/ VAT)": "1.000"
            },
            {
                " Item ": 2,
                "Component\n": "Capacitor",
                "Device Package": "0805",
                " Description ": "10uF 25V X7R",
                "Unit": "PCS",
                "Classification ": "B",
                "Manufacturer": "TDK",
                "Manufacturer P/N": "C2012X7R1E106K",
                "UL/VDE \tNumber": "",
                "Validated at": "EB0",
                "Qty": 2,
                "Designator": "C1,C2",
                "U/P \n(RMB W/ VAT)": "0.100",
                "Sub-Total \n(RMB W/ VAT)": "0.200"
            }
        ])

        expected = [
            Item(
                item="1",
                component_type="Relay",
                device_package="DIP",
                description="12VDC Relay",
                unit="PCS",
                classification="A",
                manufacturer="PANASONIC",
                mfg_part_number="SRG-S-112DM-F",
                ul_vde_number="VDE 40037165",
                validated_at="EB0",
                qty="1",
                designator="RY1",
                unit_price="1.000",
                sub_total="1.000"
            ),
            Item(
                item="2",
                component_type="Capacitor",
                device_package="0805",
                description="10uF 25V X7R",
                unit="PCS",
                classification="B",
                manufacturer="TDK",
                mfg_part_number="C2012X7R1E106K",
                ul_vde_number="",
                validated_at="EB0",
                qty="2",
                designator="C1,C2",
                unit_price="0.100",
                sub_total="0.200"
            )
        ]

        with self.subTest("Basic"):
            result = v3_parser._parse_board_table(table_df)
            self.assertEqual(result, expected)


class TestParseBoardTableRow(unittest.TestCase):

    def test_true_with_messy_header(self):
        """
        Test parsing a BOM row with varied header formatting into an Item instance.
        """
        # Simulated messy BOM row from Excel
        row = pd.Series({
            " Item ": 1,
            "Component\n": "Relay",
            "Device Package": "DIP",
            " Description ": "12VDC Relay",
            "Unit": "PCS",
            "Classification ": "A",
            "Manufacturer": "PANASONIC",
            "Manufacturer P/N": "SRG-S-112DM-F",
            "UL/VDE \tNumber": "VDE 40037165",
            "Validated at": "EB0",
            "Qty": 1,
            "Designator": "RY1",
            "U/P \n(RMB W/ VAT)": "1.000",
            "Sub-Total \n(RMB W/ VAT)": "1.000"
        })

        # Expected output dataclass
        expected = Item(
            item="1",
            component_type="Relay",
            device_package="DIP",
            description="12VDC Relay",
            unit="PCS",
            classification="A",
            manufacturer="PANASONIC",
            mfg_part_number="SRG-S-112DM-F",
            ul_vde_number="VDE 40037165",
            validated_at="EB0",
            qty="1",
            designator="RY1",
            unit_price="1.000",
            sub_total="1.000"
        )

        # Execute and assert
        with self.subTest("Basic"):
            result = v3_parser._parse_board_table_row(row)
            self.assertEqual(result, expected)


class TestParseBoard(unittest.TestCase):

    def test_of_bom_with_four_items(self):
        """
        Test parsing a version 3 BOM with 4 items.
        """
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "test_data", "Version3BomSample.xlsx")
        df = pd.read_excel(file_path, dtype=str, header=None)

        expected = Board(
            header=Header(
                model_no="BM250",
                board_name="POWER PCBA",
                manufacturer="Kimball",
                build_stage="PP1",
                date="2025-08-10 00:00:00",
                material_cost="1.5",
                overhead_cost="2.34",
                total_cost="3.84"
            ),
            items=[
                Item(
                    item="1",
                    component_type="PCB",
                    device_package="",
                    description="FR-4, double layer, 1OZ, 1.6mm, 213mm*70mm",
                    unit="PCS",
                    classification="A",
                    manufacturer="Quick PCB",
                    mfg_part_number="1670A_V1.1_A",
                    ul_vde_number="E351308",
                    validated_at="EB0",
                    qty="1",
                    designator="PCB",
                    unit_price="0.5",
                    sub_total="0.5"
                ),
                Item(
                    item="",
                    component_type="ALT1",
                    device_package="",
                    description="FR-4, double layer, 1OZ, 1.6mm, 213mm*70mm",
                    unit="PCS",
                    classification="A",
                    manufacturer="Fast Turn",
                    mfg_part_number="3694AC",
                    ul_vde_number="E314919",
                    validated_at="EB1",
                    qty="0",
                    designator="",
                    unit_price="0.7",
                    sub_total="0"
                ),
                Item(
                    item="2",
                    component_type="Relay",
                    device_package="DIP",
                    description="12VDC 17A/250VAC SPST -40~105℃ 21*16*21.8mm",
                    unit="PCS",
                    classification="A",
                    manufacturer="Sanyou",
                    mfg_part_number="SRG-S-112DM-F",
                    ul_vde_number="VDE 40037165",
                    validated_at="FOT/EB0",
                    qty="1",
                    designator="RY1",
                    unit_price="1",
                    sub_total="1"
                ),
                Item(
                    item="",
                    component_type="ALT1",
                    device_package="DIP",
                    description="12VDC 17A/250VAC SPST -40~105℃ 21*16*21.8mm",
                    unit="PCS",
                    classification="A",
                    manufacturer="Panasonic",
                    mfg_part_number="Y3U-SS-112LMF",
                    ul_vde_number="TUV R50446369",
                    validated_at="EB1/MP",
                    qty="0",
                    designator="",
                    unit_price="1.2",
                    sub_total="0"
                )
            ]
        )

        result = v3_parser._parse_board_sheet(df)
        self.assertEqual(result, expected)


class TestParseBom(unittest.TestCase):

    def test_parse_multiple_boards_from_version3_excel(self):
        """
        Test parsing version 3 BOM with two valid boms.
        """
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "test_data", "Version3BomMultiBoard.xlsx")
        xls = pd.ExcelFile(file_path)

        # Convert all sheets to (sheet name, dataframe) tuples
        sheets = [(name, xls.parse(name, dtype=str, header=None)) for name in xls.sheet_names]

        expected = Bom(
            file_name="",
            boards=[
                Board(
                    header=Header(
                        model_no="BM250",
                        board_name="Power PCBA",
                        manufacturer="Kimball",
                        build_stage="PP1",
                        date="2025-08-10 00:00:00",
                        material_cost="0.9",
                        overhead_cost="1.25",
                        total_cost="2.15"
                    ),
                    items=[
                        Item(
                            item="1",
                            component_type="Substrate",
                            device_package="—",
                            description="Generic 2-layer, 1OZ, 1.6mm, 210mm × 70mm",
                            unit="PCS",
                            classification="A",
                            manufacturer="FabVendor A",
                            mfg_part_number="SUB-01",
                            ul_vde_number="CERT-0001",
                            validated_at="PP1",
                            qty="1",
                            designator="PCB1",
                            unit_price="0.8",
                            sub_total="0.8"
                        ),
                        Item("", "ALT1", "—", "Generic 2-layer, 1OZ, 1.6mm, 210mm × 70mm", "PCS", "A",
                             "FabVendor B", "SUB-ALT1", "CERT-0002", "PP0", "0", "", "0.9", "0"),
                        Item("2", "Switch", "DIP", "12VDC 15A SPST, 20×15×20mm, -40~105℃", "PCS", "A",
                             "SwitchMfr A", "SW-01", "CERT-1001", "PP0/PP1", "1", "SW1", "0.1", "0.1"),
                        Item("", "ALT1", "DIP", "12VDC 15A SPST, 20×15×20mm, -40~105℃", "PCS", "A",
                             "SwitchMfr B", "SW-ALT1", "CERT-1002", "PP0", "0", "", "0.2", "0")
                    ]
                ),
                Board(
                    header=Header(
                        model_no="BM250",
                        board_name="MCU PCBA",
                        manufacturer="Kimball",
                        build_stage="PP1",
                        date="2025-08-15 00:00:00",
                        material_cost="1.8",
                        overhead_cost="2.35",
                        total_cost="4.15"
                    ),
                    items=[
                        Item(
                            item="1",
                            component_type="Resistor",
                            device_package="603",
                            description="10kΩ ±1%, 1/10W, 0603",
                            unit="PCS",
                            classification="A",
                            manufacturer="ResiTech",
                            mfg_part_number="R-10K-0603",
                            ul_vde_number="UL123456",
                            validated_at="EV1",
                            qty="1",
                            designator="R1",
                            unit_price="0.1",
                            sub_total="0.1"
                        ),
                        Item("2", "Capacitor", "805", "1uF ±10%, 50V, X7R, 0805", "PCS", "A", "Captek", "C-1U-0805",
                             "UL654321", "EV2", "1", "C1", "0.2", "0.2"),
                        Item("", "ALT1", "805", "1uF ±10%, 50V, X7R, 0805", "PCS", "A", "AltCap", "AC-1U-0805",
                             "UL654322", "EV3", "0", "", "0.22", "0"),
                        Item("3", "Diode", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "Diotronics",
                             "D-1A-100V", "UL987654", "EV4", "1", "D1", "1.5", "1.5"),
                        Item("", "ALT1", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "SemiComp",
                             "SC-D100", "UL987655", "EV5", "0", "", "1.45", "0"),
                        Item("", "ALT2", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "FastFlow",
                             "FF-1A100V", "UL987656", "EV6", "0", "", "1.48", "0")
                    ]
                )
            ]
        )

        # Parse BOM
        bom = v3_parser.parse_v3_bom(sheets)

        result = v3_parser.parse_v3_bom(sheets)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
