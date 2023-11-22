import os
from tp_engine.yt_api import download_single_audio
from tp_conversion.converter import convert_to_m4a
from tp_interface.app import start_app

url = "https://www.youtube.com/watch?v=VWoIpDVkOH0"


def main():
    # out_file = download_single_audio(url, out_path="data", file_name="test.opus")
    # print(out_file)
    # convert_to_m4a(out_file, out_file.replace(".opus", ".m4a"), delete_in_file=True)

    start_app()


if __name__ == '__main__':
    main()
