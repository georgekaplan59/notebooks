# -*- coding: utf-8 -*-
def get_antivote_category(row, xpath):
    return row.xpath(xpath).extract()[0]


def get_party(row):
    return row.xpath("./th/text()").extract()[0]


def get_votes(row, xpath):
    votes_str = row.xpath(xpath).extract()
    votes_str = votes_str[0].replace('.', '') if len(votes_str) == 1 else 0
    return int(votes_str)


def get_antivotes(row, number_of_elements):
    votes_str = row.xpath("./td[@class='s15']/text()").extract()
    votes_str = votes_str[0].replace('.', '') if len(votes_str) == number_of_elements else 0
    return int(votes_str)


def get_list_of_regions_by_province():
    return {'Barcelona': [u'Alt Penedès', 'Anoia', 'Bages', 'Baix Llobregat', u'Barcelonès', u'Berguedà',
                          'Garraf', 'Maresme', u'Moianès', 'Osona', u'Vallès Occidental', u'Vallès Oriental'],
            'Girona': [u'Alt Empordà', u'Baix Empordà', 'Cerdanya', 'Garrotxa', u'Gironès', "Pla de l'Estany",
                       u'Ripollès', 'Selva', 'Osona'],
            'Lleida': [u'Alta Ribagorça', 'Alt Urgell', 'Cerdanya', 'Garrigues', 'Noguera', u'Pallars Jussà',
                       u'Pallars Sobirà', "Pla d'Urgell", 'Segarra', u'Segrià', u'Solsonès', 'Urgell', "Aran"],
            'Tarragona': ['Alt Camp', 'Baix Camp', 'Baix Ebre', u'Baix Penedès', u'Conca de Barberà',
                          "Ribera d'Ebre", u'Montsià', 'Priorat', u'Tarragonès', 'Terra Alta']}


def get_province_for_regions_dict():
    province_region_dict = get_list_of_regions_by_province()
    return {region: province for province, regions in province_region_dict.items() for region in regions}
