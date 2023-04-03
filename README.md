<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/YourLocalAsian/SCRATCH">
    <img src="Jing Poolian.png" alt="Logo" width="350" height="200">
  </a>

<h1 align="center">SCRATCH</h1>
<h2 align="center">Shot Consultation and Refinement Applied Through Computer Hardware</h2>
<h4><a href="https://www.youtube.com/playlist?list=PLlgu_g88BshhSsnBhApKZGy7s1Rak5IEG">View YouTube Playlist</a></h3>
</br>
</div>

<!-- ABOUT THE PROJECT -->
# About The Project

The game of billiards, commonly known as pool, is enjoyed by millions of players daily. In many situations, the game of billiards can serve as an icebreaker and a facilitator of social interactions between different people. In other situations, the game is played competitively by professional athletes. Nevertheless, there are many people who cannot reap the social benefits of the game due to a lack of proficiency. Additionally, there has not been any significant effort to include visually impaired individuals in the game by making it accessible to them. While there have been a couple of papers written, information is scarce and the projects were never commercialized. This creates two problems: (1) there exists a proficiency wall that beginners face and find difficult to overcome when trying to play the game of billiards and (2) visually impaired personnel are excluded from the game, regardless of talent or ability. As engineers, it is our job to solve such problems through technology.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Usage

## Normal Mode
### Non-Blind Mode
1. Ensure that all peripherals are powered on
2. Place the HUD on the user's head
3. Have them stand near the table with the cue stick lying flat on the table
4. Navigate to the CCU Final Application folder
    ```sh
    cd '.\CCU\Final_Application\'
    ```

5. Run the main program without any arguments
    ```sh
    python3 .\SCRATCH.py
    ```

6. Follow the audio prompts played on the HUD to enter non-blind mode

<br>

### Blind Mode
1. Ensure that all peripherals are powered on
2. Assist the blind user in putting the HUD on their head
3. Place both the cue stick and glove flat on the cue table
4. Have the blind user place their hands on the cue stick buttons and glove in order for them to start using SCRATCH
5. Navigate to the CCU Final Application folder
    ```sh
    cd '.\CCU\Final_Application\'
    ```

6. Run the main program without any arguments
    ```sh
    python .\SCRATCH.py
    ```
7. Follow the audio prompts played on the HUD to enter blind mode

<br>

## Debug Mode<br>
1. Ensure that all peripherals are powered on and are laying flat on the table
2. Navigate to the CCU Final Application folder
    ```sh
    cd '.\CCU\Final_Application\'
3. Run the main program with the debug flag
    ```sh
    python .\SCRATCH --d
    ```
    or

    ```sh
    python .\SCRATCH --debug
    ```
4. Use the on-screen menus to test each subsystem's functionality
<br><br>

## Other Arguments<br>
1. List available arguments: ```--help``` or ```--h ```

2. Enter demo mode: ```--demo```
3. Enable real connection to VISION: ```--VISION```  or ```--V```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Luke Ambray - lukeambray@knights.ucf.edu </p>
Mark Nelson - marknelson@knights.ucf.edu </p>
Goran Lalich - goranlalich@knights.ucf.edu </p>
Mena Mishriky - menamishriky@knights.ucf.edu</p>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



