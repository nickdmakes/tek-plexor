import os

class YtDownloadPayload:
    # class/static variables for keys
    URL = "url"
    TITLE = "title"
    ARTIST = "artist"
    CONVERSION_ENABLED = "conversion_enabled"
    COMPRESSION = "compression"
    BITRATE = "bitrate"
    DELETE_OG = "delete_og"
    OUT_PATH = "out_path"
    ADD_TAGS = "add_tags"
    
    BIT_RATES = [96, 128, 192, 256, 320]
    FORMATS = ["ogg", "m4a", "mp4", "mp3"]
    FORMAT_OGG = 0
    FORMAT_M4A = 1
    FORMAT_MP4 = 2
    FORMAT_MP3 = 3
    OGG = "ogg"
    M4A = "m4a"
    MP4 = "mp4"
    MP3 = "mp3"
    
    def __init__(self):
        self.payload = {
            self.URL: "",
            self.TITLE: "",
            self.ARTIST: "",
            self.CONVERSION_ENABLED: True,
            self.COMPRESSION: self.M4A,
            self.BITRATE: 320,
            self.DELETE_OG: False,
            self.OUT_PATH: "",
            self.ADD_TAGS: True
        }
    
    def __init__(self, url: str = "", title: str = "", artist: str = "", conversion_enabled: bool = True,
                 compression: str = M4A, bitrate: int = 320, delete_og: bool = False, out_path: str = ""):
        self.payload = {
            self.URL: url,
            self.TITLE: title,
            self.ARTIST: artist,
            self.CONVERSION_ENABLED: conversion_enabled,
            self.COMPRESSION: compression,
            self.BITRATE: bitrate,
            self.DELETE_OG: delete_og,
            self.OUT_PATH: out_path,
            self.ADD_TAGS: True
        }
    
    def isValid(self):
        reason = ""
        if self.payload[self.URL] == "":
            reason += "URL field is empty"
        if self.payload[self.TITLE] == "":
            if reason != "":
                reason += ", "
            reason += "Title field is empty"
        if self.payload[self.ARTIST] == "":
            if reason != "":
                reason += ", "
            reason += "Artist field is empty"
        if self.payload[self.OUT_PATH] == "":
            if reason != "":
                reason += ", "
            reason += "Destination field is empty"
        if not os.path.exists(self.payload[self.OUT_PATH]):
            if reason != "":
                reason += ", "
            reason += "Destination folder does not exist"
        if self.payload[self.COMPRESSION] not in self.FORMATS:
            if reason != "":
                reason += ", "
            reason += "Invalid compression format"
        if self.payload[self.BITRATE] not in self.BIT_RATES:
            if reason != "":
                reason += ", "
            reason += "Invalid bitrate"
        return reason == "", reason
    
    def getPayload(self):
        return self.payload


class MetadataPayload:
    # class/static variables for keys
    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"
    YEAR = "year"
    GENRE = "genre"
    TRACK = "track"
    DISC = "disc"
    COMMENT = "comment"
    
    def __init__(self):
        self.payload = {
            self.TITLE: "",
            self.ARTIST: "",
            self.ALBUM: "",
            self.YEAR: "",
            self.GENRE: "",
            self.TRACK: "",
            self.DISC: "",
            self.COMMENT: ""
        }
    
    def __init__(self, title: str = "", artist: str = "", album: str = "", year: str = "",
                 genre: str = "", track: str = "", disc: str = "", comment: str = ""):
        self.payload = {
            self.TITLE: title,
            self.ARTIST: artist,
            self.ALBUM: album,
            self.YEAR: year,
            self.GENRE: genre,
            self.TRACK: track,
            self.DISC: disc,
            self.COMMENT: comment
        }
    
    def getPayload(self):
        return self.payload
    
    def __str__(self):
        return f'MetadataPayload(title={self.payload[self.TITLE]}, artist={self.payload[self.ARTIST]}, ' \
               f'album={self.payload[self.ALBUM]}, year={self.payload[self.YEAR]}, ' \
               f'genre={self.payload[self.GENRE]}, track={self.payload[self.TRACK]}, ' \
               f'disc={self.payload[self.DISC]}, comment={self.payload[self.COMMENT]})'
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, MetadataPayload):
            return NotImplemented
        return self.payload == other.payload
    
    def __ne__(self, other):
        if not isinstance(other, MetadataPayload):
            return NotImplemented
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.payload[self.TITLE], self.payload[self.ARTIST], self.payload[self.ALBUM],
                     self.payload[self.YEAR], self.payload[self.GENRE], self.payload[self.TRACK],
                     self.payload[self.DISC], self.payload[self.COMMENT]))
