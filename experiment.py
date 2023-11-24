from pytube import YouTube, Playlist


# Function that takes a YouTube link. If the link is a playlist, it will get the title and artist of each video in the playlist.
# If the link is a single video, it will get the title and artist of that video.
def main():
    url = "https://www.youtube.com/watch?v=BEufF-oBFvc"
    p_url = "https://www.youtube.com/playlist?list=PLKReIDf1n32TCEiEYPyRfoi04ZK-OxCB4"
    if "playlist" in p_url:
        print("playlist")
        playlist = Playlist(p_url)
        for video in playlist.videos:
            yt = YouTube(video.watch_url)
            print(video.watch_url)
            print(video.title)
            print(video.author)
    else:
        yt = YouTube(url)
        print(yt.title)
        print(yt.author)



if __name__ == "__main__":
    main()
