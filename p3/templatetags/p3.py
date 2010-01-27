# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import mimetypes
import os
import os.path
import re
import random
import sys
import urllib2
from collections import defaultdict

from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe
import twitter

from p3 import models
from pages import models as PagesModels
from conference import models as ConferenceModels

mimetypes.init()

register = template.Library()

@register.inclusion_tag('p3/box_pycon_italia.html')
def box_pycon_italia():
    return {}

@register.inclusion_tag('p3/box_newsletter.html')
def box_newsletter():
    return {}

@register.inclusion_tag('p3/box_download.html', takes_context = True)
def box_download(context, fname, label=None):
    if '..' in fname:
        raise template.TemplateSyntaxError("file path cannot contains ..")
    if fname.startswith('/'):
        raise template.TemplateSyntaxError("file path cannot starts with /")
    if label is None:
        label = os.path.basename(fname)
    try:
        fpath = os.path.join(settings.STUFF_DIR, fname)
        stat = os.stat(fpath)
    except (AttributeError, OSError), e:
        fsize = ftype = None
    else:
        fsize = stat.st_size
        ftype = mimetypes.guess_type(fpath)[0]
        
    return {
        'url': context['STUFF_URL'] + fname,
        'label': label,
        'fsize': fsize,
        'ftype': ftype,
    }

@register.inclusion_tag('p3/box_didyouknow.html', takes_context = True)
def box_didyouknow(context):
    try:
        d = ConferenceModels.DidYouKnow.objects.order_by('?')[0]
    except IndexError:
        d = None
    return {
        'd': d,
        'LANGUAGE_CODE': context.get('LANGUAGE_CODE'),
    }

@register.inclusion_tag('p3/box_googlemaps.html', takes_context = True)
def box_googlemaps(context, what='', zoom=13):
    what = ','.join([ "'%s'" % w for w in what.split(',') ])
    print what
    return {
        'rand': random.randint(0, sys.maxint - 1),
        'what': what,
        'zoom': zoom
    }

@register.inclusion_tag('p3/box_speaker_talks.html', takes_context = True)
def box_speaker_talks(context, speaker):
    conf = defaultdict(list)
    for t in speaker.get_all_talks():
        conf[t.conference].append(t)

    talks = []
    for c in reversed(sorted(conf.keys())):
        talks.append((c, conf[c]))

    return { 'talks': talks }

@register.inclusion_tag('p3/box_latest_tweets.html', takes_context=True)
def box_latest_tweets(context):
    request = context['request']
    page = context['current_page']
    return {}

# I tweet venogno scaricati ogni 5 minuti, a volte però twitter non risponde o
# solleva un errore, in questo caso mostriamo gli ultimi tweet validi che
# abbiamo.
_LastGoodTweets = []

@register.tag
def latest_tweets(parser, token):
    """
    {% latest_tweets [ n_tweets ] as var %}
    inserisce in var la lista degli ultimi tweet (opzionalmente è possibile
    selezionare il numero di tweet da visualizzare).
    """
    def getLatestTweets(n_tweets):
        global _LastGoodTweets
        key = 'bs_latest_tweets'
        tweets = cache.get(key)
        if not tweets:
            api = twitter.Api()
            # il modulo twitter fornisce un meccanismo di caching, ma
            # preferisco disabilitarlo per due motivi:
            #
            # 1. voglio usare la cache di django, in questo modo modificando i
            # settings modifico anche la cache per twitter
            # 2. di default, ma è modificabile con le api pubbliche, la cache
            # del modulo twitter è file-based e sbaglia a decidere la directory
            # in cui salvare i file; finisce per scrivere in
            # /tmp/python.cache_nobody/... che non è detto sia scrivibile
            # (sopratutto se la directory è stata creata da un altro processo
            # che gira con un utente diverso).
            api.SetCache(None)
            try:
                tweets = api.GetUserTimeline(settings.P3_TWITTER_USER, n_tweets)
            except (ValueError, urllib2.HTTPError):
                # ValueError: a volte twitter.com non risponde correttamente, e
                # twitter (il modulo) non verifica. Di conseguenza viene
                # sollevato un ValueError quando twitter (il modulo) tenta
                # parsare un None come se fosse una stringa json.

                # HTTPError: a volte twitter.com non risponde proprio :) (in
                # realtà risponde con un 503)

                # Spesso questi errori durano molto poco, ma per essere gentile
                # con twitter cacho un risultato nullo per poco tempo.
                tweets = None
            except:
                # vista la stabilità di twitter meglio cachare tutto per
                # evitare errori sul nostro sito
                tweets = None
            if not tweets:
                tweets = _LastGoodTweets
            else:
                _LastGoodTweets = tweets
                cache.set(key, tweets, 60 * 5)
        return [{
                "text": tweet.GetText(),
                "timestamp": tweet.GetCreatedAtInSeconds(),
                "followers_count": tweet.user.GetFollowersCount(),
                "id": tweet.GetId(),
            } for tweet in tweets]

    contents = token.split_contents()
    tag_name = contents[0]
    if contents[-2] != 'as':
        raise template.TemplateSyntaxError("%r tag had invalid arguments" %tag_name)
    var_name = contents[-1]
    if len(contents) > 3:
        n_tweets = contents[1]
    else:
        n_tweets = 3

    class TweetNode(template.Node):
        def __init__(self, n_tweets, var_name):
            self.var_name = var_name
            self.n_tweets = n_tweets
        def render(self, context):
            context[self.var_name] = getLatestTweets(self.n_tweets)
            return ''
    return TweetNode(n_tweets, var_name)    

@register.filter
def render_time(tweet, args=None):
    time = tweet["timestamp"]
    time = datetime.datetime.fromtimestamp(time)
    return time.strftime("%d-%m-%y @ %H:%M") 

@register.filter
def convert_links(tweet, args=None):
    text = tweet["text"]
    text = re.sub(r'(https?://[^\s]*)', r'<a href="\1">\1</a>', text)
    text = re.sub(r'@([^\s]*)', r'@<a href="http://twitter.com/\1">\1</a>', text)
    text = re.sub(r'([^&])#([^\s]*)', r'\1<a href="http://twitter.com/search?q=%23\2">#\2</a>', text)
    return mark_safe(text)
