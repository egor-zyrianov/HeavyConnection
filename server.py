import asyncio
#HOST = ('127.0.0.1', 8888)
FILE_FLAG = 'w+' #write and read (could be 'a' - add)

#data receiver
async def handle_echo(reader, writer, package_size = 10000):
 #initial package (thinking about rework)
   data = await reader.read(package_size)
   message = data.decode()
   addr = writer.get_extra_info('peername')
 #with creating file, data receiving till the end 
   directory = "data/source_"+addr[0]+"_data.txt"
   with open(directory, FILE_FLAG) as f:
      f.write(message)
      while True:
         data = await reader.read(package_size)
         print(data)
         if data[-3::] == "end".encode():
            message = data.decode()
            f.write(message)
            break
         message = data.decode()
         f.write(message)
      print(f"Received successful from {addr!r}")
 #sending code of the result
   response = {"code": 200}
   print(f"response: {response!r}")
   writer.write(str(response).encode())
   await writer.drain()

   writer.close()
   print("Connection closed")

#running the server
async def main():
   server = await asyncio.start_server(
       handle_echo, '127.0.0.1', 8888)

   addr = server.sockets[0].getsockname()
   print(f'Serving on {addr}')

   async with server:
       await server.serve_forever()
         
#running the machine
if __name__ == '__main__':
   asyncio.run(main())
