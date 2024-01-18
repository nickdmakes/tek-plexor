from pytube import YouTube, Playlist
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import time


class YTAudioDownloadException(Exception):
    """Raised when there's a problem downloading audio"""
    pass


class YTTitleRetrievalException(Exception):
    """Raised when there's a problem retrieving a video title"""
    pass


class YtInfoPayload:
    """
    Payload for YouTube video info
        :param info: list of tuples containing (title, artist, url)
        :param is_playlist: whether the info is for a playlist
    """
    def __init__(self, info: list[tuple[str, str, str]], is_playlist: bool):
        self.info = info
        self.is_playlist = is_playlist


def get_yt_info_from_link(url: str):
    """
    Retrieves info for a YouTube link
        :param url: the YouTube video url
        :returns: YTInfoPayload
    """
    try:
        if "playlist" in url:
            playlist = Playlist(url)
            if not playlist.video_urls:
                raise YTTitleRetrievalException("Couldn't retrieve any video urls from playlist")
            playlist_videos = get_playlist_videos(playlist)
            info_list = []
            for title, author, info_artist, video_url in playlist_videos:
                optimized_info = optimize_yt_info(title,
                                                  author,
                                                  info_artist=info_artist,
                                                  url=video_url)
                info_list.append(optimized_info)
            return YtInfoPayload(info_list, True)
        else:
            yt = YouTube(url)
            optimized_info = optimize_yt_info(yt.title,
                                              yt.author,
                                              yt.vid_info['videoDetails']['author'],
                                              yt.watch_url)
            return YtInfoPayload([optimized_info], False)
    except Exception as e:
        raise YTTitleRetrievalException(e)


# asynchronous function to get video info. Called by get_playlist_videos
def get_playlist_video_info_fn(url):
    yt = YouTube(url)
    return yt.title, yt.author, yt.vid_info['videoDetails']['author'], yt.watch_url


# Parsing a Playlist object requires creating a new YouTube object for each video in the playlist.
# This is slow, so we use a ThreadPoolExecutor to make it A LOT faster.
def get_playlist_videos(playlist: Playlist):
    start = time.time()
    processes = []
    with ThreadPoolExecutor(max_workers=cpu_count()-1) as executor:
        for url in playlist.video_urls:
            processes.append(executor.submit(get_playlist_video_info_fn, url))

    video_titles = []
    for task in as_completed(processes):
        video_titles.append(task.result())

    end = time.time()
    print(f"Time elapsed: {end - start}")
    return video_titles


def optimize_yt_info(title: str, author: str, info_artist: str, url: str):
    author = author.strip()
    artist = author
    if artist == "":
        artist = info_artist

    title = title.strip()
    split_title = title.split("-")
    if len(split_title) < 2:
        title = split_title[0].strip()
    elif len(split_title) > 2:
        # keep title as is and use author as artist
        pass
    else:
        title = split_title[1].strip()
        temp_artist = split_title[0].strip()
        if artist == "":
            artist = temp_artist
        elif artist != temp_artist and temp_artist != "":
            # replace artist with filed to left of dash
            artist = temp_artist

    # add the author if it's not the same as the artist
    if artist != info_artist and info_artist != "":
        artist += f" ({info_artist})"

    return title, artist, url


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
        return stream.download(filename=filename, output_path=out_path, skip_existing=True), filename
    except Exception as e:
        raise YTAudioDownloadException(e)
