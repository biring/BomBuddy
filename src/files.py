# manage file data
import pandas as pd

def get_totals_data(path):
    # Read the costed bill of material file
    tempFileData = pd.ExcelFile(path)
    # make a list of all the tabs
    tempFileTabNames = tempFileData.sheet_names
    # get the name of tab with overall quote data
    totalTabName = ""
    for name in tempFileTabNames:
        if "Total" in name:
            totalTabName = name
            break  # we only expect one summary quote
    # get totals tab data.
    df = pd.read_excel(path, sheet_name=totalTabName, header=None)
    return df

def process_totals_data(df):
    # set the search string to 'OHP'.
    searchString = 'OHP'
    # check each element in the DataFrame for a partial string match
    matches = df.apply(lambda x: x.astype(str).str.contains(searchString, case=False))
    # get row and column where the partial string matches
    rows, cols = matches.values.nonzero()
    rowToDelete = rows[0] - 1
    # Drop rows above OHP
    df.drop(index=rowToDelete, axis=0, inplace=True)
    # Reindexing the rows
    df = df.reset_index(drop=True)

    return df

def write_totals_data(path, df):
    # Writing DataFrame to a CSV file
    df.to_csv(path, index=False, header=False, sep='\t')


def get_excel_file_data(file_path):
    """
    Read an Excel file and return its contents as a DataFrame if the file has only one tab.
    If the file has multiple tabs, prompt the user to select a tab.

    Parameters:
        file_path (str): The full path to the Excel file.

    Returns:
        pandas.DataFrame: The DataFrame containing the contents of the selected tab from the Excel file.

    Raises:
        ValueError: If reading the file fails.

    Example:
        # Example usage:
        excel_path = input("Enter the full path to the Excel file: ")
        data_frame = get_excel_file_data(excel_path)
        print(data_frame.head())  # Just an example to show the first few rows of the DataFrame
    """

    import pandas as pd

    try:
        # Open the Excel file
        xls = pd.ExcelFile(file_path, engine='openpyxl')

        # Check the number of tabs
        sheet_names = xls.sheet_names
        if len(sheet_names) == 1:
            # Read the data from the Excel file directly if there's only one tab
            df = pd.read_excel(xls, sheet_names[0])
            print(f'Read of one tab Excel file successful.')
            print(f'Read {df.shape[0]} rows and {df.shape[1]} columns')
            # Clearing the DataFrame header
            df.columns = [''] * len(df.columns)
            return df
        elif len(sheet_names) > 1:
            # Print the available tables and prompt the user to select one
            print("Available Tables:")
            for i, sheet_name in enumerate(sheet_names, 1):
                print(f"{i}. {sheet_name}")

            while True:
                user_input = input("Enter the number of the table you want to select (or 'x' to exit): ")

                if user_input.lower() == 'x':
                    print("Exiting...")
                    exit()

                try:
                    selected_table_index = int(user_input) - 1
                    if selected_table_index < 0 or selected_table_index >= len(sheet_names):
                        raise ValueError("Invalid table number.")
                    selected_sheet_name = sheet_names[selected_table_index]
                    df = pd.read_excel(xls, selected_sheet_name)
                    print(f'Selected table: {selected_sheet_name}')
                    print(f'Read {df.shape[0]} rows and {df.shape[1]} columns')
                    # Clearing the DataFrame header
                    df.columns = [''] * len(df.columns)
                    return df
                except ValueError:
                    print("Invalid input. Please enter a valid table number or 'x' to exit.")
        else:
            raise ValueError("The Excel file is empty.")
    except Exception as e:
        print("Excel file read failed. Error:", e)
        print("File may be open. Please close it and retry")
        exit()
