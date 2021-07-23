import asyncio
import os
#echo machine
async def tcp_echo_client(director = "source_data", package_size = 1000):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
#make file iterable
    def bite(inp):
        while True:
            data = inp.read(package_size)
            if not data:
                break
            yield data
#case of direct file accessing
    if os.path.isfile(director):
        with open(director, 'r') as fd:
            for clod in bite(fd):
                writer.write(clod.encode())
                await writer.drain()
#case of search with file name
    else:
        tree = os.walk(os.getcwd())
        files = []
    #explore directory space
        for dirs in tree:   #any file with given name will be found
            for files_name in dirs[2]:
                if director in files_name:
                    files.append(dirs[0]+'/'+files_name)
    #repeatedly send a package_size data until it's come to an end
        for file in files:  #all of them will be send part by part
            with open(file, 'r') as fd:
                for clod in bite(fd):
                    writer.write(clod.encode())
                    await writer.drain()
        writer.write("end".encode())    #end code
        await writer.drain()

#responce part
    response = await reader.read(100)
    print(f'Received: {response.decode()!r}')
    writer.close()
    await writer.wait_closed()
    print('Connection closed')

#---------------------------------------------#
#running that machine
asyncio.run(tcp_echo_client())
