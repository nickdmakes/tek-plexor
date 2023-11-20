from pytube import YouTube


class YTAudioDownloadException(Exception):
    """Raised when there's a problem downloading audio"""
    pass


class YTTitleRetrievalException(Exception):
    """Raised when there's a problem retrieving a video title"""
    pass


# get the title of a YouTube video
def get_title(url: str):
    try:
        yt = YouTube(url)
        info = yt.vid_info
        title = info['videoDetails']['title']
        artist = info['videoDetails']['author']
        full_title = artist + ' - ' + title
        return full_title
    except Exception as e:
        raise YTAudioDownloadException(e)


def download_single_audio(url: str, file_name: str, out_path="./"):
    try:
        yt = YouTube(url)
        all_streams = yt.streams.filter(only_audio=True, audio_codec="opus")
        sorted_streams = sorted(all_streams, key=lambda stream: stream.abr)
        return sorted_streams[0].download(filename=file_name, output_path=out_path)
    except Exception as e:
        raise YTAudioDownloadException(e)
