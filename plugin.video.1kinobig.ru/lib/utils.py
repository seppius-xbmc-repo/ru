import xbmc
import xbmcgui


def show_message(title, message, icon, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (title, message, times, icon))


def show_alert(title, message):
    xbmcgui.Dialog().ok(title, message)


def fix_string(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string


def fix_1251(string):
    return string.decode('cp1251')


def resort_categories(categories):
    sorted_list = categories[::2]
    sorted_list += categories[1::2]
    return sorted_list


def encode_url(query):
    query = query.items()
    query_str = []
    for k, v in query:
        query_str.append(k + '=' + v)
    return '&'.join(query_str)

