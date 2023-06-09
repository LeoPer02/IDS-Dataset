import http.server, sys
import socketserver

class color:
	PURPLE = '\033[1;35;48m'
	CYAN = '\033[1;36;48m'
	BOLD = '\033[1;37;48m'
	BLUE = '\033[1;34;48m'
	GREEN = '\033[1;32;48m'
	YELLOW = '\033[1;33;48m'
	RED = '\033[1;31;48m'
	BLACK = '\033[1;30;48m'
	UNDERLINE = '\033[4;37;48m'
	END = '\033[1;37;0m'

PORT = int(sys.argv[1])
try:
	handler = http.server.SimpleHTTPRequestHandler

	with socketserver.TCPServer(("", PORT), handler) as httpd:
	    print(color.GREEN + '[*]' + color.END + " Server started at localhost:" + str(PORT))
	    httpd.serve_forever()
except KeyboardInterrupt:
	httpd.server_close()
	sys.exit()
