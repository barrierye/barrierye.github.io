#-*- coding:utf8 -*-
# Copyright (c) 2020 barriery
# Python release: 3.7.0
# Create time: 2020-04-18

import yaml
import re

class Line(object):
    def __init__(self, text, type='checkbox', state=''):
        if state not in ['', 'checked', 'checked class="green"',
                'class="indeterminate red"', 'class="green"',
                'checked class="orange"']:
            raise Exception(f'state({state}) error')
        self._text = f'<input type="{type}" {state}> {text}'
        self._context = None
    def set_context(self, ul):
        self._context = ul
    def gen_line(self):
        html_str = f'<li> {self._text}'
        if self._context:
            html_str += '\n' + self._context + '\n'
        html_str += '</li>'
        return html_str

class List(object):
    def __init__(self, name, major=False):
        #  self._id = name
        self._style = "list-style:none;"
        if major:
            self._style += "margin:0; padding:0;"
        self._lines = []
    def add_line(self, li):
        self._lines.append(li.gen_line())
    def gen_list(self):
        html_str = f'<ul style="{self._style}">' + '\n'
        #  html_str = f'<ul id="{self._id}" style="{self._style}">' + '\n'
        html_str += '\n'.join(self._lines)
        html_str += '\n</ul>'
        return html_str

def parse_list(yaml_obj, major):
    status = {'TODO': '',
              'deprecated': 'class="indeterminate red"',
              'Doing': 'class="green"',
              'Done': 'checked class="green"',
              'WIP': 'checked class="orange"'}
    res = {}
    for name, lists in yaml_obj.items():
        ul = List(name, major)
        for state_item in lists:
            for state, item_list in state_item.items():
                if state not in status:
                    raise Exception(f'state({state}) error')
                for item in item_list:
                    li = None
                    if isinstance(item, str):
                        li = Line(item, type='checkbox', state=status[state])
                    elif isinstance(item, dict):
                        list_name, list_str = parse_list(item, False)
                        li = Line(list_name, type='checkbox', state=status[state])
                        li.set_context(list_str)
                    else:
                        raise Exception(f'error type{type(item)}.')
                    ul.add_line(li)
        res[name] = ul.gen_list()
    (key, value), = res.items()
    return (key, value)

def parse_yaml(yaml_obj):
    def replace_href(matched):
        string = matched.group()
        p = re.compile(r'\[(?P<brief>.*?)\]\((?P<url>.*?)\)')
        r = p.match(string)
        return '<a href="{}">{}</a>'.format(r.group('url'), r.group('brief'))
    res = '''
<ul style="list-style:none;margin:0; padding:0;">
<li> <input type="checkbox"> TODO</li>
<li> <input type="checkbox" class="green"> Doing</li>
<li> <input type="checkbox" checked class="green"> Done</li>
<li> <input type="checkbox" checked class="orange"> WIP</li>
<li> <input type="checkbox" class="indeterminate red"> deprecated </li>
''' + '<br><br>\n'
    for li in yaml_obj:
        name, html = parse_list(li, True)
        res += '\n## {}\n{}\n'.format(name, html)
    pattern = r'\[.*?\]\(.*?\)'
    return re.sub(pattern, replace_href, res)

if __name__ == '__main__':
    with open('todo.yaml') as f:
        yaml_obj = yaml.load(f)
    print(parse_yaml(yaml_obj))
