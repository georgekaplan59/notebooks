import networkx as nx
import numpy as np
from utils import copy_list_and_remove_element


def is_valid_knockout_draw(fixtures):
    """
    A draw is valid if each game confronts teams belonging to different countries and different groups.
    :param fixtures: the set of matches to be checked
    :return: a boolean
    """
    return all([w.group != r.group and w.country != r.country for w, r in fixtures])


def filter_winners(runner_up, winners):
    """
    Valid winners for the runner_up club are those having different association and
    having played in a different group in the previous stage.
    :param runner_up: list of Team instances for runner-up clubs
    :param winners: list of Team instances for winner clubs
    :return: a filtered list of winners
    """
    return filter(lambda w: w.group != runner_up.group and w.country != runner_up.country, winners)


def has_no_dead_end_winner(winner, winners_pot, remaining_runners):
    """
    Drawing winner from the winners_pot against the current runner_up would not lead to a dead end.
    :param winner: candidate Team to be drawn
    :param winners_pot: list of Team instances for winner clubs remaining in the pot
    :param remaining_runners: list of Team instances for remaining runner-up clubs
    :return: a boolean
    """
    remaining_winners = copy_list_and_remove_element(winner, winners_pot)
    return exist_maximum_matching_for_knockout(remaining_runners, remaining_winners)


def remove_winners_leading_to_dead_ends(eligible_winners, winners_pot, runner_up, runners_up_pot):
    """
    From the list eligible_winners must be removed those clubs leading to dead ends in the draw.
    :param eligible_winners: candidate Team to be drawn
    :param winners_pot: list of Team instances for winner clubs remaining in the pot
    :param runner_up: runner-up club just drawn
    :param runners_up_pot: list of Team instances for remaining runner-up clubs
    :return: a filtered list of winners
    """
    remaining_runners = copy_list_and_remove_element(runner_up, runners_up_pot)
    return filter(lambda w: has_no_dead_end_winner(w, winners_pot, remaining_runners), eligible_winners)


def exist_maximum_matching_for_knockout(remaining_runners, remaining_winners):
    """
    A bipartite graph is built using remaining_runners clubs (first class) and
    remaining_winners clubs (second class). For each club in the first class, eligible clubs
    from the second class are calculated, and for each of these pairs of nodes (1st class, 2nd class)
    an edge is built. If the maximum matching for this bipartite graph is exactly the sum of
    the sizes of remaining_runners and remaining_winners, then there is no dead ends yet.
    :param remaining_runners: list of Team instances for remaining runner-up clubs
    :param remaining_winners: list of Team instances for remaining winner clubs
    :return: a boolean
    """
    graph = nx.Graph()
    size = len(remaining_runners)
    graph.add_nodes_from(range(size), bipartite=0)
    graph.add_nodes_from(range(size, 2*size), bipartite=1)
    for idx, r in enumerate(remaining_runners):
        for fw in filter_winners(r, remaining_winners):
            w_idx = remaining_winners.index(fw)
            graph.add_edge(idx, w_idx + size)
    max_size = len(nx.algorithms.bipartite.maximum_matching(graph))
    return max_size == 2 * size


def unfold_probability_tree(pot1, pot2, pairings, log_probability, depth=1):
    """
    Recursively build the full probability tree for the draw taking into account the constraints.
    For perfomance reasons:
    - A generator is used to avoid memory issues.
    - Bipartite graphs and maximum matching algorithm are used just after the second pairing,
      because Chelsea, being the most constrained club in the draw, has three elegible rivals.
    To avoid accuracy problems logarithmic probability is used as input parameter but a common
    probability value is returned as output.
    :param pot1: list of Team instances for runner-up clubs
    :param pot2: list of Team instances for winner clubs
    :param pairings: dictionary of fixtures
    :param log_probability: cumulative log_probability
    :param depth: counter for the tree depth
    :return: a generator returning valid branches for the knockout draw
    """
    if len(pot1) == 0 or len(pot2) == 0:
        yield (pairings, np.exp(log_probability))
    else:
        p1 = -np.log(len(pot1))
        for runner_up in pot1:
            new_pot1 = copy_list_and_remove_element(runner_up, pot1)
            eligible_winners = filter_winners(runner_up, pot2)
            if depth > 2:
                eligible_winners = remove_winners_leading_to_dead_ends(eligible_winners, pot2,
                                                                       runner_up, pot1)
            p2 = -np.log(len(eligible_winners))
            new_log_probability = log_probability + p1 + p2
            for winner in eligible_winners:
                new_pairings = pairings.copy()
                new_pairings[runner_up] = winner
                new_pot2 = copy_list_and_remove_element(winner, pot2)
                for x in unfold_probability_tree(new_pot1, new_pot2, new_pairings,
                                                 new_log_probability, depth + 1):
                    yield x


def build_html_table(runners_up, winners, probabilities):
    """
    Build the HTML code for a table showing the probabilities for each fixture
    :param runners_up: list of Team instances for runner-up clubs
    :param winners: list of Team instances for winner clubs
    :param probabilities:  array containing the fixture probabilities
    :return: the HTML table
    """
    html = "<table>"
    html += "<tr><td>&nbsp;</td>"
    html += "<td><b>%s</b></td>" % ("</b></td><td><b>".join([x.name for x in runners_up]))
    html += "<td>CHECK</td></tr>"

    for w_idx in range(len(winners)):
        html += "<tr><td><b>%s</b></td>" % winners[w_idx].name
        html += "<td>%s</td>" % "</td><td>".join(["%.1f%%" % (x) for x in probabilities[w_idx, :]])
        html += "<td>%.1f%%</td></tr>" % sum(probabilities[w_idx, :])

    html += "<tr><td>CHECK</td>"
    html += "<td>%s</td><td>&nbsp;</td></tr>" % ("</td><td>".join(["%.1f%%" % (sum(probabilities[:, x]))
                                                                   for x in range(len(runners_up))]))
    html += "</table>"
    return html
