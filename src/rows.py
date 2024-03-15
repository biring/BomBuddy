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

