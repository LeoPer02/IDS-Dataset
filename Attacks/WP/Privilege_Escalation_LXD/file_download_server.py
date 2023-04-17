import http.server, sys
import socketserver

PORT = int(sys.argv[1])
try:
	handler = http.server.SimpleHTTPRequestHandler

	with socketserver.TCPServer(("", PORT), handler) as httpd:
	    print("Server started at localhost:" + str(PORT))
	    httpd.serve_forever()
except KeyboardInterrupt:
	httpd.server_close()
	sys.exit()
