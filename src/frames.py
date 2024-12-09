# This file has functions to manipulate both rows and columns in a data frame
from typing import Type

import pandas as pd

import columns
import header
import rows

from src.enumeration import SourceFileType, OutputFileType, BomTempVer

# Standardized header names used across eBOM, cBOM and cost walk. They are based off the bom template v2.0 and v3.0
itemHdr = "Item"
componentHdr = "Component"
descriptionHdr = "Description"
typeHdr = "Type"
pkgHdr = "Device Package"
criticalHdr = "Critical Component"
classHdr = "Classification"
manufacturerHdr = "Manufacturer"
partNoHdr = "Manufacturer P/N"
qtyHdr = "Qty"
designatorHdr = "Designator"
unitPriceHdr = "U/P RMB W/O VAT"
featureHdr = "Feature"
boardHdr = "Board"

# strings to look for when searching for the bom header
header_search_string_list = [designatorHdr, manufacturerHdr, qtyHdr]

cost_walk_header_list_v2 = [itemHdr, designatorHdr, componentHdr, descriptionHdr,
                            manufacturerHdr, partNoHdr, qtyHdr, unitPriceHdr, typeHdr]

cost_walk_header_list_v3 = [itemHdr, designatorHdr, componentHdr, descriptionHdr,
                            manufacturerHdr, partNoHdr, qtyHdr, unitPriceHdr, pkgHdr]

cbom_header_list_v2 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       criticalHdr, manufacturerHdr, partNoHdr, unitPriceHdr, typeHdr]

ebom_header_list_v2 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       criticalHdr, manufacturerHdr, partNoHdr, typeHdr]

cbom_header_list_v3 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       classHdr, manufacturerHdr, partNoHdr, unitPriceHdr, pkgHdr]

ebom_header_list_v3 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       classHdr, manufacturerHdr, partNoHdr, pkgHdr]

# Dictionary of component type reference strings (case-insensitive) and normalized stella component type names.
component_dict = {
    # list based on db template
    "Battery Terminals": [
        "Battery Terminals"],
    "Buzzer": [
        "Buzzer", "Speaker"],
    "Cable": [
        "Cable"],
    "Capacitor": [
        "Capacitor", "Electrolytic Capacitor", "Disc Ceramic Capacitor", "Capartion",
        "X1 Cap", "X1 Capacitor", "X1 Capacitance",
        "X2 Cap", "X2 Capacitor", "X2 Capacitance",
        "Y1 Cap", "Y1 Capacitor", "Y1 Capacitance",
        "Y2 Cap", "Y2 Capacitor", "Y2 Capacitance"],
    "Connector": [
        "Connector", "PCB Tab", "Quick fit terminal", "Plug piece terminal"],
    "Crystal": [
        "Crystal"],
    "Diode": [
        "Diode", "Switching diode", "Rectifier Bridge", "Bridge Rectifiers", "FRD", "Rectifier",
        "TVS", "Zener", "Zener Diode", "Bridge Rectifier", "Rectifier Diode", "Schottky", "Schottky Diode",
        "IR Receiver"],
    "Electromagnet": [
        "Electromagnet"],
    "Foam": [
        "Foam"],
    "FUSE": [
        "FUSE"],
    "Heatsink": [
        "Heatsink"],
    "IC": [
        "IC", "Operational amplifier"],
    "Inductor": [
        "Inductor", "Common mode choke", "Choke"],
    "Jumper": [
        "Jumper"],
    "LCD": [
        "LCD"],
    "LED": [
        "LED", "LED Module"],
    "MCU": [
        "MCU"],
    "MOV/Varistor": [
        "MOV/Varistor", "MOV", "Varistor"],
    "Optocoupler": [
        "Optocoupler"],
    "PCB": [
        "PCB"],
    "Relay": [
        "Relay"],
    "Resistor": [
        "Resistor", "Wire wound resistor", "Wire wound non flame resistor"],
    "Sensor": [
        "Sensor"],
    "Spring": [
        "Spring", "Touch spring"],
    "Switch": [
        "Switch", "Tact Switch", "Slide Switch"],
    "TCO": [
        "TCO"],
    "Thermistors": [
        "Thermistors", "NTC"],
    "Transformer": [
        "Transformer"],
    "Transistor": [
        "Transistor", "BJT", "MOS", "Mosfet", "N-CH", "P-CH", "PNP Transistor", "NPN Transistor"],
    "Triac/SCR": [
        "Triac/SCR", "Triac", "SCR"],
    "Unknown/Misc": [
        "Unknown/Misc", "Unknown", "Misc"],
    "Voltage Regulator": [
        "Voltage Regulator", "Regulator", "LDO", "three-terminal adjustable regulator"],
    "Wire": [
        "Wire"],
    # list based on test data
    "Chimney": [
        "Chimney"],
    "Heat Shrink": [
        "Heat Shrink", "Heat Shrink Tubing"],
    "Heat Sink": [
        "Heat Sink"],
    "Lens": [
        "Lens"],
    "Screw": [
        "Screw"]
}

# List of strings to determine which rows to delete based on string match with description header
unwanted_db_ebom_description_list = [
    "Glue", "Solder", "Compound", "Conformal", "Coating", "Screw"]

# List of strings to determine which rows to delete based on string match with description header
unwanted_db_cbom_description_list = [
    "Glue", "Solder", "Compound", "Conformal", "Coating", "Screw"]

# List of strings to determine which rows to delete based on string match with component type
unwanted_db_ebom_component_list = [
    "PCB", "Wire", "Lens", "Chimney", "Heat Shrink", "Screw"]

# List of strings to determine which rows to delete based on string match with component type
unwanted_db_cbom_component_list = [
    "Wire", "Lens", "Chimney", "Heat Shrink", "Screw"]


def search_and_set_bom_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    Search and set header for bom.

    Args:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The modified DataFrame with rows dropped.
    """

    # user interface message
    print()
    print("Searching for bom header row... ")

    # search for header row
    header_row = header.search_row_matching_header(df, header_search_string_list)

    # drop rows above the row containing the match
    df.drop(index=df.index[:header_row], inplace=True)

    # reset the row index
    df = df.reset_index(drop=True)

    # set top row as header
    df = header.set_top_row_as_header(df)

    # user interface message
    print(f'Bom header data found in row {header_row + 1}.')

    return df


def get_bom_template_version(df: pd.DataFrame, enum_bom_temp_version: Type[BomTempVer]) -> BomTempVer:
    # user interface message
    print()
    print("Determining BOM template version... ")

    # determine the BOM template version
    if criticalHdr in df.columns:
        bom_temp_ver = enum_bom_temp_version.v2
    elif classHdr in df.columns:
        bom_temp_ver = enum_bom_temp_version.v3
    else:
        raise ValueError("This application can only process data for BOM template version 2.0 and 3.0")

    # user interface message
    print(f"BOM template version = {bom_temp_ver}")

    return bom_temp_ver


def get_source_bom_header_labels(
        bom_temp_ver: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        source_file_type: SourceFileType,
        enum_source_file_type: Type[SourceFileType]) -> list[str]:
    # user interface message
    print()
    print("Determining source file BOM header format... ")

    source_bom_header_labels = []

    # Determine the BOM template version
    if bom_temp_ver == enum_bom_temp_version.v2:
        if source_file_type == enum_source_file_type.EB:
            source_bom_header_labels = ebom_header_list_v2
        elif source_file_type == enum_source_file_type.CB:
            source_bom_header_labels = cbom_header_list_v2
    elif bom_temp_ver == enum_bom_temp_version.v3:
        if source_file_type == enum_source_file_type.EB:
            source_bom_header_labels = ebom_header_list_v3
        elif source_file_type == enum_source_file_type.CB:
            source_bom_header_labels = cbom_header_list_v3

    if not source_bom_header_labels:
        raise ValueError(f"Application was not able to determine the source bom header. "
                         f"BOM template = {bom_temp_ver}. Source BOM type = {source_file_type}")

    # User interface message
    print(f"Source file BOM header format = {source_bom_header_labels}")

    return source_bom_header_labels


def get_output_bom_header_labels(
        bom_temp_ver: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        output_file_type: OutputFileType,
        enum_output_file_type: Type[OutputFileType]) -> list[str]:
    # user interface message
    print()
    print("Determining output file BOM header labels... ")

    output_bom_header_labels = []

    if bom_temp_ver == enum_bom_temp_version.v2:
        if output_file_type == enum_output_file_type.CW:
            output_bom_header_labels = cost_walk_header_list_v2
        elif output_file_type == enum_output_file_type.dB_CB:
            output_bom_header_labels = cbom_header_list_v2
        elif output_file_type == enum_output_file_type.db_EB:
            output_bom_header_labels = ebom_header_list_v2

    elif bom_temp_ver == enum_bom_temp_version.v3:
        if output_file_type == enum_output_file_type.CW:
            output_bom_header_labels = cost_walk_header_list_v3
        elif output_file_type == enum_output_file_type.dB_CB:
            output_bom_header_labels = cbom_header_list_v3
        elif output_file_type == enum_output_file_type.db_EB:
            output_bom_header_labels = ebom_header_list_v3

    if not output_bom_header_labels:
        raise ValueError(f"Application was not able to determine the source bom header. "
                         f"BOM template = '{bom_temp_ver}'. Output data format = '{output_file_type}'")

    # user interface message
    print(f"Output BOM header = {output_bom_header_labels}")

    return output_bom_header_labels


def delete_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete rows containing either NaN values or empty strings from a pandas DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to delete empty rows.

    Returns:
    pandas.DataFrame: DataFrame with rows containing NaN values or empty strings removed.
    """

    # user interface message
    print()
    print('Deleting empty rows... ')

    # Drop rows with all NaN values
    mdf = df.dropna(axis=0, how='all')

    # Drop rows with all empty strings
    mdf = mdf.replace('', pd.NA).dropna(axis=0, how='all')

    rows_before = df.shape[0]
    rows_after = mdf.shape[0]
    print(f"Number of rows reduced from {rows_before} to {rows_after}")

    return mdf


def delete_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete columns containing either NaN values or empty strings from a pandas DataFrame.

    Parameters:
    dataframe (pandas.DataFrame): The DataFrame from which to delete empty columns.

    Returns:
    pandas.DataFrame: DataFrame with columns containing NaN values or empty strings removed.
    """
    # message
    print()
    print('Deleting empty columns... ')

    # Drop columns with all NaN values
    mdf = df.dropna(axis=1, how='all')

    # Drop columns with all empty strings
    mdf = mdf.replace('', pd.NA).dropna(axis=1, how='all')

    # user interface message
    columns_before = df.shape[1]
    columns_after = mdf.shape[1]
    print(f"Number of columns reduced from {columns_before} to {columns_after}")

    return df


def set_bom_column_datatype(df: pd.DataFrame) -> pd.DataFrame:
    # By default, all columns of data are treated as string
    df = df.astype(str)

    # panda dataframe places a 'nan' for empty cells. When converted to string we end up with 'nan' string
    # this should be removed and replaced with an empty cell
    df = df.replace("nan", "")

    # items column data contains numbers. It may be decimal data so convert to float.
    df[itemHdr] = df[itemHdr].replace("", 0)  # empty cells are treated as zeros
    df[itemHdr] = df[itemHdr].astype(float)

    # qty column data contains numbers. It will contain some decimal data (like glue qty) so convert to float.
    df[qtyHdr] = df[qtyHdr].replace("", 0)  # empty cells are treated as zeros
    df[qtyHdr] = df[qtyHdr].astype(float)

    # EBOMs do not contain unit price data
    if unitPriceHdr in df.columns:
        # unit price column data contains numbers. It will be decimal data so convert to float.
        df[unitPriceHdr] = df[unitPriceHdr].replace("", 0)  # empty cells are treated as zeros
        df[unitPriceHdr] = df[unitPriceHdr].astype(float)

    return df


def split_manufacturers_to_separate_rows(
        original_df: pd.DataFrame,
        bom_template_version: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        source_file_type: SourceFileType,
        enum_source_file_type: Type[SourceFileType]) -> pd.DataFrame:
    """
    Split manufacturer names and corresponding part numbers to separate rows in the DataFrame.

    Args:
    original_df (DataFrame): The original DataFrame containing manufacturer names and part numbers.

    Returns:
    DataFrame: Updated DataFrame with each manufacturer name and part number in separate rows.

    Raises:
    ValueError: If there are multiple or no columns matching the reference strings for manufacturer name or part number.
                If the number of manufacturer names does not match the number of part numbers.
                If an error is detected in the data during processing.
    """
    # message
    print()
    print('Separating manufacturer names to separate rows...')

    # local variables
    exception_list = []

    # List of component type that do not need to be split
    if bom_template_version == enum_bom_temp_version.v2:
        exception_list = ["Res", "Cap", "Ind"]
    elif bom_template_version == enum_bom_temp_version.v3:
        exception_list = []  # for version 3.0 we separate all alternatives

    # Get the index of manufacturer name column
    name_index = columns.get_single_header_index(original_df, 'Manufacturer', True)

    # Get the index of component header
    component_index = columns.get_single_header_index(original_df, 'Component', True)

    # Get the index of the part number column
    part_number_index = columns.get_single_header_index(original_df, 'P/N', False)

    # Get the index of the quantity column
    qty_index = columns.get_single_header_index(original_df, 'Qty', False)

    # Get the index of the price column
    if source_file_type == enum_source_file_type.CB:
        price_index = columns.get_single_header_index(original_df, 'U/P RMB W/O VAT', False)
    else:
        price_index = 0

    # Get the index of the description column
    description_index = columns.get_single_header_index(original_df, 'Description', False)

    # Create an empty data frame with same header
    updated_df = pd.DataFrame(columns=original_df.columns)

    # read each row on at a time
    for index, row in original_df.iterrows():
        # get values we need
        component_string = row.iloc[component_index]
        name_string = row.iloc[name_index]
        description_string = row.iloc[description_index]
        # part number may be all numbers so force data to string
        part_number_string = str(row.iloc[part_number_index])
        name_list = name_string.split('\n')
        part_number_list = part_number_string.split('\n')
        description_list = description_string.split('\n')
        # remove any "" items from the list.
        name_list = [item for item in name_list if item != ""]
        part_number_list = [item for item in part_number_list if item != ""]
        description_list = [item for item in description_list if item != ""]

        # number of manufacturer names must be the same as manufacturer part numbers
        if len(name_list) != len(part_number_list):
            if len(part_number_list) == 1:
                for i in range(len(name_list)):
                    part_number_list.append(part_number_list[0])
            else:
                print("*** ERROR *** ")
                print("Number of part numbers must be one or the same as number of manufacturers")
                print(f"{len(name_list)} Manufacturer names {name_list}")
                print(f"{len(part_number_list)} Manufacturer part numbers {part_number_list}")
                print("Please fix the source data file and retry")
                exit()

        # when component name is exception list we don't split the row
        split_flag = True
        for reference_string in exception_list:
            if reference_string.lower() in component_string.lower():
                split_flag = False

        # When we want to split, split the manufacturer names and part numbers into separate rows
        if not split_flag:
            updated_df.loc[len(updated_df)] = row
        else:
            for i in range(len(name_list)):
                new_row = row.copy()
                new_row.iloc[name_index] = name_list[i]
                new_row.iloc[part_number_index] = part_number_list[i]
                new_row.iloc[description_index] = description_list[i]
                # Except for first occurrence, all other rows have zero quantity
                if i != 0:
                    new_row.iloc[qty_index] = 0
                # If version 3.0, set price to 0 for all rows except the first
                if bom_template_version == 3.0 and i != 0:
                    new_row.iloc[price_index] = 0
                if bom_template_version == 3.0:
                    new_row.iloc[description_index] = description_list[i]
                # add row to updated data frame
                updated_df.loc[len(updated_df)] = new_row

    # user interface message
    original_row_count = original_df.shape[0]
    updated_row_count = updated_df.shape[0]

    print(f"Number of row in the BOM increased from {original_row_count} to {updated_row_count}")

    return updated_df


def check_qty_matched_ref_des_count(df):
    """
    Check if the quantity matches the number of reference designators for each item in the DataFrame.

    Parameters:
    - df: pandas DataFrame
        The DataFrame containing the data to be checked.

    Raises:
    - ValueError: If the quantity does not match the number of reference designators for any item.
        This can occur if:
        - More than one column matches the reference string 'Qty'.
        - No column matches the reference string 'Qty'.
        - More than one column matches the designator column search string 'Designator'.
        - No column matches the designator column search string 'Designator'.
        - Quantity does not match the number of reference designators for any item.

    Returns:
    - None: If all checks pass successfully, prints a message indicating that the quantity count matches the number
      of reference designators in all rows of the DataFrame.
    """

    # message
    print()
    print('Checking quantity matches number of reference designators... ')

    # Get quantity column index
    quantity_columns = []
    for index, name in enumerate(list(df.columns)):
        # Looking for an exact match
        if "Qty" == name:
            quantity_columns.append(index)
    # We only expect one match
    if len(quantity_columns) == 1:
        qty_index = quantity_columns[0]  # Select the first matching column
        # print(f"Quantity data found in column ", qty_index)
    elif len(quantity_columns) > 1:
        # Raise an error if more than one column matches
        raise ValueError("More than one column matched the reference string.")
    else:
        # Raise an error if no column match
        raise ValueError("No partial match found in the header.")

    # Get reference designator column index
    designator_columns = []
    for index, name in enumerate(list(df.columns)):
        # looking for partial match
        if "Designator" in name:
            designator_columns.append(index)
    # We only expect one match
    if len(designator_columns) == 1:
        designator_index = designator_columns[0]  # Select the first matching column
        # print(f"Designator data found in column ", designator_index)
    elif len(designator_columns) > 1:
        # Raise an error if more than one column matches
        raise ValueError("More than one column matched the designator column search.")
    else:
        # Raise an error if no partial match is found
        raise ValueError("Designator column not found.")

    # Get one row at a time
    for _, row in df.iterrows():
        # get the quantity
        count_of_quantity = row.iloc[qty_index]
        # Count the number of reference designators
        designator_string = row.iloc[designator_index]
        count_of_designator = len(designator_string.split(','))
        # raise an error when counts don't match
        if count_of_designator != count_of_quantity:
            print(f"Quantity does not match number of designators for item {row.iloc[0]}")
            print('Fix input data file and try again')
            exit()

    # Message
    print(f'Quantity count matches number of reference designators in all {df.shape[0]} rows')


def normalize_component_type_label(df):
    import strings

    # message
    print()
    print('Refactoring component column data... ')

    # Get component type column
    matching_columns = []
    for index, name in enumerate(list(df.columns)):
        if "Component" in name:
            matching_columns.append(index)
            break  # pick the first one

    # We only expect one match
    if len(matching_columns) == 1:
        type_index = matching_columns[0]  # Select the first matching column
        # print(f"Manufacturer name found in column =", type_index)
    elif len(matching_columns) > 1:
        raise ValueError(
            "More than one column matched the reference string.")  # Raise an error if more than one column matches
    else:
        raise ValueError("No partial match found in the header.")  # Raise an error if no partial match is found

    # Create an empty DataFrame to store the updated rows
    updated_df = pd.DataFrame(columns=df.columns)

    # Get one row at a time
    count = 0
    key_count = 0
    for _, row in df.iterrows():
        # Get component type
        component_type_name = row.iloc[type_index]
        # ignore SMD, DIP if found in component type name as they add not value
        component_string = component_type_name.replace("SMD", "").replace("DIP", "").replace("ALT", "")
        # Get all values from the component dict
        value_list = [value for sublist in component_dict.values() for value in sublist]
        # Get the best matched value
        value_match1 = strings.find_best_match_jaccard(component_string, value_list)
        value_match2 = strings.find_best_match_levenshtein(component_string, value_list)
        key_match = "*" + component_type_name
        if value_match1 == value_match2:
            # for debug keep track of number of items changed
            count += 1
            # Get the key of the matched value
            for key, values in component_dict.items():
                if value_match1 in values:
                    key_match = key
                    key_count += 1
                    # raise exception when multiple keys are found
                    try:
                        key_count > 1
                    except Exception as e:
                        raise ValueError(f"Multiple component match found for {component_type_name}.", e)
        # replace the component type name in the row
        row.iloc[type_index] = key_match

        # add row to updated data frame
        updated_df.loc[len(updated_df)] = row
        # debug message
        print(f'{component_type_name:30} -> {key_match:30} [{value_match1}/{value_match2}]')

    # message for how many rows changed
    print(f"{count} rows updated")

    return updated_df


def drop_rows_with_unwanted_ebom_items(df):
    # message
    print()
    print('Removing unwanted electrical bill of material rows... ')

    # List of strings to determine which rows to delete based on string match with description header
    unwanted_description_strings_list = ["Glue", "Solder", "Compound", "Conformal", "Coating", "Screw", "Wire", "AWG"]

    # Get the index of description column
    description_index = columns.get_single_header_index(df, 'Description', True)

    # Remove unwanted description rows
    updated_df = rows.delete_row_when_element_contains_string(df, description_index, unwanted_description_strings_list)

    # List of strings to determine which rows to delete based on string match with component header
    unwanted_component_strings_list = ["PCB", "Wire"]

    # Get the index of component column
    component_index = columns.get_single_header_index(updated_df, 'Component', True)

    # Remove unwanted description rows
    updated_df = rows.delete_row_when_element_contains_string(updated_df,
                                                              component_index, unwanted_component_strings_list)

    return updated_df


def remove_part_number_from_description(data_frame):
    # message
    print()
    print('Removing part numbers from description... ')

    # Get the index of the part number column
    part_number_index = columns.get_single_header_index(data_frame, 'P/N', False)

    # Get the index of description column
    description_index = columns.get_single_header_index(data_frame, 'Description', True)

    mdf = columns.refactor_string_if_matched(data_frame, part_number_index, description_index)

    # remove duplicate, starting and trailing comma that may be left after part number is removed from description
    mdf[descriptionHdr] = mdf[descriptionHdr].str.lstrip(',')
    mdf[descriptionHdr] = mdf[descriptionHdr].str.rstrip(',')
    mdf[descriptionHdr] = mdf[descriptionHdr].str.replace(r',{2,}', ',', regex=True)

    return data_frame


def primary_above_alternative(df: pd.DataFrame,
                              bom_template_version: BomTempVer,
                              enum_bom_temp_version: Type[BomTempVer]) -> pd.DataFrame:
    """
    Move primary component above alternatives based on quantity.
    After adding a row to the top, swap the first and second rows for `pkgHdr`, `itemHdr`, and `componentHdr`.

    The primary component (non-zero quantity) is moved to the top of each part group, followed by its alternatives.

    Args:
        enum_bom_temp_version:
        bom_template_version:
        df (DataFrame): The input DataFrame to process.

    Returns:
        mdf (DataFrame): The modified DataFrame with primary components above alternatives.
    """
    print()
    print('Moving primary item above alternative items...')

    # Initialize an empty DataFrame to collect rows (df_temp)
    df_temp = pd.DataFrame(columns=df.columns)
    mdf = pd.DataFrame(columns=df.columns)

    # Not required for template version 2.0
    if bom_template_version == enum_bom_temp_version.v2:
        mdf = df

    # Only needed for template version 3.0
    elif bom_template_version == enum_bom_temp_version.v3:

        # Read each row one at a time
        for _, row in df.iterrows():
            # If df_temp is not empty, check for designator change or empty designatorHdr
            if (not df_temp.empty and (df_temp[designatorHdr].iloc[0] != row[designatorHdr])) or row[
                designatorHdr] == "":
                # Merge current df_temp into mdf
                mdf = pd.concat([mdf, df_temp], axis=0, ignore_index=True)
                # Reset df_temp for the next part group
                df_temp = pd.DataFrame(columns=df.columns)

            # If row quantity is non-zero, move it to the top of the current group
            if row[qtyHdr] != 0:
                # Add row to the top of df_temp
                df_temp = pd.concat([pd.DataFrame(row).T, df_temp], axis=0, ignore_index=True)

                # After adding to the top, check if we have at least two rows to swap
                if len(df_temp) > 1:
                    # Select columns to swap
                    cols_to_swap = [pkgHdr, itemHdr, componentHdr]

                    # Swap values between the first and second rows for the selected columns
                    df_temp.loc[0, cols_to_swap], df_temp.loc[1, cols_to_swap] = \
                        df_temp.loc[1, cols_to_swap].values, df_temp.loc[0, cols_to_swap].values
            else:
                # Move row to the bottom of the current group if quantity is zero
                df_temp = pd.concat([df_temp, pd.DataFrame(row).T], axis=0, ignore_index=True)

        # After the last group, merge the remaining df_temp into mdf
        if not df_temp.empty:
            mdf = pd.concat([mdf, df_temp], axis=0, ignore_index=True)

    # User interface message
    print("Done")

    return mdf


def fill_merged_designators(df: pd.DataFrame,
                              bom_template_version: BomTempVer,
                              enum_bom_temp_version: Type[BomTempVer]) -> pd.DataFrame:
    print()
    print('Fill in designators when designator cells are merged in excel BOM... ')

    # Not required for template version 2.0
    if bom_template_version == enum_bom_temp_version.v2:
        pass

    # Only needed for template version 3.0
    elif bom_template_version == enum_bom_temp_version.v3:
        # Iterate over the rows of the DataFrame
        for n in range(1, len(df)):  # Start from index 1 to avoid IndexError on n-1
            # Check if the designator is empty in the current row
            if not df.loc[n, designatorHdr]:
                # Check if the description matches with the previous row
                if df.loc[n, descriptionHdr] == df.loc[n - 1, descriptionHdr]:
                    # Copy the designator from the previous row
                    df.loc[n, designatorHdr] = df.loc[n - 1, designatorHdr]

    # User interface message
    print("Done")
    return df


def merge_alternative(df_in):
    """
    merge alternative items with primary item row using "/n" delimiter.

    This is done to allow CBOM version 3.0 to work with application designed for CBOM template version 2.0.
    We merge data so CBOM version 3.0 looks like CBOM version 2.0 and then split it later

    """
    # message
    print()
    print('Merging alternatives items with primary item...')

    # Reference string to detect alternative item row
    alt_ref_string = "ALT"

    # Initialize variables to store previous primary item values
    prev_desc = ''
    prev_mfg = ''
    prev_pn = ''

    # Create an empty data frame with same header
    df_out = pd.DataFrame(columns=df_in.columns)
    df_merger = df_out

    # read each row on at a time
    for _, row in df_in.iterrows():

        if alt_ref_string not in row[componentHdr]:

            # first time around no need to concat as there is no data
            if len(df_merger) != 0:
                df_out = pd.concat([df_out, pd.DataFrame(df_merger).T], axis=0, ignore_index=True)
            df_merger = row
            prev_desc = row[designatorHdr]
            prev_mfg = row[manufacturerHdr]
            prev_pn = row[partNoHdr]
        else:
            if row[descriptionHdr]:
                df_merger[descriptionHdr] += "\n" + row[descriptionHdr]
            else:
                df_merger[descriptionHdr] += "\n" + prev_desc

            if row[manufacturerHdr]:
                df_merger[manufacturerHdr] += "\n" + row[manufacturerHdr]
            else:
                df_merger[manufacturerHdr] += "\n" + prev_mfg

            if row[partNoHdr]:
                df_merger[partNoHdr] += "\n" + row[partNoHdr]
            else:
                df_merger[partNoHdr] += "\n" + prev_pn

    # last row merger needs to be done outside the for loop
    df_out = pd.concat([df_out, pd.DataFrame(df_merger).T], axis=0, ignore_index=True)

    # user interface message
    print(f"Number of row in the BOM changed from {df_in.shape[0]} to {df_out.shape[0]}")

    return df_out


def merge_type_data_with_description(df: pd.DataFrame, bom_template_version: BomTempVer):
    # message
    print()
    print('Merging type column data with description column data... ')

    # local variables
    part_number_index = -1

    # Get the index of the type column
    if bom_template_version == BomTempVer.v2:
        part_number_index = columns.get_single_header_index(df, typeHdr, True)
    elif bom_template_version == BomTempVer.v3:
        part_number_index = columns.get_single_header_index(df, pkgHdr, True)

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    df = rows.merge_row_data_when_no_found(df, part_number_index, description_index)

    return df


def select_build(df: pd.DataFrame) -> pd.DataFrame:
    # get all the build names for which data is available in the dataframe
    build_dict = rows.get_build_name_and_column(df)

    # delete column when it has unwanted build data
    df = columns.delete_columns_with_unwanted_build_data(df, build_dict)

    return df


def split_multiple_quantity(data_frame: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Splitting multiple quantity to separate rows... ')

    # keep tack of total rows before clean up
    original_row_count = data_frame.shape[0]

    # duplicate rows till qty is less than one while splitting ref des
    data_frame = rows.duplicate_row_for_multiple_quantity(data_frame)

    # user interface message
    updated_row_count = data_frame.shape[0]
    print(f"Number of rows increased from {original_row_count} to {updated_row_count}")

    return data_frame


def get_bom_columns(df: pd.DataFrame, source_bom_header: list[str]) -> pd.DataFrame:
    # user interface message
    print()
    print('Extracting BOM columns... ')

    mdf = header.standardize_header_names(df, source_bom_header)

    # Reorder header based on list and drop remaining columns
    mdf = mdf[source_bom_header]

    # user interface message
    header_strings = ", ".join(mdf.columns)
    print(f'Columns are [{header_strings}]')

    return mdf


def cleanup_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up description column data... ')

    # remove duplicate spaces
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[^\S\r\n]+', ' ', regex=True)

    # special 'characters' cases...
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[，]', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[（]', '(', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[）]', ')', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[；]', ';', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[：]', ':', regex=True)

    # sometimes data is semi-colon separated
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[;]', ',', regex=True)

    # multiple comma, space before and after a comma are replaced by just a comma
    df[descriptionHdr] = df[descriptionHdr].str.replace(r',{2,}', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r' ,', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r', ', ',', regex=True)

    # remove starting and trailing comma
    df[descriptionHdr] = df[descriptionHdr].str.lstrip(',')
    df[descriptionHdr] = df[descriptionHdr].str.rstrip(',')

    # remove starting and trailing space
    df[descriptionHdr] = df[descriptionHdr].str.lstrip(' ')
    df[descriptionHdr] = df[descriptionHdr].str.rstrip(' ')

    print('Done.')

    return df


def cleanup_designators(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up designator column data... ')

    # remove spaces
    df[designatorHdr] = df[designatorHdr].str.replace(r'\s+', '', regex=True)

    # replace special characters used to separate designators by comma
    df[designatorHdr] = df[designatorHdr].str.replace(r'[:;、\'，]', ',', regex=True)

    # replace duplicate commas by one comma
    df[designatorHdr] = df[designatorHdr].str.replace(r',{2,}', ',', regex=True)

    # remove starting and trailing comma
    df[designatorHdr] = df[designatorHdr].str.lstrip(',')
    df[designatorHdr] = df[designatorHdr].str.rstrip(',')

    print('Done.')

    return df


def cleanup_manufacturer(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up manufacturer column data... ')

    # special case when start is with MFG or Manufacturer case-insensitive
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MANUFACTURER', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MANU', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MFG', ' ', regex=True)

    # replace ".," with space. Special case for "Co.,Ltd" to "Co Ltd"
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'.,', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'.，', ' ', regex=True)

    # replace colon and dot with space
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'[:.]', ' ', regex=True)

    # remove starting and trailing space
    df[manufacturerHdr] = df[manufacturerHdr].str.lstrip(' ')
    df[manufacturerHdr] = df[manufacturerHdr].str.rstrip(' ')

    # elements are comma separated
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'\n', ',', regex=True)

    # remove duplicate spaces
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r' {2,}', ' ', regex=True)
    # replace duplicate commas by one comma
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r',{2,}', ',', regex=True)

    print('Done.')

    return df


def cleanup_part_number(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up part number column data... ')

    # remove duplicate spaces
    df[partNoHdr] = df[partNoHdr].str.replace(r' {2,}', ' ', regex=True)

    # elements are comma separated
    df[partNoHdr] = df[partNoHdr].str.replace(r'\n', ',', regex=True)

    print('Done.')

    return df


def drop_unwanted_db_ebom_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted eBOM description items... ')

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    # delete row when the description is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, description_index, unwanted_db_ebom_description_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_cbom_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted cbom description...')

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    # delete row when the description is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, description_index, unwanted_db_cbom_description_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_ebom_component(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted ebom component... ')

    # Get the index of component column
    component_index = columns.get_single_header_index(df, componentHdr, True)

    # delete row when the component is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, component_index, unwanted_db_ebom_component_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_cbom_component(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted cbom components... ')

    # Get the index of component column
    component_index = columns.get_single_header_index(df, componentHdr, True)

    # delete row when the component is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, component_index, unwanted_db_cbom_component_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_item_with_zero_quantity(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with zero quantity... ')

    # delete row when quantity is zero
    mdf = rows.delete_row_when_element_zero(df, qtyHdr)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_item_with_quantity_less_than_one(df: pd.DataFrame) -> pd.DataFrame:
    threshold = 1

    # user interface message
    print()
    print(f'Removing items with quantity less than {threshold}... ')

    # delete row when quantity is less than one
    mdf = rows.delete_row_when_element_less_than_threshold(df, qtyHdr, threshold)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_items_with_empty_designator(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with empty designator.... ')

    # delete row when designator is empty
    mdf = df[df[designatorHdr] != ""]

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf
