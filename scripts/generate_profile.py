#!/usr/bin/env python3
"""Build clean GitHub README SVGs from real ASCII text, not a raster screenshot.

Use --offline for first-time preview; the GitHub workflow fetches public stats.
Only the SVGs are published; the source photograph is NOT needed in GitHub.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from html import escape
from datetime import datetime, timezone
import json, argparse, os, sys
ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com'
USERNAME='xn4k'
FAMILY="'DejaVu Sans Mono','Liberation Mono',Consolas,monospace"

def fetch(url, token):
    headers={'User-Agent':'xn4k-ascii-profile','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    if token:headers['Authorization']='Bearer '+token
    with urlopen(Request(url,headers=headers),timeout=20) as resp: return json.load(resp)

def live(token):
    u=fetch(f'{API}/users/{USERNAME}',token)
    total=0; page=1
    while True:
        r=fetch(f'{API}/users/{USERNAME}/repos?type=owner&per_page=100&page={page}',token)
        if not isinstance(r,list):raise RuntimeError('Cannot retrieve public repositories')
        total+=sum(int(p.get('stargazers_count',0)) for p in r if not p.get('fork'))
        if len(r)<100:break
        page+=1
        if page>30:raise RuntimeError('Excessive pagination')
    return {'repos':str(u['public_repos']),'stars':str(total),'followers':str(u['followers']),'stamp':datetime.now(timezone.utc).strftime('%d %b %Y UTC')}

def label(x,y,s,*,size=17,color='ink',weight=400,spacing=None):
    extra=(f' letter-spacing="{spacing}"' if spacing else '')
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}"{extra}>{escape(str(s))}</text>'

def svg_theme(theme,art,stats):
    dark=theme=='dark'
    p = {
      'bg':'#080f1b' if dark else '#edf2f8',
      'panel':'#0e1b2b' if dark else '#ffffff',
      'card':'#132338' if dark else '#f4f8fc',
      'border':'#2d4862' if dark else '#bccbdc',
      'primary':'#f4f8ff' if dark else '#17273a',
      'muted':'#98afc6' if dark else '#5d7286',
      'accent':'#6fdcff' if dark else '#006eab',
      'secondary':'#c5acff' if dark else '#7549a5',
      'art':'#e6edf3' if dark else '#f9fbfd',
      'artborder':'#a6b9c9' if dark else '#c8d6e2',
    }
    a = [
      '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="760" viewBox="0 0 1440 760" role="img" aria-labelledby="title desc">',
      f'<title id="title">xn4k profile - {theme} mode - dot-matrix portrait</title>',
      '<desc id="desc">ASCII typography portrait based on an actual close-up photo, beside Mikhail Zhivoderov\'s developer information and public GitHub metrics.</desc>',
      f'<rect width="1440" height="760" fill="{p["bg"]}"/>',
      f'<rect x="18" y="18" width="1404" height="724" rx="24" fill="{p["panel"]}" stroke="{p["border"]}" stroke-width="2"/>',
      f'<circle cx="48" cy="56" r="8" fill="#fa6a6a"/><circle cx="75" cy="56" r="8" fill="#efc65a"/><circle cx="102" cy="56" r="8" fill="#54ca97"/>',
      f'<g font-family="{FAMILY}">',
      label(140,64,'xn4k / terminal / portrait.sh',color=p['muted'],size=18,weight=600),
      label(1172,64,'● TEXT / SVG',color=p['accent'],size=16,weight=600),
      f'<line x1="19" y1="87" x2="1420" y2="87" stroke="{p["border"]}"/>',
      f'<rect x="44" y="106" width="604" height="592" rx="18" fill="{p["art"]}" stroke="{p["artborder"]}"/>',
      f'<clipPath id="portrait-cut"><rect x="50" y="112" width="592" height="577" rx="15"/></clipPath>',
      f'<g clip-path="url(#portrait-cut)">',
    ]
    # Unicode Braille is REAL text. Each character is a 2x4-dot tile.
    # Its higher effective pixel density preserves the actual face much better
    # than a low-resolution ramp of random symbols. No image is embedded.
    for y,line in enumerate(art):
        a.append(f'<text xml:space="preserve" x="66" y="{125+y*10.52:.2f}" font-size="15.1" font-family="DejaVu Sans, Segoe UI Symbol, Apple Symbols, sans-serif" fill="#172534">{escape(line)}</text>')
    a.extend([
      '</g>',
      f'<rect x="57" y="671" width="183" height="18" rx="8" fill="{p["art"]}" opacity="0.92"/>',
      label(69,684,'UNICODE PORTRAIT / 01',size=12,color='#566b7c',weight=700),
      f'<rect x="673" y="106" width="722" height="592" rx="18" fill="{p["card"]}" stroke="{p["border"]}"/>',
      label(711,157,'mikhail@xn4k',size=37,color=p['primary'],weight=700),
      label(1112,153,'~ $ whoami',size=19,color=p['accent']),
      f'<line x1="709" y1="178" x2="1357" y2="178" stroke="{p["border"]}"/>',
      label(711,210,'[ 01 ] IDENTITY',size=15,color=p['secondary'],weight=700,spacing='1.6'),
      label(712,243,'ROLE',size=17,color=p['accent'],weight=700),
      label(931,243,'Software Developer / Security',size=19,color=p['primary']),
      label(712,277,'BASE',size=17,color=p['accent'],weight=700),
      label(931,277,'Cologne, Germany',size=19,color=p['primary']),
      label(712,311,'FOCUS',size=17,color=p['accent'],weight=700),
      label(931,311,'Web · Recon · Automation',size=19,color=p['primary']),
      f'<line x1="709" y1="333" x2="1357" y2="333" stroke="{p["border"]}"/>',
      label(711,361,'[ 02 ] STACK',size=15,color=p['secondary'],weight=700,spacing='1.6'),
      label(712,395,'CODE',size=17,color=p['accent'],weight=700),
      label(931,395,'Go · Python · TypeScript',size=19,color=p['primary']),
      label(712,427,'FRONTEND',size=17,color=p['accent'],weight=700),
      label(931,427,'Vue 3 · JS · HTML · CSS',size=19,color=p['primary']),
      label(712,459,'SYSTEMS',size=17,color=p['accent'],weight=700),
      label(931,459,'Linux · Docker · PostgreSQL',size=19,color=p['primary']),
      f'<line x1="709" y1="482" x2="1357" y2="482" stroke="{p["border"]}"/>',
      label(711,508,'[ 03 ] SHIPPING',size=15,color=p['secondary'],weight=700,spacing='1.6'),
      label(712,541,'HERMES',size=18,color=p['accent'],weight=700),
      label(931,541,'Self-hosted command center',size=19,color=p['primary']),
      label(712,571,'ISOBAR',size=18,color=p['accent'],weight=700),
      label(931,571,'Forecast model comparisons',size=19,color=p['primary']),
      label(712,601,'DEVPAGE',size=18,color=p['accent'],weight=700),
      label(931,601,'Portfolio + security lab',size=19,color=p['primary']),
      f'<line x1="709" y1="621" x2="1357" y2="621" stroke="{p["border"]}"/>',
      label(711,650,f'PUBLIC REPOS  {stats["repos"]}    ·    STARS  {stats["stars"]}    ·    FOLLOWERS  {stats["followers"]}',size=16,color=p['primary'],weight=500),
      label(712,678,'SYNC: '+stats['stamp'],size=13,color=p['muted']),
      label(56,723,'// portrait built from Unicode dots  ·  no embedded raster',size=15,color=p['muted']),
      label(1201,723,'github.com/xn4k',size=16,color=p['accent'],weight=600),
      '</g></svg>'
    ])
    return '\n'.join(a)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    art=(ROOT/'assets/portrait-braille.txt').read_text(encoding='utf8').splitlines()
    if args.offline:stats={'repos':'—','stars':'—','followers':'—','stamp':'Run GitHub Action for live numbers'}
    else:
        try: stats=live(os.getenv('GITHUB_TOKEN'))
        except Exception as e:
            print('Could not update SVGs; keeping existing files: '+str(e),file=sys.stderr)
            sys.exit(1)
    for theme in ('dark','light'):
        target=ROOT/'assets'/f'{theme}_mode.svg'
        target.write_text(svg_theme(theme,art,stats),encoding='utf8')
        print('Wrote',target)
if __name__=='__main__':main()
