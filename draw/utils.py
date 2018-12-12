from IPython.display import display_html


def copy_list_and_remove_element(element, list_of_elements):
    """
    Return a copy of the list_of_elements having removed element from it.
    :param element: element to be removed from list_of_elements
    :param list_of_elements: list containing element
    :return: a fresh copy of the list without the element removed
    """
    copied_list = list_of_elements[:]
    copied_list.remove(element)
    return copied_list


def show_group_stage_draw_result(draw, clubs, clubs_per_pot):
    """
    Print the result of a draw in the form of group composition.
    :param draw: a [clubs_per_pot]x[number_of_pots] numpy 2D-array containing club indexes
    :param clubs: list of clubs ordered by association and UEFA ranking
    :param clubs_per_pot: number of clubs in each pot
    """
    for group in range(clubs_per_pot):
        print("Group %s: %s" % (chr(65+group), ", ".join([clubs[club] for club in draw[group, :]])))


def print_html(string):
    """
    Utility function to display HTML into a code cell.
    """
    display_html(string, raw=True)
