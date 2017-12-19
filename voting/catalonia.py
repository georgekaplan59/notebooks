# -*- coding: utf-8 -*-
def get_invalid_vote_literals():
    return ['Abstención', 'Votos nulos']


def get_blank_vote():
    return 'Votos en blanco'


def get_party_blocks_list():
    """
    Tuple containing the lists of parties belonging to each ideology
    """
    return get_pro_independence_parties(), ["C's", 'PSC', 'CatSíqueesPot', 'PP']


def get_pro_independence_parties():
    """
    Parties of pro-independence ideology
    """
    return ['JxSí', 'CUP']


def split_parliament(parliament_df):
    """
    Group parliament composition by anti-independence vs pro-independence
    """
    pro_independence = get_pro_independence_parties()
    votes = parliament_df['votos'].to_dict()
    deputies = parliament_df['diputados'].to_dict()
    const_votes = sum([v for k,v in votes.items() if k not in pro_independence])
    indep_votes = sum([v for k,v in votes.items() if k in pro_independence])
    const_diput = sum([v for k,v in deputies.items() if k not in pro_independence])
    indep_diput = sum([v for k,v in deputies.items() if k in pro_independence])
    return {'no-independentistas': {'votos': const_votes, 'diputados': const_diput},
            'independentistas':  {'votos': indep_votes, 'diputados': indep_diput}}
