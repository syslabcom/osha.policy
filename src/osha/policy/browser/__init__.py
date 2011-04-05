
# browser package
from Products.Five import BrowserView
import socket

class HostnameView(BrowserView):
    """Utility view"""

    def __call__(self, **args):
        return socket.gethostname()
