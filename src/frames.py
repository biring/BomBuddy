# This file has functions to manipulate both rows and columns in a data frame
import pandas as pd

import columns
import rows


def drop_rows_above_string_match(df, string):
    """
    Drops rows above the row containing an element that matches the specified string.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        string (str): The string to match.

    Returns:
        pandas.DataFrame: The modified DataFrame with rows dropped.
    """
    # Flag to indicate if a match has been found
    found_match = False
    rows_removed = 0

    # Iterate over rows of the DataFrame
    for index, row in df.iterrows():
        # Check if the string is present in any cell of the current row
        if string in row.values:
            found_match = True
            rows_removed = index
            break

    # If no match is found, print a message and exit
    if not found_match:
        print("No row matches the provided string.")
        exit()

    # Print message indicating the number of rows removed above the match
    print(f"Removed {rows_removed} row(s) above the row containing the match.")

    # Drop rows above the row containing the match
    df.drop(index=df.index[:rows_removed], inplace=True)

    # Reset the row index
    df = df.reset_index(drop=True)
    return df


def delete_empty_rows(df):
    """
    Delete rows containing either NaN values or empty strings from a pandas DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to delete empty rows.

    Returns:
    pandas.DataFrame: DataFrame with rows containing NaN values or empty strings removed.
    """
    # Drop rows with all NaN values
    df_cleaned = df.dropna(axis=0, how='all')

    # Drop rows with all empty strings
    df_cleaned = df_cleaned.replace('', pd.NA).dropna(axis=0, how='all')

    return df_cleaned


def delete_empty_rows_columns(dataframe):
    """
    Delete rows or columns containing only NaN values and/or empty strings.

    Parameters:
    dataframe (pandas.DataFrame): Input DataFrame.

    Returns:
    pandas.DataFrame: DataFrame with empty rows or columns removed.
    """
    # Count empty rows before deletion
    empty_rows_before = dataframe.shape[0] - dataframe.dropna(how='all').shape[0]

    # Count empty columns before deletion
    empty_columns_before = dataframe.shape[1] - dataframe.dropna(how='all', axis=1).shape[1]

    # Remove empty rows
    dataframe = dataframe.replace('', float('nan')).dropna(how='all', axis=0)

    # Remove empty columns
    dataframe = dataframe.replace('', float('nan')).dropna(how='all', axis=1)

    # Count empty rows after deletion
    empty_rows_after = dataframe.shape[0] - dataframe.dropna(how='all').shape[0]

    # Count empty columns after deletion
    empty_columns_after = dataframe.shape[1] - dataframe.dropna(how='all', axis=1).shape[1]

    # Print messages for the number of empty rows and columns deleted
    print(f"Deleted {empty_rows_before - empty_rows_after} empty rows and "
          f"{empty_columns_before - empty_columns_after} empty columns.")
    return dataframe


def set_top_row_as_header(df):
    """
    Takes the top row of a DataFrame and sets it as the header.
    Removes the top row from the DataFrame after setting it as the header.

    Args:
    - df (pandas.DataFrame): The DataFrame containing tabular data.

    Returns:
    - pandas.DataFrame: The modified DataFrame with the header set and the top row removed.
    """
    header = df.iloc[0]  # Extract the top row as header
    modified_df = df[1:]  # Remove the top row
    modified_df.columns = header  # Set the header

    return modified_df


def drop_rows_below_threshold_for_column(df, reference_string, threshold):
    """
    Drop rows from a DataFrame where the value in a column determined by the specified string in the header is below a certain threshold.

    Parameters:
    - df (pandas DataFrame): The DataFrame from which rows will be dropped.
    - reference_string (str): The string in the header used to determine the column.
    - threshold (int or float): The threshold value. Rows with values below this threshold will be dropped.

    Returns:
    - df_dropped (pandas DataFrame): A DataFrame with rows dropped where the specified column's value is below the threshold.
    """
    # List of index that match the header based on the reference string in the header
    matching_columns = [i for i, header in enumerate(df.columns) if reference_string in header]

    # We only expect one match
    if len(matching_columns) == 1:
        column_index = matching_columns[0]  # Select the first matching column
        print(f"{reference_string} found in column ", column_index)
    elif len(matching_columns) > 1:
        raise ValueError(
            "More than one column matched the reference string.")  # Raise an error if more than one column matches
    else:
        raise ValueError("No partial match found in the header.")  # Raise an error if no partial match is found

    # Create a mask to identify rows where the value is less than the threshold
    mask = (df.iloc[1:, column_index].astype(float) < threshold)

    # Count the number of rows to be dropped
    count_dropped = mask.sum()

    # Print the count of dropped rows
    print(f"Dropped {count_dropped} row(s) because they were below the {threshold} for {reference_string} column.")

    if count_dropped > 0:
        # Apply the mask and drop rows
        df_dropped = df.loc[~mask]
    else:
        # No rows to drop, return the original DataFrame
        df_dropped = df

    return df_dropped


def keep_partial_matched_columns(df, strings):
    """
    Keep columns in DataFrame `df` that partially match any string in `strings`.

    Parameters:
        df (pandas.DataFrame): The input DataFrame.
        strings (list): List of strings to match against DataFrame columns.

    Returns:
        pandas.DataFrame: DataFrame with only the columns that partially match.

    Raises:
        ValueError: If the number of matched columns is less than the length of the list `strings`.

    Example usage:
        Assuming you have a DataFrame called `data` and a list of strings called `match_strings`
        filtered_data = keep_partial_matched_columns(data, match_strings)
    """
    # Convert the list of strings to lowercase
    strings = [s.lower() for s in strings]

    # Get columns that partially match with any string in the list
    matching_columns = [col for col in df.columns if any(s in col.lower() for s in strings)]

    if len(matching_columns) < len(strings):
        raise ValueError("Number of matched columns is less than the length of the list 'strings'.")

    # Determine the number of columns dropped
    columns_dropped = len(df.columns) - len(matching_columns)

    # Print message for number of columns dropped
    if columns_dropped > 0:
        print(f"Dropped {columns_dropped} columns.")
    else:
        print("No columns dropped.")

    # Print message for number of columns found
    print(f"Found {len(matching_columns)} matching columns.")

    # only keep the partially matched columns
    df = df[matching_columns]

    # print column headers
    header_text = ', '.join(df.columns)
    print(f'Data now only has the following headers = {header_text}')

    # Return DataFrame with matching columns
    return df[matching_columns]


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
        part_number_string = row.iloc[part_number_index]
        name_list = name_string.split('\n')
        part_number_list = part_number_string.split('\n')

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
    print('Refactoring component type labels... ')

    component_dict = {
        "Battery Terminals": "Battery Terminals",
        "Buzzer": "Buzzer",
        "Cable": "Cable",
        "Capacitor": "Capacitor",
        "Connector": "Connector",
        "Crystal": "Crystal",
        "Diode": "Diode",
        "Electromagnet": "Electromagnet",
        "Foam": "Foam",
        "FUSE": "FUSE",
        "Fuse": "FUSE",
        "Heatsink": "Heatsink",
        "IC": "IC",
        "Inductor": "Inductor",
        "IR Receiver": "IR Receiver",
        "Jumper": "Jumper",
        "LCD": "LCD",
        "LED": "LED",
        "LED Module": "LED Module",
        "MCU": "MCU",
        "MOV": "MOV/Varistor",
        "Varistor": "MOV/Varistor",
        "Optocoupler": "Optocoupler",
        "PCB": "PCB",
        "Relay": "Relay",
        "Resistor": "Resistor",
        "Sensor": "Sensor",
        "Spring": "Spring",
        "Switch": "Switch",
        "TCO": "TCO",
        "Thermistors": "Thermistors",
        "Transformer": "Transformer",
        "Transistor": "Transistor",
        "Triac": "Triac/SCR",
        "SCR": "Triac/SCR",
        "Unknown": "Unknown/Misc",
        "Misc": "Unknown/Misc",
        "Voltage Regulator": "Voltage Regulator",
        "Regulator": "Voltage Regulator",
        "Wire": "Wire"
    }

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
    for _, row in df.iterrows():
        # Get component type
        component_type_name = row.iloc[type_index]
        # Get the key list
        keys_list = list(component_dict.keys())
        # Get the best matched key to component type key
        key_match = strings.find_best_match_jaccard(component_type_name, keys_list)
        strings.find_best_match_levenshtein(component_type_name, keys_list)
        # Get the value of the matched key
        value_match = component_dict[key_match]
        # replace the component type name in the row
        row.iloc[type_index] = value_match
        # debug message
        # print(f'{component_type_name} matched with {key_match} so changed to {value_match}')
        # add row to updated data frame
        updated_df.loc[len(updated_df)] = row
        # when data has been updated
        if component_type_name != value_match:
            # for debug keep track of number of items changed
            count += 1

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
    updated_df = rows.remove_rows_containing_string(df, description_index, unwanted_description_strings_list)

    # List of strings to determine which rows to delete based on string match with component header
    unwanted_component_strings_list = ["PCB", "Wire"]

    # Get the index of component column
    component_index = columns.get_single_header_index(updated_df, 'Component', True)

    # Remove unwanted description rows
    updated_df = rows.remove_rows_containing_string(updated_df, component_index, unwanted_component_strings_list)

    return updated_df


def remove_part_number_from_description(data_frame):
    # message
    print()
    print('Removing part numbers from description... ')

    # Get the index of the part number column
    part_number_index = columns.get_single_header_index(data_frame, 'P/N', False)

    # Get the index of description column
    description_index = columns.get_single_header_index(data_frame, 'Description', True)

    data_frame = columns.refactor_string_if_matched(data_frame, part_number_index, description_index)

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
