class Team:
    """
    Team representation storing club information regarding:
        - short name
        - association/country to which the club belongs
        - group in the previous stage of the Champions League
    """
    def __init__(self, name, country, group):  # Constructor
        self.name = name
        self.country = country
        self.group = group

    def __repr__(self):  # String representation of instances
        return '{} ({}, {})'.format(self.name, self.group, self.country)

    def __hash__(self):  # Required for list.index working
        return hash((self.name, self.country, self.group))

    def __eq__(self, other):  # Required for list.index working
        try:
            return (self.name, self.country, self.group) == (other.name, other.country, other.group)
        except AttributeError:
            return NotImplemented
