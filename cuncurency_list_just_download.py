import os.path
import re
import shutil
import concurrent.futures
import requests
import time
import sys

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}

SEG = "seg_full"
ARG = False


def get_m3u8_list(url):
    req = requests.get(url=url, headers=headers)
    video_data = req.json()
    video_author = video_data['author']['name']
    video_title = video_data['title']
    dict_repl = ["/", "\\", "[", "]", "?", "'", '"', ":", "."]
    for repl in dict_repl:
        if repl in video_title:
            video_title = video_title.replace(repl, "")
        if repl in video_author:
            video_author = video_author.replace(repl, "")
    video_title = video_title.replace(" ", "_")
    video_author = video_author.replace(" ", "_")

    video_m3u8 = video_data['video_balancer']['m3u8']
    return video_author, video_title, video_m3u8


def get_link_from_m3u8(url_m3u8):
    if not os.path.isdir(SEG):
        os.mkdir(SEG)
    req = requests.get(url=url_m3u8, headers=headers)
    data_m3u8_dict = []
    with open(f"{SEG}\\pl_list.txt", 'w', encoding='utf-8') as file:
        file.write(req.text)
    with open(f"{SEG}\\pl_list.txt", 'r', encoding='utf-8') as file:
        src = file.readlines()

    for item in src:
        data_m3u8_dict.append(item)

    url_playlist = data_m3u8_dict[-1]
    return url_playlist


def get_segment_count(m3u8_link):
    req = requests.get(url=m3u8_link, headers=headers)
    data_seg_dict = []
    for seg in req:
        data_seg_dict.append(seg)
    seg_count = str(data_seg_dict[-2]).split("/")[-1].split("-")[1]
    return seg_count


def get_download_link(m3u8_link):
    link = f'{m3u8_link.split(".m3u8")[0]}/'
    return link


def get_download_segment(link, count):
    print('get_download_segment')
    if not os.path.isdir(SEG):
        os.mkdir(SEG)

    # Функция для загрузки одного сегмента
    def download_segment(item):
        print(f'[+] - Загружаю сегмент {item}/{count}')
        req = requests.get(f'{link}segment-{item}-v1-a1.ts')
        with open(f"{SEG}\\segment-{item}-v1-a1.ts", 'wb') as file:
            file.write(req.content)

    # Создаем ThreadPoolExecutor с максимальным количеством потоков 20
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Запускаем загрузку сегментов в пуле потоков
        if ARG:
            num = ARG
            executor.map(download_segment, range(num, num + 1))
        else:
            executor.map(download_segment, range(1, count + 1))
        # executor.map(download_segment, range(1, count + 1))
        # num = 2108
        # executor.map(download_segment, range(num - 1, num + 1))
        # executor.map(download_segment, range(1, count + 1))

    print('[INFO] - Все сегменты загружены')


def merge_ts(author, title, count):
    print('merge_ts')
    save_dir = f"full\\{author}"
    if not os.path.isdir("full"):
        os.mkdir("full")
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    with open(f"{SEG}\\{title}.ts", 'wb') as merged:
        for ts in range(1, count + 1):
            with open(f"{SEG}\\segment-{ts}-v1-a1.ts", 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    # os.system(f"ffmpeg -i {SEG}\\{title}.ts -c:v hevc_nvenc -b:v 1M -preset p7 -c:a copy {save_dir}\\{title}.mp4")
    print('[+] - Объединение завершено')

    file_dir = os.listdir('seg')
    for file in file_dir:
        os.remove(f"{SEG}\\{file}")
    os.removedirs(SEG)


def main():
    with open('links.txt', 'r') as f:
        links = f.read().splitlines()
    total_start_time = time.time()  # начальное время выполнения всего скрипта
    link_durations = []

    for link in links:
        print(link)
        link_start_time = time.time()
        url = link.split("/")[-2]
        m3u8_url = get_m3u8_list(
            f'https://rutube.ru/api/play/options/{url}/?no_404=true&referer=https%3A%2F%2Frutube.ru')
        print(m3u8_url)
        try:
            m3u8_link = get_link_from_m3u8(m3u8_url[2])
            print(m3u8_link)
            seg_count = int(re.search(r'\d+', get_segment_count(m3u8_link)).group())
            # seg_count = int(get_segment_count(m3u8_link))
            print(seg_count)
            dwnl_link = get_download_link(m3u8_link)
            print(dwnl_link)

            if not os.path.isdir('seg'):
                os.mkdir('seg')
            # Загрузка сегментов асинхронно
            get_download_segment(dwnl_link, seg_count)
            # При догрузке
            if ARG:
                exit()
            # После завершения всех задач загрузки, запускаем объединение сегментов в один файл
            merge_ts(m3u8_url[0], m3u8_url[1], seg_count)
            link_end_time = time.time()  # конечное время выполнения для каждого URL
            link_duration = link_end_time - link_start_time  # время выполнения для каждого URL
            link_durations.append((link_duration, url))  # сохраняем время выполнения и URL
        except Exception as e:
            print(f"Ошибка при скачивании ссылки {link}: {e}")
            continue

    total_end_time = time.time()  # конечное время выполнения всего скрипта
    total_duration = total_end_time - total_start_time  # общее время выполнения всего скрипта
    print(f"Общее время выполнения скрипта: {total_duration} секунд")

    # Вывод времени выполнения для каждого URL в конце
    for duration, url in link_durations:
        print(f"Время выполнения для {url}: {duration} секунд")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            # Try to convert the argument to an integer
            ARG = int(sys.argv[1])
        except ValueError:
            print("Argument must be an integer")
            sys.exit(1)  # Exit the script with an error status
    else:
        # No argument provided, CONFIG_VALUE remains False
        ARG = False
    print("ARG", ARG)
    main()
