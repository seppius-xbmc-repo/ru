# -*- coding: utf-8 -*-
import sys
import urlparse
import xbmcgui
import xbmcplugin
from lib.postnaukalib import (
        Logger,
        MultipleActions,
        Parser,
        List,
        Plugin,
        SCIENCES,
        SITE,
        URLS,
        youtubeAddonUrl,
    )

args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(Plugin.handle, 'movies')
sci_urls_dict = dict((sci, SITE + "themes/" + sci) for sci in SCIENCES)
URLS.update(sci_urls_dict)

menu = List()
parser = Parser()
log = Logger()
log.debug("Base URL: {0}".format(Plugin.url))
log.debug("Args: {0}".format(args))


def play_video_page(url):
    log.debug("Playing video {video_url}".format(video_url=url))
    video_id = menu.get_video_id_from_url(url)
    path = youtubeAddonUrl + video_id
    listitem = xbmcgui.ListItem(path=path, )
    xbmcplugin.setResolvedUrl(Plugin.handle, True, listitem)

# def test():
#     log.info("Testing")


action = args.get("action")
log.debug("Action = '{action}'".format(action=action))


if action is None:
    menu.main_menu()
elif len(action) > 1:
    log.error("Action: {0}".format(str(action)))
    raise MultipleActions("Multiple actions in URL!")
elif action[0] == "list":
    Plugin.handle = int(sys.argv[1])
    page = int(args["page"][0]) if "page" in args else 1
    menu.display_topic(args["topic"][0], page)
elif action[0] == "play_video":
    Plugin.handle = int(sys.argv[1])
    play_video_page(args["video_url"][0])
elif action[0] == "search":
    Plugin.handle = int(sys.argv[1])
    page = int(args["page"][0]) if "page" in args else 1
    menu.list_search(page, args.get("query"))
# elif action[0] == "test":
#     Plugin.handle = int(sys.argv[1])
#     test()
