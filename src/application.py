import paths
import files
import strings
import frames


def process_cbom_for_cost_walk() -> None:

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract cbom table ***
    # drop rows above cBOM header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    frames.determine_bom_template_version(df, "CBOM")
    # keep only the columns needed based on cBOM cost walk
    df = frames.extract_cost_walk_columns(df)
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # merge alternative components to one row
    df = frames.merge_alternative(df)

    # *** Clean up data ***
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # split multiple quantity to separate rows
    df = frames.split_multiple_quantity(df)

    # *** write cBOM data to file ***
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "CW_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None


def process_cbom_for_db_upload() -> None:

    # *** read cBOM Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract sheet to process ***
    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract cbom data ***
    # drop rows above BOM header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    frames.determine_bom_template_version(df, "CBOM")
    # keep only the columns needed based on cBOM template
    df = frames.extract_bom_columns(df)
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # merge alternative components to one row
    df = frames.merge_alternative(df)

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
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "dBcBOM_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None


def process_ebom_for_db_upload():

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract ebom table ***
    # drop rows above cBOM header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    frames.determine_bom_template_version(df, "EBOM")
    # keep only the columns needed based on dB bom
    df = frames.extract_bom_columns(df)
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # merge alternative components to primary
    df = frames.merge_alternative(df)

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
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "dBeBOM_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None
