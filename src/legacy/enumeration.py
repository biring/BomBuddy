from enum import Enum

class BomTempVer(Enum):
    v1 = "version 1" # Default not supported
    v2 = "version 2"
    v3 = "version 3"

    def __str__(self):
        return self.value # So it will return the string representation when used

class SourceFileType(Enum):
    NA = "N/A"  # Default not supported
    CB = "CB"  # Costed BOM
    EB = "EB"  # Engineering BOM

    def __str__(self):
        return self.value # So it will return the string representation when used


class OutputFileType(Enum):
    NA = "NA "  # Default not supported
    CW = "CW "  # Cost Walk
    dB_CB = "dB_CBOM "  # CBOM for dB upload
    db_EB = "dB_EBOM "  # EBOM for dB uploadEngineering BOM

    def __str__(self):
        return self.value  # So it will return the string representation when used

