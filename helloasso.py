import os
import json
import html.parser
import urllib.request
import urllib.parse
import argparse
import subprocess

class HelloassoParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_card = False
        self.in_card_goal = False
        self.collected_eur = 0
        self.goal_eur = 0
        self.contrib_num = 0
        self.last_eur = 0
        self.last_num = 0
        self.img_src = ''
    
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        cls = attr_dict.get('class', '').split()
        if 'CardNumbers--Main' in cls or 'WidgetHorizontale' in cls or 'WidgetVignette' in cls:
            self.in_card = True
        if not self.img_src and tag == 'img':
            self.img_src = attr_dict.get('src', '')

    def handle_data(self, data):
        if not self.in_card:
            return
        numstr = ''.join(filter(str.isdigit, data))
        if numstr:
            self.last_num = int(numstr)
        if '€' in data:
            self.last_eur = self.last_num
        if not self.collected_eur and ('collectés' in data.lower() or 'collected' in data.lower()):
            self.collected_eur = self.last_eur
            self.last_eur = self.last_num = 0
        if not self.goal_eur and ('objectif' in data.lower() or 'goal' in data.lower()):
            self.goal_eur = self.last_eur
            self.last_eur = self.last_num = 0
        if not self.contrib_num and ('contributeurs' in data.lower() or 'contributors' in data.lower()):
            self.contrib_num = self.last_num
            self.last_eur = self.last_num = 0

def request_access_token(helloasso_client_id, helloasso_client_secret, api_url = 'https://api.helloasso.com/oauth2/token'):
    data = urllib.parse.urlencode({"grant_type" : "client_credentials", "client_id": helloasso_client_id, "client_secret" : helloasso_client_secret})
    resp = urllib.request.urlopen(urllib.request.Request(api_url, headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': args.user_agent}, data = data.encode() ))
    access_token = json.load(resp)['access_token']
    return access_token

def scrape(url, chrome_exe, user_agent):
    html_str = subprocess.check_output([chrome_exe, '--headless', '--no-sandbox', '--disable-features=dbus', '--disable-gpu', '--lang=fr_FR', f"--user-agent='{user_agent}'", '--incognito', '--dump-dom', url], text = True)
    helloasso_parser = HelloassoParser()
    helloasso_parser.feed(html_str)
    res = dict(scraped_goal_eur = helloasso_parser.goal_eur, scraped_collected_eur = helloasso_parser.collected_eur, scraped_contrib_num = helloasso_parser.contrib_num, scraped_img_src = helloasso_parser.img_src)
    return res

def main(args):
    chrome_exe = os.getenv('CHROME_EXE', 'google-chrome-stable')
    config = json.load(open(args.config_path)) if args.config_path and os.path.exists(args.config_path) else {}

    helloasso_client_id = config.get('helloasso_client_id', os.getenv('HELLOASSO_CLIENT_ID', ''))
    helloasso_client_secret = config.get('helloasso_client_secret', os.getenv('HELLOASSO_CLIENT_SECRET', ''))
    helloasso_organization_slug = config.get('helloasso_organization_slug', '')
    
    helloasso_campaign_type = 'CrowdFunding'

    if args.input_path:
        res = {}
        if helloasso_client_id and helloasso_client_secret:
            parsed = urllib.parse.urlparse(args.input_path).path.split('/');
            helloasso_organization_slug = parsed[2]
            helloasso_campaign_slug = parsed[4]
            helloasso_campaign_type = dict(collectes = 'CrowdFunding', adhesions = 'Membership', evenements = 'Event', formulaires = 'Donation', paiements = 'PaymentForm', boutiques = 'Shop').get(parsed[3], '') # '' : 'Checkout'
            access_token = request_access_token(helloasso_client_id, helloasso_client_secret)
            api_url = f'https://api.helloasso.com/v5/organizations/{helloasso_organization_slug}/forms/{helloasso_campaign_type}/{helloasso_campaign_slug}/public';
            resp = urllib.request.urlopen(urllib.request.Request(api_url, headers = {'Accept': 'application/json', 'Authorization': f'Bearer {access_token}', 'User-Agent': args.user_agent}))
            res.update(json.load(resp))
        if args.scrape:
            scraped = scrape(args.input_path, chrome_exe, args.user_agent)
            res.update(scraped)
    else:
        assert helloasso_client_id and helloasso_client_secret
    
        access_token = request_access_token(helloasso_client_id, helloasso_client_secret)
        api_url = f'https://api.helloasso.com/v5/organizations/{helloasso_organization_slug}/forms'
        resp = urllib.request.urlopen(urllib.request.Request(api_url, headers = {'Accept': 'application/json', 'Authorization': f'Bearer {access_token}', 'User-Agent': args.user_agent}))
        campaigns = json.load(resp)['data']
        res = [campaign for campaign in campaigns if campaign['state'] == 'Public' and campaign['formType'] == 'CrowdFunding']
        if args.scrape:
            for i in range(len(res)):
                scraped = scrape(res[i]['widgetCounterUrl'], chrome_exe, args.user_agent)
                res[i].update(scraped)

    with open(args.output_path, 'w') as f:
        json.dump(res, f, indent = 2, ensure_ascii = False)
    print(args.output_path)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path', '-i')
    parser.add_argument('--config-path', '-c')
    parser.add_argument('--output-path', '-o')
    parser.add_argument('--user-agent', default = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
    parser.add_argument('--scrape', action = 'store_true')
    args = parser.parse_args()

    main(args)
