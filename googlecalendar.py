import argparse
import urllib.request
import json
import icalendar

#function formatIcalStr(vevent)
#{
#    // https://stackoverflow.com/a/18847018/445810
#    const vcal = new ICAL.Component(['vcalendar', [], []]);
#    vcal.addSubcomponent(vevent);
#    const icalsample = vcal.toString();
#    return icalsample;
#    //return "data:text/calendar," + encodeURIComponent(icalsample);
#}
#function isPast(evt, now = new Date())
#{
#    const withoutTime = dt => dt.setHours(0,0,0,0);
#    return withoutTime(evt.startDate.toJSDate()) < withoutTime(now);
#}
#const ical_url      = `https://calendar.google.com/calendar/ical/${googlecalendar_id}/public/basic.ics?orderby=starttime&sortorder=descending`; 
#// curl -L 'https://calendar.google.com/calendar/ical/c_8b8659dad12e20ac1130806694372259da336128023574166b99a96057a2c6ad@group.calendar.google.com/public/basic.ics?orderby=starttime&sortorder=descending&iCalUID=1npf1hn8t83cgismpm26ofnm5j@google.com'
#// &futureevents=true
#// https://www.googleapis.com/calendar/v3/calendars/${googlecalendar_id}/events
#const ics = await fetch(ical_url).then(r => {if(!r.ok) throw r; return r.text()}).catch(() => (''));
#let events = [];
#if(ics !== '')
#{
#    const jcalData = ICAL.parse(ics);
#    const comp = new ICAL.Component(jcalData);
#    const vevents_events = Array.from(comp.getAllSubcomponents("vevent")).map(vevent => [vevent, new ICAL.Event(vevent)]);
#    const past_events = vevents_events.filter(([vevent, evt]) =>  isPast(evt)).map(([vevent, evt]) => [vevent, evt, true]);
#    const past_events = vevents_events.filter(([vevent, evt]) => !isPast(evt)).map(([vevent, evt]) => [vevent, evt, false]);
#    if(auto)
#    {
#        events = future_events.length > 0 ? future_events : past_events;
#    }
#    else
#    {
#        if(!past && future)
#        {
#            events = future_events;
#        }
#        else if(past && !future)
#        {
#            events = past_events;
#        }
#        else if(!past && !future)
#        {
#            events = [];
#        }
#    }
#}
#const events_joined = events.map(([vevent, evt, past]) => ({summary: evt.summary, location: evt.location, description: evt.description, startdate_iso: evt.startDate.toJSDate().toISOString(), past: past, ical_str : formatIcalStr(vevent)}));


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
            res.append(dict(
                uid = component.get('uid'),
                name = component.get("name"),
                summary = component.get("summary"),
                description = component.get("description"),
                organizer = component.get("organizer"),
                location = component.get("location"),
                dtstart_iso = component.decoded("dtstart").isoformat(),
                dtend_iso = component.decoded("dtend").isoformat(),
                ical_str = ''
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
