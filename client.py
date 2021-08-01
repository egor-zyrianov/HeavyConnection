import asyncio
from os import walk
from os import path
import errno

BUFFER_SIZE = 500
DIRECTORY = "source_data/"
FILE_DATA = "source_data"



#iterate through the file
#parameters: (pathlike obj, read length (bits))
#output: (str)
def bite(inp):
    while True:
        data = inp.read(BUFFER_SIZE)
        if not data:
            break
        yield data



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



###############################################
#parameters: (asyncio connection pair, str)
#output: (int\Error)
def send_data(connection, file_name=FILE_DATA):
    writer = connection[1]
    #-----------------------------------------
    async def hand_over(directory, wr = writer):
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
        result = hand_over(DIRECTORY +file_name)
        return result
    # -----------------------------------------
    files = find(file_name, DIRECTORY)
    result = None
    for file in files:
        print("data on stage of upload\n", file)
        if path.isfile(file):
            result = hand_over(file)
        else:
            print("file upload failed: \n", file)
    return result



#client
#parameters: non
#output: non
async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    # ---------------------------------------------
    writer.write("POST".encode())
    await writer.drain()
    response = await reader.read(BUFFER_SIZE)
    print(f'Received: {response.decode()!r}')
    if "200".encode() in response:
        result = await send_data((reader, writer))
        writer.write("END".encode())
    # ---------------------------------------------
    response = await reader.read(BUFFER_SIZE)
    print(f'Received: {response.decode()!r}')
    print('Close the connection')
    writer.close()
    await writer.wait_closed()
###############################################
#start the program
if __name__ == '__main__':
   asyncio.run(tcp_echo_client())