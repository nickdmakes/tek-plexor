from pytube import YouTube, Playlist


# Function that takes a YouTube link. If the link is a playlist, it will get the title and artist of each video in the playlist.
# If the link is a single video, it will get the title and artist of that video.
def main():
    url = input("Enter a YouTube link: ")
    if "playlist" in url:
        playlist = Playlist(url)
        for video in playlist.videos:
            yt = YouTube(video)
            print(yt.title)
            print(yt.author)
    else:
        yt = YouTube(url)
        print(yt.title)
        print(yt.author)



if __name__ == "__main__":
    main()
