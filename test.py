import asyncio
import os

async def tcp_echo_client(director = "source_data"):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    def bite(inp):
        while True:
            data = inp.read(1000)
            if not data:
                break
            yield data

    if os.path.isfile(director):
        with open(director, 'r') as fd:
            for clod in bite(fd):
                writer.write(clod.encode())
                await writer.drain()


    else:
        tree = os.walk(os.getcwd())
        files = []

        for dirs in tree: #any file with given name will be found
            for files_name in dirs[2]:
                if director in files_name:
                    files.append(dirs[0]+'/'+files_name)

        for file in files:  #all of them will be send part by part
            with open(file, 'r') as fd:
                for clod in bite(fd):
                    writer.write(clod.encode())
                    await writer.drain()
        writer.write("end".encode())
        await writer.drain()

###########responce part##############
    response = await reader.read(100)
    print(f'Received: {response.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

#---------------------------------------------#

asyncio.run(tcp_echo_client())
