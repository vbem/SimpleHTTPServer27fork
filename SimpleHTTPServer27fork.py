#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Modified SimpleHTTPServer with MultiThread/MultiProcess and IP bind support.

Original:   https://docs.python.org/2.7/library/simplehttpserver.html
Modified:   https://github.com/vbem/SimpleHTTPServer27fork
"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os, sys, pwd, posixpath, BaseHTTPServer, urllib, cgi, shutil, mimetypes, socket, SocketServer, BaseHTTPServer
from cStringIO import StringIO

USERNAME = pwd.getpwuid(os.getuid()).pw_name
HOSTNAME = socket.gethostname()
PORT_DFT = 8000

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = "SimpleHTTP/0.6"

    def do_GET(self):
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        try:
            list = ['..'] + os.listdir(path) # 
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>%s %s</title>\n<body>" % (HOSTNAME, displaypath))
        f.write("%s@%s:<strong>%s</strong>\n" % (USERNAME, HOSTNAME, path.rstrip('/')+'/'))
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n<pre>%s</pre>\n</body>\n</html>\n" % __doc__)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({'': 'text/plain'})

class ProcessedHTTPServer(SocketServer.ForkingMixIn, BaseHTTPServer.HTTPServer):
    r"""Handle requests in multi process."""

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    r"""Handle requests in a separate thread."""
 
SERVER_DICT = {
    'thread'    : ThreadedHTTPServer,
    'process'   : ProcessedHTTPServer,
}
SERVER_DFT = 'thread'
 
def run(sCwd=None, sServer=SERVER_DFT, nPort=PORT_DFT, *lArgs, **dArgs):
    r"""
    """
    sys.stderr.write('start with %r\n' % sys._getframe().f_locals)
    if sCwd is not None:
        os.chdir(sCwd)
    cServer = SERVER_DICT[sServer]
    oHttpd = cServer(("", nPort), SimpleHTTPRequestHandler)
    sys.stderr.write('http://%s:%s/\n' % (HOSTNAME, nPort))
    oHttpd.serve_forever()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main

def _main():
    r"""Main.
    """
    import argparse

    oParser = argparse.ArgumentParser(
        description = __doc__,
        formatter_class = argparse.RawTextHelpFormatter,
        epilog = 'NOTE: stdin for input, stdout for result, stderr for logging',
    )
    oParser.add_argument('--pydoc', action='store_true',
        help = "show this module's pydoc",
    )
    
    oGroupR = oParser.add_argument_group(title='run arguments', description='')
    oGroupR.add_argument('--port', action='store', type=int, default=PORT_DFT,
        help = 'specify server port (default: %(default)r)',
    )
    oGroupR.add_argument('--type', action='store', default=SERVER_DFT, choices=SERVER_DICT.keys(),
        help = 'specify server type (default: %(default)r)',
    )
    oGroupR.add_argument('--root', action='store', default=os.getcwd(),
        help = 'specify root directory (default: cwd %(default)r)',
    )
    oGroupR.add_argument('--run', action='store_true',
        help = '\n'.join((
            'run http server foreground',
    )))
    
    oArgs = oParser.parse_args()
    
    if oArgs.pydoc:
        help(os.path.splitext(os.path.basename(__file__))[0])
    elif oArgs.run:
        return run(sCwd=oArgs.root, sServer=oArgs.type, nPort=oArgs.port)
    else:
        oParser.print_help()
        return 1
        
    return 0
    
if __name__ == "__main__":
    exit(_main())
