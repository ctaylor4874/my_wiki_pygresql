import pg
import app


class Page:
    def placeHolder(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = "select page_content,last_modified_date,author_last_modified, id from page where title = '%s'" % self.title
            entry = Database.getAll(query)
            for result in entry:
                self.page_content = result.page_content
                self.last_modified_date = result.last_modified_date
                self.author_last_modified = result.author_last_modified
        return exists

    def login(self):
        query= "select username,password from login where username = '%s'" % self.username
        result_list=Database.getAll(query)
        login_dict = {}
        if result_list != None:
            for result in result_list:
                login_dict.update({'username': result.username})
                login_dict.update({'password': result.password})
        return login_dict

    def save(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = "UPDATE page SET page_content = '%s', author_last_modified = '%s', last_modified_date = now() WHERE title = '%s'" % (
                Database.escape(self.page_content), Database.escape(self.author_last_modified), self.title)
            Database.doQuery(query)
            query = "select page_content,last_modified_date,author_last_modified, id from page where title = '%s'" % self.title
            entry = Database.getAll(query)
            for result in entry:
                self.page_content = result.page_content
                self.last_modified_date = result.last_modified_date
                self.author_last_modified = result.author_last_modified
                self.id = result.id
            self.pageid = self.id
            query = "insert into pagehistory (title, page_content, author_last_modified, last_modified_date, pageid) values('%s', '%s', '%s',now(), %d)" % (
                self.title, Database.escape(self.page_content), Database.escape(self.author_last_modified), self.pageid)
            Database.doQuery(query)
        else:
            query = "insert into page (title, page_content, author_last_modified, last_modified_date) values('%s', '%s', '%s',now())" % (
                self.title, Database.escape(self.page_content), Database.escape(self.author_last_modified))
            Database.doQuery(query)
            query = "select page_content,last_modified_date,author_last_modified,id from page where title = '%s'" % self.title
            entry = Database.getAll(query)
            for result in entry:
                self.page_content = result.page_content
                self.last_modified_date = result.last_modified_date
                self.author_last_modified = result.author_last_modified
                self.id = result.id
            self.pageid = self.id
            query = "insert into pagehistory (title, page_content, author_last_modified, last_modified_date, pageid) values('%s', '%s', '%s',now(), %d)" % (
                self.title, Database.escape(self.page_content), Database.escape(self.author_last_modified), self.pageid)
            Database.doQuery(query)

    def update(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = ("select page_content from page where title = '%s'") % (self.title)
            self.page_content = Database.getContent(query)

    @staticmethod
    def getArchives(page_name):
        query = "SELECT id FROM page WHERE title = '%s'" % (page_name)
        id = Database.getResult(query)
        pageid = id[0]
        query = "SELECT last_modified_date, revisionid FROM pagehistory WHERE pageid = %d" % (pageid)
        archives = {}
        list = Database.getResult(query)
        for item in list:
            archives.update({item[0]: item[1]})
        return archives

    @staticmethod
    def archiveContent(revisionid):
        print revisionid
        archiveContent = {}
        query = "select page_content,author_last_modified,last_modified_date from pagehistory where revisionid = '%d'" % int(
            revisionid)
        entry = Database.getAll(query)
        for result in entry:
            archiveContent.update({'page_content':result.page_content})
            archiveContent.update({'last_modified_date':result.last_modified_date})
            archiveContent.update({'author_last_modified':result.author_last_modified})
        return archiveContent

    # def __str__(self):
    #     return self.name

    @staticmethod
    def getObjects():
        query = "SELECT title,author_last_modified,last_modified_date FROM page"
        result_set = Database.getResult(query)
        return result_set


class Database(object):
    @staticmethod
    def getConnection():
        return pg.DB(host=app.DBHOST, user=app.DBUSER, passwd=app.DBPASS, dbname=app.DBNAME)

    @staticmethod
    def escape(value):
        return value.replace("'", "''")

    @staticmethod
    def getAll(query):
        db=Database.getConnection()
        entry = db.query(query)
        entry=entry.namedresult()
        return entry

    @staticmethod
    def getContent(query):
        db=Database.getConnection()
        entry=db.query(query)
        entry=entry.getresult()
        page_content=entry[0]
        print type(page_content)
        return page_content

    @staticmethod
    def getResult(query, getOne=False):
        db = Database.getConnection()
        entry = db.query(query)
        result_set=entry.getresult()
        return result_set

    @staticmethod
    def checkTitles(title):
        db=Database.getConnection()
        sql=db.query("SELECT id FROM page WHERE title = '%s'"% (title))
        sel=sql.namedresult()
        if sel:
            exists=True
        else:
            exists=False
        return exists

    @staticmethod
    def doQuery(query):
        db=Database.getConnection()
        db.query(query)
