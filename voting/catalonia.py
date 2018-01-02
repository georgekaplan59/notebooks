# -*- coding: utf-8 -*-
from constants import *


PRO_INDEPENDENCE = 'Independentistas'
NO_INDEPENDENCE = 'No-independentistas'


def get_party_blocks_list():
    """
    Tuple containing the lists of parties belonging to each ideology
    """
    return get_pro_independence_parties(), ["C's", 'PSC', 'CatSíqueesPot', 'PP']


def get_pro_independence_parties():
    """
    Parties of pro-independence ideology
    """
    return ['JxSí', 'CUP', 'JUNTSxCAT', 'ERC-CatSí', 'Govern']


def split_parliament(parliament_df):
    """
    Group parliament composition by anti-independence vs pro-independence
    """
    pro_independence = get_pro_independence_parties()
    votes = parliament_df[VOTES].to_dict()
    deputies = parliament_df[SEATS].to_dict()
    const_votes = sum([v for k, v in votes.items() if k not in pro_independence])
    indep_votes = sum([v for k, v in votes.items() if k in pro_independence])
    const_diput = sum([v for k, v in deputies.items() if k not in pro_independence])
    indep_diput = sum([v for k, v in deputies.items() if k in pro_independence])
    return {NO_INDEPENDENCE: {VOTES: const_votes, SEATS: const_diput},
            PRO_INDEPENDENCE:  {VOTES: indep_votes, SEATS: indep_diput}}


def join_govern_parties(df):
    """
    Create a new dataframe joining the rows beloging to ERC and JxCat
    :param df: original dataframe
    :return: new dataframe with some rows grouped and renamed as 'Govern'
    """
    govern_selector = df.index.get_level_values(OPTION).isin(['ERC-CatSí', 'JUNTSxCAT'])
    govern_df = df[govern_selector].groupby(CONSTITUENCY).sum()
    govern_df[OPTION] = 'Govern'
    govern_df.set_index(OPTION, append=True, inplace=True)
    no_govern_df = df[~govern_selector]
    return no_govern_df.append(govern_df)
