#!/usr/bin/env python
"""This script processes the lyrics files from
https://www.cygnus-x1.net/links/rush/albums-... to prepare them as input to a
text generation program"""

import os
import re
import collections
from string import capwords

INPUT_FILE_LIST = ['albums-2112.php', 'albums-afarewelltokings.php',
                   'albums-caressofsteel.php', 'albums-clockworkangels.php',
                   'albums-counterparts.php', 'albums-feedback.php',
                   'albums-flybynight.php', 'albums-graceunderpressure.php',
                   'albums-hemispheres.php', 'albums-holdyourfire.php',
                   'albums-movingpictures.php', 'albums-myfavoriteheadache.php',
                   'albums-permanentwaves.php', 'albums-powerwindows.php',
                   'albums-presto.php', 'albums-rollthebones.php',
                   'albums-rush.php', 'albums-signals.php',
                   'albums-snakesandarrows.php', 'albums-testforecho.php',
                   'albums-vaportrails.php', 'albums-victor.php']

fileLine = collections.namedtuple('fileLine', 'num text')
songInfoTuple = collections.namedtuple('songInfo', 'tag title time')

def truncate_line_list(lineList, start, end=0):
    if start < 0 or (end > 0 and end < start):
        print("start and end ordered wrong")
        return []
    lineNums = [a.num for a in lineList]
    if start not in lineNums or (end > 0 and end not in lineNums):
        print("start or end not in list")
        return[]
    for ii in range(len(lineList)):
        if lineList[ii].num == start:
            startLine = ii
            if end==0:
                endLine = len(lineList)
                break
        elif end > 0 and lineList[ii].num == end:
            endLine = ii
            break
    return lineList[startLine:endLine]


def remove_bracketed_text(line):
    output_string=''
    OUT_STATE = 1
    IN_STATE = 2
    state = OUT_STATE
    #print(line)
    for ii in range(len(line.text)):
        if state == OUT_STATE:
            if line.text[ii]=='<':
                state = IN_STATE
                continue
            else:
                #print(f"character num({ii}) to append: {line.text[ii]}")
                output_string += line.text[ii]
                continue
        else: #IN_STATE
            if line.text[ii]=='>':
                state = OUT_STATE
            continue
    return fileLine(line.num, output_string)

def find_album_title(lineList):
    found_first = False
    for line in lineList:
        if 'h5' not in line.text:
            continue
        elif not found_first:
            found_first = True
        else:
            return line

def find_LYR_line(lineList):
    for line in albumList:
        if "a name=LYR" not in line.text:
            continue
        return line


def find_song_info(lineList):
    songList = []
    start_not_found = True
    tag_pattern = r'href\=\"#([A-Z0-9]{2,4})\"'
    title_pattern = r'>([A-Za-z0-9:\(\)\[\]\.\-\' ]+)<'
    time_pattern = r'\(([0-9: ]+)\)'
    for line in lineList:
        if start_not_found and "a href" not in line.text:
            #print("line not started yet")
            #print(line)
            continue
        else:
            start_not_found = False
        #print("line started")
        if len(line.text.strip()) == 0:
            #print("line ended")
            return songList
        if '#PED' in line.text:
            continue
        try:
            tag_match = re.search(tag_pattern, line.text)
            songTag = tag_match[1]
            title_match = re.search(title_pattern, line.text)
            songTitle = title_match[1]
            time_match = re.search(time_pattern, line.text)
            songTime = time_match[1]
            #print(songTag, songTitle, songTime, line)
            songList.append(songInfoTuple(songTag, songTitle, songTime))
        except:
            print(f"pattern matching failed for line: {line.text}")


def find_next_lyrics(lineList, pattern):

    found_start = False
    #print("STARTING find next lyrics")
    #print(lineList[0])
    for line in lineList:
        #print(line)
        if not found_start and not re.search(pattern, line.text):
            continue
        if not found_start:
            start_num = line.num
            #print(f"START LINE = {line}")
            found_start = True
            continue
        #print("LINX"+line.text.strip()+"LINX")
        if len(line.text.strip()) != 0 and '<a name=' not in line.text: #if the line has contents
            continue
        end_num = line.num
        #print(f"END LINE = {line}")
        #print("LINES: ",start_num, end_num)
        lines = truncate_line_list(lineList, start_num, end_num)
        break
    #print("ENDING find next lyrics")
    return start_num, end_num, lines


def strip_text(line):
    return fileLine(line.num, line.text.strip())

def clean_lyrics_list(roughLyrics):
    # delete more than one empty line in a row
    # replace &nbsp; with 2 spaces?
    # remove byline
    # add 5 empty lines above
    # replace Music: line with empty line to put blank between song title and text
    cleaned_lyrics = []
    last_line_blank = False
    for line in roughLyrics:
        line = remove_bracketed_text(line)
        line = strip_text(line)
        if len(line.text) != 0: #if the line has no contents
            last_line_blank = False
            # process other things in text line see above
            # then pack line text into new fileLine using old number and new text
            out_text = line.text
            if 'Music:' in out_text:
                out_text = ''
            else:
                out_text = re.sub('\&nbsp;','  ', out_text)
            new_line = fileLine(line.num, out_text)
            cleaned_lyrics.append(new_line)
        else:
            if not last_line_blank:
                # if not lastLineBlank then output new blank line with this line number
                new_line = fileLine(line.num, '')
                cleaned_lyrics.append(new_line)
            last_line_blank = True
    if len(cleaned_lyrics[1].text) > 0:
        if cleaned_lyrics[1].num - cleaned_lyrics[0].num > 1:
            new_num = cleaned_lyrics[0].num + 1
        else:
            new_num = cleaned_lyrics[0].num + 0.5
        cleaned_lyrics.insert(1, fileLine(new_num,''))
    top_line_num = cleaned_lyrics[0].num
    empty_header = []
    for ii in range(top_line_num-5,top_line_num):
        empty_header.append(fileLine(ii,''))
    cleaned_lyrics = empty_header + cleaned_lyrics
    return cleaned_lyrics


def find_lyrics_list(lineList, sngInfoList):
    lyrics_list = []
    numSongs = len(sngInfoList)
    song_tags = [a.tag for a in sngInfoList]
    #print(numSongs, song_tags)
    for song_tag in song_tags:
        song_pattern = r'<a name\=' + song_tag
        start_line, end_line, song_lines = find_next_lyrics(lineList, song_pattern)
        cleaned_lyrics = clean_lyrics_list(song_lines)
        lyrics_list.append(cleaned_lyrics)
        lineList = truncate_line_list(lineList, end_line)
    return lyrics_list

    #songTagsQueue = collections.deque(songTags)
    #for line in lineList:
    #    thisSong_tag = songTagsQueue.popleft()
    #    thisSong_pattern = r'<a name\=' + thisSong_tag
    #    if not re.search(thisSong_pattern, line.text):
    #        continue
    #    start_num = line.num
    #    if line.text.strip: #if the line has contents
    #        continue


def print_all_songs(songInfo,lyricsList):
    for songData in zip(songInfo, lyricsList):
        for line in songData[1]:
            print(line.text)


albumNum = 0        
for albumName in INPUT_FILE_LIST:
    #albumName='albums-permanentwaves.php'
    albumList = []

    with open(os.path.join('inputData',albumName), 'rt') as albumFile:
        lineNum = 1
        for line in albumFile:
            albumList.append(fileLine(num=lineNum, text=line))
            lineNum += 1

    albumTitleLine = find_album_title(albumList)
    #print(albumTitleLine)
    #print()
    albumTitleText = capwords(remove_bracketed_text(albumTitleLine).text)
    print(albumTitleText)
    #print(albumNum, albumTitleText)
    albumNum += 1
    newLineList = truncate_line_list(albumList, albumTitleLine.num, 0)
    albumLYRline = find_LYR_line(newLineList)
    #print(albumLYRline)
    newLineList = truncate_line_list(newLineList, albumLYRline.num + 3, 0)
    songInfoList = find_song_info(newLineList)
    print(songInfoList)
    lyricsList = find_lyrics_list(newLineList, songInfoList)
    #print(lyricsList)
    print_all_songs(songInfoList, lyricsList)
