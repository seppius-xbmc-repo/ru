# seppius-xbmc-repo
Exported from code.google.com/p/seppius-xbmc-repo

Скачать плагин seppius-xbmc-repo https://github.com/seppius-xbmc-repo/ru/raw/master/repository.seppius.zip

# Для разработчиков :

. Клонируем удалённый git на компьютер:

git clone https://github.com/seppius-xbmc-repo/ru.git

. Входим в дирректорию :

cd ru

. Инициализируем Git :

git init 

. Индексируем содержимое:

git add . или sudo git add -A

. Копируем свой плагин в дирректорию /ru. В каталог с плагином копируем zip плагина с указанием версии.

. Индексируем изменения в локальном Git :

sudo git add .

. Создаём коммит :

git commit -a -m 'add plugin.video.x'

. Удаляем старый список :

rm addons_xml

rm addons.xml.md5

. Генерируем новый список плагинов в Git :

sudo python addons_xml_generator.py

. Индексируем список :

sudo git add .

git commit -a -m 'add addons.xml'

. Отправляем в удалённый Git :

git push -u https://github.com/seppius-xbmc-repo/ru.git

Username for 'https://github.com': xbmcrepo@list.ru

Password for 'https://xbmcrepo@list.ru@github.com': ask me

. Для удаления некорректного коммита на один шаг назад :

git log

sudo git reset --hard HEAD~1

git push -f origin master

Некорректный коммит и плагин будет удалён из удалённого Git .

. Для обновления локального Git получаем обновления из удалённого перед предстоящими изменениями в локальном Git :

git pull 

From https://github.com/seppius-xbmc-repo/ru

 * branch            master     -> FETCH_HEAD

Already up-to-date.

. После обновления можем изменять в локальном и отправлять изменения в удалённый Git.

 Good luck!