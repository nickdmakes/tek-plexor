from pytube import YouTube


class YTAudioDownloadException(Exception):
    """Raised when there's a problem downloading audio"""
    pass


class YTTitleRetrievalException(Exception):
    """Raised when there's a problem retrieving a video title"""
    pass


def get_title(url: str):
    try:
        yt = YouTube(url)
        info = yt.vid_info
        info_title = info['videoDetails']['title'].strip()
        info_artist = info['videoDetails']['author'].strip()
        
        author = yt.author.strip()
        artist = author
        if artist == "":
            artist = info_artist
        
        title = yt.title.strip()
        split_title = title.split("-")
        if len(split_title) < 2:
            title = split_title[0].strip()
        else:
            temp_artist = split_title[0].strip()
            if artist == "":
                artist = temp_artist
            elif artist != temp_artist and temp_artist != "":
                # replace artist with filed to left of dash
                artist = temp_artist
            title = split_title[1].strip()
        
        # add the author if it's not the same as the artist
        if artist != info_artist and info_artist != "":
            artist += f" ({info_artist})"
        
        return (title, artist)
    except Exception as e:
        raise YTAudioDownloadException(e)


def download_single_audio(url: str, filename: str, out_path="./"):
    try:
        yt = YouTube(url)
        all_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        # debug
        for stream in all_streams:
            print(stream)
        
        # extension handling
        stream = all_streams.first()
        ext = stream.subtype
        filename += f".{ext}"
        return (stream.download(filename=filename, output_path=out_path, skip_existing=True), filename)
    except Exception as e:
        raise YTAudioDownloadException(e)
