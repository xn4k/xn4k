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


def get_commit_count(token):
    """Commits in GitHub's public contribution collection (last 12 months)."""
    if not token: return 'n/a'
    try:
        q={'query':'query($login:String!){user(login:$login){contributionsCollection{totalCommitContributions}}}',
           'variables':{'login':USERNAME}}
        headers={'Authorization':'Bearer '+token,'User-Agent':'xn4k-ascii-profile',
                 'Content-Type':'application/json'}
        with urlopen(Request('https://api.github.com/graphql',data=json.dumps(q).encode(),
                             headers=headers),timeout=25) as resp:
            return str(json.load(resp)['data']['user']['contributionsCollection']['totalCommitContributions'])
    except Exception as ex:
        print('GitHub commit metric unavailable:',ex,file=sys.stderr)
        return 'n/a'

def get_loc(repos):
    """Count tracked source lines from public, owned, non-fork default branches.
    Snapshot only: excludes dependency directories, generated files and binaries.
    An incomplete scan is reported as n/a instead of a misleading total.
    """
    import tempfile, subprocess
    code_ext={'.py','.go','.js','.jsx','.ts','.tsx','.vue','.html','.css','.scss',
              '.sql','.sh','.bash','.java','.c','.cc','.cpp','.h','.hpp',
              '.rs','.rb','.php','.swift','.kt','.lua','.ps1','.svelte'}
    excluded={'node_modules','vendor','vendors','dist','build','coverage','.next',
              '.nuxt','.git','__pycache__','generated','.venv','venv',
              'site-packages','third_party','third-party','target','minified'}
    count=0; errors=[]; checked=0
    with tempfile.TemporaryDirectory(prefix='xn4k-loc-') as tmp:
        for r in repos:
            if r.get('fork') or r.get('archived') or r.get('disabled'): continue
            if r.get('size',0)>150000:
                errors.append(r['name']+' oversized'); continue
            dest=Path(tmp)/('r'+str(checked)); checked+=1
            try:
                subprocess.run(['git','clone','--quiet','--depth=1','--single-branch',
                                r['clone_url'],str(dest)],check=True,timeout=60,
                               stderr=subprocess.PIPE)
                paths=subprocess.check_output(['git','ls-files','-z'],
                                              cwd=dest,timeout=15).decode('utf8','replace').split('\0')
                for relative in paths:
                    if not relative: continue
                    f=Path(relative)
                    if f.suffix.lower() not in code_ext or any(x.lower() in excluded for x in f.parts[:-1]): continue
                    if f.name.endswith(('.min.js','.min.css','.lock')): continue
                    path=dest/f
                    if not path.is_file() or path.is_symlink() or path.stat().st_size>1048576: continue
                    raw=path.read_bytes()
                    if b'\0' in raw: continue
                    count+=raw.count(b'\n')+(1 if raw and not raw.endswith(b'\n') else 0)
            except Exception as ex:
                errors.append(r['name']+': '+str(ex)[:60])
    if errors:
        print('LOC scan incomplete:',errors,file=sys.stderr)
        return 'n/a'
    return format(count,',')

def live(token):
    u=fetch(f'{API}/users/{USERNAME}',token)
    repos=[]
    for page in range(1,31):
        batch=fetch(f'{API}/users/{USERNAME}/repos?type=owner&per_page=100&page={page}',token)
        if not isinstance(batch,list): raise RuntimeError('Cannot retrieve repositories')
        repos+=batch
        if len(batch)<100:break
    return {'repos':str(u['public_repos']),
            'stars':str(sum(int(r.get('stargazers_count',0)) for r in repos if not r.get('fork'))),
            'followers':str(u['followers']),
            'commits':get_commit_count(token),
            'loc':get_loc(repos),
            'since':u['created_at'][:4],
            'stamp':datetime.now(timezone.utc).strftime('%d %b %Y · %H:%M UTC')}


def label(x,y,s,*,size=17,color='ink',weight=400,spacing=None):
    extra=(f' letter-spacing="{spacing}"' if spacing else '')
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}"{extra}>{escape(str(s))}</text>'


def svg_theme(theme,art,stats):
    dark=theme=='dark'
    p={
      'bg':'#080d16' if dark else '#edf2f8',
      'panel':'#0d1623' if dark else '#ffffff',
      'card':'#111e30' if dark else '#f4f8fc',
      'border':'#2b4058' if dark else '#c0ccda',
      'primary':'#ecf4fe' if dark else '#14263a',
      'muted':'#91a7bf' if dark else '#61758b',
      'accent':'#81dcff' if dark else '#006eac',
      'secondary':'#b8a3ff' if dark else '#7051b6',
      'yellow':'#f7c56f' if dark else '#93600a',
      'art':'#eef2f6' if dark else '#f9fbfe',
    }
    a=[
      '<svg xmlns="http://www.w3.org/2000/svg" width="1560" height="1040" viewBox="0 0 1560 1040" role="img" aria-labelledby="title desc">',
      f'<title id="title">xn4k profile - {theme} terminal</title>',
      '<desc id="desc">Unicode text portrait, workstation, languages, hobbies, contacts, and real public GitHub metrics.</desc>',
      f'<rect width="1560" height="1040" fill="{p["bg"]}"/>',
      f'<rect x="16" y="16" width="1528" height="1008" rx="24" fill="{p["panel"]}" stroke="{p["border"]}" stroke-width="2"/>',
      '<circle cx="47" cy="53" r="7" fill="#fa706c"/><circle cx="72" cy="53" r="7" fill="#f0c368"/><circle cx="97" cy="53" r="7" fill="#52c794"/>',
      f'<g font-family="{FAMILY}">',
      label(128,60,'xn4k ~ fastfetch --profile',color=p['muted'],size=21,weight=600),
      label(1286,60,'● LIVE / SVG',color=p['accent'],size=18,weight=700),
      f'<line x1="16" y1="83" x2="1544" y2="83" stroke="{p["border"]}"/>',
      f'<rect x="44" y="111" width="597" height="678" rx="16" fill="{p["art"]}" stroke="{p["border"]}"/>',
      '<clipPath id="portrait-cut"><rect x="50" y="117" width="585" height="665" rx="11"/></clipPath>',
      '<g clip-path="url(#portrait-cut)">'
    ]
    for y,line in enumerate(art):
        a.append(f'<text xml:space="preserve" x="64" y="{155+y*11.05:.2f}" font-size="15.1" font-family="DejaVu Sans, Segoe UI Symbol, Apple Symbols, sans-serif" fill="#1a2c3f">{escape(line)}</text>')
    a+=['</g>',
      f'<rect x="44" y="807" width="597" height="192" rx="16" fill="{p["card"]}" stroke="{p["border"]}"/>',
      label(72,846,'$ cat portrait.txt',color=p['accent'],size=19,weight=700),
      label(72,885,'UNICODE DOT-MATRIX · REAL TEXT',color=p['primary'],size=16),
      label(72,920,'No embedded raster / source in repo',color=p['muted'],size=16),
      label(72,971,'github.com/xn4k',color=p['secondary'],size=20,weight=700),
      f'<rect x="662" y="111" width="856" height="888" rx="16" fill="{p["card"]}" stroke="{p["border"]}"/>',
      label(688,163,'mikhail@xn4k',color=p['primary'],size=38,weight=700),
      label(1298,161,'STATUS: ONLINE',color=p['accent'],size=16,weight=700),
      f'<line x1="688" y1="182" x2="1493" y2="182" stroke="{p["border"]}"/>'
    ]
    def section(y,title):
        a.append(label(691,y,'— '+title,color=p['secondary'],size=16,weight=700))
    def entry(y,name,value):
        a.append(label(691,y,name,color=p['yellow'],size=16,weight=600))
        a.append(f'<path d="M940 {y-5} H971" stroke="{p["muted"]}" stroke-width="1.5" stroke-dasharray="2 5" opacity="0.6"/>')
        a.append(label(988,y,value,color=p['primary'],size=17))
    section(214,'SYSTEM')
    for y,k,v in [
       (243,'OS','macOS · Windows · Linux'),
       (273,'Uptime','GitHub since '+stats['since']),
       (303,'Host','MacBook Air M4 · Desktop PC'),
       (333,'Kernel','Darwin · Linux · NT'),
       (363,'IDE','VS Code · GoLand')
    ]: entry(y,k,v)
    section(402,'LANGUAGES')
    for y,k,v in [
       (433,'Programming','Python · Go · JavaScript · TypeScript'),
       (463,'Computer','HTML · CSS · SQL · JSON · YAML'),
       (493,'Real','German · Russian · English')
    ]: entry(y,k,v)
    section(533,'HOBBIES')
    entry(564,'Software','CTFs · Recon · Web Security')
    entry(594,'Hardware','Raspberry Pi · Homelab · Pico')
    section(635,'CONTACT')
    entry(665,'Email.Personal','stueckholz@hotmail.com')
    entry(695,'Email.Work','not published')
    entry(725,'LinkedIn','/in/mikhail-zhivoderov')
    entry(755,'Discord','not published')
    section(798,'GITHUB STATS')
    entry(828,'Repos',stats['repos'])
    entry(858,'Commits (12m)',stats['commits'])
    entry(888,'LOC (public HEAD)',stats['loc'])
    entry(918,'Stars (received)',stats['stars'])
    entry(948,'Followers',stats['followers'])
    a+=[f'<line x1="688" y1="972" x2="1493" y2="972" stroke="{p["border"]}"/>',
        label(690,992,'SYNC: '+stats['stamp'],color=p['muted'],size=13),
        label(44,1016,'// commits = last 12 months · LOC = current public source snapshot',color=p['muted'],size=14),
        '</g></svg>']
    return '\n'.join(a)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    art=(ROOT/'assets/portrait-braille.txt').read_text(encoding='utf8').splitlines()
    if args.offline:
        stats={'repos':'—','stars':'—','followers':'—','commits':'n/a',
               'loc':'n/a','since':'—','stamp':'Run GitHub Action for live stats'}
    else:
        try: stats=live(os.getenv('GITHUB_TOKEN'))
        except Exception as ex:
            print('Profile update failed; existing SVG files preserved:',ex,file=sys.stderr)
            sys.exit(1)
    for theme in ('dark','light'):
        target=ROOT/'assets'/f'{theme}_mode.svg'
        target.write_text(svg_theme(theme,art,stats),encoding='utf8')
        print('Wrote',target)

if __name__=='__main__': main()
