# Helper file that does most of the API call to PumpOut
# Pump It Up Charts data are all credited to PumpOut
import json, requests, random
from re import sub

LEVEL_ID_DICT = {
    20: 'bd2e8732ff22aee8360b5e0986d62a7f',
    21: '4c7172d577a2b4621fd31a86dd76abef',
    22: 'b4ee3f64e43f195e532b2ecb4126a65a',
    23: '2fb236c4ab7ab050fff144d7c3446817',
    24: '406871232e4d445c0902977b673937ff',
    25: 'c6c316166a8ff31b0237496e74a85fa0',
    26: '067897b42c6dcd429174892c0a89776f',
    27: 'd8c9513f4ab7b0856dbca622176a25ab',
    28: '22c1878e69b7988a252b36c1b351a042',
}
API_URL = "https://pumpout2.anyhowstep.com:17593/api/search/result?atVersion=154&languageCode=en&display=CHART&rowsPerPage=100"


# String processing for markdown in Telegram
def escape_telegram(text):
    text = sub('[.]', r'\.', text)
    text = sub('[-]', r'\-', text)
    text = sub('\(', r'\(', text)
    text = sub('\)', r'\)', text)
    text = sub('[~]', r'\~', text)
    text = sub('[!]', r'\!', text)
    text = sub('[<]', r'\<', text)
    text = sub('[>]', r'\>', text)
    text = sub('[#]', r'\#', text)
    return text

def escape_array(arr):
    res = []
    for song in arr:
        res.append(escape_telegram(song))
    return res


# API call and processing of JSON
def get_array_of_json_from_url(level):
    result = []

    page = 0
    search_id = LEVEL_ID_DICT[level]
    url = API_URL + f"&page={page}&searchId={search_id}"

    response = requests.get(url)
    content = response.content.decode("utf8")
    js = json.loads(content)

    while js["rows"]:
        result.append(js)
        page += 1
        url = API_URL + f"&page={page}&searchId={search_id}"

        response = requests.get(url)
        content = response.content.decode("utf8")
        js = json.loads(content)
    
    return result

def process_array_of_json(array_of_json, mode_filter=None, cut_filter=None):
    result = []
    for js in array_of_json:
        arr_to_process = js["rows"]

        for song in arr_to_process:
            song_level_string = ""

            if not song["inVersion"]:  # ignore songs not in version
                continue

            song_level_string += "*"
            song_level_string += song["internalTitle"]
            song_level_string += "* "
            chart_id = song["chartId"]

            # some songs have two or more charts with the same level
            correct_index = -1
            for index in range(len(song["charts"])):
                chart = song["charts"][index]
                if not chart_id == chart["chartId"]:
                    continue

                if not chart["inVersion"]:
                    continue
                
                correct_index = index
                song_level_string += chart["rating"]["mode"]["internalAbbreviation"]
                song_level_string += chart["rating"]["difficulty"]["internalTitle"]
                break

            if correct_index == -1:  # ignore charts not in version
                continue

            # filter based on Single, Double
            if mode_filter and song["charts"][correct_index]["rating"]["mode"]["internalAbbreviation"] not in mode_filter:
                continue

            # filter based on Arcade, Remix, Full Song, Short Cut
            if cut_filter and song["cut"]["internalTitle"] not in cut_filter:
                continue

            song_level_string += " _("
            song_level_string += song["cut"]["internalTitle"]
            song_level_string += ")_"

            result.append(song_level_string)

    return result

def get_array_for_level(level):
    return process_array_of_json(get_array_of_json_from_url(level))


# Helper functions for randomiser
def randomise_songs(level):
    result = get_array_for_level(level)
    index = random.randrange(0, len(result))
    return escape_telegram(result[index])

def randomise_single_arcade(level):
    result = process_array_of_json(get_array_of_json_from_url(level), ["S"], ["Arcade"])
    return escape_telegram(result[random.randrange(0, len(result))]) if result else None

def randomise_double_arcade(level):
    result = process_array_of_json(get_array_of_json_from_url(level), ["D"], ["Arcade"])
    return escape_telegram(result[random.randrange(0, len(result))]) if result else None

def randomise_single_train(level):
    result = process_array_of_json(get_array_of_json_from_url(level), ["S"], ["Arcade"])
    sample = random.sample(range(0, len(result)), 4)
    train = ""
    for i in range(4):
        index = sample[i]
        if i == 3:
            train += escape_telegram(result[index])
        else:
            train = train + escape_telegram(result[index]) + "\n"
    return train

def randomise_double_train(level):
    result = process_array_of_json(get_array_of_json_from_url(level), ["D"], ["Arcade"])
    sample = random.sample(range(0, len(result)), 4)
    train = ""
    for i in range(4):
        index = sample[i]
        if i == 3:
            train += escape_telegram(result[index])
        else:
            train = train + escape_telegram(result[index]) + "\n"
    return train
