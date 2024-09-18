import paths
import files
import strings
import frames

# global variable with NULL value.
# Should be removed when refactoring to OOP programming is completed
# or create getters and setters in lower modules, so we don't use globals.
excel_data = None
df = None
file_name = None


def sequence_cbom_for_cost_walk() -> None:
    global df

    # *** read Excel data file ***
    steps_to_read_an_excel_file()

    # *** Extract cbom sheet to process ***
    steps_to_get_user_selected_excel_sheet()

    # *** Extract cbom table ***
    # drop rows above cBOM header
    steps_to_get_bom_data_from_excel_sheet("CW")

    # *** Clean up data ***
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # split multiple quantity to separate rows
    df = frames.split_multiple_quantity(df)

    # *** write cBOM data to file ***
    steps_to_write_bom_to_single_sheet_excel_file("COST WALK ")

    return None


def sequence_cbom_for_db_upload() -> None:
    global df

    # *** read cBOM Excel data file ***
    steps_to_read_an_excel_file()

    # *** Extract sheet to process ***
    steps_to_get_user_selected_excel_sheet()

    # *** Extract cbom data ***
    steps_to_get_bom_data_from_excel_sheet("CBOM")

    # *** Clean up cbom data ***
    # remove empty designator data
    df = frames.drop_items_with_empty_designator(df)
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove less than one quantity
    df = frames.drop_item_with_quantity_less_than_one(df)

    # clean up description column data
    df = frames.cleanup_description(df)
    # remove rows that have unwanted description items
    df = frames.drop_unwanted_db_cbom_description(df)

    # normalize component type labels
    df = frames.normalize_component_type_label(df)
    # remove rows that have unwanted component type items
    df = frames.drop_unwanted_db_cbom_component(df)

    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # check reference designator format
    df = strings.check_ref_des_name(df)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(df)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(df)

    # separate manufacturers to separate rows
    df = frames.split_manufacturers_to_separate_rows(df)
    # clean up manufacturer name
    df = frames.cleanup_manufacturer(df)

    # clean up part number
    df = frames.cleanup_part_number(df)

    # add type information to description. Note do this before removing P/N from description or nan cell causes issue
    df = frames.merge_type_data_with_description(df)
    # remove part number from description
    df = frames.remove_part_number_from_description(df)

    # *** write scrubbed cBOM data to file ***
    steps_to_write_bom_to_single_sheet_excel_file("CBOM DB ")

    return None


def sequence_ebom_for_db_upload():
    global df

    # *** read Excel data file ***
    steps_to_read_an_excel_file()

    # *** Extract cbom sheet to process ***
    steps_to_get_user_selected_excel_sheet()

    # *** Extract ebom table ***
    steps_to_get_bom_data_from_excel_sheet("EBOM")

    # *** Clean up ebom table ***
    # remove empty designator data
    df = frames.drop_items_with_empty_designator(df)
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove less than one quantity
    df = frames.drop_item_with_quantity_less_than_one(df)

    # clean up description column data
    df = frames.cleanup_description(df)
    # remove rows that have unwanted description items
    df = frames.drop_unwanted_db_ebom_description(df)

    # normalize component type labels
    df = frames.normalize_component_type_label(df)
    # remove rows that have unwanted component type items
    df = frames.drop_unwanted_db_ebom_component(df)

    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # check reference designator format
    df = strings.check_ref_des_name(df)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(df)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(df)

    # remove rows that have unwanted items
    df = frames.drop_rows_with_unwanted_ebom_items(df)

    # separate manufacturers to separate rows
    df = frames.split_manufacturers_to_separate_rows(df)
    # clean up manufacturer name
    df = frames.cleanup_manufacturer(df)

    # clean up part number
    df = frames.cleanup_part_number(df)

    # add type information to description. Note do this before removing P/N from description or nan cell causes issue
    df = frames.merge_type_data_with_description(df)
    # remove part number from description
    df = frames.remove_part_number_from_description(df)

    # *** write eBOM data to file ***
    steps_to_write_bom_to_single_sheet_excel_file("EBOM DB ")

    return None


def steps_to_read_an_excel_file() -> None:
    global excel_data
    global file_name
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)
    return None


def steps_to_get_user_selected_excel_sheet() -> None:
    global excel_data
    global df
    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)
    return None


def steps_to_get_bom_data_from_excel_sheet(bom_type: str) -> None:
    global df
    # drop rows above cBOM header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    frames.determine_bom_template_version(df, bom_type)
    # keep only the columns needed based on cBOM cost walk
    if bom_type == "CW":
        df = frames.extract_cost_walk_columns(df)
    elif bom_type == "CBOM":
        df = frames.extract_bom_columns(df)
    elif bom_type == "EBOM":
        df = frames.extract_bom_columns(df)
    else:
        raise ValueError(f"BOM_TYPE = '{bom_type}' is not supported")
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # merge alternative components to one row
    df = frames.merge_alternative(df)
    return None


def steps_to_write_bom_to_single_sheet_excel_file(prefix: str) -> None:
    global file_name
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = prefix + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)
    return None
