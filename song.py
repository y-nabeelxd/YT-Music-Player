import os
import re
import yt_dlp
import sys
import requests
from urllib.parse import quote
import json
import mpv
from colorama import init, Fore, Back, Style
import math

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_duration(seconds):
    """Convert seconds to MM:SS format"""
    if not seconds:
        return "??:??"
    minutes = math.floor(seconds / 60)
    seconds = math.floor(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def search_youtube(query):
    search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(Fore.RED + "Failed to fetch YouTube results")
            return []

        html = response.text
        initial_data = {}
        
        try:
            start = html.index('var ytInitialData = ') + len('var ytInitialData = ')
            end = html.index('};</script>', start) + 1
            json_str = html[start:end]
            initial_data = json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            print(Fore.RED + "Failed to parse YouTube data:", e)
            return []

        videos = []
        contents = initial_data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [{}])[0].get('itemSectionRenderer', {}).get('contents', [])
        
        for content in contents:
            if 'videoRenderer' in content:
                video = content['videoRenderer']
                video_id = video.get('videoId')
                title = video.get('title', {}).get('runs', [{}])[0].get('text')
                
                duration_text = video.get('lengthText', {}).get('simpleText', '')
                duration_seconds = None
                if duration_text:
                    try:
                        mins, secs = map(int, duration_text.split(':'))
                        duration_seconds = mins * 60 + secs
                    except:
                        duration_seconds = None
                
                if video_id and title:
                    videos.append({
                        'title': title,
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'duration': duration_seconds
                    })
                    if len(videos) >= 10:
                        break

        return videos

    except Exception as e:
        print(Fore.RED + f"Error searching YouTube: {e}")
        return []

def play_song(video_url, song_name):
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + "\n🎵 Now playing: " + Fore.YELLOW + Style.BRIGHT + f"{song_name}\n")
    print(Fore.GREEN + "Playing...")
    
    player = mpv.MPV(
        ytdl=True,
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        video=False
    )
    player.play(video_url)
    player.wait_for_playback()
    player.terminate()

if __name__ == "__main__":
    try:
        clear_screen()
        print(Fore.MAGENTA + Style.BRIGHT + "✨ MUSIC PLAYER ✨")
        print(Fore.BLUE + "="*40 + "\n")
        
        print(Fore.CYAN + Style.BRIGHT + "Enter the song name: " + Fore.YELLOW, end='')
        query = input().strip()
        if not query:
            print(Fore.RED + "Please enter a valid song name!")
            sys.exit(1)

        results = search_youtube(query)
        
        if not results:
            print(Fore.RED + "No results found!")
            sys.exit(1)

        clear_screen()
        colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, 
                 Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTRED_EX, 
                 Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX]
        
        print(Fore.CYAN + Style.BRIGHT + "🔍 Search results:\n")
        for idx, video in enumerate(results, 1):
            color = colors[idx % len(colors)]
            duration = format_duration(video.get('duration'))
            print(color + f"{idx}. {video['title']}" + Fore.WHITE + f" [{duration}]")

        print(Fore.CYAN + Style.BRIGHT + "\nChoose the number of the song you want to listen to " + 
              Fore.YELLOW + "(1-10): " + Fore.WHITE, end='')
        try:
            choice = int(input()) - 1
            if 0 <= choice < len(results):
                video_url = results[choice]['url']
                song_name = results[choice]['title']
                play_song(video_url, song_name)
            else:
                print(Fore.RED + "Invalid choice! Please select a number between 1 and 10.")
        except ValueError:
            print(Fore.RED + "Invalid input! Please enter a number.")
    except KeyboardInterrupt:
        print(Fore.RED + "\nOperation cancelled by user.")
        sys.exit(0)
