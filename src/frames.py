# This file has functions to manipulate both rows and columns in a data frame
import pandas as pd

import header
import columns
import rows

# Standardized header names used across eBOM, cBOM and cost walk. They are based off the bom template
itemHdr = "Item"
componentHdr = "Component"
descriptionHdr = "Description"
typeHdr = "Type"
criticalHdr = "Critical Component"
manufacturerHdr = "Manufacturer"
partNoHdr = "Manufacturer P/N"
qtyHdr = "Qty"
designatorHdr = "Designator"
unitPriceHdr = "U/P RMB W/O VAT"
featureHdr = "Feature"
boardHdr = "Board"

# strings to look for when searching for the bom header
header_search_string_list = [designatorHdr, manufacturerHdr, qtyHdr]

cost_walk_header_list = [itemHdr, designatorHdr, componentHdr, typeHdr, descriptionHdr,
                         manufacturerHdr, partNoHdr, qtyHdr, unitPriceHdr]

bom_header_list = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                   criticalHdr, manufacturerHdr, partNoHdr, unitPriceHdr, typeHdr]

# Dictionary of component type reference strings and normalized stella component type names
component_dict = {
    # list based on db template
    "Battery Terminals": [
        "Battery Terminals"],
    "Buzzer": [
        "Buzzer", "Speaker"],
    "Cable": [
        "Cable"],
    "Capacitor": [
        "Capacitor", "Electrolytic Capacitor", "Disc Ceramic Capacitor", "Capartion"],
    "Connector": [
        "Connector", "PCB Tab", "Quick fit terminal", "Plug piece terminal"],
    "Crystal": [
        "Crystal"],
    "Diode": [
        "Diode", "Switching diode", "Rectifier Bridge", "Bridge Rectifiers", "FRD", "Rectifier",
        "TVS", "Zener", "Bridge Rectifier", "Rectifier Diode", "Schottky", "Schottky Diode",
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
        "Inductor"],
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
        "Switch", "Tact Switch"],
    "TCO": [
        "TCO"],
    "Thermistors": [
        "Thermistors", "NTC"],
    "Transformer": [
        "Transformer"],
    "Transistor": [
        "Transistor", "BJT", "MOS", "Mosfet", "N-CH", "P-CH"],
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


def split_manufacturers_to_separate_rows(original_df):
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

    # List of component type that do not need to be split
    exception_list = ["Res", "Cap", "Ind"]

    # Get the index of manufacturer name column
    name_index = columns.get_single_header_index(original_df, 'Manufacturer', True)

    # Get the index of component header
    component_index = columns.get_single_header_index(original_df, 'Component', True)

    # Get the index of the part number column
    part_number_index = columns.get_single_header_index(original_df, 'P/N', False)

    # Get the index of the quantity column
    qty_index = columns.get_single_header_index(original_df, 'Qty', False)

    # Create an empty data frame with same header
    updated_df = pd.DataFrame(columns=original_df.columns)

    # read each row on at a time
    for index, row in original_df.iterrows():
        # get values we need
        component_string = row.iloc[component_index]
        name_string = row.iloc[name_index]
        # part number may be all numbers so force data to string
        part_number_string = str(row.iloc[part_number_index])
        name_list = name_string.split('\n')
        part_number_list = part_number_string.split('\n')
        # remove any "" items from the list.
        name_list = [item for item in name_list if item != ""]
        part_number_list = [item for item in part_number_list if item != ""]

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
                # Except for first occurrence, all other rows have zero quantity
                if i != 0:
                    new_row.iloc[qty_index] = 0
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
    keyCount = 0
    for _, row in df.iterrows():
        # Get component type
        component_type_name = row.iloc[type_index]
        # ignore SMD if found in component column element
        component_string = component_type_name.replace("SMD", "")
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
                    keyCount += 1
                    # raise exception when multiple keys are found
                    try:
                        keyCount > 1
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

    # user interface message
    print(f"Number of rows reduced from {mdf.shape[0]} to {mdf.shape[0]}")

    return data_frame


def merge_type_data_with_description(df):
    # message
    print()
    print('Merging type column data with description column data... ')

    # Get the index of the type column
    part_number_index = columns.get_single_header_index(df, 'Type', True)

    # Get the index of description column
    description_index = columns.get_single_header_index(df, 'Description', True)

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


def extract_cost_walk_columns(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Extracting columns for cost walk...')

    mdf = header.standardize_header_names(df, cost_walk_header_list)

    # Reorder header based on list and drop remaining columns
    mdf = mdf[cost_walk_header_list]

    # user interface message
    header_strings = ", ".join(mdf.columns)
    print(f'Columns header are [{header_strings}]')

    return mdf


def extract_bom_columns(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Extracting columns for bom...')

    mdf = header.standardize_header_names(df, bom_header_list)

    # Reorder header based on list and drop remaining columns
    mdf = mdf[bom_header_list]

    # user interface message
    header_strings = ", ".join(mdf.columns)
    print(f'Columns header are [{header_strings}]')

    return mdf


def cleanup_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up description column data... ')

    # remove duplicate spaces
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'\s+', ' ', regex=True)

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

    # elements are comma separated1
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


def drop_item_with_empty_quantity(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with empty quantity... ')

    # delete row when quantity is empty
    mdf = rows.delete_row_with_empty_element(df, qtyHdr)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_items_with_empty_designator(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with empty designator.... ')

    # delete row when designator is empty
    mdf = rows.delete_row_with_empty_element(df, designatorHdr)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf
