import numpy as np
import pandas as pd
from utils import get_constituency_votes
from constants import *


def filter_data_by_minimum_percentage(dataframe, minimum_percentage):
    """
    Filter parties from constituency above of <minimum_percentage> of the valid votes
    :param dataframe: assume at least two columns <OPTION> and <VOTES>
    :param minimum_percentage: float as a percentage non as a ratio
    :return: filtered dataframe
    """
    valid_votes_selector = ~dataframe[OPTION].isin(IGNORED_OPTION_LIST)
    valid_votes = dataframe[valid_votes_selector][VOTES].sum()
    dataframe['porcentaje'] = 100 * dataframe[VOTES] / valid_votes
    dataframe['apto'] = dataframe['porcentaje'] > minimum_percentage
    no_blank_votes = ~(dataframe[OPTION] == OPTION_BLANK_VOTE)
    return dataframe[(valid_votes_selector) & (no_blank_votes) & (dataframe['apto'])][[OPTION, VOTES]]


def get_allowed_formulas():
    """
    Allowed formulae are: d'Hondt, Sainte-Lague, Modified Sainte-Lague, Danish, Imperiali
    :return: a list of strings
    """
    return ["d'Hondt", 'Sainte-Lague', 'Modified Sainte-Lague', 'Danish', 'Imperiali']


def get_divisors(formula, number_of_representatives):
    """
    Generate the list of divisors to calculate the apportionment by a highest averages formula
    :param number_of_representatives:  integer
    :param formula: apportionment rule.
                     Valid values: d'Hondt, Sainte-Lague, Modified Sainte-Lague, Danish, Imperiali
    :return: a list of floats or integers depending on the strategy
    """
    if formula == "d'Hondt":
        return range(1, number_of_representatives + 1)
    elif formula == 'Sainte-Lague':
        return range(1, 2*number_of_representatives + 1, 2)
    elif formula == 'Modified Sainte-Lague':
        return [(10*n-5)/7.0 if n > 1 else 1 for n in range(1, number_of_representatives+1)]
    elif formula == 'Danish':
        return range(1, 3 * number_of_representatives - 1, 3)
    elif formula == 'Imperiali':
        return [(n+1)/2.0 for n in range(1, number_of_representatives + 1)]
    else:
        raise ValueError("formula parameter must be one of the following values: %s" % ", ".join(get_allowed_formulas()))


def assign_constituency_representatives(dataframe, number_of_representatives, formula="d'Hondt", minimum_percentage=3.0):
    """
    Distribute <number_of_representatives> seats among the parties included in the rows of the dataframe
    according to the <formula> proportional procedure
    :param dataframe: assume at least two columns <OPTION> and <VOTES>
    :param number_of_representatives:  integer
    :param formula: apportionment rule.
                    Valid values: d'Hondt, Sainte-Lague, Modified Sainte-Lague, Danish, Imperiali
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :return: dataframe with a row for each party with a least one seat assigned, indexing by <OPTION> and
             having two columns <SEATS> and <VOTES>
    """
    n = number_of_representatives
    df = filter_data_by_minimum_percentage(dataframe, minimum_percentage)
    parties = df[OPTION].tolist()
    votes = df[VOTES].tolist()
    divisors = get_divisors(formula, n)
    averages_table = np.array([[vote/float(r) for r in divisors] for vote in votes])
    seats = np.dstack(np.unravel_index(np.argsort(-averages_table.ravel()), averages_table.shape))[0, 0:n, 0:2]
    party_with_seat_idx = set([x for x, y in seats])
    seats = {parties[idx]:max([(y+1) for x, y in seats if x == idx]) for idx in party_with_seat_idx}
    df = df.set_index(OPTION)
    df[SEATS] = pd.Series(seats)
    df.dropna(inplace=True)
    df[SEATS] = df[SEATS].astype('int64')
    return df.sort_values([SEATS], ascending=False)


def calculate_parliament(dataframe, constituencies, formula="d'Hondt", minimum_percentage=3.0, verbose=True):
    """
    For each constituency in <constituencies>, distribute a number of seats among the parties included
    in the rows of the dataframe according to the <formula> for proportional representation
    :param dataframe: assume two indexes <OPTION, CONSTITUENCY> and one column <VOTES>
    :param constituencies: dictionary with constituency name as keys and number of seats as values
    :param formula: apportionment rule.
                    Valid values: d'Hondt, Sainte-Lague, Modified Sainte-Lague, Danish, Imperiali
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :param verbose: if True it is shown the apportionment details by constituency
    :return: a sorted dataframe by number of seats assigned having
    """
    votes_by_option = dataframe.groupby([OPTION]).sum()
    parlament = pd.DataFrame(columns=[VOTES, SEATS])
    for constituency, number_of_representatives in constituencies.items():
        constituency_df = get_constituency_votes(dataframe, constituency)
        constituency_df = assign_constituency_representatives(constituency_df,
                                                              number_of_representatives,
                                                              formula,
                                                              minimum_percentage)
        if verbose:
            print("%s: %s" % (constituency, constituency_df[SEATS].to_dict()))
        parlament = parlament.append(constituency_df)
    parlament.index.name = PARTY
    parlament = parlament.reset_index().groupby(PARTY).sum()
    # Add votes removed by 3% rule for parties with representatives
    for party_with_representative in parlament.index:
        total_votes = votes_by_option.loc[party_with_representative]
        parlament.at[party_with_representative, VOTES] = total_votes
    return parlament.sort_values([SEATS], ascending=False)
