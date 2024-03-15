import re


def strip_string(df, string, column_index):
    """

    :type df: data frame
    """
    # selecting the column
    selected_column = df.iloc[:, column_index]
    # Removing the string you don't want in it
    selected_column_without_string = selected_column.str.replace(string, '')
    # Replace the original column in the DataFrame with the modified one
    df.iloc[:, column_index] = selected_column_without_string
    return df


def strip_whitespace(df, column_index):
    # Selecting column by index
    selected_column = df.iloc[:, column_index]
    # Removing white space from text
    selected_column_without_whitespace = selected_column.str.strip()
    # Replace the original column in the DataFrame with the modified one
    df.iloc[:, column_index] = selected_column_without_whitespace
    return df


def strip_after_char(df, char, row_index):
    # Selecting the row by index
    selected_row = df.iloc[row_index]

    # Removing string after the first instance of character for the selected row
    modified_row = selected_row.apply(lambda x: x.split(char, 1)[0])

    # Assigning the modified row back to the original DataFrame
    df.iloc[row_index] = modified_row
    return df


def round_column_to_precision(dataframe, column_number, precision):
    """
    Rounds a specified column of a DataFrame to the given precision,
    but only for elements that are numbers.

    Parameters:
        dataframe (pandas.DataFrame): The DataFrame containing the column to be rounded.
        column_number (int): The index number of the column to be rounded.
        precision (int): The number of digits of precision to round to.

    Returns:
        pandas.DataFrame: The DataFrame with the specified column rounded to the given precision.
    """
    # Iterate over each element in the specified column
    for index, value in enumerate(dataframe.iloc[:, column_number]):
        # Check if the value is a number
        if isinstance(value, (int, float)):
            # Round the number to the given precision
            dataframe.iloc[index, column_number] = round(value, precision)

    return dataframe


def check_ref_des_name(df):
    """
    Check and reformat data in the reference designator column of a DataFrame.

    Args:
    df (DataFrame): The DataFrame containing the reference designator column.

    Returns:
    DataFrame: The DataFrame with the reference designator column reformatted.

    Raises:
    ValueError: If no match or more than one match is found for the reference designator column.
    """

    # message
    print()
    print('Checking designator format...')

    # Get reference designator column
    matching_columns = [i for i, header in enumerate(df.columns) if 'Designator' in header]

    # We only expect one match
    if len(matching_columns) == 1:
        column_index = matching_columns[0]  # Select the first matching column
        # print("Designator found in column ", column_index)
    elif len(matching_columns) > 1:
        # Raise an error if more than one column matches
        raise ValueError("More than one column matched the 'Designator' raw_string.")
    else:
        # Raise an error if no partial match is found
        raise ValueError("No match found for Ref des column.")

    # Keep track of number of rows for which reference designators were changed
    rows_changed_count = 0

    # Loop through each row one at a time
    for index, row in df.iterrows():
        # get reference designator column data as a raw_string
        raw_string = str(row.iloc[column_index])
        # split reference designator column data raw_string to a list
        string_list = re.split(r'[,:;]', raw_string)
        # Iterate through the list and remove leading and trailing whitespace
        cleaned_list = [x.strip() for x in string_list]
        # Iterate through the list and make it upper case
        uppercase_list = [x.upper() for x in cleaned_list]
        # Reference designator raw_string pattern
        pattern = r'^[A-Z].*[0-9]$'
        designator_list = []
        # check each reference designator
        for element in uppercase_list:
            if re.match(pattern, element):
                designator_list.append(element)
            elif element == 'PCB':
                designator_list.append(element)
            else:
                print(f'Invalid reference designator {element}')
                exit()
        # Convert the designator list to a comma-separated raw_string
        designators = ','.join(designator_list)

        # Replace reference designator with reformatted raw_string
        df.iloc[index - 1, column_index] = designators

        # update number of rows updated count
        if designators != raw_string:
            print(f'changed {raw_string} to {designators}')
            rows_changed_count += 1

    # debug message
    print(f'Fixed reference designators in {rows_changed_count} rows')
    return df  # Moved outside the loop to return after all rows are processed


def check_duplicate_ref_des(df):
    """
    Check for duplicate reference designators in a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing reference designators.

    Raises:
    - ValueError: If no matching column is found or if more than one column matches 'Designator' header.

    Returns:
    - None
    """
    # message
    print()
    print('Checking for duplicate reference designators...')

    # Get reference designator column index
    matching_columns = [i for i, header in enumerate(df.columns) if 'Designator' in header]

    # We only expect one match
    if len(matching_columns) == 1:
        column_index = matching_columns[0]  # Select the first matching column
        # print("Reference designator data found in column ", column_index)
    elif len(matching_columns) > 1:
        raise ValueError(
            "More than one column matched the 'Designator' header.")  # Raise an error if more than one column matches
    else:
        raise ValueError("No match found for Ref des column.")  # Raise an error if no partial match is found

    designator_list = []
    duplicate_designators = []  # List to store duplicate designators

    # Loop through each row one at a time
    for index, row in df.iterrows():
        # get reference designator column data as a string
        raw_string = str(row.iloc[column_index])
        # split reference designator column data string to a list using delimiters ',',';',':'
        string_list = re.split(r'[,:;]', raw_string)
        # add reference designators to list
        designator_list.extend(string_list)

    # check for duplicate reference designators
    seen = set()
    for item in designator_list:
        if item in seen:
            duplicate_designators.append(item)
        else:
            seen.add(item)

    if duplicate_designators:
        print("Duplicates reference designators found:", ', '.join(duplicate_designators))
        print("This application can not determine which ref des is correct")
        print("Please fix the data in the excel file and retry.")
        exit()
    else:
        print("No duplicates found.")


def find_best_match_levenshtein(test_string, reference_strings):
    """
    Finds the best match for a test string from a list of reference strings based on Levenshtein distance.

    Args:
        test_string (str): The string to find the best match for.
        reference_strings (list of str): List of reference strings to compare against.

    Returns:
        str: The best matching reference string.

    Example:
        test_string = "apple"
        reference_strings = ["banana", "orange", "pineapple", "grape"]
        find_best_match(test_string, reference_strings)
        'pineapple'
    """

    import Levenshtein

    # Initialize variables to keep track of the best match and its distance
    best_match = None
    min_distance = float('inf')  # Start with a distance of positive infinity

    # Loop through each reference string
    for ref_string in reference_strings:
        # Compute the Levenshtein distance between the test string and the current reference string
        distance = Levenshtein.distance(test_string, ref_string)

        # If the distance is smaller than the current minimum distance, update the best match
        if distance < min_distance:
            min_distance = distance
            best_match = ref_string

    # Return the best matching reference string
    return best_match


def find_best_match_jaccard(test_string, reference_strings):
    """
    Finds the best match for a test string from a list of reference strings based on Jaccard similarity.

    Args:
        test_string (str): The string to find the best match for.
        reference_strings (list of str): List of reference strings to compare against.

    Returns:
        str: The best matching reference string.

    Example:
       test_string = "apple"
       reference_strings = ["banana", "orange", "pineapple", "grape"]
       find_best_match_jaccard(test_string, reference_strings)
       'pineapple'
    """

    best_match = None
    max_similarity = 0

    # Iterate through each reference string
    for ref_string in reference_strings:
        # Compute Jaccard similarity coefficient
        set1 = set(test_string)
        set2 = set(ref_string)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        similarity = intersection / union

        # Update best match if similarity is higher
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = ref_string

    return best_match


def check_consecutive_characters_presence(test_string, reference_string, consecutive_chars=3):
    """
    Checks if at least the specified number of consecutive characters from the reference string are present in the test string.

    Args:
        test_string (str): The string to check for presence of consecutive characters.
        reference_string (str): The string whose consecutive characters presence is to be checked.
        consecutive_chars (int): The minimum number of consecutive characters required for a match. Default is 3.

    Returns:
        bool: True if at least consecutive_chars consecutive characters of the reference string
        are present in the test string, False otherwise.
    """
    # Get the length of the reference string
    reference_length = len(reference_string)

    # Iterate through each possible consecutive substring in the reference string
    for i in range(reference_length - consecutive_chars + 1):
        # Extract consecutive substring of length consecutive_chars
        consecutive_substring = reference_string[i:i + consecutive_chars]

        # Check if the consecutive substring exists in the test string
        if consecutive_substring in test_string:
            return True

    print("At least three consecutive characters of the reference string are present in the test string:", result)

    # If no matching consecutive substring found, return False
    return False




