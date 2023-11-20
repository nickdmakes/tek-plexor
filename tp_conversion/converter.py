import os


class AudioConversionException(Exception):
    """Raised when an audio conversion fails"""
    pass


# function to convert opus to m4a
def opus_to_m4a(in_file: str, out_file: str, delete_in_file: bool = True):
    try:
        cmd = f'ffmpeg -y -i {in_file} -c:a libfdk_aac -vbr 5 -cutoff 18000 {out_file}'
        os.system(cmd)
        if delete_in_file:
            os.remove(in_file)
    except Exception as e:
        raise AudioConversionException(e)
