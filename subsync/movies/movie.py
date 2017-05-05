class Movie:
    """
    represents movie, 1<->1 with imdb id
    todo merge this with imdbpy when it fully supports py3
    """
    def __init__(self, name=None, imdb_id=None, metadata=None):
        self.name = name
        self.imdb_id = imdb_id
        self.metadata = metadata or dict()
