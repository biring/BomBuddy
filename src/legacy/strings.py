import re
import pandas as pd


def strip_string(df: pd.DataFrame, string: str, column_index: int) -> pd.DataFrame:
    """
    Remove occurrences of a specified string from a column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which the string will be removed.
        string (str): The string to be removed from the specified column.
        column_index (int): Index of the column from which the string will be removed.

    Returns:
        pd.DataFrame: Modified DataFrame with the specified string removed from the selected column.
    """
    # selecting the column
    selected_column = df.iloc[:, column_index]
    # Removing the string you don't want in it
    selected_column_without_string = selected_column.str.replace(string, '')
    # Replace the original column in the DataFrame with the modified one
    df.iloc[:, column_index] = selected_column_without_string
    return df


def strip_whitespace(df: pd.DataFrame, column_index: int) -> pd.DataFrame:
    """
    Remove leading and trailing whitespace from text in the specified column of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which whitespace will be removed.
        column_index (int): Index of the column in which whitespace will be removed.

    Returns:
        pd.DataFrame: Modified DataFrame with leading and trailing whitespace removed from the specified column.
    """
    # Selecting column by index
    selected_column = df.iloc[:, column_index]
    # Removing white space from text
    selected_column_without_whitespace = selected_column.str.strip()
    # Replace the original column in the DataFrame with the modified one
    df.iloc[:, column_index] = selected_column_without_whitespace
    return df


def strip_after_char(df: pd.DataFrame, char: str, row_index: int) -> pd.DataFrame:
    """
    Remove characters occurring after the first instance of a specified character in the selected row of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which characters will be removed.
        char (str): The character after which characters will be removed.
        row_index (int): Index of the row in which characters will be removed.

    Returns:
        pd.DataFrame: Modified DataFrame with characters removed after
        the first instance of the specified character in the selected row.
    """
    # Selecting the row by index
    selected_row = df.iloc[row_index]

    # Removing string after the first instance of character for the selected row
    modified_row = selected_row.apply(lambda x: x.split(char, 1)[0])

    # Assigning the modified row back to the original DataFrame
    df.iloc[row_index] = modified_row
    return df


def round_column_to_precision(dataframe: pd.DataFrame, column_number: int, precision: int) -> pd.DataFrame:
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


def check_ref_des_name(df: pd.DataFrame) -> pd.DataFrame:
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
    for i, (_, row) in enumerate(df.iterrows()):
        # get reference designator column data as a raw_string
        raw_string = str(row.iloc[column_index])
        # split reference designator column data raw_string to a list
        string_list = re.split(r'[,:;]', raw_string)
        # Iterate through the list and remove leading and trailing whitespace
        cleaned_list = [x.strip() for x in string_list]
        # Iterate through the list and make it upper case
        uppercase_list = [x.upper() for x in cleaned_list]
        # Reference designator raw_string pattern
        # Rule:
        # - Start with a letter
        # - Contains letters, digits, plus, minus, underscore
        # - Ends with letter, digit, plus, or minus
        pattern = r'^[A-Za-z][A-Za-z0-9+\-_]*[A-Za-z0-9+\-]$'
        designator_list = []
        # check each reference designator
        for element in uppercase_list:
            if re.match(pattern, element):
                designator_list.append(element)
            elif element == 'PCB':
                designator_list.append(element)
            else:
                print(f'Invalid reference designator in row {row} = "{element}"')
                exit()
        # Convert the designator list to a comma-separated raw_string
        designators = ','.join(designator_list)

        # Replace reference designator with reformatted raw_string
        df.iloc[i, column_index] = designators

        # update number of rows updated count
        if designators != raw_string:
            print(f"changed '{raw_string}' to '{designators}'")
            rows_changed_count += 1

    # debug message
    print(f'Fixed reference designators in {rows_changed_count} rows')
    return df  # Moved outside the loop to return after all rows are processed


def check_duplicate_ref_des(df: pd.DataFrame) -> None:
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


def find_best_match_levenshtein(test_string: str, reference_strings: list) -> str:
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

    max_threshold_for_valid_match = 5.0  # 0.0 is a perfect match, higher is lesser match
    perfect_match = 0.0

    # Initialize variables to keep track of the best match and its distance
    best_match = "  "
    min_distance = float('inf')  # Start with a distance of positive infinity

    # Loop through each reference string
    for ref_string in reference_strings:
        lower_test_string = test_string.lower().strip()
        lower_ref_string = ref_string.lower().strip()
        # Compute the Levenshtein distance between the test string and the current reference string
        distance = Levenshtein.distance(lower_test_string, lower_ref_string)
        # print(f'L = {distance:2.2f} {test_string:20} {ref_string:20}')

        # If the distance is smaller than the current minimum distance, update the best match
        if (min_distance > distance) and (distance < max_threshold_for_valid_match):
            min_distance = distance
            best_match = ref_string

        # stop checking once a perfect match is found
        if min_distance == perfect_match:
            break

    # Return the best matching reference string
    return best_match


def find_best_match_jaccard(test_string: str, reference_strings: list) -> str:
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

    best_match = " "
    max_similarity = 0
    minimum_similarity_threshold = 0.5  # 1.0 is a perfect match. 0.0 is no match
    perfect_match = 1.0

    # Iterate through each reference string
    for ref_string in reference_strings:
        # Compute Jaccard similarity coefficient
        set1 = set(test_string.lower().strip())
        set2 = set(ref_string.lower().strip())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        similarity = intersection / union
        # print(f'J = {similarity:2.2f} {test_string:20} {ref_string:20}')

        # Update best match if similarity is higher
        if (similarity > max_similarity) and (similarity > minimum_similarity_threshold):
            max_similarity = similarity
            best_match = ref_string

        # stop checking once a perfect match is found
        if similarity == perfect_match:
            break

    return best_match


def check_consecutive_characters_presence(test_string: str, reference_string: str, consecutive_chars=3) -> bool:
    """
    Checks if at least the specified number of consecutive characters
    from the reference string are present in the test string.

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

    # If no matching consecutive substring found, return False
    return False


def reduce_multiple_trailing_zeros_to_one(numeric_string: str) -> str:
    """
    Reduce multiple trailing zeros in the numeric part of a string to a single zero,
    while preserving the units.

    Example:
    - "2.1000mm" => "2.10mm"
    - "3.000kg" => "3.0kg"
    - "2.0lb"   => "2.0lb"
    - "5mm"     => "5mm"

    Args:
    numeric_string (str): The input string containing numeric and unit information.

    Returns:
    str: A string where multiple trailing zeros are reduced to one.
    """
    numeric_normalization_pattern = r'(\.\d*)0+(?=\D*$)'
    return re.sub(numeric_normalization_pattern, r'\g<1>0', numeric_string)

def strip_match_from_string(df: pd.DataFrame, pattern_column, search_column) -> pd.DataFrame:
    """
    Remove occurrences of a specified pattern from a string in a column of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        pattern_column (str or int): The column name or index in the DataFrame containing the patterns to search for.
        search_column (str or int): The column name or index in the DataFrame containing the strings from which patterns will be removed.

    Returns:
        pd.DataFrame: The modified DataFrame with the specified patterns removed from the `search_column`.

    Example:
        # Example with simple strings and special characters ('#' and '-')
        data = {'pattern_column': ['123', '#123', '-456', '#789-', '000'],
                'search_column': ['abc123xyz', 'abc#123xyz', 'def-456ghi', 'ghi#789-xyz', 'jkl000']}
        df = pd.DataFrame(data)

        # Before calling the function:
        #       pattern_column  search_column
        # 0     123             abc123xyz
        # 1     #123            abc#123xyz
        # 2     -456            def-456ghi
        # 3     #789-           ghi#789-xyz
        # 4     000             jkl000

        # Call the function to remove the pattern from search_column
        df = strip_match_from_string(df, 'pattern_column', 'search_column')

        # After calling the function:
        #       pattern_column  search_column
        # 0     123             abcxyz
        # 1     #123            abcxyz
        # 2     -456            defghi
        # 3     #789-           ghi-xyz
        # 4     000             jkl
    """
    # Print message indicating the operation is starting
    print(f"\tRemoving data found in '{pattern_column}' from '{search_column}'")

    # Keep track of number of cells changed
    count = 0

    # Iterate through each row of the DataFrame
    for n, row in df.iterrows():
        # Get the pattern string from the specified column
        pattern = row[pattern_column].strip()  # Remove leading and trailing spaces from the pattern
        # Get the string from the search column
        old_string = row[search_column]

        # Check if the pattern is found in the search string
        is_found = pattern in old_string

        # If the pattern is found, perform replacement
        if is_found:
            new_string = old_string.replace(pattern, '')  # Replace the pattern with an empty string
            df.at[n, search_column] = new_string  # Update the DataFrame at the current row
            count += 1  # Increment the count of changes
            print(f"\t\tFound '{pattern}' Changed '{old_string}' to '{new_string}'")

    # Print a summary of the number of cells updated
    print(f'\t{count} cells updated.')

    return df


def main():
    pass  # do nothing


if __name__ == '__main__':
    main()
