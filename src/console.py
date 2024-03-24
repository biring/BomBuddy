

def get_user_selection(options: list, header_msg='Available items',
                       select_msg='Enter the number to make a selection') -> int:
    """
    Allows the user to select an option from a list of options.

    Parameters:
    options (list): A list of options from which the user will make a selection.
    header_msg (str, optional): Message displayed as the header before displaying options.
    select_msg (str, optional): Message prompting the user to enter a selection.

    Returns:
    int: The index of the selected option in the provided list.

    Raises:
    ValueError: If the list of options is empty.

    Example:
    # options = ['Option 1', 'Option 2', 'Option 3']
    # selected_index = get_user_selection(options)
    """

    # local variables
    select_msg += ' (or "x" to exit): '
    length = len(options)

    # when there are no option we generate an error
    if length == 0:
        raise ValueError('Empty list provided for user selection')
    # when we only have one option we select it
    elif length == 1:
        user_selection = 0
    # when we have multiple options
    else:
        while True:
            try:
                print()
                print(f'*** {header_msg.upper()} ***')
                # Print the list of options available for the user to select
                for index, key in enumerate(options):
                    print(f"[{index}] {key}")
                # first check user selection as a string
                user_selection = input(select_msg)
                # Check if the user wants to exit the application
                if user_selection.lower() == 'x':
                    exit_application("User selected to exit the application")
                # then check user selection as an integer
                user_selection = int(user_selection)
                # Check if the entered number is within the valid range
                if user_selection < 0 or user_selection >= length:
                    print("Invalid selection. Please enter a valid number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    return user_selection


def exit_application(msg) -> None:
    """
    Prints a message and exits the application.

    Parameters:
    msg (str): The message to be printed before exiting.

    Returns:
    None

    Example:
    # exit_application("Exiting due to user request.")
    """

    print('*** WARNING ***')
    print(msg)
    exit()


def main():
    # select_list = []
    # print(get_user_selection(select_list))
    select_list = ['ABC']
    print(get_user_selection(select_list))
    select_list = ['A1', 'B2', 'C3']
    print(get_user_selection(select_list))


if __name__ == '__main__':
    main()
