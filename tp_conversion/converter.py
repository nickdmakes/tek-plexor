import os
from ffmpeg import FFmpeg, FFmpegError
from mutagen.mp4 import MP4
from mutagen.mp3 import EasyMP3 as MP3
from mutagen.oggopus import OggOpus


class AudioConversionException(Exception):
    """Raised when an audio conversion fails"""
    pass


class FileExistsException(Exception):
    """Raised when a (converted) file already exists"""
    def __init__(self, message, filename: str = None):
        super().__init__(message)
        self.message = message
        self.filename = filename
    
    def __str__(self):
        return f"{self.message} ({self.filename})"
    
    def __repr__(self):
        return f"{self.message} ({self.filename})"


class EncoderMappings:
    # mapping of file container to highest quality encoder
    MAPPINGS = {
        "ogg": "libopus",
        "m4a": "aac",
        "mp4": "aac",
        "mp3": "libmp3lame",
    }
    
    def __init__(self, container: str):
        self._container = container
    
    def get_encoder(self):
        return self.MAPPINGS[self._container]


def add_tags_mp4(file, title, artist):
    tag_file = MP4(file)
    # tag_file.tags['\xa9nam'] = s_title # potentially another way to do this
    tag_file.update({'\xa9nam': title})
    tag_file.update({'\xa9ART': artist})
    tag_file.save()


def add_tags_mp3(file, title, artist):
    tag_file = MP3(file)
    tag_file["title"] = title
    tag_file["artist"] = artist
    tag_file.save()


def add_tags_ogg(file, title, artist):
    tag_file = OggOpus(file)
    tag_file.update({"title": title})
    tag_file.update({"artist": artist})
    tag_file.save()


def add_tags(file, params: dict):
    format = params["compression"]
    if format == "m4a" or format == "mp4":
        add_tags_mp4(file, params["title"], params["artist"])
    elif format == "mp3":
        add_tags_mp3(file, params["title"], params["artist"])
    elif format == "ogg":
        add_tags_ogg(file, params["title"], params["artist"])
    else:
        raise AudioConversionException(f"Unsupported file format: {format}")


def convert(file: str, params: dict):
    base, ext = os.path.splitext(file)
    while os.path.splitext(base)[1] != "":
        base, ext = os.path.splitext(base)
    conv_file = f"{base}.{params['compression']}"
    
    if os.path.exists(conv_file):
        raise FileExistsException(f"File already exists", conv_file)
    
    encoder = EncoderMappings(params["compression"]).get_encoder()
    bitrate = str(params["bitrate"]) + "k"
    try:
        # "q:a": 2 is highest option, range is [0.1:2]
        # this is almost the same as b:a because aac will always be variable bitrate so even 320k b:a will be adjusted a little
        # q:a will override b:a so either use one or the other
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(file)
            .output(
                conv_file,
                {"c:a": encoder, "b:a": bitrate},
            )
        )
        ffmpeg.execute()
        if params["delete_og"]:
            os.remove(file)
    except FFmpegError as e:
        raise AudioConversionException(e)
    
    # TODO have an option in params to add tags or not
    add_tags(conv_file, params)


# converts a file to m4a and adds tags
def convert_to_m4a(in_file: str, title: str, artist: str, delete_in_file: bool = True):
    base, ext = os.path.splitext(in_file)
    while os.path.splitext(base)[1] != "":
        base, ext = os.path.splitext(base)
    conv_file = f'{base}.m4a'
    
    if os.path.exists(conv_file):
        raise FileExistsException(f"File already exists", conv_file)
    
    try:
        # cutoff will hard limit the frequency to whatever is specified
        # "cutoff": 18000
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(in_file)
            .output(
                conv_file,
                {"c:a": "aac", "b:a": "320k"},
            )
        )
        ffmpeg.execute()
        if delete_in_file:
            os.remove(in_file)
    except FFmpegError as e:
        raise AudioConversionException(e)

    add_tags_mp4(conv_file, title, artist)


# function to convert opus to m4a
def opus_to_m4a_cmd(in_file: str, out_file: str, delete_in_file: bool = True):
    try:
        cmd = f'ffmpeg -y -i {in_file} -c:a libfdk_aac -vbr 5 -cutoff 18000 {out_file}'
        os.system(cmd)
        if delete_in_file:
            os.remove(in_file)
    except Exception as e:
        raise AudioConversionException(e)
