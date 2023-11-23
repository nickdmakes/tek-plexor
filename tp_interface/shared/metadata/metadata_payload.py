class MetadataPayload:
    def __init__(self, title: str, artist: str, album: str, year: str, genre: str, track: str, disc: str, comment: str):
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year
        self.genre = genre
        self.track = track
        self.disc = disc
        self.comment = comment

    def __repr__(self):
        return f'MetadataPayload(title={self.title}, artist={self.artist}, album={self.album}, year={self.year}, ' \
               f'genre={self.genre}, track={self.track}, disc={self.disc}, comment={self.comment})'

    def __str__(self):
        return f'MetadataPayload(title={self.title}, artist={self.artist}, album={self.album}, year={self.year}, ' \
               f'genre={self.genre}, track={self.track}, disc={self.disc}, comment={self.comment})'

    def __ne__(self, other):
        if not isinstance(other, MetadataPayload):
            return NotImplemented
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.title, self.artist, self.album, self.year, self.genre, self.track, self.disc, self.comment))
