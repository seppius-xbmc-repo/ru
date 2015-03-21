#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2010-2011 Eugene Bond
# *	     eugene.bond@gmail.com
# *
# *      XBMC medialibrary stuff
# */

try:
	import xbmc
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
			self.LOGDEBUG = 1
		
		def output(self, data, level = 0):
			print data
		
		def getInfoLabel(self, param):
			return '%s unknown' % param
		
		def translatePath(self, param):
			return param
		
		def getCacheThumbName(self, path):
			return ''
	
	xbmc = xbmc_boo()
	

VIDEODB_ID_TITLE = 0
VIDEODB_ID_PLOT = 1
VIDEODB_ID_PLOTOUTLINE = 2
VIDEODB_ID_TAGLINE = 3
VIDEODB_ID_VOTES = 4
VIDEODB_ID_RATING = 5
VIDEODB_ID_CREDITS = 6
VIDEODB_ID_YEAR = 7
VIDEODB_ID_THUMBURL = 8
VIDEODB_ID_IDENT = 9
VIDEODB_ID_SORTTITLE = 10
VIDEODB_ID_RUNTIME = 11
VIDEODB_ID_MPAA = 12
VIDEODB_ID_TOP250 = 13
VIDEODB_ID_GENRE = 14
VIDEODB_ID_DIRECTOR = 15
VIDEODB_ID_ORIGINALTITLE = 16
VIDEODB_ID_THUMBURL_SPOOF = 17
VIDEODB_ID_STUDIOS = 18
VIDEODB_ID_TRAILER = 19
VIDEODB_ID_FANART = 20
VIDEODB_ID_COUNTRY = 21


import string, os, re, urllib

try:
	from sqlite3 import dbapi2 as sqlite
	xbmc.output("Loading sqlite3 as DB engine")
except:
	from pysqlite2 import dbapi2 as sqlite
	xbmc.output("Loading pysqlite2 as DB engine")


def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			return "" # ignore tags
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return unichr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return unicode(entity, "iso-8859-1")
		return text # leave as is
	return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)


class movielibmovie:
	def __init__(self, path):
		
		self.title = ''
		self.description = ''
		self.genres = []
		self.actors = []
		self.year = None
		self.files = []
		self.image = ''
		self.path = path
		self.studio = ''
		self.director = ''
		self.writter = ''
		self.trailer = ''
		self.rating = 0
		self.country = None
		xbmc.output('[movielib] creating a movie object')
		
	def setTitle(self, title):
		self.title = title
	def setDescription(self, description):
		self.description = strip_html(description)
	def setGenres(self, genres):
		self.genres = []
		for genre in genres:
			self.addGenre(genre)
	def addGenre(self, genre):
		self.genres.append(genre)
	def setActors(self, actors):
		self.actors = []
		for actor in actors:
			self.addActor(actor)
	def addActor(self, actor):
		self.actors.append(actor)
	def setYear(self, year):
		self.year = year
	def setImage(self, image):
		self.image = image
	def setRating(self, rating):
		self.rating = rating
	def setStudio(self, studio):
		self.studio = studio
	def setDirector(self, director):
		self.director = director
	def setWritter(self, writter):
		self.writter = writter
	def setCountry(self, country):
		self.country = country
	def setFiles(self, files):
		self.files = []
		for filename in files:
			self.addFile(filename)
	def addFile(self, filename, title = ''):
		self.files.append((filename, title,))
	def setTrailer(self, url):
		self.trailer = url

class movielib:
	
	def __init__(self, db = None):
		if not db:
			db = 'special://profile/Database/MyVideos34.db'
		db = xbmc.translatePath(db)
		self.connection = sqlite.connect(db)
		self.connection.row_factory = sqlite.Row
		self.db = self.connection.cursor()
	
	def addMovie(self, movie):
		if len(movie.files):
			xbmc.output('[movielib] adding a "%s" movie' % movie.title.encode('utf-8'))
			counter = 0
			for filename, filetitle in movie.files:
				mid = self._vdbAddMovie(movie.path, filename)
				if not mid:
					continue
				for genre in movie.genres:
					self._vdbAddGenreToMovie(mid, genre)
				for actor in movie.actors:
					self._vdbAddActorToMovie(mid, actor)
				title = movie.title
				sorttitle = '%s - %02d' % (title, counter)
				counter += 1
				if filetitle:
					title = '%s (%s)' % (title, filetitle)
				self._vdbUpdateMovieTitle(mid, title)
				self._vdbUpdateMovieRating(mid, movie.rating)
				self._vdbUpdateMovieDescription(mid, movie.description)
				self._vdbUpdateMovieYear(mid, movie.year)
				self._vdbUpdateMovieImage(mid, movie.image, '%s%s' % (movie.path, filename))
				self._vdbUpdateMovieGenres(mid, movie.genres)
				self._vdbUpdateMovieTrailer(mid, movie.trailer)
				self._vdbUpdateMovieDirector(mid, movie.director)
				self._vdbUpdateMovieWritters(mid, movie.writter)
				self._vdbUpdateMovieStudio(mid, movie.studio)
				self._vdbUpdateMovieCountry(mid, movie.country)
				
				if len(movie.files) > 1:
					sid = self._vdbAddSet(movie.title)
					self._vdbAddSetToMovie(sid, mid)
				
			self.connection.commit()
			return mid
		else:
			xbmc.output('[movielib] movie is here, but files are not here.. skipping %s' % movie.title.encode('utf-8'))
	
	def _vdbDeleteMovie(self, mid):
		xbmc.output('[movielib] removing movie #%s' % mid)
		self.db.execute("DELETE FROM setlinkmovie WHERE idMovie=?", (mid,))
		self.db.execute("DELETE FROM genrelinkmovie WHERE idMovie=?", (mid,))
		self.db.execute("DELETE FROM actorlinkmovie WHERE idMovie=?", (mid,))
		self.db.execute("DELETE FROM studiolinkmovie WHERE idMovie=?", (mid,))
		self.db.execute("DELETE FROM countrylinkmovie WHERE idMovie=?", (mid,))
		self.db.execute("DELETE FROM movie WHERE idMovie=?", (mid,))
		self.connection.commit()
		
	
	def vdbFileExists(self, path, filename):
		pid = self._vdbGetPathId(path)
		if not pid:
			return False
		return self._vdbGetFileId(pid, filename)
	
	def _vdbGetPathId(self, path):
		path = self._addSlashAtEnd(path)
		self.db.execute("SELECT idPath FROM path WHERE strPath=?", (path,))
		res = self.db.fetchone()
		if res:
			return res['idPath']
	
	def _vdbAddPath(self, path):
		path = self._addSlashAtEnd(path)
		if self.db.execute("INSERT INTO path (idPath, strPath, strContent, strScraper) VALUES (NULL,?,'','')", (path,)):
			return self.db.lastrowid
	
	def _vdbGetFileId(self, pathid, filename):
		self.db.execute("SELECT idFile FROM files WHERE idPath=? AND strFileName = ? ", (pathid, filename,))
		res = self.db.fetchone()
		if res:
			return res['idFile']
	
	def _vdbGetMovieId(self, fileid):
		self.db.execute("SELECT idMovie FROM movie WHERE idFile=? ", (fileid,))
		res = self.db.fetchone()
		if res:
			return res['idMovie']
	
	def _vdbUpdateMovieField(self, mid, field, value):
		self.db.execute("UPDATE movie SET c%02d=? WHERE idMovie=?" % field, (value, mid,))
	
	def _vdbUpdateMovieTitle(self, mid, title, sorttitle = None):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_TITLE, title)
		self._vdbUpdateMovieField(mid, VIDEODB_ID_SORTTITLE, sorttitle)
	
	def _vdbUpdateMovieDescription(self, mid, string):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_PLOT, string)
		self._vdbUpdateMovieField(mid, VIDEODB_ID_PLOTOUTLINE, string)
	
	def _vdbUpdateMovieYear(self, mid, year):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_YEAR, year)
	
	def _vdbUpdateMovieWritters(self, mid, writters):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_CREDITS, writters)
	
	def _vdbUpdateMovieDirector(self, mid, director):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_DIRECTOR, director)
	
	def _vdbUpdateMovieRating(self, mid, rating):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_RATING, rating)
	
	def _vdbUpdateMovieImage(self, mid, img, path = None):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_THUMBURL, img)
		#self._vdbUpdateMovieField(mid, VIDEODB_ID_FANART, img)
		if path:
			cache = xbmc.getCacheThumbName(path)
			if cache:
				THUMB_CACHE_PATH   = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
				cache = os.path.join(THUMB_CACHE_PATH, cache[0], cache)
				xbmc.output('[movielib] downloading image %s to cache %s' % (img, cache))
				urllib.urlretrieve(img, cache)
	
	def _vdbUpdateMovieTrailer(self, mid, url):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_TRAILER, url)
	
	def _vdbUpdateMovieStudio(self, movieid, studio):
		self._vdbUpdateMovieField(movieid, VIDEODB_ID_STUDIOS, studio)
		sid = self._vdbAddStudio(studio)
		if sid:
			self._vdbAddToLinkTable("studiolinkmovie", "idStudio", sid, "idMovie", movieid)
	
	def _vdbUpdateMovieCountry(self, movieid, country):
		self._vdbUpdateMovieField(movieid, VIDEODB_ID_COUNTRY, country)
		cid = self._vdbAddCountry(country)
		if cid:
			self._vdbAddToLinkTable("countrylinkmovie", "idCountry", cid, "idMovie", movieid)
	
	def _vdbUpdateMovieGenres(self, mid, genres):
		self._vdbUpdateMovieField(mid, VIDEODB_ID_GENRE, ", ".join(genres))
	
	def _vdbAddMovie(self, path, filename):
		fid = self.vdbAddFile(path, filename)
		if not fid:
			return
		mid = self._vdbGetMovieId(fid)
		if not mid:
			if self.db.execute("INSERT INTO movie (idMovie, idFile) VALUES (NULL,?)", (fid,)):
				mid = self.db.lastrowid
		return mid
	
	def _vdbAddGenre(self, genre):
		return self._vdbAddToTable("genre", "idGenre", "strGenre", genre)
	
	def _vdbAddActor(self, actor):
		return self._vdbAddToTable("actors", "idActor", "strActor", actor)
	
	def _vdbAddCountry(self, country):
		return self._vdbAddToTable("country", "idCountry", "strCountry", country)
	
	def _vdbAddStudio(self, studio):
		return self._vdbAddToTable("studio", "idStudio", "strStudio", studio)
	
	def _vdbAddSet(self, name):
		return self._vdbAddToTable("sets", "idSet", "strSet", name)
	
	def _vdbAddSetToMovie(self, setid, movieid):
		self._vdbAddToLinkTable("setlinkmovie", "idSet", setid, "idMovie", movieid)
	
	def _vdbAddGenreToMovie(self, movieid, genre):
		gid = self._vdbAddGenre(genre)
		if gid:
			self._vdbAddToLinkTable("genrelinkmovie", "idGenre", gid, "idMovie", movieid)
	
	def _vdbAddActorToMovie(self, movieid, actor):
		aid = self._vdbAddActor(actor)
		if aid:
			self._vdbAddToLinkTable("actorlinkmovie", "idActor", aid, "idMovie", movieid)
	
	def _vdbAddToLinkTable(self, table, firstField, firstValue, secondField, secondValue):
		sql1 = "SELECT * FROM %s WHERE %s = ? AND %s = ?" % (table, firstField, secondField)
		sql2 = "INSERT INTO %s (%s, %s) VALUES (?, ?)" % (table, firstField, secondField)
		
		self.db.execute(sql1, (firstValue,secondValue,))
		res = self.db.fetchone()
		if not res:
			self.db.execute(sql2, (firstValue,secondValue,))
		
	def _vdbAddToTable(self, table, idField, valueField, value):
		sql1 = "SELECT %s FROM %s WHERE %s = ?" % (idField, table, valueField)
		sql2 = "INSERT INTO %s (%s, %s) VALUES (NULL, ?)" % (table, idField, valueField)
		
		self.db.execute(sql1, (value,))
		res = self.db.fetchone()
		if res:
			return res[idField]
		
		self.db.execute(sql2, (value,))
		return self.db.lastrowid
	
	def vdbAddFile(self, path, filename):
		pid = self._vdbGetPathId(path)
		if not pid:
			pid = self._vdbAddPath(path)
		if not pid:
			return
		fid = self._vdbGetFileId(pid, filename)
		if not fid:
			xbmc.output('[movielib] adding a new file %s' % filename.encode('utf-8'))
			if self.db.execute("INSERT INTO files (idFile,idPath,strFileName) VALUES (NULL,?,?)", (pid, filename,)):
				fid = self.db.lastrowid
		
		return fid
	
	def vdbCleanUp(self, path, removeFiles = True):
		xbmc.output('[movielib] starting cleanup of %s' % path)
		path = self._addSlashAtEnd(path)
		pid = self._vdbGetPathId(path)
		if pid:
			sql = "SELECT files.idFile, idMovie FROM files LEFT JOIN movie ON files.idFile = movie.idFile WHERE files.idPath = ?"
			self.db.execute(sql, (pid,))
			for res in self.db.fetchall():
				fid, mid = res
				if mid:
					self._vdbDeleteMovie(mid)
				if removeFiles and fid:
					self.db.execute("DELETE FROM files WHERE idFile = ?", (fid,))
					self.connection.commit()
	
	def vdbMovieByPathAndTrailer(self, path, trailer):
		pid = self._vdbGetPathId(path)
		if not pid:
			return
		sql = "SELECT idMovie FROM files JOIN movie ON files.idFile = movie.idFile WHERE files.idPath = ? AND movie.c%02d = ?" % VIDEODB_ID_TRAILER
		self.db.execute(sql, (pid, trailer,))
		return self.db.fetchone()		
	
	def _addSlashAtEnd(self, path):
		# disabled for now as plugins on Windows uses non-system slashes?
		if not path.endswith(os.path.sep):
			#path += os.path.sep
			xbmc.output('[movielib] path %s was not translated to %s' % (path, path + os.path.sep))
			
		return path
	
	
	def test(self):
		import pprint
		
		m = movielibmovie('/foo/bar/')
		m.addGenre('Pipetka')
		m.addGenre('Kanserva')
		m.addFile('baz.avi')
		m.setTitle('File Test')
		pprint.pprint(m.files)
		pprint.pprint(m)
		
		test = self.addMovie(m)
		
		m = movielibmovie('/foo/bar/')
		m.addGenre('Kanserva')
		m.addFile('blah-01.avi', 'Part 1')
		m.addFile('blah-02.avi', 'Part 2')
		m.setImage('foo.jpg')
		m.setTitle('Set Test')
		m.setYear('2010')
		self.addMovie(m)
		
		
		m = movielibmovie('http://www.google.com/search')
		m.addGenre('Google')
		m.addGenre('Search')
		m.addFile('?q=preved', 'dummy')
		m.setTitle('Google search')
		m.setDescription('This is a google search!')
		self.addMovie(m)
		
		self.vdbCleanUp('/foo/bar/')
		
		#self._vdbDeleteMovie(test)

if __name__ == '__main__':
	foo = movielib('./MyVideos34.db')
	foo.test()   