#!/usr/bin/env python

"""
Exports Github Issues from a specified repository to a JSON file
"""

import json
from parse_link import parse_link_value
import requests
import sys

repo = 'httpwg/http-extensions'  # format is username/repo
repo_url = 'https://api.github.com/repos/%s/issues?state=all' % repo

def getIssues(url, issues=None):
    sys.stderr.write("* %s\n" % url)
    if not issues:
        issues = []
    res = requests.get(url)
    issues.append(res.json()[:])
    
    if 'link' in res.headers:
        links = parse_link_value(res.headers['link'])
        rel_next = rel_last = None
        for link, params in links.items():
            rel = params.get('rel', None)
            if rel == 'next':
                rel_next = link
            elif rel == 'last':
                rel_last = link
        if rel_next:
            getIssues(rel_next, issues)
        elif rel_last:
            getIssues(rel_last, issues)
    return issues

issues = getIssues(repo_url)
print json.dumps(issues, indent=1)


