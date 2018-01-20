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


def assign_constituency_representatives_by_dhont(dataframe, number_of_representatives, minimum_percentage=3.0):
    """
    Distribute <number_of_representatives> seats among the parties included in the rows of the dataframe
    according to the D'Hont proportional procedure
    :param dataframe: assume at least two columns <OPTION> and <VOTES>
    :param number_of_representatives:  integer
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :return: dataframe with a row for each party with a least one seat assigned, indexing by <OPTION> and
             having two columns <SEATS> and <VOTES>
    """
    n = number_of_representatives
    df = filter_data_by_minimum_percentage(dataframe, minimum_percentage)
    parties = df[OPTION].tolist()
    votes = df[VOTES].tolist()
    dhont_table = np.array([[vote/float(r) for r in range(1, n+1)] for vote in votes])
    seats = np.dstack(np.unravel_index(np.argsort(-dhont_table.ravel()), dhont_table.shape))[0,0:n,0:2]
    party_with_seat_idx = set([x for x,y in seats])
    seats = {parties[idx]:max([(y+1) for x,y in seats if x == idx]) for idx in party_with_seat_idx}
    df = df.set_index(OPTION)
    df[SEATS] = pd.Series(seats)
    df.dropna(inplace=True)
    df[SEATS] = df[SEATS].astype('int64')
    return df.sort_values([SEATS], ascending=False)


def calculate_parliament_by_dhont(dataframe, constituencies, minimum_percentage=3.0):
    """
    For each constituency in <constituencies>, distribute a number of seats among the parties included
    in the rows of the dataframe according to the D'Hont proportional procedure
    :param dataframe: assume two indexes <OPTION, CONSTITUENCY> and one column <VOTES>
    :param constituencies: dictionary with constituency name as keys and number of seats as values
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :return: a sorted dataframe by number of seats assigned having
    """
    votes_by_option = dataframe.groupby([OPTION]).sum()
    parlament = pd.DataFrame(columns=[VOTES, SEATS])
    for constituency, number_of_representatives in constituencies.items():
        constituency_df = get_constituency_votes(dataframe, constituency)
        constituency_df = assign_constituency_representatives_by_dhont(constituency_df,
                                                                       number_of_representatives,
                                                                       minimum_percentage)
        print("%s: %s" % (constituency, constituency_df[SEATS].to_dict()))
        parlament = parlament.append(constituency_df)
    parlament.index.name = PARTY
    parlament = parlament.reset_index().groupby(PARTY).sum()
    # Add votes removed by 3% rule for parties with representatives
    for party_with_representative in parlament.index:
        total_votes = votes_by_option.loc[party_with_representative]
        parlament.at[party_with_representative, VOTES] = total_votes
    return parlament.sort_values([SEATS], ascending=False)
