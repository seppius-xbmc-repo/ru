ContentType = ''
class ItemPaging:
    itemsOnPage = '0'
    pageNumber = '0'
    totalItems = '0'
    totalPages = '0'
    def get(self):
        req = ''
        if self.itemsOnPage == '0' and self.pageNumber == '0' and self.totalItems == '0' and self.totalPages == '0':
            req = '<d4p1:paging xmlns:d5p1="http://schemas.datacontract.org/2004/07/IVS.Common" i:nil="true" />'
        else:
            req = '<d4p1:paging xmlns:d5p1="http://schemas.datacontract.org/2004/07/IVS.Common">'
            self.itemsOnPage = '<d5p1:itemsOnPage>' + self.itemsOnPage + '</d5p1:itemsOnPage>'
            self.pageNumber = '<d5p1:pageNumber>' + self.pageNumber + '</d5p1:pageNumber>'
            self.totalItems = '<d5p1:totalItems>' + self.totalItems + '</d5p1:totalItems>'
            self.totalPages = '<d5p1:totalPages>' + self.totalPages + '</d5p1:totalPages>'
            req = req + self.itemsOnPage + self.pageNumber + self.totalItems + self.totalPages + '</d4p1:paging>'
        return req
    
     
    
    
    