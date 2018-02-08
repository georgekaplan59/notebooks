# -*- coding: utf-8 -*-
from catalonia import split_parliament, PRO_INDEPENDENCE, NO_INDEPENDENCE
from constants import *
from sklearn.linear_model import LinearRegression
import numpy as np
from math import pow, sqrt


def calculate_votes_and_seats_percentages(parliament_df, total_votes_df):
    """
    Calculate the percentages of votes and seats for each party from the input dataframes
    :param parliament_df: dataframe having as index: <PARTY> and as columns: <VOTES, SEATS>.
                          Just parties with at least one seat are included
    :param total_votes_df: dataframe having as index: <OPTION> and a column: <VOTES>.
                           All parties with votes are included
    :return: a list of tuples containing (percentage of votes, percentage of seats)
    """
    valid_votes_options = set(total_votes_df.index).difference(set(IGNORED_OPTION_LIST))
    parties_with_seat = set(parliament_df.index)
    parties_with_votes_no_seat = valid_votes_options.difference(parties_with_seat)
    if OPTION_BLANK_VOTE in parties_with_votes_no_seat:
        parties_with_votes_no_seat.remove(OPTION_BLANK_VOTE)

    total_valid_votes = total_votes_df.loc[valid_votes_options].sum()[0]
    vote_percentages = 100 * parliament_df[VOTES] / total_valid_votes
    deputy_percentages = 100 * parliament_df[SEATS] / parliament_df[SEATS].sum()
    percentages = zip(vote_percentages.tolist(), deputy_percentages.tolist())
    no_seat_percentages = (100*(total_votes_df.loc[parties_with_votes_no_seat] / total_valid_votes))[VOTES]
    return percentages + [(r, 0) for r in no_seat_percentages]


def calculate_rae_index(vote_seat_percentages_list):
    """
    Calculate the Rae index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return sum([abs(v-s) for v, s in vote_seat_percentages_list])/float(len(vote_seat_percentages_list))


def calculate_loosemore_hanby_index(vote_seat_percentages_list):
    """
    Calculate the Loosemore-Hanby index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return sum([abs(v-s) for v, s in vote_seat_percentages_list])/2.0


def calculate_gallagher_index(vote_seat_percentages_list):
    """
    Calculate the Gallagher index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return sqrt(sum([pow(v - s, 2) for v, s in vote_seat_percentages_list])/2.0)


def calculate_effective_number_of_parties(vote_seat_percentages_list):
    """
    Calculate the effective number of parties as used by adjusted Loosemore-Hanby (Grofman) index of disproportionality.
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a dictionary using the keys EFFECTIVE_NUMBER_OF_PARTIES_BY_VOTES and EFFECTIVE_NUMBER_OF_PARTIES_BY_SEATS
    """
    n_v = 1.0/sum([pow(v/100.0, 2) for v, s in vote_seat_percentages_list])
    n_s = 1.0/sum([pow(s/100.0, 2) for v, s in vote_seat_percentages_list])
    return {EFFECTIVE_NUMBER_OF_PARTIES_BY_VOTES: n_v,  EFFECTIVE_NUMBER_OF_PARTIES_BY_SEATS: n_s}


def calculate_grofman_index(vote_seat_percentages_list):
    """
    Calculate the adjusted Loosemore-Hanby (Grofman) index of disproportionality.
    There is two ways to calculate this index. Here the effective number of parties by the ratio of votes is used.
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    summatory = sum([abs(v-s) for v, s in vote_seat_percentages_list])
    effective_number_of_parties = calculate_effective_number_of_parties(vote_seat_percentages_list)
    return summatory/effective_number_of_parties[EFFECTIVE_NUMBER_OF_PARTIES_BY_VOTES]


def calculate_lijphart_index(vote_seat_percentages_list):
    """
    Calculate the Lijphart index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return max([abs(v-s) for v, s in vote_seat_percentages_list])


def calculate_saint_lague_index(vote_seat_percentages_list):
    """
    Calculate the Saint-Lague index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return sum([pow(v - s, 2)/v for v, s in vote_seat_percentages_list])


def calculate_dhondt_index(vote_seat_percentages_list):
    """
    Calculate the D'Hondt index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    return max([s/v for v, s in vote_seat_percentages_list])


def calculate_cox_shugart_index(vote_seat_percentages_list):
    """
    Calculate the Cox-Shugart (regression) index of disproportionality
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    model = LinearRegression(fit_intercept=False)
    X = np.array([v for v, s in vote_seat_percentages_list]).reshape(-1, 1)
    y = np.array([s for v, s in vote_seat_percentages_list])
    model.fit(X, y)
    b = model.coef_[0]
    return b


def calculate_disproportionality_indexes(parliament_df, total_votes_df, verbose=True, include_catalan=False):
    """
    Print all the disproportionality measurements
    :param parliament_df: dataframe having as index: <PARTY> and as columns: <VOTES, SEATS>.
                          Just parties with at least one seat are included
    :param total_votes_df: dataframe having as index: <option> and a column: <VOTES>.
                           All parties with votes are included
    :param verbose: output index values
    :param include_catalan: boolean if Catalan indicators are included
    :return: dictionary containing all the indexes
    """
    percentage_pairings = calculate_votes_and_seats_percentages(parliament_df, total_votes_df)
    indicators = {'rae': calculate_rae_index(percentage_pairings),
                  'loosemore_hanby': calculate_loosemore_hanby_index(percentage_pairings),
                  'gallagher': calculate_gallagher_index(percentage_pairings),
                  'grofman': calculate_grofman_index(percentage_pairings),
                  'lijphart': calculate_lijphart_index(percentage_pairings),
                  'saint_lague': calculate_saint_lague_index(percentage_pairings),
                  'dhondt': calculate_dhondt_index(percentage_pairings),
                  'cox_shugart': calculate_cox_shugart_index(percentage_pairings)}
    if include_catalan:
        blocks = split_parliament(parliament_df)
        indicators['indep_s'] = blocks[PRO_INDEPENDENCE][SEATS]
        indicators['no_indep_s'] = blocks[NO_INDEPENDENCE][SEATS]
        indicators['indep_v'] = blocks[PRO_INDEPENDENCE][VOTES]
        indicators['no_indep_v'] = blocks[NO_INDEPENDENCE][VOTES]

    if verbose:
        print("Índice de Rae:             %.3f" % indicators['rae'])
        print("Índice de Loosemore-Hanby: %.3f" % indicators['loosemore_hanby'])
        print("Índice de Gallagher:       %.3f" % indicators['gallagher'])
        print("Índice de Grofman:         %.3f" % indicators['grofman'])
        print("Índice de Lijphart:        %.3f" % indicators['lijphart'])
        print("Índice de Saint-Lague:     %.3f" % indicators['saint_lague'])
        print("Índice de D'Hondt:         %.3f" % indicators['dhondt'])
        print("Índice de Cox-Shugart:     %.3f" % indicators['cox_shugart'])
        if include_catalan:
            print("#diputados (indepes):      %d" % indicators['indep_s'])
            print("#diputados (no-indepes):   %d" % indicators['no_indep_s'])
            print("#votos     (indepes):      %d" % indicators['indep_v'])
            print("#votos     (no-indepes):   %d" % indicators['no_indep_v'])

    return indicators
