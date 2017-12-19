# -*- coding: utf-8 -*-
from catalonia import get_invalid_vote_literals, get_blank_vote, split_parliament
from sklearn.linear_model import LinearRegression
import numpy as np
from math import pow, sqrt


def calculate_votes_and_seats_percentages(parliament_df, total_votes_df):
    """
    Calculate the percentages of votes and seats for each party from the input dataframes
    :param parliament_df: dataframe having as index: <partido> and as columns: <votos, diputados>. Just parties with
                          at leaast one seat are included
    :param total_votes_df: dataframe having as index: <option> and a column: <votos>. All parties with votes are
                           included
    :return: a list of tuples containing (percentage of votes, percentage of seats)
    """
    valid_votes_options = set(total_votes_df.index).difference(set(get_invalid_vote_literals()))
    parties_with_seat = set(parliament_df.index)
    parties_with_votes_no_seat = valid_votes_options.difference(parties_with_seat)
    parties_with_votes_no_seat.remove(get_blank_vote())

    total_valid_votes = total_votes_df.loc[valid_votes_options].sum()[0]
    vote_percentages = 100 * parliament_df['votos'] / total_valid_votes
    deputy_percentages = 100 * parliament_df['diputados'] / parliament_df['diputados'].sum()
    percentages = zip(vote_percentages.tolist(), deputy_percentages.tolist())
    no_seat_percentages = (100 * (total_votes_df.loc[parties_with_votes_no_seat] / total_valid_votes))['votos']
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


def calculate_grofman_index(vote_seat_percentages_list):
    """
    Calculate the adjusted Loosemore-Hanby (Grofman) index of disproportionality.
    As there is two ways to calculate this index, the minimum of them is returned
    :param vote_seat_percentages_list: list of tuples containing (percentage of votes, percentage of seats)
    :return: a float (percentages, instead of shares, are used)
    """
    summatory = sum([abs(v-s) for v, s in vote_seat_percentages_list])
    n_v = 1.0/sum([pow(v/100.0, 2) for v, s in vote_seat_percentages_list])
    n_s = 1.0/sum([pow(s/100.0, 2) for v, s in vote_seat_percentages_list])
    return min(summatory/n_v, summatory/n_s)


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


def calculate_dhont_index(vote_seat_percentages_list):
    """
    Calculate the D'Hont index of disproportionality
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


def calculate_disproportionality_indexes(parliament_df, total_votes_df, verbose=True):
    """
    Print all the disproportionality measurements
    :param parliament_df: dataframe having as index: <partido> and as columns: <votos, diputados>. Just parties with
                          at leaast one seat are included
    :param total_votes_df: dataframe having as index: <option> and a column: <votos>. All parties with votes are
                           included
    :param verbose: output index values
    :return: dictionary containing all the indexes
    """
    percentage_pairings = calculate_votes_and_seats_percentages(parliament_df, total_votes_df)
    I = calculate_rae_index(percentage_pairings)
    D = calculate_loosemore_hanby_index(percentage_pairings)
    G = calculate_gallagher_index(percentage_pairings)
    D_adj = calculate_grofman_index(percentage_pairings)
    L = calculate_lijphart_index(percentage_pairings)
    SL = calculate_saint_lague_index(percentage_pairings)
    DH = calculate_dhont_index(percentage_pairings)
    b = calculate_cox_shugart_index(percentage_pairings)
    blocks = split_parliament(parliament_df)
    id = blocks['independentistas']['diputados']
    nid = blocks['no-independentistas']['diputados']
    iv = blocks['independentistas']['votos']
    niv = blocks['no-independentistas']['votos']
    if verbose:
        print("Índice de Rae:             %.3f" % I)
        print("Índice de Loosemore-Hanby: %.3f" % D)
        print("Índice de Gallagher:       %.3f" % G)
        print("Índice de Grofman:         %.3f" % D_adj)
        print("Índice de Lijphart:        %.3f" % L)
        print("Índice de Saint-Lague:     %.3f" % SL)
        print("Índice de D'Hont:          %.3f" % DH)
        print("Índice de Cox-Shugart:     %.3f" % b)
        print("#diputados (indepes):      %d" % id)
        print("#diputados (no-indepes):   %d" % nid)
        print("#votos     (indepes):      %d" % iv)
        print("#votos     (no-indepes):   %d" % niv)
    return {'rae': I, 'loosemore_hanby': D, 'gallagher': G, 'grofman': D_adj, 'lijphart': L, 'saint_lague': SL,
            'dhont': DH, 'cox_shugart': b, 'indep_d': id, 'no_indep_d': nid, 'indep_v': iv, 'no_indep_v': niv}
