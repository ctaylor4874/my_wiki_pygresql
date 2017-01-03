import mysql.connector
import dbconfig


class Page:
    def placeHolder(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = "select page_content,last_modified_date,author_last_modified, id from page where title = '%s'" % self.title
            entry = Database.getAll(query)
            self.page_content = entry[0]
            self.last_modified_date = entry[1]
            self.author_last_modified = entry[2]
        return exists

    def login(self):
        query = ("select username, password from login where username = '%s'" % self.username)
        result_list = Database.getAll(query)
        login_dict = {}
        if result_list != None:
            login_dict.update({'username': result_list[0]})
            login_dict.update({'password': result_list[1]})
        return login_dict

    def save(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = "UPDATE page SET page_content = '%s', author_last_modified = '%s', last_modified_date = now() WHERE title = '%s'" % (
                Database.escape(self.page_content), Database.escape(self.author_last_modified), self.title)
            Database.doQuery(query)
            query = "select page_content,last_modified_date,author_last_modified, id from page where title = '%s'" % self.title
            entry = Database.getAll(query)
            self.page_content = entry[0]
            self.last_modified_date = entry[1]
            self.author_last_modified = entry[2]
            self.id = entry[3]
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
            self.page_content = entry[0]
            self.last_modified_date = entry[1]
            self.author_last_modified = entry[2]
            self.id = entry[3]
            self.pageid = self.id
            query = "insert into pagehistory (title, page_content, author_last_modified, last_modified_date, pageid) values('%s', '%s', '%s',now(), %d)" % (
                self.title, Database.escape(self.page_content), Database.escape(self.author_last_modified), self.pageid)
            Database.doQuery(query)

    def update(self):
        exists = Database.checkTitles(self.title)
        if exists:
            query = "select page_content from page where title = '%s'" % self.title
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
        archiveContent.update({'page_content': entry[0]})
        archiveContent.update({'author_last_modified': entry[1]})
        archiveContent.update({'last_modified_date': entry[2]})
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
        return mysql.connector.connect(user=dbconfig.dbUser, password=dbconfig.dbPassword, host=dbconfig.dbHost,
                                       database=dbconfig.dbName)

    @staticmethod
    def escape(value):
        return value.replace("'", "''")

    @staticmethod
    def getAll(query):
        conn = Database.getConnection()
        cur = conn.cursor()
        cur.execute(query)
        entry = cur.fetchone()
        cur.close()
        conn.close()
        return entry

    @staticmethod
    def getContent(query):
        conn = Database.getConnection()
        cur = conn.cursor()
        cur.execute(query)
        entry = cur.fetchone()
        page_content = entry[0]
        cur.close()
        conn.close()
        return page_content

    @staticmethod
    def getResult(query, getOne=False):
        conn = Database.getConnection()
        cur = conn.cursor()
        cur.execute(query)
        if getOne:
            result_set = cur.fetchone()
        else:
            result_set = cur.fetchall()
        cur.close()
        conn.close()
        return result_set

    @staticmethod
    def checkTitles(title):
        conn = Database.getConnection()
        cur = conn.cursor()
        sql = "SELECT COUNT(1) FROM page WHERE title = '%s'" % title
        cur.execute(sql)
        if cur.fetchone()[0]:
            exists = True
        else:
            exists = False
        cur.close()
        conn.close()
        return exists

    @staticmethod
    def doQuery(query):
        conn = Database.getConnection()
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
