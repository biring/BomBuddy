import application
import console


def main():
    try:
        # list of main menu option
        menu_options = ['eBOM scrub for stella', 'cBOM scrub for cost walk']
        # get user to make a selection
        msg = "*** MAIN MENU ***"
        user_selection = console.get_user_selection(menu_options, header_msg=msg)
        # run user selection
        if user_selection == 0:
            application.ebom_scrub_for_stella()
        elif user_selection == 1:
            application.cbom_scrub_for_cost_walk()
        else:
            print("Invalid selection. Please choose a valid option.")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Regardless of whether an exception occurred or not, print this message.
        print("We are done. Exiting application.")
        print()


if __name__ == "__main__":
    main()