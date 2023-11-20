from pytube import YouTube


class YTAudioDownloadException(Exception):
    """Raised when there's a problem downloading audio"""
    pass


def download_single_audio(url: str, file_name: str, out_path="./"):
    try:
        yt = YouTube(url)
        all_streams = yt.streams.filter(only_audio=True, audio_codec="opus")
        sorted_streams = sorted(all_streams, key=lambda stream: stream.abr)
        return sorted_streams[0].download(filename=file_name, output_path=out_path)
    except Exception as e:
        raise YTAudioDownloadException(e)
