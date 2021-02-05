
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, os

from html_parser import create_songs_json

#each line in the file will be of the form:
#playlist_id [custom_playlist_name]
#where playlist_id is the youtube playlist id and custom_playlist_name is any valid filename.
#custom_playlist_name should not contain whitespace.
playlists_filename = 'playlists.txt'
output_folder = 'output'

def parse_playlists():
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    lines: list[tuple[str, str]] = []
    existing_json = os.listdir(output_folder)
    with open(playlists_filename) as f:
        line = f.readline().strip()
        line = line.split(' ')
        if len(line) == 1:
            line.append(line[0]) #let playlist id be name of output filename
        already_exists = f'{line[1]}.json' in existing_json
        if not already_exists:
            lines.append(line)

    if not lines:
        print('No new playlists given. Delete existing in output folder if you want to redo')
        return

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)

    for playlist_id, playlist_name in lines:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        print("Getting page")
        driver.get(url)
        print("Finding elements")
        elem = driver.find_element_by_tag_name("html")
        print("Scrolling")
        elem.send_keys(Keys.END)
        time.sleep(3)
        elem.send_keys(Keys.END)
        print("Getting inner html")
        innerHTML = driver.execute_script("return document.body.innerHTML")

        print("Writing html to file")
        html_folder = os.path.join(output_folder, 'html')
        if not os.path.exists(html_folder):
            os.mkdir(html_folder)

        html_filename = os.path.join(output_folder, 'html', f'{playlist_name}.html')
        with open(html_filename, 'w') as f:
            f.write(innerHTML)

        output_filename = os.path.join(output_folder, f'{playlist_name}.json')
        create_songs_json(html_filename, output_filename)
        time.sleep(2)

    driver.close()
    print("Done")