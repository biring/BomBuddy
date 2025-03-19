import application
import console
import version


def run_menu():
    try:
        # list of main menu option
        menu_options = ['Process cBOM for cost walk',
                        'Process cBOM for database upload',
                        'Process eBOM for database upload']
        # get user to make a selection
        header_msg = 'main menu'
        select_msg = 'Enter the number of the menu option to execute'
        user_selection = console.get_user_selection(menu_options, header_msg=header_msg, select_msg=select_msg)
        # run user selection
        if user_selection == 0:
            application.sequence_cbom_for_cost_walk()
        elif user_selection == 1:
            application.sequence_cbom_for_db_upload()
        elif user_selection == 2:
            application.sequence_ebom_for_db_upload()
        else:
            print("WARNING! Invalid selection. Please select a valid option.")
    except Exception as e:
        print('*** ERROR ***')
        print(f"An error occurred: {e}")
        return False

    return True


def show_title():
    print(f'Version {version.__version__} ')
    print(f'Build {version.__build__} ')


def main():
    # Menu title
    show_title()
    # Forever loop

    while run_menu():
        pass

    # Exit message
    print()
    print("Exiting application.")


if __name__ == "__main__":
    main()
