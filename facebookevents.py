import argparse
import os
import re
import json
import csv
import codecs
import urllib.request
import urllib.parse
import html.parser

def extract_links_from_markdown(markdown_text):
    inline_link_pattern = r'(?<!!)\[[^\]]*\]\(([^)]+)\)'
    links = re.findall(inline_link_pattern, markdown_text)
    return links

class MetaParser(html.parser.HTMLParser):
    def __init__(self, hydration_prefix = []):
        super().__init__()
        self.metadata = dict(title = '', meta = {}, link = [], ld_json = [], hydration = [])
        self.in_title = False
        self.in_ld_json = False
        self.in_script = True
        self.hydration_prefix = hydration_prefix

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            name = attr_dict.get('name', '') or attr_dict.get('property', '')
            content = attr_dict.get('content', '')
            if name:
                self.metadata[tag][name] = content
        if tag == 'link':
            self.metadata[tag].append(attr_dict)
        if tag == 'script' and attr_dict.get('type', '') == 'application/ld+json':
            self.in_ld_json = True
        elif tag == 'script':
            self.in_script = True
            

    def handle_data(self, data):
        if self.in_title:
            self.metadata['title'] = data
            self.in_title = False

        if self.in_ld_json:
            self.metadata['ld_json'].append(json.loads(data))
            self.in_ld_json = False

        if self.in_script:
            data_lstrip = data.lstrip()
            for prefix in self.hydration_prefix:
                if data_lstrip.startswith(prefix):
                    data_lstrip_noprefix = data_lstrip.removeprefix(prefix).lstrip().removeprefix('=').replace('undefined', '{}').replace('null', '{}')
                    self.metadata['hydration'].append(json.loads(data_lstrip_noprefix))
            self.in_script = False

def main(args):
    input_urls = []
    for path in args.input_path:
        print(path)
        if path.endswith('.md'):
            with open(path) as f:
                markdown = f.read()
            input_urls += extract_links_from_markdown(markdown)
        else:
            input_urls.append(path)
    print(input_urls)

    res = []
    for path in input_urls:
        print(path)
        try:
            with (urllib.request.urlopen(urllib.request.Request(path, headers = {'User-Agent': args.user_agent})) if path.startswith('https://') else open(path, 'rb')) as f:
                html_str = f.read().decode('utf-8')
            meta_parser = MetaParser()
            meta_parser.feed(html_str)
            res.append(dict(meta_parser.metadata, url = path))
        except Exception as e:
            res.append(dict(url = path))
            print('  error:', str(e))
            pass

    with open(args.output_path, 'w') as f:
        json.dump(res, f, indent = 2, ensure_ascii = False)
    print(args.output_path)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path', '-i', nargs = '*', default = [])
    parser.add_argument('--output-path', '-o', default = 'content/scrape/facebookevents.json')
    parser.add_argument('--user-agent', default = 'curl/8.7.1')
    args = parser.parse_args()

    main(args)
