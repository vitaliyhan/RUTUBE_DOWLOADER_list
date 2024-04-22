## Программа для скачивания видео с RuTube
### Для корректной работы, в папке где работает программа, должен быть файл с декодером ffmpeg.
#### Для скачивания видео, нужно вставить ссылку в программу, можно через ПКМ. Затем жмём Enter
#### Начнётся процесс скачивания видео. Сначала программа находит сегменты видео, и скачивает их во временную папку.
#### Затем, идёт обработка этих сегментов кодеком FFMPEG и результат сохраняется в папку с названием канала, откуда было скачано видео.
#### Временные файлы будут удалены, чтобы не засорять мусором.

#### [cuncurency_list.py](cuncurency_list.py) - download from list
#### [cuncurent.py](cuncurent.py) - download concurrent
#### [rt_downloader.py](rt_downloader.py) - default
#### [cuncurency_list_just_download.py](cuncurency_list_just_download.py) - only download from list
