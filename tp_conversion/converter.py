import os
from ffmpeg import FFmpeg, Progress, FFmpegError


class AudioConversionException(Exception):
    """Raised when an audio conversion fails"""
    pass


def opus_to_m4a2(in_file: str, out_file: str, delete_in_file: bool = True):
    try:
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(in_file)
            .output(
                out_file,
                {"codec:a": "libfdk_aac", "vbr": 5, "cutoff": 18000},
            )
        )
        ffmpeg.execute()
        if delete_in_file:
            os.remove(in_file)
    except FFmpegError as e:
        raise AudioConversionException(e)


# function to convert opus to m4a
def opus_to_m4a(in_file: str, out_file: str, delete_in_file: bool = True):
    try:
        cmd = f'ffmpeg -y -i {in_file} -c:a libfdk_aac -vbr 5 -cutoff 18000 {out_file}'
        os.system(cmd)
        if delete_in_file:
            os.remove(in_file)
    except Exception as e:
        raise AudioConversionException(e)
