import google.generativeai as genai
import json
import sqlite3
from autoshell.scripts.macros import *

class User:
    def __init__(self,username,password,API_KEY):
        self.username = username
        self.API_KEY = API_KEY
        self.password = password
        self.client = None

    def set_client(self):
        genai.configure(api_key=self.API_KEY)

class DB:
    def __init__(self):
        self.connection = sqlite3.connect("UsersDB.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS USERS(
                                username TEXT PRIMARY KEY,
                                password TEXT,
                                API_KEY TEXT
                            )''')
        self.connection.commit()

    def close_db(self):
        self.connection.close()

    def write_users(self,users):
        for user in users:
            self.cursor.execute(''' 
                INSERT INTO USERS (username,password,API_KEY) VALUES (?,?,?)
                ''',(user.username,user.password,user.API_KEY))
        
        self.connection.commit()
    
    def read_users(self):
        self.cursor.execute("SELECT * FROM USERS")
        users = self.cursor.fetchall()

        return users
    
    def write_user(self,user):
        self.cursor.execute("INSERT INTO USERS (username,password,API_KEY) VALUES (?,?,?)",(user.username,user.password,user.API_KEY))
        self.connection.commit()
    
    def update_API_KEY(self,user,API_KEY):
        self.cursor.execute("UPDATE USERS SET API_KEY = ? WHERE username = ? AND password = ?",(API_KEY,user.username,user.password))
        self.connection.commit()

    def authenticate(self,username,password):
        self.cursor.execute("SELECT * FROM USERS WHERE username = ?",(username))
        user = self.cursor.fetchone()
        
        if(user==None):
            return USER_NOT_FOUND
        
        if(user.password==password):
            return SUCCESS
        else:
            return INVALID_PASSWORD