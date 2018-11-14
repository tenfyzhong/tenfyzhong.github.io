#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import urllib
import json
import yaml
import requests
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# 拉取所有的评论issue
def get_issues(token, owner, repo, labels):
    label_str = ','.join(labels)
    label_str = urllib.quote(label_str)
    url = 'https://api.github.com/repos/%s/%s/issues?access_token=%s&labels=%s'%(owner, repo, token, label_str)
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def issue_label(issues):
    if not issues:
        return []
    labels = []
    for issue in issues:
        if not issue[u'labels']:
            continue
        for label in issue[u'labels']:
            if not label or label[u'name'] == '' or label[u'name'] == 'comment':
                continue
            labels.append(label[u'name'].encode('ascii','ignore'))
    return labels


# 解析sitemap.xml，解析出需要生产的issue列表及对应的标签
def post_path(sitemap, domain):
    tree = ET.ElementTree(file=sitemap)
    root = tree.getroot()
    if not root:
        return []
    ns = {
        'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
    }
    urls = [url.find('sitemap:loc', ns).text
              for url in root.findall('sitemap:url', ns)
              if url is not None]
    result = [url[len(domain):] for url in urls if url.startswith(domain) and url.endswith('/')]
    return result


# 对比已有的issue和sitemap的结果，产生需要新生成的issue
def subtraction(paths, labels):
    return list(set(paths)-set(labels))


class TitleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.match = False
        self.title = ''

    def handle_starttag(self, tag, attributes):
        self.match = True if tag == 'title' else False

    def handle_data(self, data):
        if self.match:
            self.title = data
            self.match = False


# 获取标题
def post_title(label):
    if not label:
        return ''

    filename = os.path.join('public', label[1:], 'index.html') if \
        label.startswith('/') else \
        os.path.join('public', label, 'index.html')

    parser = TitleParser()
    title = ''
    with open(filename, 'r') as stream:
        content = stream.read()
        parser.feed(content)
        title = parser.title
    parser.close()
    return title


# 创建issue
def post_issue(token, owner, repo, title, body, labels):
    url = 'https://api.github.com/repos/%s/%s/issues?access_token=%s'%(owner, repo, token)
    headers = {'Content-Type': 'application/json' }
    values = {'title' : title, 'body': body, 'labels': labels}
    r = requests.post(url, json=values, headers=headers)
    if r.status_code != 201:
        return None
    print('post issue title: %s' % title)
    return r.json()


def init_issue_with_label(token, owner ,repo, domain, comment_label, labels):
    for label in labels:
        title = post_title(label)
        body = domain + label
        post_issue(token, owner, repo, title, body, [comment_label, label])


def load_main_config(config):
    with open(config, mode='r') as stream:
        m = yaml.load(stream)
        return m
    return None


def load_theme_config(theme):
    path = os.path.join('themes', theme, '_config.yml')
    with open(path, mode='r') as stream:
        m = yaml.load(stream)
        return m
    return None


if __name__ == '__main__':
    token = os.getenv('AUTH-TOKEN')
    if not token:
        sys.exit(1)

    main_config = load_main_config('_config.yml')
    if not main_config:
        sys.exit(2)

    theme = main_config.get('theme', '')
    if not theme:
        sys.exit(3)

    theme_config = load_theme_config(theme)
    if not theme_config:
        sys.exit(4)

    comment_repo = theme_config.get('comment_repo', {})
    owner = comment_repo.get('owner', '')
    repo = comment_repo.get('repo', '')
    label = comment_repo.get('label', '')
    domain = main_config.get('url', '')
    if not owner or not repo or not label or not domain:
        sys.exit(5)

    issues = get_issues(token, owner, repo, [label])
    labels = issue_label(issues)
    sitemap = os.path.join('public', 'sitemap.xml')
    paths = post_path(sitemap, domain)
    want_init_label = subtraction(paths, labels)
    init_issue_with_label(token, owner, repo, domain, label, want_init_label)
