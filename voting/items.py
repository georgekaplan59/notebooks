import scrapy


class VotesByRegionItem(scrapy.Item):
    opcion = scrapy.Field()
    votos = scrapy.Field()
    comarca = scrapy.Field()
    provincia = scrapy.Field()


class VotesByTownItem(scrapy.Item):
    opcion = scrapy.Field()
    votos = scrapy.Field()
    municipio = scrapy.Field()
    provincia = scrapy.Field()


def build_data_item(opcion, votos, provincia, municipio=None, comarca=None):
    data_item = VotesByTownItem() if municipio else VotesByRegionItem()
    data_item['opcion'] = opcion
    data_item['votos'] = votos
    data_item['provincia'] = provincia
    if municipio:
        data_item['municipio'] = municipio
    if comarca:
        data_item['comarca'] = comarca
    return data_item
