import pandas as pd
import numpy as np
import os
import re
from constants import *
from disproportionality import calculate_disproportionality_indexes
from disproportionality import calculate_votes_and_seats_percentages
from disproportionality import calculate_effective_number_of_parties
from apportionment import calculate_parliament, assign_constituency_representatives, get_allowed_formulas


def convert_dict_to_df(dictionary, names=(DATE, SINGLE_CONSTITUENCY)):
    """
    Transform a dictionary into a pandas.Dataframe setting DATE as the index
    :param dictionary: the dictionary to be transformed
    :param names: a tuple of strings containing dictionary keys to be used as the dataframe index
    :return: a dataframe with DATE as index, remaining elements in <names> become columns into the dataframe
    """
    df = pd.DataFrame.from_dict(dictionary, orient='index')
    df.index.names = list(names)
    df.reset_index(inplace=True)
    pd.to_datetime(df[DATE])
    df.index = df[DATE]
    del df[DATE]
    return df


def calculate_dispr_indexes_and_parties():
    """
    Estimate a set disproportionality indexes, the number of parties with at least one seat in Parliament and
    the effective number of parties in legislature for all the legislative elections in Spain from 1977.
    :return: a 3-tuple of dataframes with a double index (a string containing year and month, and a boolean for
             single district;). and
             - The first dataframe containing the following columns: rae, loosemore_hanby, gallagher, grofman, lijphart,
                                                                     saint_lague, dhondt, cox_shugart.
             - The second dataframe containing a single columns: SEATS
             - The third dataframe containing two columns: EFFECTIVE_NUMBER_OF_PARTIES_BY_VOTES and
                                                           EFFECTIVE_NUMBER_OF_PARTIES_BY_SEATS
    """
    dispr = {}
    seats = {}
    eff_n_parties = {}

    directory = "./data/"
    elections = [f for f in os.listdir(directory) if re.match(r'spanish_congress_\d{4}_\d{2}', f)]

    for election in elections:
        matching = re.match(r'spanish_congress_(\d{4})_(\d{2})', election)
        election_date = "%s-%s" % (matching.group(1), matching.group(2))

        df = pd.read_csv('./data/%s' % election)
        total_seats_in_parliament = df.groupby([REGION, CONSTITUENCY]).sum()[SEATS].sum()

        spain_df = df[[OPTION, VOTES, SEATS]].groupby(OPTION).sum()
        spain_df = spain_df.sort_values([SEATS, VOTES], ascending=False).reset_index()
        df_total_votes = spain_df.set_index(OPTION)
        parliament = spain_df[spain_df[SEATS] > 0]
        parliament = parliament.set_index(OPTION)

        # Actual parliament config
        d = calculate_disproportionality_indexes(parliament, df_total_votes, verbose=False)
        vote_seat_percentages_list = calculate_votes_and_seats_percentages(parliament, df_total_votes)
        dispr[(election_date, False)] = d
        seats[(election_date, False)] = {SEATS: spain_df[spain_df[SEATS] > 0].shape[0]}
        eff_n_parties[(election_date, False)] = calculate_effective_number_of_parties(vote_seat_percentages_list)

        # Single constituency parliament config
        parliament_single_cons = assign_constituency_representatives(spain_df,
                                                                     total_seats_in_parliament,
                                                                     formula="d'Hondt",
                                                                     minimum_percentage=0.0)
        d = calculate_disproportionality_indexes(parliament_single_cons, df_total_votes, verbose=False)
        vote_seat_percentages_list = calculate_votes_and_seats_percentages(parliament_single_cons, df_total_votes)
        dispr[(election_date, True)] = d
        seats[(election_date, True)] = {SEATS: parliament_single_cons.shape[0]}
        eff_n_parties[(election_date, True)] = calculate_effective_number_of_parties(vote_seat_percentages_list)

    dispr_df = convert_dict_to_df(dispr)
    dispr_df[['rae', 'loosemore_hanby', 'gallagher', 'grofman',
              'lijphart', 'saint_lague', 'dhondt', 'cox_shugart']].round(3)
    seats_df = convert_dict_to_df(seats)
    eff_n_parties_df = convert_dict_to_df(eff_n_parties)

    return dispr_df, seats_df, eff_n_parties_df


def calculate_disproportionality_indexes_by_formula():
    """
    Estimate a set disproportionality indexes for all the legislative elections in Spain from 1977 and for all the
    electoral formulas returned by <pre>get_allowed_formulas</pre>. The case for a single constituency with no
    electoral threshold is calculated.
    :return: a dataframe with a double index (a string containing year and month, and the formula used) and the
             following columns: rae, loosemore_hanby, gallagher, grofman, lijphart, saint_lague, dhondt, cox_shugart.
    """
    dispr = {}
    directory = "./data/"
    elections = [f for f in os.listdir(directory) if re.match(r'spanish_congress_\d{4}_\d{2}', f)]
    formulas = get_allowed_formulas()
    for election in elections:
        matching = re.match(r'spanish_congress_(\d{4})_(\d{2})', election)
        election_date = "%s-%s" % (matching.group(1), matching.group(2))

        df = pd.read_csv('./data/%s' % election)
        constituencies = df[[CONSTITUENCY, SEATS]].groupby(by=CONSTITUENCY).agg({SEATS: sum}).to_dict()[SEATS]
        total_seats_in_parliament = df.groupby([REGION, CONSTITUENCY]).sum()[SEATS].sum()
        dataframe = df[[CONSTITUENCY, OPTION, VOTES]].set_index([CONSTITUENCY, OPTION])

        spain_df = df[[OPTION, VOTES, SEATS]].groupby(OPTION).sum()
        spain_df = spain_df.sort_values([SEATS, VOTES], ascending=False).reset_index()
        df_total_votes = spain_df.set_index(OPTION)

        # Actual parliament config
        for formula in formulas:
            parliament = calculate_parliament(dataframe, constituencies, formula=formula, verbose=False)
            d = calculate_disproportionality_indexes(parliament, df_total_votes, verbose=False)
            dispr[(election_date, formula)] = d

        # Single constituency parliament config
        parliament_single_cons = assign_constituency_representatives(spain_df,
                                                                     total_seats_in_parliament,
                                                                     formula="d'Hondt",
                                                                     minimum_percentage=0.0)
        d = calculate_disproportionality_indexes(parliament_single_cons, df_total_votes, verbose=False)
        dispr[(election_date, 'Single Constituency')] = d

    dispr_df = convert_dict_to_df(dispr, names=(DATE, 'Formula'))
    dispr_df[['rae', 'loosemore_hanby', 'gallagher', 'grofman',
              'lijphart', 'saint_lague', 'dhondt', 'cox_shugart']].round(3)

    return dispr_df


def get_parliaments_by_election(year, month, threshold=0.0):
    """
    Return the parliament compositions calculated using the current law and the d'Hondt formula for a single
    district with the <threshold>
    :param year: year of the election
    :param month: month of the election
    :param threshold: minimum percentage to enter in the apportionment
    :return: A 2-tuple of dataframes containing party, votes (number and percentage) and seats (number and percentage)
    """
    names = pd.read_csv('./data/spanish_congress_party_names.csv')
    names = names[names[YEAR] == year][[ACRONYM, PARTY]]
    names.set_index(ACRONYM, inplace=True)
    columns = [VOTES, VOTES_PERCENTAGE, SEATS, SEATS_PERCENTAGE]

    df = pd.read_csv('./data/spanish_congress_%d_%02d.csv' % (year, month))
    total_seats_in_parliament = df.groupby([REGION, CONSTITUENCY]).sum()[SEATS].sum()
    total_valid_votes = df[~df[OPTION].isin(IGNORED_OPTION_LIST)][VOTES].sum()

    # Actual parliament config
    spain_df = df[[OPTION, VOTES, SEATS]].groupby(OPTION).sum()
    spain_df = spain_df.sort_values([SEATS, VOTES], ascending=False).reset_index()
    parliament = spain_df[spain_df[SEATS] > 0]
    parliament = parliament.set_index(OPTION)
    parliament[VOTES + '_%'] = np.round(100.0 * parliament[VOTES] / total_valid_votes, 2)
    parliament[SEATS + '_%'] = np.round(100.0 * parliament[SEATS] / total_seats_in_parliament, 2)
    parliament = parliament.join(names)
    parliament.sort_values([SEATS, VOTES], ascending=False, inplace=True)

    # Single constituency parliament config
    virtual = assign_constituency_representatives(spain_df,
                                                  total_seats_in_parliament,
                                                  formula="d'Hondt",
                                                  minimum_percentage=0.0)
    virtual[VOTES + '_%'] = np.round(100.0 * virtual[VOTES] / total_valid_votes, 2)
    virtual[SEATS + '_%'] = np.round(100.0 * virtual[SEATS] / total_seats_in_parliament, 2)
    virtual = virtual.join(names)
    virtual.sort_values([SEATS, VOTES], ascending=False, inplace=True)
    parliament.set_index(PARTY, inplace=True)
    virtual.set_index(PARTY, inplace=True)

    return parliament[columns], virtual[columns]


def get_parliaments_by_election_and_formula(year, month, formulas, threshold=3.0):
    """
    Return the parliament compositions calculated using the <formulas> and the <threshold>
    :param year: year of the election
    :param month: month of the election
    :param formulas: list of electoral formulas to convert votes into seats
    :param threshold: minimum percentage to enter in the apportionment
    :return: a n-tuple of dataframes containing party, votes (number and percentage) and seats (number and percentage)
    """
    names = pd.read_csv('./data/spanish_congress_party_names.csv')
    names = names[names[YEAR] == year][[ACRONYM, PARTY]]
    names.set_index(ACRONYM, inplace=True)
    columns = [VOTES, VOTES_PERCENTAGE, SEATS, SEATS_PERCENTAGE]

    df = pd.read_csv('./data/spanish_congress_%d_%02d.csv' % (year, month))
    constituencies = df[[CONSTITUENCY, SEATS]].groupby(by=CONSTITUENCY).agg({SEATS: sum}).to_dict()[SEATS]
    total_seats_in_parliament = df.groupby([REGION, CONSTITUENCY]).sum()[SEATS].sum()
    total_valid_votes = df[~df[OPTION].isin(IGNORED_OPTION_LIST)][VOTES].sum()

    parliaments = []

    # Actual parliament config
    spain_df = df[[OPTION, VOTES, SEATS]].groupby(OPTION).sum()
    spain_df = spain_df.sort_values([SEATS, VOTES], ascending=False).reset_index()
    parliament = spain_df[spain_df[SEATS] > 0]
    parliament = parliament.set_index(OPTION)
    parliament[VOTES + '_%'] = np.round(100.0 * parliament[VOTES] / total_valid_votes, 2)
    parliament[SEATS + '_%'] = np.round(100.0 * parliament[SEATS] / total_seats_in_parliament, 2)
    parliament = parliament.join(names)
    parliament.sort_values([SEATS, VOTES], ascending=False, inplace=True)
    parliaments.append(parliament[columns])

    # formulas
    dataframe = df[[CONSTITUENCY, OPTION, VOTES]].set_index([CONSTITUENCY, OPTION])
    for formula in formulas:
        apportionment = calculate_parliament(dataframe, constituencies, formula=formula,
                                             minimum_percentage=threshold, verbose=False)
        apportionment[VOTES + '_%'] = np.round(100.0 * apportionment[VOTES] / total_valid_votes, 2)
        apportionment[SEATS + '_%'] = np.round(100.0 * apportionment[SEATS] / total_seats_in_parliament, 2)
        apportionment = apportionment.join(names)
        apportionment.sort_values([SEATS, VOTES], ascending=False, inplace=True)
        #apportionment.set_index(PARTY, inplace=True)
        parliaments.append(apportionment[columns])

    # Single constituency parliament config
    virtual = assign_constituency_representatives(spain_df,
                                                  total_seats_in_parliament,
                                                  formula="d'Hondt",
                                                  minimum_percentage=0.0)
    virtual[VOTES + '_%'] = np.round(100.0 * virtual[VOTES] / total_valid_votes, 2)
    virtual[SEATS + '_%'] = np.round(100.0 * virtual[SEATS] / total_seats_in_parliament, 2)
    virtual = virtual.join(names)
    virtual.sort_values([SEATS, VOTES], ascending=False, inplace=True)
    parliament.set_index(PARTY, inplace=True)
    #virtual.set_index(PARTY, inplace=True)
    parliaments.append(virtual[columns])

    return tuple(parliaments)
