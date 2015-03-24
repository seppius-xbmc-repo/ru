== Clone seppius-xbmc-repo ==

* Exported from code.google.com/p/seppius-xbmc-repo

* Скачать плагин seppius-xbmc-repo 

https://github.com/seppius-xbmc-repo/ru/raw/master/repository.seppius.zip



== Для разработчиков ==

* Клонируем удалённый(origin) Git на компьютер 

git clone https://github.com/seppius-xbmc-repo/ru.git

* Входим в директорию c Git

cd ru

* Инициализируем Git 

git init   -- если в системе нет других Git, то команду вводим один раз 

* Индексируем содержимое локального  Git 

git add -A

* Копируем свой плагин в директорию /ru. В каталог с плагином копируем zip плагина с указанием версии.

* Индексируем изменения в локальном Git 

git add -A

* Создаём коммит 

git commit -a -m 'add plugin.video.name'

* Генерируем новый список плагинов в Git 

python addons_xml_generator.py

* Индексируем список плагинов в локальном Git

git add -A

* Создаём коммит

git commit -a -m 'add addons.xml'

* Отправляем в удалённый Git 

git push -f origin master

* или так :

git push -u https://github.com/seppius-xbmc-repo/ru.git

* Авторизуемся в нашем Git

* Username for 'https://github.com':                        введите e-mail, Вашей авторизации в системе Git

* Password for 'https://github.com/seppius-xbmc-repo:       для получения админ пароля этого Git пишите в личку форума

* Для удаления некорректного коммита на один шаг назад 

git log   -- смотрим последние коммиты, сделаные нами в локальном Git

* Удаляем, пошагово убираем изменения до нужного коммита в локальном Git

git reset --hard HEAD~1 

* Отправляем в удалённый Git 

git push -f origin master

* После этого некорректный коммит и/или плагин будет удалён из удалённого(/remotes/origin/) Git

**

* Для обновления локального(/heads/master) Git, получаем обновления из удалённого(/remotes/origin/) перед предстоящими изменениями в локальном Git 

cd ru

* Мы работаем в команде и коммиты на сервер делает ещё кто-то кроме нас. 

* Поэтому перед перед началом работы с локальным Git нужно загрузить все изменения, которые произвели другие члены команды в origin репозиторий. 

* Заливаем свежую версию origin Git  в локальный Git :

git pull origin master

* После обновления локального Git, можем изменять аддон(ы) в локальном Git(master) и отправлять изменения в удалённый Git(origin).

* В дальнейшем коммиты и индексации потребуют sudo

* Если нужно удаляем старый список аддонов в репо

rm addons.xml (подтверждаем, если нужно, "y")

rm addons.xml.md5

* Если нужно удаляем каталог с плагином в локальном github

sudo rm -r plugin.video.xxx.com


== Windows утилиты в работе с Git ==

* Pyrthon  https://www.python.org/downloads/

* TortoiseGit https://code.google.com/p/tortoisegit/ - для git clone из контекстного меню на рабочем столе

* SmartGit 7  http://www.syntevo.com/smartgit/early-access - для слияния, синхронизации, коммитов и отправки изменений в Git. 

* Мануал для старого интерфейса на русском http://jakeroid.com/osnovy-sistemy-upravleniya-versiyami-git-dlya-novichkov.html . 

* Последовательность работы с утилитой SmartGit : 

* Добавляем в окне утилиты клонированный Git(ru), заполняем свою авторизацию в утилите для Git, закрываем утилиту. 

* Копируем плагин, удаляем старые addons.xml и addons.xml.md5, щелкаем addons_xml_generator.py для получения новых.

* Запускаем утилиту SmartGit. 

* Старую версию плагина в контекстном меню "Remove", остальное индексируем - Edit - Select all.  На выделенных файлах в контекстном меню "Commit & Push".

* Изменить Git, авторизацию  можно в меню Repository > Settings

* Мы работаем в команде и коммиты на сервер делает ещё кто-то кроме нас. 

* Поэтому в дальнейшем перед началом работы с локальным Git нужно загрузить все изменения, которые произвели другие члены команды в origin репозиторий. 

* Для получения синхронизации с удалённым Git, используем кнопку утилиты SmartGit "Pull".

* После обновления локального Git, продолжаем работу по изменениям в локальном Git и отправке в удалённый Git.

* Good luck!