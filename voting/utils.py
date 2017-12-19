def get_constituency_votes(dataframe, constituency):
    """
    Select the rows in <dataframe> matching the value <constituency> in its index
    :param dataframe: assume a dataframe with an index containing the value <constituency>
    :param constituency: the index value by which the dataframe will be filtered
    :return: a filtered dataframe with the remaining indexes as columns
    """
    return dataframe.loc[constituency].reset_index()
