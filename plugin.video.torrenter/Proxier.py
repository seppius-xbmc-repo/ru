import socket
import thread
import re
import os

class Proxier:
    HOST = '127.0.0.1'
    PORT = 51515
    PATH = ''
    CHUNK_SIZE = 1024
    seekBytes = 0
    buffering = 0

    def server(self, path):
        self.PATH = path
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(600)
        s.bind((self.HOST, self.PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            conn.setblocking(1) 
            data = conn.recv(1024)
            range = re.compile('Range: bytes=(\d+)-(\d*)')
            size = os.path.getsize(self.PATH)    
            byte1, byte2 = 0, None
        
            if range.search(data):
                g = range.search(data).groups()
                if g[0]: byte1 = int(g[0])
                if g[1]: byte2 = int(g[1])
        
            length = size - byte1
            if byte2 is not None:
                length = byte2 - byte1

            thread.start_new_thread(self.streamer, (conn, byte1, byte2, length, size, ))

    def streamer(self, conn, byte1, byte2, length, size):
        send = ''
        if byte1 > 0 or byte2 != None:
            send = send + "HTTP/1.1 206 Partial Content"
            send = send + "\r\n"
            send = send + "Content-Range: %s-%s/%s" % (str(byte1), str(byte1 + length - 1), str(size))
            send = send + "\r\n"
            self.seekBytes = byte1
        else:
            send = send + "HTTP/1.1 200 OK"
            send = send + "\r\n"
        send = send + "Content-Type: video/mp4"
        send = send + "\r\n"
        send = send + "Content-Length: " + str(length)
        send = send + "\r\n"
        send = send + "Accept-Ranges: bytes"
        send = send + "\r\n"
        send = send + "Connection: close"
        send = send + "\r\n"
        send = send + "\r\n"
        conn.send(send)
        fp = open(self.PATH, "rb")
        fp.seek(byte1)
        sent = 0
        while length > sent:
            chunk = fp.read(self.CHUNK_SIZE)
            if chunk:
                self.buffering = 0
                try:
                    sent = sent + conn.send(chunk)
                except socket.error, e:
                    conn.close()
                    break
            else:
                self.buffering = self.buffering + 1
                time.sleep(1)
                if self.buffering > 60:
                    break
        fp.close()
        conn.close()
