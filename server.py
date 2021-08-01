import asyncio
from os import walk
from os import path
from os import makedirs
from datetime import datetime

DIRECTORY = "data/"
STORAGE = "storage/"
RESPONSE_FILE = None #DIRECTORY + "youtubePage.html"
FILE_ACCESS_SPEC = None
BUFFER_SIZE = 10000



#search by key word
#parameters: (str, str\pathlike obj)
#output: (nested array)
def find(keyWord, director = DIRECTORY):
   result = []
   for root, dirs, files in walk(director):
       for name in files:
          if keyWord in name:
             result.append(path.join(root, name))
   return result



#iterate through the file
#parameters: (pathlike obj, read length (bits))
#output: (str)
def bite(inp, bite_size = BUFFER_SIZE):
   while True:
      data = inp.read(bite_size)
      if not data:
         break
      yield data



#save loaded data from connected client
#parameters: (asyncio connecton pair, str, str)
#output: (int\Error)
async def load_data(connection,
              save_dir = STORAGE,
              client = "anon"):
   reader = connection[0]
   errors = []
   #------------------------------------------------------------
   directory = save_dir
   if not path.isfile(save_dir):
      directory += client +datetime.now().strftime("%d%m%Y_%H%M_data.txt")
      makedirs(path.dirname(directory), exist_ok=True)
   #------------------------------------------------------------
   try:
      with open(directory, 'w+') as fd:
         print("storage directory", fd.name)
         count = 0
         while True:
            count += 1
            print("received data package", count)
            data = await reader.read(BUFFER_SIZE)
            if (data[-3::] == "END".encode()
            or data is None
            or data == ""
            or not data):
               try:
                  message = data.decode()
                  fd.write(message)
               except Exception as error_0:
                  errors.append(error_0)
               break
            message = data.decode()
            fd.write(message)
         print(f"Received successful from {client!r}")
   except Exception as error:
      return error
   #------------------------------------------------------------
   return 200



#parameters: (asyncio connection pair, str)
#output: (int\Error)
def send_data(connection, file_name=RESPONSE_FILE):
   writer = connection[1]
   # -----------------------------------------
   async def hand_over(directory, wr=writer):
      with open(directory, 'r') as fd:
         print("data directory", fd.name)
         count = 0
         for clod in bite(fd):
            count += 1
            print("clod", count)
            wr.write(clod.encode())
            await wr.drain()
      return 200
   # -----------------------------------------
   if path.isfile(file_name):
      result = hand_over(file_name)
      return result
   # -----------------------------------------
   if path.isfile(DIRECTORY + file_name):
      result = hand_over(DIRECTORY + file_name)
      return result
   # -----------------------------------------
   files = find(file_name, DIRECTORY)
   result = None
   if files.__len__() > 1:
      print("There is a several files:\n",
            files,"\n,I give you first one")
      #print("yes/no?\n")
      #if input() == "no":
      #  return 200
   print("data on stage of upload\n", files[0])
   if path.isfile(files[0]):
      result = hand_over(files[0])
   else:
      print("file upload failed: \n", files[0])
   return result



#ways to request file
#parameters: (str)
#output: (str)
def file_declaration(flag):
   if not flag:
      if not RESPONSE_FILE:
         return 300
      else:
         return DIRECTORY + RESPONSE_FILE
   else:
      if ("__keyboard__" in flag
              or "k" in flag):
         return input()
      return flag



###########################################
#server
#parameters: (asyncio connection pair)
#output: non
async def handle_echo(reader, writer):
   data = await reader.read(BUFFER_SIZE)
   addr = writer.get_extra_info('peername')
   # -----------------------------------------
   message = data.decode()
   if "GET" in message:
      result = send_data(
         (reader, writer), file_declaration(FILE_ACCESS_SPEC))
   if "POST" in message:
      response = 200  # !
      print(f"end code: {response!r}")  # !
      writer.write(str(response).encode())  # !
      await writer.drain()  # !
      result = await load_data(
         (reader, writer))
   # -----------------------------------------
   response = 200#!
   print(f"end code: {response!r}")#!
   writer.write(str(response).encode())#!
   await writer.drain()#!
   print("Close the connection")#!
   writer.close()#!



#main program
async def main():
   server = await asyncio.start_server(
       handle_echo, '127.0.0.1', 8888)
   addr = server.sockets[0].getsockname()
   print(f'Serving on {addr}')

   async with server:
       await server.serve_forever()
##############################################
#start the program
if __name__ == '__main__':
   asyncio.run(main())

