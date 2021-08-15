from logic.book import Book, BookRatings
import sqlite3

from pathlib import Path
from logic.user import User, UserSettings
from ast import literal_eval

class Database:
    __db_con: sqlite3.dbapi2

    @staticmethod
    def get_database_location():
        return str(Path.home()) + "/snakebrary.db"

    @staticmethod
    def create_connection():
        global __db_con
        __db_con = sqlite3.connect(Database.get_database_location())

    @staticmethod
    def close_connection():
        global __db_con
        __db_con.close()

    @staticmethod
    def create_new_tables():
        Database.create_new_users_table()
        Database.create_new_account_settings_table()
        Database.create_new_books_table()
        Database.create_new_books_ratings_table()

    @staticmethod
    def create_new_users_table():
        global __db_con
        __db_con.execute('''CREATE TABLE users
        (username   TEXT  PRIMARY KEY  NOT NULL,
        password    TEXT    NOT NULL,
        password_hint   TEXT    NOT NULL,
        name    TEXT    NOT NULL,
        privilege   INT NOT NULL,
        photo   BLOB,
        date_time_created    TEXT    NOT NULL);''')

    @staticmethod
    def create_new_account_settings_table():
        global __db_con
        __db_con.execute('''CREATE TABLE account_settings
        (username   TEXT  PRIMARY KEY  NOT NULL,
        theme    TEXT    NOT NULL,
        accent_colour   TEXT    NOT NULL);''')
    
    @staticmethod
    def create_new_books_table():
        global __db_con
        __db_con.execute('''CREATE TABLE books
        (ISBN   TEXT  PRIMARY KEY  NOT NULL,
        name    TEXT    NOT NULL,
        author   TEXT    NOT NULL,
        holders    TEXT    NOT NULL,
        genres    TEXT    NOT NULL,
        price   FLOAT NOT NULL,
        about   TEXT,
        photo   BLOB,
        date_time_added    TEXT    NOT NULL);''')

    @staticmethod
    def create_new_books_ratings_table():
        global __db_con
        __db_con.execute('''CREATE TABLE books_ratings
        (ISBN   TEXT  PRIMARY KEY  NOT NULL,
        ratings   TEXT    NOT NULL);''')


    @staticmethod
    def create_new_user(new_user: User):
        global __db_con

        if new_user.photo == None:
            __db_con.execute(f'''INSERT INTO users(username, password, password_hint, name, privilege, photo, date_time_created)
            VALUES ("{new_user.username}", "{new_user.password}", 
            "{new_user.password_hint}", "{new_user.name}", "{new_user.privilege}", NULL,
            "{new_user.date_time_created}");''')
        else:
            __db_con.execute(f'''INSERT INTO users(username, password, password_hint, name, privilege, photo, date_time_created)
            VALUES ("{new_user.username}", "{new_user.password}", 
            "{new_user.password_hint}", "{new_user.name}", "{new_user.privilege}", ?,
            "{new_user.date_time_created}");''', [sqlite3.Binary(new_user.photo)])

        __db_con.execute(f'''INSERT INTO account_settings(username, theme, accent_colour)
        VALUES ("{new_user.username}", "light", "purple")''')

        Database.save_database()
    
    @staticmethod
    def update_user(user: User):
        global __db_con

        if user.photo == None:
            __db_con.execute(f'''UPDATE users
            SET password="{user.password}", password_hint="{user.password_hint}", name="{user.name}", 
            privilege="{user.privilege}", photo=NULL
            WHERE username="{user.username}"''')
        else:
            __db_con.execute(f'''UPDATE users
            SET password="{user.password}", password_hint="{user.password_hint}", name="{user.name}", 
            privilege="{user.privilege}", photo=?
            WHERE username="{user.username}"''', [sqlite3.Binary(user.photo)])

        Database.save_database()

    @staticmethod
    def create_new_book(new_book: Book):
        global __db_con

        if new_book.photo == None:
            __db_con.execute(f'''INSERT INTO books(ISBN, name, author, holders, genres, price, about, photo, date_time_added)
            VALUES ("{new_book.ISBN}", "{new_book.name}", 
            "{new_book.author}", "{new_book.holders}", "{new_book.genres}", "{new_book.price}", "{new_book.about}", NULL, "{new_book.date_time_added}");''')
        else:
            __db_con.execute(f'''INSERT INTO books(ISBN, name, author, holders, genres, price, about, photo, date_time_added)
            VALUES ("{new_book.ISBN}", "{new_book.name}", 
            "{new_book.author}", "{new_book.holders}", "{new_book.genres}", "{new_book.price}", "{new_book.about}", ?, "{new_book.date_time_added}");''', [sqlite3.Binary(new_book.photo)])

        __db_con.execute(f'''INSERT INTO books_ratings(ISBN, ratings)
        VALUES ("{new_book.ISBN}", "{{}}")''')

        Database.save_database()
    
    @staticmethod
    def update_book(book: Book):
        global __db_con

        if book.photo == None:
            __db_con.execute(f'''UPDATE books
            SET name="{book.name}", author="{book.author}", holders="{book.holders}", genres="{book.genres}", 
            price="{book.price}", about="{book.about}", photo=NULL
            WHERE ISBN="{book.ISBN}"''')
        else:
            __db_con.execute(f'''UPDATE books
            SET name="{book.name}", author="{book.author}", holders="{book.holders}", genres="{book.genres}", 
            price="{book.price}", about="{book.about}", photo=?
            WHERE ISBN="{book.ISBN}"''', [sqlite3.Binary(book.photo)])
        
        Database.save_database()

    @staticmethod
    def update_book_ratings(book_ratings: BookRatings):
        global __db_con

        __db_con.execute(f'''UPDATE books_ratings
        SET ratings="{book_ratings.ratings}" 
        WHERE ISBN="{book_ratings.ISBN}"''')

        Database.save_database()

    @staticmethod
    def get_users_by_username(username):
        return Database.__filter_users(f'SELECT * FROM users WHERE username="{username}"')

    @staticmethod
    def get_books_by_ISBN(ISBN):
        return Database.__filter_books(f'SELECT * FROM books WHERE ISBN="{ISBN}"')

    @staticmethod
    def get_all_users():
        return Database.__filter_users(f'SELECT * FROM users')

    @staticmethod
    def __filter_users(sql):
        global __db_con
        __db_con.execute(sql)
        users = list(__db_con.execute(sql))

        tbr = []

        for i in users:
            tba = User(i[0], i[1], i[2], i[3], i[4], i[5])
            tba.print_details()
            tbr.append(tba)

        return tbr
    
    @staticmethod
    def get_all_books():
        return Database.__filter_books(f'SELECT * FROM books')

    @staticmethod
    def __filter_books(sql):
        global __db_con
        __db_con.execute(sql)
        books = list(__db_con.execute(sql))

        tbr = []

        for i in books:
            tba = Book(i[0], i[1], i[2], literal_eval(i[3]), literal_eval(i[4]), i[5], i[6], i[7], i[8])
            tba.print_details()
            tbr.append(tba)

        return tbr


    @staticmethod
    def get_user_account_settings(username):
        global __db_con
        s = list(__db_con.execute(f'SELECT * FROM account_settings WHERE username="{username}"'))[0]
        return UserSettings(s[0], s[1], s[2])

    @staticmethod
    def update_user_account_settings(user_settings: UserSettings):
        global __db_con
        __db_con.execute(f'''UPDATE account_settings 
                             SET theme="{user_settings.theme}", accent_colour="{user_settings.accent_colour}" 
                             WHERE username="{user_settings.username}" ''')

        Database.save_database()
    
    @staticmethod
    def get_book_ratings(ISBN):
        global __db_con
        s = list(__db_con.execute(f'SELECT * FROM books_ratings WHERE ISBN="{ISBN}"'))[0]
        return BookRatings(s[0], literal_eval(s[1]))

    @staticmethod
    def set_book_ratings(book_ratings: BookRatings):
        global __db_con
        __db_con.execute(f'''UPDATE books_ratings 
                             SET ratings="{book_ratings.ratings}"
                             WHERE ISBN="{book_ratings.ISBN}" ''')

        Database.save_database()

    @staticmethod
    def save_database():
        global __db_con
        __db_con.commit()

    @staticmethod
    def print_all_users():
        global __db_con
        print(list(__db_con.execute("SELECT * FROM users")))
    
    @staticmethod
    def print_all_books():
        global __db_con
        print(list(__db_con.execute("SELECT * FROM books")))

    @staticmethod
    def is_new_setup():
        global __db_con
        return len(list(__db_con.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users";'))) == 0

    @staticmethod
    def delete_user(username):
        global __db_con
        __db_con.execute(f'DELETE FROM users WHERE username="{username}"')
        __db_con.execute(f'DELETE FROM account_settings WHERE username="{username}"')  

        Database.save_database()
    
    @staticmethod
    def delete_book(ISBN):
        global __db_con
        __db_con.execute(f'DELETE FROM books WHERE ISBN="{ISBN}"')
        __db_con.execute(f'DELETE FROM books_ratings WHERE ISBN="{ISBN}"')  

        Database.save_database()