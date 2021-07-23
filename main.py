import asyncio

async def handle_echo(reader, writer):
   data = await reader.read(10000)
   message = data.decode()
   addr = writer.get_extra_info('peername')

   directory = "data/source_"+addr[0]+"_data.txt"

   with open(directory, 'w+') as f:
      f.write(message)
      while True:
         data = await reader.read(10000)
         print(data)
         if data[-3::] == "end".encode():
            message = data.decode()
            f.write(message)
            break
         message = data.decode()
         f.write(message)
      print(f"Received successful from {addr!r}")

   response = {"code": 200}
   print(f"response: {response!r}")
   writer.write(str(response).encode())
   await writer.drain()

   print("Close the connection")
   writer.close()

async def main():
   server = await asyncio.start_server(
       handle_echo, '127.0.0.1', 8888)

   addr = server.sockets[0].getsockname()
   print(f'Serving on {addr}')

   async with server:
       await server.serve_forever()

if __name__ == '__main__':
   asyncio.run(main())
