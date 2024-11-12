from enum import Enum

class BomType(Enum):
    CW = "CW"  # Cost Walk BOM
    CBOM = "CBOM"  # Component BOM
    EBOM = "EBOM"  # Engineering BOM

    def __str__(self):
        return self.value  # So it will return the string representation when used

class FilePrefix(Enum):
    CW = "COST_WALK "
    CBOM = "CBOM FOR DB "
    EBOM = "EBOM FOE DB "

    def __str__(self):
        return self.value # So it will return the string representation when used

class BomTemplateVersion(Enum):
    v1 = "version 1"
    v2 = "version 2"
    v3 = "version 3"

    def __str__(self):
        return self.value # So it will return the string representation when used
