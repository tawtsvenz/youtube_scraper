from bs4 import BeautifulSoup as bs

import json
import random
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

# folders containing already used names
files_dirs = ['../quizappstaticfiles/', '../quizappstaticfiles/audio', ]
# json files must end with .json
json_output_dir = 'output'


class SongConstants:
    ARTIST = 'ARTIST'
    FEATURES = 'FEATURES'
    TITLE = 'TITLE'
    TIME = 'TIME'
    YEAR = 'YEAR'
    RANDOM_FILENAME = 'RANDOM_FILENAME'


_used_numbers = []


def get_valid_random_name():
    if not _used_numbers:
        # populate used numbers
        # check used in static files
        _files = []
        for d in files_dirs:
            if os.path.exists(d) and os.path.isdir(d):
                _files.extend(os.listdir(d))
        files = []
        for f in _files:
            absname = os.path.basename(f)
            dot_index = absname.rfind('.')
            if dot_index > 0:
                absname = absname[: dot_index].strip()
            if (absname.isdigit()):
                _used_numbers.append(absname)
        # check all json in output folder for used numbers
        if os.path.exists(json_output_dir):
            json_files = [f for f in os.listdir(json_output_dir) if
                          os.path.isfile(os.path.join(json_output_dir, f))
                          and f.lower().endswith('.json')]
            for f in json_files:
                try:
                    json_obj = None
                    with open(os.path.join(json_output_dir, f)) as f:
                        json_obj = json.loads(f.read())
                    obj: dict
                    for obj in json_obj:
                        if type(obj) is dict and SongConstants.RANDOM_FILENAME in obj:
                            _used_numbers.append(
                                str(obj[SongConstants.RANDOM_FILENAME]))
                except Exception as e:
                    print(e)
                    print()
        print(_used_numbers)
        print(len(_used_numbers))
    # find unique random number
    num: str = str(random.randint(1000, 2000000000))
    count = 0
    while num in _used_numbers:
        num = str(random.randint(1000, 2000000000))

        count += 1
        if count % 1000000:
            print(f'Number not found yet after {count} tries')
    _used_numbers.append(num)  # add found num
    return num


def rfind_nth(string: str, substring: str, n):
    end = len(string)
    index = -1
    for x in range(n):
        index = string.rfind(substring, 0, end)
        if index < 0:
            return index
        else:
            end = index
    return index


def get_year(yt_date_str: str):
    current_date: datetime = datetime.now()
    time_types: tuple[str, ...] = (
        'years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds')
    value: str
    time_type: str
    value, time_type = yt_date_str.strip().split(' ')
    try:
        value = int(value.strip())
    except ValueError:
        print('Date not found')
        return None
    time_type = time_type.strip()
    found_type = None
    for default_type in time_types:
        if time_type in default_type:
            found_type = default_type
            break
    if found_type:
        delta = relativedelta(**{found_type: value})
        year = (current_date - delta).year
        return year
    else:
        return None


ft_strings = (' ft ', ' ft. ', ' feat ', ' feat.')
artist_separators = (',', ' x ', ' & ', ' and ', ' + ')


def get_official_video_index(string):
    index_official_video = -1
    if index_official_video < 0:
        index_official_video = string.lower().find('(official')
    if index_official_video < 0:
        index_official_video = string.lower().find('( official')
    if index_official_video < 0:
        index_official_video = string.lower().find('[official')
    if index_official_video < 0:
        index_official_video = string.lower().find('[ official')
    if index_official_video < 0:
        index_official_video = string.lower().find('(video')
    if index_official_video < 0:
        index_official_video = string.lower().find('( video')
    if index_official_video < 0:
        index_official_video = string.lower().find('[video')
    if index_official_video < 0:
        index_official_video = string.lower().find('[ video')
    if index_official_video < 0:
        index_official_video = string.lower().find('(audio')
    if index_official_video < 0:
        index_official_video = string.lower().find('( audio')
    if index_official_video < 0:
        index_official_video = string.lower().find('[audio')
    if index_official_video < 0:
        index_official_video = string.lower().find('[ audio')
    if index_official_video < 0:
        index_official_video = string.lower().find('(lyric')
    if index_official_video < 0:
        index_official_video = string.lower().find('( lyric')
    if index_official_video < 0:
        index_official_video = string.lower().find('[lyric')
    if index_official_video < 0:
        index_official_video = string.lower().find('[ lyric')
    if index_official_video < 0:
        index_official_video = string.lower().find('official video')
    if index_official_video < 0:
        index_official_video = string.lower().find('official audio')
    if index_official_video < 0:
        index_official_video = string.lower().find('official music')
    if index_official_video < 0:
        index_official_video = string.lower().find('official video')

    return index_official_video


def get_artists(yt_artist_string):
    string = yt_artist_string
    ft_index = -1
    for ft_string in ft_strings:
        ft_index = string.lower().find(ft_string)
        if ft_index > 0:
            break
    if ft_index > 0:
        string = string[:ft_index]
    string = string.replace(artist_separators[1], ',')
    string = string.replace(artist_separators[1].upper(), ',')
    string = string.replace(artist_separators[2], ',')
    string = string.replace(artist_separators[3], ',')
    string = string.replace(artist_separators[3].upper(), ',')
    string = string.replace(artist_separators[4], ',')

    return string.strip()


def get_featured(yt_artist_or_title_string):
    string = yt_artist_or_title_string
    ft_string_used = None
    for ft_string in ft_strings:
        ft_index = string.lower().find(ft_string)
        if ft_index > 0:
            ft_string_used = ft_string
            break
    if ft_index > 0:
        string = string[ft_index + len(ft_string_used):]
    else:
        # no features
        return None
    string = get_artists(string)
    index_official_video = get_official_video_index(string)
    if index_official_video > 0:
        string = string[:index_official_video]

    return string.strip()


def get_title(yt_title_section):
    string: str = yt_title_section

    index_official_video = get_official_video_index(string)
    if index_official_video > 0:
        string = string[:index_official_video]

    ft_index = -1
    for ft_string in ft_strings:
        ft_index = string.lower().find(ft_string)
        if ft_index > 0:
            break
    if ft_index > 0:
        string = string[: ft_index]

    return string.strip()


def parse_song(song_details: str):
    song: dict = {}
    ago_index = song_details.rfind(' ago')
    if ago_index >= 0:
        song[SongConstants.TIME] = song_details[ago_index + 4:].strip()
        song_details = song_details[:ago_index].strip()

    date_index = rfind_nth(song_details, ' ', 2)
    date_string = song_details[date_index:]
    year = get_year(date_string)
    song[SongConstants.YEAR] = year
    song_details = song_details[: date_index].strip()
    by_index = song_details.rfind(' by ')
    song_details = song_details[:by_index].strip()
    hyphen_index = song_details.find('-')
    if hyphen_index < 0:
        raise ValueError('Cant find hyphen separator!')
    artist_section = song_details[:hyphen_index].strip()
    title_section = song_details[hyphen_index + 1:].strip()
    artists = ''
    a = get_artists(artist_section)
    if a:
        artists += a
    song[SongConstants.ARTIST] = artists
    a = get_featured(artist_section)
    featured_artists = ''
    if a:
        featured_artists += a
    a = get_featured(title_section)
    if a:
        comma = "," if featured_artists else ""
        featured_artists += comma + a
    song[SongConstants.FEATURES] = featured_artists
    title = get_title(title_section)
    song[SongConstants.TITLE] = title

    random_name = get_valid_random_name()
    song[SongConstants.RANDOM_FILENAME] = random_name

    return song


def create_songs_json(input_html_filename, output_filename):
    innerhtml = ""
    with open(input_html_filename) as f:
        innerhtml = f.read()

    soup = bs(innerhtml, "html.parser")
    results = soup.find_all(
        'a', {'class': 'yt-simple-endpoint style-scope ytd-playlist-video-renderer'})

    songs: list = []
    for result in results:
        song_details = result.get('aria-label')
        try:
            song = parse_song(song_details)
            songs.append(song)
        except (ValueError, AttributeError) as e:
            print(song_details)
            print(e)
            print()

    with open(output_filename, 'w') as f:
        f.write(json.dumps(songs, indent=2))
