import pandas as pd


def get_single_header_index(df, reference_string, full_match=True):
    """
    Retrieve the index of a single header in the DataFrame based on a reference string.
    Search is case-insensitive

    Parameters:
    - df (DataFrame): The pandas DataFrame containing the headers.
    - reference_string (str): The string to match against the column headers.
    - full_match (bool): If True, perform a full string match against the header names.
                          If False, allow partial matches.

    Returns:
    - header_index (int): The index of the matched header.

    Raises:
    - ValueError: If no header matches the reference string or if more than one header matches.
    """
    # Get a list of header indices that match the string
    matched_headers_list = []
    for header_index, header_name in enumerate(list(df.columns)):
        if full_match:
            # compare is case-insensitive
            if reference_string.lower() == header_name.lower():
                matched_headers_list.append(header_index)
        else:
            # compare is case-insensitive
            if reference_string.lower() in header_name.lower():
                matched_headers_list.append(header_index)

    # We only expect one match
    if len(matched_headers_list) == 1:
        header_index = matched_headers_list[0]
    # Raise an error if more than one column matches
    elif len(matched_headers_list) > 1:
        raise ValueError("More than one header matched the reference string.")
    # Raise an error if no partial match is found
    else:
        raise ValueError("No header matched the reference string.")

    return header_index


def refactor_string_if_matched(df, pattern_column, data_column):
    count = 0

    # Get one pattern at a time
    for _, row_pattern in df.iterrows():
        pattern = row_pattern.iloc[pattern_column]
        for index, row_data in df.iterrows():
            data = row_data.iloc[data_column]
            result = data.replace(pattern + ",", "")\
                .replace("," + pattern, "").replace(", " + pattern, "")\
                .replace(pattern, "")


            # when data has been updated
            if result != data:
                # for debug keep track of number of items changd
                count += 1
                # print(f'In row {index} found {pattern} in {data} so changed it to {result}')
                # replace the data string
                df.at[index, df.columns[data_column]] = result

    # message for how many rows changed
    print(f"{count} rows updated")

    return df


def remove_unwanted_build_cost_data(df: pd.DataFrame, build_dict: dict) -> pd.DataFrame:

    # Get the value associated with the first key
    first_key = list(build_dict.keys())[0]
    first_value = build_dict[first_key]

    # Create a list of elements that start at zero and go up to the first build colum
    columns_to_keep = list(range(0, first_value))
    # get the key for the build analyse
    selected_index = 0
    if len(build_dict) > 1:
        # prompt user to select a build for analysis
        print()
        print("Data for multiple builds found: ")
        for index, key in enumerate(build_dict, start=1):
            print(f"[{index}]. {key}")
        # Prompt user to select an element by number
        while True:
            try:
                selected_index = int(input("Enter the number corresponding to the build you want to keep: ")) - 1
                # Check if the entered number is within the valid range
                if selected_index < 0 or selected_index >= len(build_dict):
                    print("Invalid element number. Please enter a valid number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    # Get the selected element
    selected_key = list(build_dict.keys())[selected_index]

    start_value = build_dict[selected_key]
    # Generating list with the selected value and the next consecutive five numbers
    columns_to_keep.extend(list(range(start_value, start_value + 6)))

    # Creating a new DataFrame with only the selected columns
    new_df = df[columns_to_keep]

    return new_df


def rename_and_reorder_headers(df: pd.DataFrame, item_list: list) -> pd.DataFrame:

    order_list = []
    for item in item_list:
        ref = item[0]
        match = item[1]
        column_index = get_single_header_index(df, ref, match)
        # New header name
        label = item[2]
        # Change header name by index
        df = df.rename(columns={df.columns[column_index]: label})
        order_list.append(label)

    # Reorder DataFrame by the provided list and drop remaining columns
    df = df[order_list]

    return df


def reorder_header_to_list(df: pd.DataFrame, order: list) -> pd.DataFrame:
    # Reorder DataFrame by the provided list and drop remaining columns
    mdf = df[order]
    return mdf