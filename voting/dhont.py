import numpy as np
import pandas as pd
from catalonia import get_invalid_vote_literals
from utils import get_constituency_votes


def filter_data_by_minimum_percentage(dataframe, minimum_percentage):
    """
    Filter parties from constituency above of <minimum_percentage> of the valid votes
    :param dataframe: assume at least two columns <opcion> and <votos>
    :param minimum_percentage: float as a percentage non as a ratio
    :return: filtered dataframe
    """
    invalid = get_invalid_vote_literals()
    valid_votes_selector = ~dataframe['opcion'].isin(invalid)
    valid_votes = dataframe[valid_votes_selector]['votos'].sum()
    dataframe['porcentaje'] = 100 * dataframe['votos']/valid_votes
    dataframe['apto'] = dataframe['porcentaje'] > minimum_percentage
    return dataframe[(valid_votes_selector) & (dataframe['apto'])][['opcion', 'votos']]


def assign_constituency_representatives_by_dhont(dataframe, number_of_representatives, minimum_percentage=3.0):
    """
    Distribute <number_of_representatives> seats among the parties included in the rows of the dataframe
    according to the D'Hont proportional procedure
    :param dataframe: assume at least two columns <opcion> and <votos>
    :param number_of_representatives:  integer
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :return: dataframe with a row for each party with a least one seat assigned, indexing by <opcion> and having
            two columns <diputados> and <votos>
    """
    n = number_of_representatives
    df = filter_data_by_minimum_percentage(dataframe, minimum_percentage)
    parties = df['opcion'].tolist()
    votes = df['votos'].tolist()
    dhont_table = np.array([[vote/float(r) for r in range(1, n+1)] for vote in votes])
    seats = np.dstack(np.unravel_index(np.argsort(-dhont_table.ravel()), dhont_table.shape))[0,0:n,0:2]
    party_with_seat_idx = set([x for x,y in seats])
    seats = {parties[idx]:max([(y+1) for x,y in seats if x == idx]) for idx in party_with_seat_idx}
    df = df.set_index('opcion')
    df['diputados'] = pd.Series(seats)
    df.dropna(inplace=True)
    df['diputados'] = df['diputados'].astype('int64')
    return df.sort_values(['diputados'], ascending=False)


def calculate_parliament_by_dhont(dataframe, constituencies, minimum_percentage=3.0):
    """
    For each constituency in <constituencies>, distribute a number of seats among the parties included
    in the rows of the dataframe according to the D'Hont proportional procedure
    :param dataframe: assume two indexes <opcion, provincia> and one column <votos>
    :param constituencies: dictionary with constituency name as keys and number of seats as values
    :param minimum_percentage: float as a percentage non as a ratio. Default value according to the Spanish law
    :return: a sorted dataframe by number of seats assigned having
    """
    votes_by_option = dataframe.groupby(['opcion']).sum()
    parlament = pd.DataFrame(columns=['votos', 'diputados'])
    for constituency, number_of_representatives in constituencies.items():
        constituency_df = get_constituency_votes(dataframe, constituency)
        constituency_df = assign_constituency_representatives_by_dhont(constituency_df,
                                                                       number_of_representatives,
                                                                       minimum_percentage)
        print("%s: %s" % (constituency, constituency_df['diputados'].to_dict()))
        parlament = parlament.append(constituency_df)
    parlament.index.name = 'partido'
    parlament = parlament.reset_index().groupby('partido').sum()
    # Add votes removed by 3% rule for parties with representatives
    for party_with_representative in parlament.index:
        total_votes = votes_by_option.loc[party_with_representative]
        parlament.at[party_with_representative, 'votos'] = total_votes
    return parlament.sort_values(['diputados'], ascending=False)
