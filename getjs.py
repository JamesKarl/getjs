#!/usr/bin/env python3

import sys, re, os, os.path

LOCAL_DOMAIN=r'ajax.googleapis.com'

LOCAL_LIBS_ROOT=r'/Users/jameskarl/devenv/libs';
JS_DIR_NAME=r'js'
CSS_DIR_NAME=r'css'
HPPT_PREFIX=r'http://'

JSPATH=os.path.join(LOCAL_LIBS_ROOT,JS_DIR_NAME)
CSSPATH=os.path.join(LOCAL_LIBS_ROOT,CSS_DIR_NAME)

js_file_list="jslists"

rehtml=re.compile('.+\.html|.+\.php')
rescript=re.compile('src=".+\.js"')

def get_res_set(thedir, reexpr):
    res = set()
    if os.path.exists(thedir):
        for root, dirs, files in os.walk(thedir):
            for name in files:
                if rehtml.match(name):
                    f = open(os.path.join(root, name))
                    for line in f:
                        mm=reexpr.search(line)
                        if mm:
                            tmp = mm.group(0)
                            if -1 == tmp.find('//'):
                                continue
                            
                            p1=tmp.index('//')
                            jsabspath=tmp[p1+2:-1]
                            #jsabspath is a string like code.jquery.com/qunit/qunit-1.16.0.js
                            res.add(jsabspath)
                
                    f.close()
    return res

#js is the relative path like
# 1. use.typekit.net/wde1aof.js
# 2. qunitjs.com/jquery-wp-content/themes/jquery/js/main.js
def create_local_libs(js):
    #print js
    curdir = os.getcwd();
    os.chdir(JSPATH)

    (js_domain, js_path, js_file) = parse_url(js)

    #print lslash,rslash, js_domain, js_path, js_file
    if (js_path != '' and os.path.isdir(js_path) == False):
        mkdirs(js_path)
    if (js_path != ''):
        os.chdir(js_path)
    if os.path.isfile(js_file) == False:
        jslink = (HPPT_PREFIX + js_domain + '/' + js_file)
        if js_path != '':
            jslink = (HPPT_PREFIX + js_domain + '/' + js_path + '/' + js_file)
        print jslink
        os.system('wget --tries=3 ' + jslink)
    os.chdir(curdir)

#ps is a sting like jquery-wp-content/themes/jquery/js
def mkdirs(ps):
    curdir = os.getcwd();
    dirs = ps.split('/')
    for d in dirs:
        os.mkdir(d)
        os.chdir(d)
    os.chdir(curdir)

#thedir is absolute path like /Users/jameskarl/docs/web/site/qunitjs.com
#jsset is a set, the item of which is something like:
#[code.jquery.com/qunit/qunit-1.16.0.js]
def update_the_files(thedir, jsset):
    if os.path.exists(thedir):
        for root, dirs, files in os.walk(thedir):
            for name in files:
                if rehtml.match(name):
                    fname = os.path.join(root, name);
                    f = open(fname)
                    fcontent=''
                    for line in f:
                        newline = line
                        for js in jsset:
                            if line.find(js) != -1 and local_js_exists(js):
                                newline = line.replace(js, local_site_url(js)).replace('src="//', 'src="http://')
                        fcontent += newline
                    f.close()
                    tmpfname = fname + 'tmpxx'
                    tmpf = open(tmpfname, 'w')
                    tmpf.write(fcontent)
                    tmpf.close()
                    os.rename(tmpfname, fname)


#thejs is something like: [code.jquery.com/qunit/qunit-1.16.0.js]
def local_js_exists(thejs):
    (d, p, f) = parse_url(thejs)
    return os.path.isfile(js_abspath(p, f))

#thejs is something like: [code.jquery.com/qunit/qunit-1.16.0.js]
def parse_url(theurl):
    lslash=theurl.index('/')
    rslash=theurl.rindex('/')
    domain=theurl[:lslash]
    path=theurl[lslash+1:rslash]
    file=theurl[rslash+1:]
    return (domain, path, file)

#p is a empty string or something like: [jquery-wp-content/themes/jquery/js]
#f is the file name like: [main.js]
def js_abspath(p, f):
    return (JSPATH + '/' + f) if p == '' else (JSPATH + '/' + p + '/' + f)

def local_site_url(theurl):
    d, p, f = parse_url(theurl)
    return (LOCAL_DOMAIN + '/js/' + p + '/' + f) if p != '' else (LOCAL_DOMAIN + '/' + f)

#thedir is absolute path like /Users/jameskarl/docs/web/site/qunitjs.com
def main(thedir):
    print 'The directory root:' + thedir
    jsset = get_res_set(thedir, rescript)
    for js in jsset:
        create_local_libs(js)

    update_the_files(thedir, jsset)

def sometest():
    os.chdir('/Users/jameskarl/')

if __name__ == '__main__':
    if len(sys.argv) != 1:
        thedir = sys.argv[1]
    else:
        thedir = os.getcwd()
    main(thedir)
