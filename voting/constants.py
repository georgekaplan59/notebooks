# -*- coding: utf-8 -*-

OPTION = 'Option'
VOTES = 'Votes'
SEATS = 'Seats'
CONSTITUENCY = 'Constituency'
CITY = 'City'
REGION = 'Region'
PARTY = 'Party'
OPTION_BLANK_VOTE = 'Votos en blanco'
OPTION_INVALID_VOTE = 'Votos nulos'
OPTION_ABSTENTION = 'Abstención'
IGNORED_OPTION_LIST = [OPTION_ABSTENTION, OPTION_INVALID_VOTE]
NO_PARTY_OPTION_LIST = [unicode(OPTION_ABSTENTION, "utf-8"),
                        unicode(OPTION_INVALID_VOTE, "utf-8"),
                        unicode(OPTION_BLANK_VOTE, "utf-8")]
