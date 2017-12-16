import json
import re

from lib import utils
from lib.models import Movie


def parse_main_page(main_page):
    return re.compile(r'<li><a title.*href=\"(\S*)\">(\S*)</a></li>').findall(main_page)


def parse_page_with_movies(page):
    image_list = re.compile(r'<div class=\"filmokimg.*data-link=\"(.*)\">[\s]*'
                            r'<img src=\"(.*)\"\s*alt=\"(.*)\"').findall(page)
    info_list = re.compile(r'<div class=\"filmtex\">\s*.*\s*<a href=\"(.*)\">(.*)</a>\s*(?:.*original">(.*)'
                           r'</div>\s*)?.*\s*.*meta-qual\">(.*)</div>').findall(page)
    movie_list = []
    for movie_from_image_list in image_list:
        combined_movie = Movie()
        combined_movie.url = movie_from_image_list[0]
        combined_movie.img_url = movie_from_image_list[1]
        combined_movie.name = movie_from_image_list[2]
        movie_list.append(combined_movie)

    for movie_from_info_list in info_list:
        index = movie_list.index(movie_from_info_list[0])
        combined_movie = movie_list[index]
        parsed_name = parse_year_from_name(movie_from_info_list[1])
        if parsed_name:
            combined_movie.name = parsed_name[0][0]
            combined_movie.year = parsed_name[0][1]
        else:
            combined_movie.name = movie_from_info_list[1]
        combined_movie.original_name = movie_from_info_list[2]
        combined_movie.quality = movie_from_info_list[3]
        movie_list[index] = combined_movie

    return movie_list


def parse_url_start(url):
    return re.compile(r'(https?://[^:/\n]+)').findall(url)[0]


def parse_cookies(iframe_html):
    cookie = re.compile("\s\swindow.(\w*)\s=\s\'(\w*)\';").findall(iframe_html)[0]
    cookie_header = cookie[0]
    cookie_header = re.sub('\'|\s|\+', '', cookie_header)
    cookie_data = cookie[1]
    cookie_data = re.sub('\'|\s|\+', '', cookie_data)
    cookies = [cookie_header, cookie_data]
    return cookies


def parse_iframe_from_page(page_html, url, client):
    iframe_url = re.compile(r'<iframe.*src=\"(\S*)\".*/iframe>').findall(page_html)[0]
    iframe_html = client.get_html(iframe_url, url)
    iframe_domain = parse_url_start(iframe_url)

    # if episode_number == 0:
    #     try:
    #         episodes = re.compile(r'episodes:\s(.*),').findall(player_page)[0]
    #         if episodes == 'null':
    #             pass
    #         else:
    #             episodes_data = json.loads(episodes)
    #             for episode in episodes_data:
    #                 get_with_referer(player_url, referer, episode[1])
    #             return
    #     except:
    #         pass

    js_path = re.compile(r'script src=\"(.*)\"').findall(iframe_html)[0]
    js_path = iframe_domain + js_path
    js_page = client.get_html(js_path, url)

    manifest_path = re.compile(r'(/manifest.*all)').findall(js_page)[0]

    video_token = re.compile(r"video_token:\s*\S?\'([0-9a-f]*)\S?\'").findall(iframe_html)[0]
    manifest_path = manifest_path.replace("\"+this.options.video_token+\"", video_token)
    manifest_path = iframe_domain + manifest_path

    mw_key = re.compile(r"mw_key:\"(\w+)\"").findall(js_page)[0]
    cookie_key = re.compile(r"iframe_version.*,(\w*):e.\w*").findall(js_page)[0]

    mw_pid = re.compile(r"partner_id:\s*(\w*),").findall(iframe_html)[0]
    p_domain_id = re.compile(r"domain_id:\s*(\w*),").findall(iframe_html)[0]
    cookies = parse_cookies(iframe_html)

    req_data = {"mw_key": mw_key, "iframe_version": "2.1", "mw_pid": mw_pid, "p_domain_id": p_domain_id,
                "ad_attr": '0', cookie_key: cookies[1]}
    headers = {
        "X-Requested-With": "XMLHttpRequest"
    }
    json_data = client.get_html(manifest_path, url, post_params=req_data, post_headers=headers)
    data = json.loads(json_data)

    manifest_file_mp4 = client.get_html(data["mans"]["manifest_mp4"], url)
    manifest_file_hls = client.get_html(data["mans"]["manifest_m3u8"], url)

    try:
        links_mp4 = json.loads(manifest_file_mp4)
    except:
        links_mp4 = re.compile("RESOLUTION=(\d*x\d*)\S*\s*(http\S*m3u8)").findall(manifest_file_mp4)

    links_hls = re.compile("RESOLUTION=(\d*x\d*)\S*\s*(http\S*m3u8)").findall(manifest_file_hls)
    if isinstance(links_mp4, list):
        links_mp4.extend(links_hls)
    else:
        links_mp4.update(links_hls)
    return dict(links_mp4)


def parse_year_from_name(name):
    return re.compile(r'(.*[^\d()\s-])\s?\(?(\d{0,4}-?\d{3,4})\)?').findall(name)
