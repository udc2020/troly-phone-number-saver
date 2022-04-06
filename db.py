import sqlite3

def connectDB():
   try:
      connect = sqlite3.connect('./numbers')
      cursor  = connect.cursor()
      print("data base connect")
      
      return {
         connect,
         cursor
      }
   except sqlite3.Error as err:
      print(f"Error Data base #{err}")
      
  
   return 



conn, cursor = connectDB()
