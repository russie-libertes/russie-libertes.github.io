import argparse
import urllib.request
import json
import icalendar

def main(args):
    if not args.input_path and args.config_path:
        config = json.load(open(args.config_path))
        googlecalendar_id = config['googlecalendar_id']
        args.input_path = f'https://calendar.google.com/calendar/r?cid={googlecalendar_id}';

    with urllib.request.urlopen(args.input_path) as f:
        ics_data = f.read().decode('utf-8')
    calendar = icalendar.Calendar.from_ical(ics_data)
    with open(args.output_path, 'w') as f:
        f.write(calendar.to_json())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path')
    parser.add_argument('--config-path', '-c')
    parser.add_argument('--output-path', '-o', default = 'content/scrape/googlecalendar.json')
    args = parser.parse_args()
    
    main(args)
