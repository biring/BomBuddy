import paths
import files
import strings
import frames


def scrub_cbom_for_cost_walk() -> None:

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    # extract user selected Excel file sheet
    raw_df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    cbom_df = frames.remove_unwanted_build_cost_data(raw_df)

    # *** Extract cbom table ***
    # drop rows above cBOM header
    cbom_df = frames.drop_rows_above_string_match(cbom_df, 'Item')
    # set the top row as header
    cbom_df = frames.set_top_row_as_header(cbom_df)
    # keep only the columns needed based on cBOM cost walk
    cbom_df = frames.extract_cost_walk_columns(cbom_df)

    # *** Clean up data ***
    # remove empty quantity data
    cbom_df = frames.remove_empty_quantity_data(cbom_df)
    # remove zero quantity data
    cbom_df = frames.remove_zero_quantity_data(cbom_df)
    # delete empty rows and columns
    cbom_df = frames.delete_empty_rows_columns(cbom_df)
    # split multiple quantity to separate rows
    cbom_df = frames.split_multiple_quantity(cbom_df)

    # *** write cBOM data to file ***
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "Scrubbed_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, cbom_df)

    return None


def scrub_cbom_for_stella_db_upload() -> None:

    # *** read cBOM Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract sheet to process ***
    # extract user selected Excel file sheet
    raw_df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    raw_one_build_df = frames.remove_unwanted_build_cost_data(raw_df)

    # *** Extract cbom data ***
    # drop rows above BOM header
    bom_df = frames.drop_rows_above_string_match(raw_one_build_df, 'Item')
    # set the top row as header
    bom_df = frames.set_top_row_as_header(bom_df)
    # keep only the columns needed based on cBOM template
    bom_df = frames.extract_cbom_template_columns(bom_df)
    # delete empty rows and columns
    bom_df = frames.delete_empty_rows_columns(bom_df)
    # remove quantity of zero and empty
    bom_df = frames.remove_zero_and_empty_quantity(bom_df)

    # *** Clean up cbom data ***
    # clean up component type column data
    bom_df = frames.normalize_cbom_component_type_label(bom_df)
    # clean up description column data
    # bom_df = frames.normalize_cbom_description(bom_df)

    # *** write scrubbed cBOM data to file ***
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "Scrubbed_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, bom_df)

    return None


def scrub_ebom_for_stella_db_upload():

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    # extract user selected Excel file sheet
    raw_df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    raw_one_build_df = frames.remove_unwanted_build_cost_data(raw_df)

    # *** Extract ebom table ***
    # drop rows above cBOM header
    bom_df = frames.drop_rows_above_string_match(raw_one_build_df, 'Item')
    # set the top row as header
    bom_df = frames.set_top_row_as_header(bom_df)
    # keep only the columns needed based on eBOM template
    column_names = ['Item', 'Comp', 'Desc', 'Qty', 'Desi', 'Crit', 'Manu', 'P/N', 'Type']
    bom_df = frames.keep_partial_matched_columns(bom_df, column_names)
    # delete empty rows and columns
    bom_df = frames.delete_empty_rows_columns(bom_df)

    # *** Clean up ebom table ***
    data_frame = bom_df
    # remove empty designator data
    data_frame = frames.remove_empty_designator_data(data_frame)
    # remove empty quantity data
    data_frame = frames.remove_empty_quantity_data(data_frame)
    # remove zero quantity data
    data_frame = frames.remove_zero_quantity_data(data_frame)
    # remove less than one quantity
    data_frame = frames.remove_less_than_threshold_quantity_data(data_frame)

    # clean up description column data
    data_frame = frames.cleanup_description(data_frame)
    # remove rows that have unwanted description items
    data_frame = frames.drop_unwanted_ebom_description_items(data_frame)

    # normalize component type labels
    data_frame = frames.normalize_component_type_label(data_frame)
    # remove rows that have unwanted component type items
    data_frame = frames.drop_unwanted_ebom_component_type_items(data_frame)

    # remove unwanted characters from designators
    data_frame = frames.cleanup_designators(data_frame)
    # check reference designator format
    data_frame = strings.check_ref_des_name(data_frame)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(data_frame)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(data_frame)

    # remove rows that have unwanted items
    data_frame = frames.drop_rows_with_unwanted_ebom_items(data_frame)

    # separate manufacturers to separate rows
    data_frame = frames.split_manufacturers_to_separate_rows(data_frame)
    # clean up manufacturer name
    data_frame = frames.cleanup_manufacturer(data_frame)

    # add type information to description. Note do this before removing P/N from description or nan cell causes issue
    data_frame = frames.merge_type_data_with_description(data_frame)
    # remove part number from description
    data_frame = frames.remove_part_number_from_description(data_frame)

    # keep only the columns needed based on eBOM template
    data_frame = frames.reorder_header_to_ebom_template(data_frame)

    # *** write eBOM data to file ***
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = "Scrubbed_" + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, data_frame)

    return None
