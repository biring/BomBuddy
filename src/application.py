import pandas as pd
import paths
import files
import strings
import frames
from enumeration import BomType, FilePrefix

def sequence_cbom_for_cost_walk() -> None:

    # *** read Excel data file ***
    excel_data, file_name = steps_to_read_an_excel_file()

    # *** Extract cbom sheet to process ***
    excel_data, df = steps_to_get_user_selected_excel_sheet(excel_data)

    # *** Extract cbom table ***
    # drop rows above cBOM header
    df = steps_to_get_bom_data_from_excel_sheet(df, BomType.CW)

    # *** Clean up data ***
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # split multiple quantity to separate rows
    df = frames.split_multiple_quantity(df)

    # *** write cBOM data to file ***
    steps_to_write_bom_to_single_sheet_excel_file(file_name, df, FilePrefix.CW)

    return None


def sequence_cbom_for_db_upload() -> None:

    # *** read cBOM Excel data file ***
    excel_data, file_name = steps_to_read_an_excel_file()

    # *** Extract sheet to process ***
    excel_data, df = steps_to_get_user_selected_excel_sheet(excel_data)

    # *** Extract cbom data ***
    df = steps_to_get_bom_data_from_excel_sheet(df, BomType.CBOM)

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
    steps_to_write_bom_to_single_sheet_excel_file(file_name, df, FilePrefix.CBOM)

    return None


def sequence_ebom_for_db_upload():

    # *** read Excel data file ***
    excel_data, file_name = steps_to_read_an_excel_file()

    # *** Extract cbom sheet to process ***
    excel_data, df = steps_to_get_user_selected_excel_sheet(excel_data)

    # *** Extract ebom table ***
    df = steps_to_get_bom_data_from_excel_sheet(df, BomType.EBOM)

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
    steps_to_write_bom_to_single_sheet_excel_file(file_name, df, FilePrefix.EBOM)

    return None


def steps_to_read_an_excel_file() -> [str, str]:

    # get path to input data folder
    folder_path = paths.get_path_to_input_file_folder()
    # get Excel file name to process
    file_name = paths.get_selected_excel_file_name(folder_path)
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)
    return excel_data, file_name


def steps_to_get_user_selected_excel_sheet(excel_data) -> (str, pd.DataFrame):

    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)
    return excel_data, df


def steps_to_get_bom_data_from_excel_sheet(df, bom_type: BomType) -> pd.DataFrame:
    """
    Processes the BOM data from an Excel sheet based on the provided BOM type.

    Args:
        df (pd.DataFrame): The dataframe containing raw BOM data.
        bom_type (BomType): The BOM type (CW, CBOM, or EBOM) to guide the cleanup process.

    Returns:
        pd.DataFrame: The processed BOM data ready for further steps.
    """

    # drop rows above cBOM header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    frames.determine_bom_template_version(df, bom_type.value)
    # keep only the columns needed based on cBOM cost walk
    if bom_type == BomType.CW:
        df = frames.extract_cost_walk_columns(df)
    elif bom_type == BomType.CBOM:
        df = frames.extract_bom_columns(df)
    elif bom_type == BomType.EBOM:
        df = frames.extract_bom_columns(df)
    else:
        raise ValueError(f"BOM_TYPE = '{bom_type}' is not supported")
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # primary component should be first
    df = frames.primary_above_alternative(df)
    # merge alternative components to one row
    df = frames.merge_alternative(df)
    return df


def steps_to_write_bom_to_single_sheet_excel_file(file_name: str, df: pd.DataFrame, prefix: FilePrefix) -> None:
    # get path to output data folder
    folder_path = paths.get_path_to_outputs_folder()
    # Set Excel file name
    file_name = prefix.value + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)
    return None
