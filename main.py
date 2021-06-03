# @ U T |-| O R : Ahnaf Hasan Shifat
# Created on : 3 July 2021

from selenium import webdriver
from gogoanime import Gogoanime
import pathlib
import os

# Current File Path
current_path = (pathlib.Path().absolute())

# Enter your desired anime name and episode
user_input = input("Enter Anime Name: ")
episode_number = int(input("Enter Episode Number: "))

# Selenium Webdriver Initialization
driver = webdriver.Chrome(executable_path='chromedriver.exe')

# Gogoanime Initialization
gogoanime = Gogoanime(driver=driver, name=user_input)

current_path = (os.path.join(current_path, f"Episode {episode_number}.mp4"))

# Get anime title
title = gogoanime.get_anime_title() # Return a string

# Get anime data
data = gogoanime.get_anime_data() # Return a dictionary

# Get download link
link = gogoanime.get_download_link(episode_number=episode_number) # Return a dictionary

# Download the episode
gogoanime.download(url=link, output_path=current_path)






