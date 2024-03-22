import pandas as pd


def remove_rows_containing_string(original_df, header_index, reference_string_list):
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

    # message for how many rows changed
    original_row_count = original_df.shape[0]
    updated_row_count = updated_df.shape[0]
    print(f"Number of rows reduced from {original_row_count} to {updated_row_count}"
          f" during '{original_df.columns[header_index].lower()}' column cleanup")

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


def get_build_name_and_index_dict(data_frame: pd.DataFrame) -> dict:
    import re
    # start with empty dict
    buildNameDict = {}

    # Pattern 1: Match strings that consist only 1 to 3 alphabets
    pattern1 = r'^[a-zA-Z]{1,2}$'
    # Pattern 2: Match strings that start with an alphabet and end with an integer
    pattern2 = r'^[a-zA-Z].*\d$'
    # Pattern 3: Match strings that start with an alphabet, end with a decimal number,
    # and optionally allow for a decimal point and additional digits after it
    pattern3 = r'^[a-zA-Z].*\d+(\.\d+)?$'
    # Combine the patterns with OR (|) operator
    pattern = f"({'|'.join([pattern1, pattern2, pattern3])})"

    # build name information is found in the top row
    top_row = data_frame.iloc[0]

    # iterate through each column to find the build name and index
    for index, value in enumerate(top_row):
        # when a build number is found
        if re.match(pattern, str(value)):
            # add it to the dictionary
            buildNameDict[value] = index

    # when dictionary is empty stop the application
    if len(buildNameDict) == 0:
        print("Error. No build name found")
        exit()

    return buildNameDict


def delete_empty_zero_rows(df: pd.DataFrame, column_name: str) -> pd.DataFrame:

    # Delete rows with empty values in the specified column
    df = df.dropna(subset=[column_name])
    # Delete rows with zero values in the specified column
    df = df[df[column_name] != 0]

    return df


def duplicate_row_for_multiple_quantity(df: pd.DataFrame) -> pd.DataFrame:

    # Create an empty DataFrame to store the updated rows
    mdf = pd.DataFrame(columns=df.columns)

    for index, old_row in df.iterrows():
        while old_row['Qty'] > 1:
            ref_des_list = old_row['Designator'].split(',')

            new_row = old_row.copy()
            new_row['Qty'] = 1
            new_row['Designator'] = ref_des_list[0]

            old_row['Qty'] -= 1
            old_row['Designator'] = ','.join(ref_des_list[1:])

            mdf.loc[len(mdf)] = new_row

        mdf.loc[len(mdf)] = old_row

    return mdf

