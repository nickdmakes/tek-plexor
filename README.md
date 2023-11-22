<!-- PROJECT LOGO -->
<div align="center">
<h1 align="center">TekPlexor</h1>

  <p align="center">
    High quality audio download tool
    <br />
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

TekPlexor was inspired by the lack of online audio downloading tools. 
Existing tools make it difficult to retrieve multiple songs at once and are often low quality. 

TekPlexor eliminates the hassle with an easy-to-use interface, leveraging ffmpeg under the hood
to bring out the best sound.

### Built With

* Python Language
* PyQt6
* PyTube


<!-- GETTING STARTED -->
## Getting Started - Development

### Prerequisites

#### poetry
poetry is a virtual environment and package manager tool used to organize TexPlexor development. Instructions for install can be found [here](https://python-poetry.org/docs/)

#### ffmpeg
In the code, Python makes system calls to the ffmpeg tool for audio codec conversion. You will need to have this tool installed on your machine for the app to work.
Instructions for install can be found [here](https://ffmpeg.org/download.html)

### Installation

1. Clone the repo and navigate into the directory
   ```sh
   git clone https://github.com/dj-devtek/tek-plexor.git
   cd tek-plexor
   ```
3. Configure and install the environemt

   First, poetry needs to be configured to add the venv directly to the project directory (optional)
   ```sh
   poetry config virtualenvs.in-project true
   ```

   Now, setup the venv and install the packages required for the application
   ```sh
   poetry install --no-root
   ```

### Development
Start by activating the virtual environment

##### Mac
```sh
source .venv/bin/activate
```
##### Windows
```sh
.venv\Scripts\activate
```

To open the PyQt6 designer editor, run
```sh
pyqt6-tools designer
```
pyqt6 .ui files can be found under **tek-plexor/tp_interface/ui**. Once you have saved new changes in designer, convert the .ui file to Python with the following command **from the tp_interface directory**...
```sh
pyuic6 -o main_window_ui.py -x ui/main_window.ui
```

<!-- RESOURCES -->
## Resources
[Pytube Docs](https://pytube.io/en/latest/api.html)

[WEBM to MP3](https://stackoverflow.com/questions/72679106/how-to-convert-in-memory-webm-audio-file-to-mp3-audio-file-in-python)

[FFMPEG Encodings](https://trac.ffmpeg.org/wiki/Encode/HighQualityAudio)

[MP4 Tags (Mutagen)](https://mutagen.readthedocs.io/en/latest/api/mp4.html)

[Opus Tags](https://www.opus-codec.org/docs/)

[eyed3 Docs](https://eyed3.readthedocs.io/en/latest/)

[Youtube Formats](https://gist.github.com/AgentOak/34d47c65b1d28829bb17c24c04a0096f)

<!-- LICENSE -->
## License

See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Nick Matthews - nickd.mf7@gmail.com  
Soma Szabo - [soma emaio]

Project Link: [https://github.com/dj-devtek/tek-plexor](https://github.com/dj-devtek/tek-plexor)

<p align="right">(<a href="#top">back to top</a>)</p>
