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
