import argparse
import urllib.request
import json
import icalendar

# curl -L 'https://calendar.google.com/calendar/ical/c_8b8659dad12e20ac1130806694372259da336128023574166b99a96057a2c6ad@group.calendar.google.com/public/basic.ics?orderby=starttime&sortorder=descending&iCalUID=1npf1hn8t83cgismpm26ofnm5j@google.com'
# &futureevents=true
# https://www.googleapis.com/calendar/v3/calendars/${googlecalendar_id}/events

def main(args):
    if not args.input_path and args.config_path:
        config = json.load(open(args.config_path))
        googlecalendar_id = config['googlecalendar_id']
        args.input_path = f'https://calendar.google.com/calendar/ical/{googlecalendar_id}/public/basic.ics?orderby=starttime&sortorder=descending'

    with urllib.request.urlopen(args.input_path) as f:
        ics_data = f.read().decode('utf-8')
    calendar = icalendar.Calendar.from_ical(ics_data)
    res = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            cal = Calendar()
            cal.add('prodid', '-//My Calendar Product//mxm.dk//')
            cal.add('version', '2.0')
            cal.add_component(component)
            ical_str = cal.to_ical().decode('utf-8')
            res.append(dict(
                uid = component.get('uid'),
                name = component.get("name"),
                summary = component.get("summary"),
                description = component.get("description"),
                organizer = component.get("organizer"),
                location = component.get("location"),
                dtstart_iso = component.decoded("dtstart").isoformat(),
                dtend_iso = component.decoded("dtend").isoformat(),
                ical_str = ical_str
            ))
    with open(args.output_path, 'w') as f:
        json.dump(res, f, ensure_ascii = False, indent = 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path')
    parser.add_argument('--config-path', '-c')
    parser.add_argument('--output-path', '-o', default = 'content/scrape/googlecalendar.json')
    args = parser.parse_args()
    
    main(args)
