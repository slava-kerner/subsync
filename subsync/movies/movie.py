class Movie:
    """
    represents movie, 1<->1 with imdb id
    todo merge this with imdbpy when it fully supports py3
    """
    def __init__(self, name=None, imdb_id=None, metadata=None):
        self.name = name
        self.imdb_id = imdb_id
        self.metadata = metadata or dict()


class MovieYoutube:
    """ represents 1 youtube """
    def __init__(self, id=None, movie=None, lng_audio=None, captions=None):
        """
        :param id: youtube_id 
        :param movie: instance of Movie 
        :param lng_audio:
        :param captions: [languages]
        """
        self.id = id
        self.movie = movie
        self.lng_audio = lng_audio
        self.captions = captions
        

class MovieFull:
    """
    represents 1 movie with youtube instances 
    """
    def __init__(self, movie, videos=None, subs=None):
        """
        
        :param movie: Movie 
        :param videos: [MovieYoutube]
        :param subs: MovieSubs
        """
        self.movie = movie
        self.videos = videos
        self.subs = subs
