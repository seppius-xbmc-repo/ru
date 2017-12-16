class Movie:
    url = ""
    img_url = ""
    name = ""
    original_name = ""
    quality = ""
    year = ""
    country = ""
    genre = ""
    director = ""
    description = ""
    translate = ""

    def __init__(self):
        pass

    def __eq__(self, other):
        if other is None:
            return False
        elif isinstance(other, Movie):
            return self.url == other.url
        elif isinstance(other, str):
            return self.url == other
        else:
            return False

    def get_title(self):
        title = self.name
        if self.original_name != '':
            title += " | " + self.original_name
        if self.quality != '':
            title += " [" + self.quality + "]"
        if self.year != '':
            title += " " + self.year
        return title
