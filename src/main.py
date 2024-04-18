import application
import console


def main():
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
            application.process_cbom_for_cost_walk()
        elif user_selection == 1:
            application.process_cbom_for_db_upload()
        elif user_selection == 2:
            application.process_ebom_for_db_upload()
        else:
            print("Invalid selection. Please choose a valid option.")
    except Exception as e:
        print('*** ERROR ***')
        print(e)
    finally:
        # Regardless of whether an exception occurred or not, print this message.
        print()
        print("Exiting application.")


if __name__ == "__main__":
    main()
