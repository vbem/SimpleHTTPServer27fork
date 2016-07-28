# SimpleHTTPServer27fork
A fork of SimpleHTTPServer.py in Python 2.7 with new features

Original [SimpleHTTPServer][1] from python standard library does NOT "*handle serving multiple files efficiently and reliably*". For instance, if you are downloading one file from it, another HTTP access to it must be hovering since `SimpleHTTPServer.py` is **a simple singal-thread HTTP server** which could **only support one connecting simultaneously**.

Fortunately, note that `SimpleHTTPServer.py` use [BaseHTTPServer.HTTPServer][2] as handler, which can be wrapped by [SocketServer.ForkingMixIn][3] and [SocketServer.ThreadingMixIn][4] also from python standard library to support multi-process and multi-thread mode, which could highly enhance simple HTTP server's "*efficience and reliability*". 

According to this idea, a **SimpleHTTPServer with multi-thread/multi-process support** modified from original one is given as follows:

    $ python2.7 ModifiedSimpleHTTPServer.py
    usage: ModifiedSimpleHTTPServer.py [-h] [--pydoc] [--port PORT]
                                       [--type {process,thread}] [--root ROOT]
                                       [--run]
    
    Modified SimpleHTTPServer with MultiThread/MultiProcess and IP bind support.
    
    Original:   https://docs.python.org/2.7/library/simplehttpserver.html
    Modified:   https://github.com/vbem/SimpleHTTPServer27fork
    
    optional arguments:
      -h, --help            show this help message and exit
      --pydoc               show this module's pydoc
    
    run arguments:
    
      --port PORT           specify server port (default: 8000)
      --type {process,thread}
                            specify server type (default: 'thread')
      --root ROOT           specify root directory (default: cwd '/home/vbem')
      --run                 run http server foreground
    
    NOTE: stdin for input, stdout for result, stderr for logging


For example, `ModifiedSimpleHTTPServer.py --run --root /var/log --type process` will run a multi-process HTTP static files server with '/var/log' as its root directory.

Last but not least, this `ModifiedSimpleHTTPServer.py` may be a "killer app" by hand for temporary use, however, Nginx is advised for long term use.

  [1]: https://docs.python.org/2.7/library/simplehttpserver.html
  [2]: https://docs.python.org/2.7/library/basehttpserver.html#BaseHTTPServer.HTTPServer
  [3]: https://docs.python.org/2.7/library/socketserver.html#SocketServer.ForkingMixIn
  [4]: https://docs.python.org/2.7/library/socketserver.html#SocketServer.ThreadingMixIn
