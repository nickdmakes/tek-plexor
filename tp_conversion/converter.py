import os
from ffmpeg import FFmpeg, FFmpegError
from mutagen.mp4 import MP4


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


def add_tags_mp4(file, title, artist):
    tag_file = MP4(file)
    # tag_file.tags['\xa9nam'] = s_title # potentially another way to do this
    tag_file.update({'\xa9nam': title})
    tag_file.update({'\xa9ART': artist})
    tag_file.save()


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
