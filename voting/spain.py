import pandas as pd
import numpy as np
import os
import re
from constants import *
from disproportionality import calculate_disproportionality_indexes
from disproportionality import calculate_votes_and_seats_percentages
from disproportionality import calculate_effective_number_of_parties
from dhont import assign_constituency_representatives_by_dhont


def convert_dict_to_df(dictionary):
    df = pd.DataFrame.from_dict(dictionary, orient='index')
    df.index.names = [DATE, SINGLE_CONSTITUENCY]
    df.reset_index(inplace=True)
    pd.to_datetime(df[DATE])
    df.index = df[DATE]
    del df[DATE]
    return df


def calculate_dispr_indexes_and_parties():
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
        parliament_single_cons = assign_constituency_representatives_by_dhont(spain_df,
                                                                              total_seats_in_parliament,
                                                                              minimum_percentage=0.0)
        d = calculate_disproportionality_indexes(parliament_single_cons, df_total_votes, verbose=False)
        vote_seat_percentages_list = calculate_votes_and_seats_percentages(parliament_single_cons, df_total_votes)
        dispr[(election_date, True)] = d
        seats[(election_date, True)] = {SEATS: parliament_single_cons.shape[0]}
        eff_n_parties[(election_date, True)] = calculate_effective_number_of_parties(vote_seat_percentages_list)

    dispr_df = convert_dict_to_df(dispr)
    dispr_df[['rae', 'loosemore_hanby', 'gallagher', 'grofman',
              'lijphart', 'saint_lague', 'dhont', 'cox_shugart']].round(3)
    seats_df = convert_dict_to_df(seats)
    eff_n_parties_df = convert_dict_to_df(eff_n_parties)

    return dispr_df, seats_df, eff_n_parties_df


def get_parliaments_by_election(year, month, threshold=0.0):
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
    virtual = assign_constituency_representatives_by_dhont(spain_df, total_seats_in_parliament,
                                                           minimum_percentage=threshold)
    virtual[VOTES + '_%'] = np.round(100.0 * virtual[VOTES] / total_valid_votes, 2)
    virtual[SEATS + '_%'] = np.round(100.0 * virtual[SEATS] / total_seats_in_parliament, 2)
    virtual = virtual.join(names)
    virtual.sort_values([SEATS, VOTES], ascending=False, inplace=True)
    parliament.set_index(PARTY, inplace=True)
    virtual.set_index(PARTY, inplace=True)

    return parliament[columns], virtual[columns]
