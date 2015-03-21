#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys

language = ('en', 'ru')[int(sys.modules[ "__main__" ].__settings__.getSetting("language"))]
dictionary = {
    'ru': {
        'Seeds searching.': 'Идёт поиск сидов.',
        'Please Wait': 'Подождите',
        'Information': 'Информация',
        'Torrent downloading is stopped.': 'Загрузка торрента прекращена.',
        '< Search >': '< Поиск >',
        'Seeds': 'Сиды',
        'Peers': 'Пиры',
        'Materials are loading now.': 'Идёт загрузка материалов.',
        'Search Phrase': 'Фраза для поиска',
        'Magnet-link is converting.': 'Идёт преобразование magnet-ссылки.',
        'Error': 'Ошибка',
        'Your library out of date and can\'t save magnet-links.': 'Ваша библиотека устарела и не может сохранять магнет-ссылки.',
        '< Bookmarks >': '< Закладки >',
        '< Logout >': '< Выход >',
        '< Login >': '< Вход >',
        '< Recent Materials >': '< Свежие Материалы  >',
        '< History >': '< История >',
        '< Register >': '< Регистрация >',
        'Bookmark': 'Закладка',
        'Item successfully added to Bookmarks': 'Элемент удачно добавлен в закладки',
        'Item successfully removed from Bookmarks': 'Элемент удачно удалён из закладок',
        'Bookmark not added': 'Закладка не добавлена',
        'Bookmark not removed': 'Закладка не удалена',
        'Add To Bookmarks': 'Добавить в закладки',
        'Remove From Bookmarks': 'Удалить из Закладок',
        'Auth': 'Авторизация',
        'Already logged in': 'Пользователь уже в системе',
        'Input Email (for password recovery):': 'Введите E-mail (для восстановления пароля):',
        'Input Email:': 'Введите E-mail:',
        'Input Password (6+ symbols):': 'Введите пароль (6+ символов):',
        'Input Password:': 'Введите пароль:',
        'Login successfull': 'Вход выполнен успешно',
        'Login failed': 'Вход не выполнен',
        'User not logged in': 'Пользователь не в системе',
        'User successfully logged out': 'Пользователь успешно покинул систему',
        'Preloaded: ': 'Предзагружено: ',
        'Do you want to STOP torrent downloading and seeding?': 'Вы хотите остановить загрузку и раздачу торрента?',
        'Torrent Downloading': 'Загрузка торрента',
        'Auth expired, please relogin': 'Авторизация истекла, пожалуйста войдите снова',
        'Storage': 'Хранилище',
        'Storage was cleared': 'Хранилище очищено',
        '< Clear Storage >': '< Очистить хранилище >',
        '< Popular >': '< Популярное >',
        'Views': 'Просмотров',
        'Uploading': 'Раздача',
        'Downloading': 'Закачка',
        'Input symbols from CAPTCHA image:': 'Введите символы с картинки CAPTCHA:',
        'Please, rate watched video:': 'Пожалуйста, оцените просмотренное видео:',
        'Bad': 'Плохо',
        'So-So': 'Такое...',
        'Good': 'Отлично',
        '< Ratings >': '< Оценки >',
        'Rating': 'Оценка',
    },
}

def localize(text):
    try:
        return dictionary[language][text]
    except:
        return text
