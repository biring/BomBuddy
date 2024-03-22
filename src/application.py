import paths
import files
import strings
import frames


def ebom_scrub_for_stella():
    # *** read eBOM Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_inputs_folder()
    # get path to input data folder
    file_path = paths.get_excel_file_path(folder_path)
    # get file data as data frame
    data_frame = files.get_excel_file_data(file_path)

    # *** clean up raw data to get header and BOM ***
    # delete empty rows
    data_frame = frames.delete_empty_rows_columns(data_frame)
    # drop rows above BOM header
    data_frame = frames.drop_rows_above_string_match(data_frame, 'Item')
    # set the top row as header
    data_frame = frames.set_top_row_as_header(data_frame)
    # remove columns that are not needed in template
    column_names = ['Item', 'Comp', 'Desc', 'Qty', 'Desi', 'Crit', 'Manu', 'P/N', 'Type']
    data_frame = frames.keep_partial_matched_columns(data_frame, column_names)
    # remove any row in which quantity is less than 1
    data_frame = frames.drop_rows_below_threshold_for_column(data_frame, 'Qty', 1)
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
    # normalize component type labels
    data_frame = frames.normalize_component_type_label(data_frame)
    # remove part number from description
    data_frame = frames.remove_part_number_from_description(data_frame)
    # add type information to description
    data_frame = frames.merge_type_data_with_description(data_frame)

    # *** write eBOM data to template ***
    folder_path = paths.get_path_to_outputs_folder()
    file_name = "scrubbed_ebom.xlsx"
    file_path = paths.build_path_to_outputs_file(folder_path, file_name)
    data_frame.to_excel(file_path, index=True)  # Set index=False to exclude the DataFrame index from being written
    return


def cbom_scrub_for_cost_walk() -> None:
    # *** read cBOM Excel data file ***
    # get path to input data folder
    folder_path = paths.get_path_to_inputs_folder()
    # get path to input data folder
    file_path = paths.get_excel_file_path(folder_path)
    # get file data as data frame
    data_frame = files.get_excel_file_data(file_path)

    # *** clean up raw data ***
    # only keep cost data for build on interest
    data_frame = frames.remove_unwanted_build_cost_data(data_frame)
    # drop rows above BOM header
    data_frame = frames.drop_rows_above_string_match(data_frame, 'Item')
    # set the top row as header
    data_frame = frames.set_top_row_as_header(data_frame)
    # remove columns that are not needed in template
    column_names = ['Desi', 'Comp', 'Desc', 'Manu', 'P/N', 'Qty', 'U/P']
    data_frame = frames.keep_partial_matched_columns(data_frame, column_names)
    # delete empty rows and columns
    data_frame = frames.delete_empty_rows_columns(data_frame)
    # remove quantity of zero and empty
    data_frame = frames.remove_zero_and_empty_quantity(data_frame)
    # reformat reference designator to correct format
    data_frame = frames.reformat_cbom_ref_des(data_frame)
    # split multiple quantity to separate rows
    data_frame = frames.split_multiple_quantity(data_frame)

    # reorder column headers for cost walk
    data_frame = frames.reorder_column_headers_for_cost_walk(data_frame)

    # *** write cBOM data to template ***
    folder_path = paths.get_path_to_outputs_folder()
    file_name = "scrubbed_cbom.xlsx"
    file_path = paths.build_path_to_outputs_file(folder_path, file_name)
    data_frame.to_excel(file_path, index=True)  # Set index=False to exclude the DataFrame index from being written

    return

