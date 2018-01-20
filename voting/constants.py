# -*- coding: utf-8 -*-

OPTION = 'Option'
VOTES = 'Votes'
VOTES_PERCENTAGE = 'Votes_%'
SEATS = 'Seats'
SEATS_PERCENTAGE = 'Seats_%'
CONSTITUENCY = 'Constituency'
CITY = 'City'
REGION = 'Region'
PARTY = 'Party'
DATE = 'Date'
ACRONYM = 'Acronym'
YEAR = 'Year'
SINGLE_CONSTITUENCY = 'Single_Constituency'
EFFECTIVE_NUMBER_OF_PARTIES_BY_VOTES = 'N_v'
EFFECTIVE_NUMBER_OF_PARTIES_BY_SEATS = 'N_s'
OPTION_BLANK_VOTE = 'Votos en blanco'
OPTION_INVALID_VOTE = 'Votos nulos'
OPTION_ABSTENTION = 'Abstención'
IGNORED_OPTION_LIST = [OPTION_ABSTENTION, OPTION_INVALID_VOTE]
NO_PARTY_OPTION_LIST = [unicode(OPTION_ABSTENTION, "utf-8"),
                        unicode(OPTION_INVALID_VOTE, "utf-8"),
                        unicode(OPTION_BLANK_VOTE, "utf-8")]
LEFT = 'Left'
CENTER_RIGHT = 'Center-right'
NATIONALIST = 'Nationalist'
SOBERANIST = 'Pro-independence'
ECOLOGIST = 'Ecologist'
