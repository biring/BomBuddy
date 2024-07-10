import strings
import pandas as pd


def delete_row_when_element_contains_string(original_df, header_index, reference_string_list):
    """
    Removes rows from the DataFrame that contain specified strings in a given column.

    Args:
        original_df (pandas.DataFrame): The original DataFrame.
        header_index (int): Index of the column to check for string matches.
        reference_string_list (list): List of strings to check for in the specified column.

    Returns:
        pandas.DataFrame: Updated DataFrame with rows removed based on the specified criteria.
    """

    # Create an empty DataFrame to store the updated rows
    updated_df = pd.DataFrame(columns=original_df.columns)

    # Get one row at a time
    for _, row in original_df.iterrows():
        # Get string to check
        string_to_check = row.iloc[header_index]
        # Check if string to check is in the reference string list
        match = False
        for reference_string in reference_string_list:
            # Compare in a case-insensitive manner
            if reference_string.lower() in string_to_check.lower():
                match = True
        # only add row if the string to check is not in the reference string list
        if not match:
            updated_df.loc[len(updated_df)] = row

    return updated_df


def merge_row_data_when_no_found(df, source_column, destination_column):
    # Create an empty DataFrame to store the updated rows
    updated_df = pd.DataFrame(columns=df.columns)

    # Debug
    debug_count = 0

    # Get one row at a time
    for index, row in df.iterrows():
        # Get source and destination string
        source_string = str(row.iloc[source_column])
        destination_string = str(row.iloc[destination_column])
        # only merge data when not found
        if source_string.lower() not in destination_string.lower():
            updated_destination_string = destination_string + "," + source_string
            debug_count = debug_count + 1
        else:
            updated_destination_string = destination_string

        # build the updated dataframe
        row.iloc[destination_column] = updated_destination_string
        updated_df.loc[len(updated_df)] = row

    # message for how many rows changed
    print(f"Description of {debug_count} of {df.shape[0]} rows updated")

    return updated_df


def get_build_name_and_column(data_frame: pd.DataFrame) -> dict:
    import re
    # start with empty dict
    build_name_dict = {}

    # Pattern 1: Match strings that consist 1 to 3 alphabets
    pattern1 = r'^[a-zA-Z]{1,3}$'
    # Pattern 2: Match strings that start with an alphabet and end with an integer
    pattern2 = r'^[a-zA-Z].*\d$'
    # Pattern 3: Match strings that start with an alphabet, end with a decimal number,
    # and optionally allow for a decimal point and additional digits after it
    pattern3 = r'^[a-zA-Z].*\d+(\.\d+)?$'
    # Combine the patterns with OR (|) operator
    pattern = f"({'|'.join([pattern1, pattern2, pattern3])})"

    # build name information is found in the top row
    top_row = data_frame.iloc[0]

    # build a dictionary with build names
    for index, value in enumerate(top_row):
        # ignore pandas NaN
        if pd.isna(value):
            continue
        # build name must match the pattern defined above
        if re.match(pattern, str(value)):
            # raise an error when duplicate build name is detected.
            if value in build_name_dict:
                raise ValueError(f"Found duplicate '{value}' value for build name."
                                 f"\nPlease fix data in source file and retry.")
            build_name_dict[value] = index

    # raise an error when no build names are found.
    if len(build_name_dict) == 0:
        raise ValueError("No build name found.")

    return build_name_dict


def delete_empty_zero_rows(df: pd.DataFrame, column_name: str) -> pd.DataFrame:

    # Delete rows with empty values in the specified column
    df = df.dropna(subset=[column_name])
    # Delete rows with zero values in the specified column
    df = df[df[column_name] != 0]

    return df


def duplicate_row_for_multiple_quantity(df: pd.DataFrame) -> pd.DataFrame:

    # Quantity column is integer
    df['Qty'] = df['Qty'].astype(float)

    # Create an empty DataFrame to store the updated rows
    mdf = pd.DataFrame(columns=df.columns)

    for index, old_row in df.iterrows():
        # only split integers when greater than one.
        while old_row['Qty'] > 1 and old_row['Qty'] % 1 == 0:
            ref_des_list = old_row['Designator'].split(',')

            new_row = old_row.copy()
            new_row['Qty'] = 1
            new_row['Designator'] = ref_des_list[0]

            old_row['Qty'] -= 1
            old_row['Designator'] = ','.join(ref_des_list[1:])

            mdf.loc[len(mdf)] = new_row

        mdf.loc[len(mdf)] = old_row

    return mdf


def standardize_component_name(df: pd.DataFrame, component_dict: dict, component_column: int) -> pd.DataFrame:

    # Create an empty DataFrame to store the updated rows
    updated_df = pd.DataFrame(columns=df.columns)

    # Get one row at a time
    count = 0
    for _, row in df.iterrows():
        # Get component type
        component_type_name = row.iloc[component_column]
        # Get the key list
        keys_list = list(component_dict.keys())
        # Get the best matched key using different methods
        key_match_1 = strings.find_best_match_jaccard(component_type_name, keys_list)
        key_match_2 = strings.find_best_match_levenshtein(component_type_name, keys_list)

        # When all the methods give the same result
        if key_match_1 == key_match_2:
            # Get the value of the matched key
            value_match = component_dict[key_match_1]
            # replace the component type name in the row
            row.iloc[component_column] = value_match
            # for debug keep track of number of items changed
            count += 1

        # add row to updated data frame
        updated_df.loc[len(updated_df)] = row

    # message for how many rows changed
    print(f"{count} rows updated")

    return updated_df


def delete_row_when_element_zero(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    # Convert the column to numeric if it's not already numeric
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')

    # Delete rows with zero values in the specified column
    mdf = df[df[column_name] != 0]
    return mdf


def delete_row_when_element_less_than_threshold(df: pd.DataFrame, column: str, threshold: int) -> pd.DataFrame:
    # Convert the column to numeric if it's not already numeric
    df[column] = pd.to_numeric(df[column], errors='coerce')

    # Delete rows with zero values in the specified column
    mdf = df[df[column] >= threshold]
    return mdf


def delete_row_with_empty_element(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    # Delete rows with empty values in the specified column
    mdf = df.dropna(subset=[column_name])
    return mdf
