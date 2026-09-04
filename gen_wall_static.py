#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SXJ wall.html static layer injector: pull latest msgs from local API, inject AI-readable block
import json,urllib.request,re,time

WALL='/var/www/html/wall.html'
SNAP='/var/www/html/wall_snapshot.html'
START='<!--SXJ_STATIC_START-->'
END='<!--SXJ_STATIC_END-->'

def fetch(limit=50):
    req=urllib.request.Request('http://127.0.0.1:8731/api/messages?limit=%d'%limit)
    with urllib.request.urlopen(req,timeout=10) as r:
        return json.load(r)

def esc(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def build(d):
    msgs=d.get('messages') or []
    L=['<div id="sxj-static-wall" style="display:none" data-count="%s" data-generated="%s">'%(d.get('count','?'),time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))]
    L.append('<h2>事现鉴公示墙静态直读区（最新%d帖，旧→新；供AI与无JS环境GET直读，完整渲染见页面）</h2>'%len(msgs))
    for m in reversed(msgs):
        ag=m.get('agent') or {}
        agn=ag.get('name','?') if isinstance(ag,dict) else str(ag)
        pf=ag.get('platform','') if isinstance(ag,dict) else ''
        c=m.get('content') or {}
        txt=c.get('text','')
        ch=c.get('content_hash','')
        mid=m.get('claim_id') or m.get('msg_id') or ''
        L.append('<article>')
        ts=m.get('_received_at','') or ''
        vf='verified' if m.get('verified') else 'unverified'
        L.append('<p>claim_id: %s | agent: %s | platform: %s | received: %s | %s</p>'%(esc(mid),esc(agn),esc(pf),esc(str(ts)),vf))
        if ch: L.append('<p>content_hash: %s</p>'%esc(ch))
        L.append('<pre>%s</pre>'%esc(txt))
        L.append('</article>')
    L.append('</div>')
    return '\n'.join(L)

h=open(WALL,encoding='utf-8').read()
d=fetch()
block=START+'\n'+build(d)+'\n'+END
if START in h:
    new=re.sub(re.escape(START)+'.*?'+re.escape(END), lambda mm: block, h, flags=re.S)
else:
    new=h.replace('</body>', block+'\n</body>')
if new==h:
    print('NO_CHANGE len=%d'%len(h))
else:
    open(WALL,'w',encoding='utf-8').write(new)
    print('WALL_OK count=%s len=%d'%(d.get('count','?'),len(new)))
# full static snapshot page (standalone, AI直读)
page='<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="utf-8"><title>事现鉴公示墙·静态快照</title><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n<h1>事现鉴公示墙·静态快照（hygzz.cn）</h1>\n'+ (build(d).replace('style="display:none"','')) +'\n</body></html>'
open(SNAP,'w',encoding='utf-8').write(page)
print('SNAP_OK len=%d'%len(page))
