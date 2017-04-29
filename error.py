class Error(Exception):
    pass

class TermError(Error):
    pass

class GrammarError(Error):
    pass

class ProductionSearchError(Error):
    pass