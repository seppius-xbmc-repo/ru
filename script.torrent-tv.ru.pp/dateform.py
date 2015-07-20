import xbmcgui
import time
import calendar
import datetime


class DateForm(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.li = None
        self.get_method = None
        self.session = None
        self.result = 'None'
        self.date = time.localtime()
        self.list = None
        pass

    def onInit(self):
        lblDate = self.getControl(102)
        lblDate.setLabel(self.date.isoformat())
        
        self.list = self.getControl(103)
        self.fillDays(self.date)
        pass

    def fillDays(self, value):
        self.list.reset()
        item = xbmcgui.ListItem("..")
        item.setProperty("type", "day")
        item.setProperty("date", value.isoformat())
        self.list.addItem(item)
        print "DATE IS %s" % value.isoformat()
        maxdays = calendar.monthrange(value.year, value.month)[1]
        i = 1
        while i <= maxdays:

            if i == self.date.day and value.month == self.date.month and value.year == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty("type", "day")
            item.setProperty("date", datetime.date(value.year, value.month, i).isoformat())
            self.list.addItem(item)
            i = i + 1
        if value.month == self.date.month and value.year == self.date.year:
            self.list.selectItem(self.date.day)
        self.setFocus(self.list)

    def fillMonth(self, value):
        self.list.reset()
        item = xbmcgui.ListItem("..")
        item.setProperty("type", "month")
        item.setProperty("date", value.isoformat())
        self.list.addItem(item)
        month = 12
        i = 1
        while i <= month:
            if i == self.date.month and value.year == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty("type", "month")
            item.setProperty("date", datetime.date(value.year, i, 1).isoformat())
            self.list.addItem(item)
            i = i + 1

        if value.year == self.date.year:
            self.list.selectItem(self.date.month)
        self.setFocus(self.list)

    def fillYear(self, value):
        self.list.reset()
        i = 2013
        while i <= value.year:
            if i == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty("date", datetime.date(i, 1, 1).isoformat())
            item.setProperty("type", "year")
            self.list.addItem(item)
            i = i + 1

        self.list.selectItem(i - 2013)
        self.setFocus(self.list)

    def onClick(self, controlId):
        if controlId == 103:
            self.list = self.getControl(controlId)
            selItem = self.list.getSelectedItem()
            if selItem.getLabel() == "..":
                stime = time.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                value = datetime.date(stime.tm_year, stime.tm_mon, stime.tm_mday)
                if selItem.getProperty("type") == "day":
                    self.fillMonth(value)
                elif selItem.getProperty("type") == "month":
                    self.fillYear(datetime.datetime.today())
            else:
                if selItem.getProperty("type") == "day":
                    print 'Choose day is %s' % selItem.getProperty("date")
                    #self.date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(selItem.getProperty("date"), "%Y-%m-%d")))
                    #self.date = datetime.datetime.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                    date = time.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                    self.date = datetime.date(date.tm_year, date.tm_mon, date.tm_mday)
                    self.close()
                elif selItem.getProperty("type") == "month":
                    print 'Choose month is %s' % selItem.getProperty("date")
                    #value = datetime.datetime.fromtimestamp(time.mktime(time.strptime(selItem.getProperty("date"), "%Y-%m-%d")))
                    #value = datetime.datetime.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                    stime = time.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                    value = datetime.date(stime.tm_year, stime.tm_mon, stime.tm_mday)
                    self.fillDays(value)
                elif selItem.getProperty("type") == "year":
                    print 'Choose year is %s' % selItem.getProperty("value")
                    date = datetime.date(int(selItem.getProperty("value")), 1, 1)
                    self.fillMonth(date)

        super(DateForm, self).onClick(controlId)
