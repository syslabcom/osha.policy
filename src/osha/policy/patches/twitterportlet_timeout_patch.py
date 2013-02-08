from fourdigits.portlet.twitter.fourdigitsportlettwitter import Renderer
import socket


REDUCED_TIMEOUT = 5

def _getuserinfo(self):
    """Get twitter user info"""
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(REDUCED_TIMEOUT)
    userinfo = self.twapi.GetUser(self.data.username)
    socket.setdefaulttimeout(original_timeout)
    return userinfo

def gettweetsofuser(self, username, userpictures, includerts):
    """Return the tweets of a certain user"""
    original_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(REDUCED_TIMEOUT)
        tweets = self.twapi.GetUserTimeline(username,
                                            include_rts=includerts,
                                            include_entities=True)
    except:
        tweets = []
    finally:
         socket.setdefaulttimeout(original_timeout)
    return tweets

def gettweetsbysearch(self, query_dict):
    """Return tweets based on a search query"""
    original_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(REDUCED_TIMEOUT)
        tweets = self.twapi.GetSearch(**query_dict)
    except:
        tweets = []
    finally:
         socket.setdefaulttimeout(original_timeout)
    return tweets


Renderer._getuserinfo = _getuserinfo
Renderer.gettweetsofuser = gettweetsofuser
Renderer.gettweetsbysearch = gettweetsbysearch
