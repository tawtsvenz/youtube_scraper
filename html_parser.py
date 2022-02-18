from bs4 import BeautifulSoup as bs

import json
import random
import os
import gzip
from datetime import datetime
from dateutil.relativedelta import relativedelta

# folders containing already used names
files_dirs = ['../quizappstaticfiles/', '../quizappstaticfiles/audio', ]
# json files must end with .json
json_output_dir = 'output'
compressed_json_dirs = ['../chorus_finder/output']


class SongConstants:
    ARTIST = 'ARTIST'
    FEATURES = 'FEATURES'
    TITLE = 'TITLE'
    TIME = 'TIME'
    YEAR = 'YEAR'
    YOUTUBE_ID = 'YOUTUBE_ID'
    RANDOM_FILENAME = 'RANDOM_FILENAME'
    # list of tuples of significant clips in the media. tuples have two element (start_sec, end_sec)
    CLIPS = 'CLIPS'
    COUNTRY = 'COUNTRY'
    AVAILABLE = 'AVAILABLE'


_used_numbers = set()


def get_valid_random_name():
    if not _used_numbers:
        # populate used numbers
       
        #check compressed json folders and populate
        compressed_json_filenames = []
        for folder in compressed_json_dirs:
            if os.path.exists(folder) and os.path.isdir(folder):
                filenames = os.listdir(folder)
                for filename in filenames:
                    abspath = os.path.join(folder, filename)
                    if os.path.isfile(abspath) and abspath.endswith('.json.gz'):
                        compressed_json_filenames.append(abspath)
        for filename in compressed_json_filenames:
            try:
                objs = []
                with gzip.open(filename) as f:
                    objs = json.loads(f.read().decode('utf-8'))
                for song in objs:
                    _used_numbers.add(song[SongConstants.RANDOM_FILENAME])
                print(f'Loaded existing names from compressed file {filename}')
            except Exception as e:
                print(f'Failed to process compressed file {filename}: {e.args}')

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
                _used_numbers.add(absname)

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
                            _used_numbers.add(
                                str(obj[SongConstants.RANDOM_FILENAME]))
                except Exception as e:
                    print(e)
                    print()
    # find unique random number
    num: str = str(random.randint(1000, 2000000000))
    count = 0
    while num in _used_numbers:
        num = str(random.randint(1000, 2000000000))

        count += 1
        if count % 1000000:
            print(f'Number not found yet after {count} tries')
    _used_numbers.add(num)  # add found num
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
    #use lower case words here
    joining_words = ('official', 'video', 'audio', 'lyric')
    standalone_words = ('official video', 'official audio', 'official music')
    tags = [tag + space for tag in ('[', '(', '{') for space in ('', ' ')]

    words = [tag + word for word in joining_words for tag in tags]
    words.extend(standalone_words)

    index_official_video = -1
    for word in words:
        index_official_video = string.lower().find(word)
        if index_official_video >= 0:
            break

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
    
    for sep in artist_separators:
        string = string.replace(sep, ',')

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


def parse_filename_as_song(filename: str):
    song_details = os.path.basename(filename)
    song = {}
    song[SongConstants.YEAR] = None
    hyphen_index = song_details.find('-')
    if hyphen_index < 0:
        #cant separate the sections, so just say both artist_section and title_section are equal
        artist_section = title_section = song_details
    else:
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


def parse_song(song_details: str):
    song: dict = {}
    ago_index = song_details.rfind(' ago')
    if ago_index >= 0:
        song[SongConstants.TIME] = song_details[ago_index + 4:].strip()
        song_details = song_details[:ago_index].strip()

    date_index = rfind_nth(song_details, ' ', 2)
    date_string = song_details[date_index:]
    # skip year we'll find it ourselves
    # year = get_year(date_string)
    song[SongConstants.YEAR] = None #year
    song_details = song_details[: date_index].strip()
    by_index = song_details.rfind(' by ')
    song_details = song_details[:by_index].strip()
    hyphen_index = song_details.find('-')
    if hyphen_index < 0:
        #cant separate the sections, so just say both artist_section and title_section are equal
        artist_section = title_section = song_details
    else:
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
    song[SongConstants.AVAILABLE] = False
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
            #get youtube_id and populate
            href: str = result.get('href')
            start_tag = '?v='
            id_start_index = href.find(start_tag) + len(start_tag)
            id_end_index = id_start_index + 11 #Youtube ID is always 11 characters long
            youtube_id = href[id_start_index: id_end_index]
            song[SongConstants.YOUTUBE_ID] = youtube_id
            songs.append(song)
        except (ValueError, AttributeError) as e:
            print(song_details)
            print(e)
            print()

    with gzip.open(output_filename, 'wb') as f:
        f.write(json.dumps(songs, indent=2).encode('utf-8'))

