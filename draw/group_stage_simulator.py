import networkx as nx
import numpy as np
import collections
from utils import copy_list_and_remove_element


def filter_groups(club, groups, updated_draw, associations, paired_clubs,
                  groups_in_first_timetable, groups_in_second_timetable):
    """
    Valid groups for the club are those having clubs from different associations and
    satisfying the TV constraints given the current state of the draw.
    :param club: club index for which the list of remaining groups will be filtered
    :param groups: list of groups that have not been assigned yet
    :param updated_draw: 2-D numpy array contaiing the current state of the draw
    :param associations: association of each club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a filter list of groups
    """
    association = associations[club]
    return filter(lambda g: has_no_same_association_club_in_group(updated_draw[g, :], association, associations)
                  and is_tv_constraint_satisfied(updated_draw, club, g, paired_clubs,
                                                 groups_in_first_timetable, groups_in_second_timetable), groups)


def exist_maximum_matching(remaining_clubs, remaining_groups, updated_draw, associations,
                           paired_clubs, groups_in_first_timetable, groups_in_second_timetable):
    """
    A bipartite graph is built using remaining_clubs (first class) and
    remaining_groups (second class). For each club, eligible groups are calculated,
    and for each of these pairs of nodes (1st class, 2nd class) an edge is built.
    If the maximum matching for this bipartite graph is exactly the sum of
    the sizes of remaining_clubs and remaining_groups, then there is no dead ends yet.
    :param remaining_clubs: list of indexes of the remaining clubs
    :param remaining_groups: list of groups that have not been assigned yet
    :param updated_draw: 2-D numpy array containing the current state of the draw
    :param associations: association of each club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a boolean
    """
    graph = nx.Graph()
    size = len(remaining_clubs)
    graph.add_nodes_from(range(size), bipartite=0)
    graph.add_nodes_from(range(size, 2*size), bipartite=1)
    for idx, c in enumerate(remaining_clubs):
        for fg in filter_groups(c, remaining_groups, updated_draw, associations, paired_clubs,
                                groups_in_first_timetable, groups_in_second_timetable):
            g_idx = remaining_groups.index(fg)
            graph.add_edge(idx, g_idx + size)
    max_size = len(nx.algorithms.bipartite.maximum_matching(graph))
    return max_size == 2 * size


def is_group_in_timetable(group, groups_in_first_timetable, groups_in_second_timetable, first_timetable=True):
    """
    Check if a group belongs to one of the two timetables.
    :param group: group index
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :param first_timetable: True for the first timetable and False otherwise
    :return: a boolean
    """
    groups = groups_in_first_timetable if first_timetable else groups_in_second_timetable
    return group in groups


def are_groups_in_same_timetable(group1, group2, groups_in_first_timetable, groups_in_second_timetable):
    """
    Check if both groups belong to the same timetable.
    :param group1: first group index
    :param group2: second group index
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a boolean
    """
    return (is_group_in_timetable(group1, groups_in_first_timetable, groups_in_second_timetable) and
            is_group_in_timetable(group2, groups_in_first_timetable, groups_in_second_timetable)) or \
           (is_group_in_timetable(group1, groups_in_first_timetable, groups_in_second_timetable, False) and
            is_group_in_timetable(group2, groups_in_first_timetable, groups_in_second_timetable, False))


def has_no_same_association_club_in_group(clubs_in_group, association, associations):
    """
    Check whether there is no club in clubs_in_group belonging to the association.
    :param clubs_in_group: list of club indexes
    :param association: association code to be checked
    :param associations: association of each club
    :return: a boolean
    """
    already_drawn_clubs_in_group = [club for club in clubs_in_group if club > -1]
    return all([associations[club] != association for club in already_drawn_clubs_in_group])


def is_tv_constraint_satisfied(draw, drawn_club_index, group_candidate, paired_clubs,
                               groups_in_first_timetable, groups_in_second_timetable):
    """
    Check if after assigning the drawn_club into the group_candidate
    the TV constraints about paired clubs are satisfied.
    :param draw: 2-D numpy array containing the current state of the draw
    :param drawn_club_index: index of the drawn club
    :param group_candidate: group candidate to be assigned to the current drawn club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a boolean
    """
    if drawn_club_index in paired_clubs:
        i, j = np.where(draw == paired_clubs[drawn_club_index])
        if (len(i) > 0) and are_groups_in_same_timetable(i[0], group_candidate,
                                                         groups_in_first_timetable, groups_in_second_timetable):
            return False
    return True


def get_numbers_of_pending_clubs_tv_constrained(draw, remaining_clubs, paired_clubs,
                                                groups_in_first_timetable, groups_in_second_timetable):
    """
    Calculate the number of clubs in remaining_clubs having a paired club already drawn
    in both TV timetable group categories.
    Return a pair of integers.
    :param draw: 2-D numpy array containing the current state of the draw
    :param remaining_clubs: list of indexes of the remaining clubs
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a tuple of integers
    """
    clubs_in_19h = 0
    clubs_in_21h = 0
    for c in remaining_clubs:
        if c in paired_clubs:
            g, p = np.where(draw == paired_clubs[c])
            if len(g) > 0:
                if is_group_in_timetable(g[0], groups_in_first_timetable, groups_in_second_timetable):
                    clubs_in_21h += 1
                else:
                    clubs_in_19h += 1
    return clubs_in_19h, clubs_in_21h


def has_no_dead_ends(draw, drawn_club_index, group_candidate, remaining_clubs, groups_available, pot,
                     paired_clubs, associations, groups_in_first_timetable, groups_in_second_timetable):
    """
    Check whether after assigning drawn_club to group,
    there will be a dead end in the draw of remaining_clubs and groups_available.
    :param draw: 2-D numpy array containing the current state of the draw
    :param drawn_club_index: index of the drawn club
    :param group_candidate: group candidate to be assigned to the current drawn club
    :param remaining_clubs: list of indexes of the remaining clubs
    :param groups_available: groups that have not been assigned yet
    :param pot: pot from which the current club has been drawn
    :param paired_clubs: pairs of clubs having opposite timetables
    :param associations: association of each club
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a boolean
    """
    updated_draw = np.copy(draw)
    updated_draw[group_candidate, pot] = drawn_club_index
    remaining_groups = copy_list_and_remove_element(group_candidate, groups_available)
    paired_clubs_in_pot = sum([1 if c in paired_clubs and paired_clubs[c] in remaining_clubs else 0
                               for c in remaining_clubs])
    pairs = paired_clubs_in_pot / 2
    clubs_forced_in_19h, clubs_forced_in_21h = get_numbers_of_pending_clubs_tv_constrained(updated_draw,
                                                                                           remaining_clubs,
                                                                                           paired_clubs,
                                                                                           groups_in_first_timetable,
                                                                                           groups_in_second_timetable)
    groups_in_19h = len([g for g in remaining_groups if is_group_in_timetable(g, groups_in_first_timetable,
                                                                              groups_in_second_timetable)])
    groups_in_21h = len([g for g in remaining_groups if is_group_in_timetable(g, groups_in_first_timetable,
                                                                              groups_in_second_timetable, False)])
    if (groups_in_19h < pairs + clubs_forced_in_19h) or (groups_in_21h < pairs + clubs_forced_in_21h):
        return False
    return exist_maximum_matching(remaining_clubs, remaining_groups, updated_draw, associations,
                                  paired_clubs, groups_in_first_timetable, groups_in_second_timetable)


def get_feasible_groups(draw, drawn_club_index, remaining_clubs, groups_available, pot,
                        associations, paired_clubs, groups_in_first_timetable, groups_in_second_timetable):
    """
    Return the first feasible group for drawn_club satisfying the draw constraints
    about TV timetables, same association clubs, and dead ends.
    The function is prepared to return a list of feasible groups
    in lexicographical order or the index of the first group.
    :param draw: 2-D numpy array contaiing the current state of the draw
    :param drawn_club_index: index of the drawn club
    :param remaining_clubs: list of indexes of the remaining clubs
    :param groups_available: groups that have not been assigned yet
    :param pot: pot from which the current club has been drawn
    :param associations: association of each club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: the list of feasible groups available for the drawn club
    """
    feasible_groups = []
    association = associations[drawn_club_index]
    for group in groups_available:
        if is_tv_constraint_satisfied(draw, drawn_club_index, group,
                                      paired_clubs, groups_in_first_timetable, groups_in_second_timetable):
            if has_no_same_association_club_in_group(draw[group, :], association, associations):
                if has_no_dead_ends(draw, drawn_club_index, group, remaining_clubs, groups_available, pot,
                                    paired_clubs, associations, groups_in_first_timetable, groups_in_second_timetable):
                    feasible_groups.append(group)
                    # return feasible_groups
    return feasible_groups


def check_draw_validity(draw, clubs, associations, paired_clubs, clubs_per_pot, number_of_pots,
                        groups_in_first_timetable, groups_in_second_timetable):
    """
    Check whether or not the draw satisfies all the constraints about
    TV timetables and same association clubs.
    :param draw: a [clubs_per_pot]x[number_of_pots] numpy 2D-array containing club indexes
    :param clubs: list of clubs ordered by association and UEFA ranking
    :param associations: association of each club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param clubs_per_pot: number of clubs in each pot
    :param number_of_pots: number of pots in the draw
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :return: a boolean
    """
    # Checking TV constraints
    for c1, c2 in paired_clubs.items():
        g1, _ = np.where(draw == c1)
        g2, _ = np.where(draw == c2)
        if are_groups_in_same_timetable(g1[0], g2[0], groups_in_first_timetable, groups_in_second_timetable):
            timetable = '19h' if is_group_in_timetable(g1[0], groups_in_first_timetable, groups_in_second_timetable) \
                              else '21h'
            print("Teams %s, %s must be in different timetables, but they are in %s side" % (clubs[c1],
                                                                                             clubs[c2],
                                                                                             timetable))
            return False
    # Checking association constraint
    for group in range(clubs_per_pot):
        valid = len(set([associations[club] for club in draw[group, :]])) == number_of_pots
        if not valid:
            print("Group %s (%s): %s" % (chr(65 + group),
                                         valid,
                                         ", ".join([clubs[club] for club in draw[group, :]])))
            return False
    return True


def simulate_draw(simulations, clubs, clubs_per_pot, number_of_pots, club_pots, associations,
                  paired_clubs, groups_in_first_timetable, groups_in_second_timetable,
                  verbose=False, show_errors=True):
    """
    Simulate the number of draw required.
    :param simulations: The number of draws to be simulated
    :param clubs: list of clubs ordered by association and UEFA ranking
    :param clubs_per_pot: number of clubs in each pot
    :param number_of_pots: number of pots in the draw
    :param club_pots: pot number of each club
    :param associations: association of each club
    :param paired_clubs: pairs of clubs having opposite timetables
    :param groups_in_first_timetable: first list of groups playing the same day
    :param groups_in_second_timetable: second list of groups playing the same day
    :param verbose: Trace the draw development printing pot compositions and clubs drawn
    :param show_errors: Print an error message where a club doesn't have any feasible group
    :return: a [simulations]x[clubs_per_pot]x[number_of_pots] numpy 3D-array containing club indexes
    """
    draws = np.full((simulations, clubs_per_pot, number_of_pots), -1)
    simulation = 0
    while simulation < simulations:
        feasible = True
        draws[simulation] = np.full((clubs_per_pot, number_of_pots), -1)
        draw = draws[simulation]
        for pot_idx in range(number_of_pots):
            clubs_in_pot = [idx for idx, pot in enumerate(club_pots) if pot == pot_idx+1]
            if verbose:
                print("\nPot #%d:%s" % (pot_idx+1, ', '.join([clubs[idx] for idx in clubs_in_pot])))
            groups_available = range(clubs_per_pot)
            while len(clubs_in_pot) > 0:
                drawn_club = np.random.choice(clubs_in_pot)
                clubs_in_pot.remove(drawn_club)
                feasible_groups = get_feasible_groups(draw, drawn_club, clubs_in_pot, groups_available,
                                                      pot_idx, associations, paired_clubs,
                                                      groups_in_first_timetable, groups_in_second_timetable)
                if len(feasible_groups) == 0:
                    if show_errors:
                        print("Not group available for club: %s, %s" % (clubs[drawn_club],
                                                                        groups_available))
                    feasible = False
                    break
                assigned_group = np.random.choice(feasible_groups)  # feasible_groups[0]
                groups_available.remove(assigned_group)
                if verbose:
                    print("\t -> %s to group %d\t%s" % (clubs[drawn_club],
                                                        assigned_group,
                                                        feasible_groups))
                draw[assigned_group, pot_idx] = drawn_club
            if not feasible:
                break
        if feasible and check_draw_validity(draw, clubs, associations, paired_clubs, clubs_per_pot, number_of_pots,
                                            groups_in_first_timetable, groups_in_second_timetable):
            simulation += 1
    return draws


def estimate_probabilities(draws, clubs, club_pots):
    """
    Using all the simulated draws, the probabilities of each pair of club
    to be in the same group are estimated.
    Probabilities are real numbers in the interval [0, 1].
    :param draws: [simulations]x[clubs_per_pot]x[number_of_pots] numpy 3D-array
                   containing the simulated draws
    :param clubs: list of clubs ordered by association and UEFA ranking
    :param club_pots: pot number of each club
    :return: a 48x48 numpy 2D-array containing the probability for each pair of clubs
             belonging to the same group
    """
    simulations = draws.shape[0]
    total_events = float(simulations)  # total number of events
    estimations = np.full((len(clubs), len(clubs)), 0,  dtype=np.float32)  # probability estimations

    # For each pair of teams, calculate the probability of belonging to the same group
    for club in range(len(clubs)):
        pot = club_pots[club]-1  # Pot to which the current team belongs
        rivals = np.array([draws[i, np.where(draws[i, :, :] == club)[0][0], :] for i in range(simulations)])
        estimations[club, club] = 1  # each team has a prob=1 of belonging to its own group
        rivals = rivals.flatten()
        counts = collections.Counter(rivals)
        for rival, counter in counts.items():
            estimations[club, rival] = float(counter)/total_events

    return estimations
