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

<!-- LICENSE -->
## License

See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Nick Matthews - nickd.mf7@gmail.com  
Soma Szabo - [soma emaio]

Project Link: [https://github.com/dj-devtek/tek-plexor](https://github.com/dj-devtek/tek-plexor)

<p align="right">(<a href="#top">back to top</a>)</p>
