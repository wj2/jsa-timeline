
import os
import re
import markdown2 as mkd
from string import Template

tt_path = 'timeline_template.html'
timeline_template = Template(open(tt_path, 'rb').read())

ed_path = 'event_display_template.html'
event_display_template = Template(open(ed_path, 'rb').read())

month_names = ['coldeve', 'snowreap', 'wintersebb', 'morningthaw', 'solclaim',
               'feedsow', 'leafdawning', 'verdanture', 'thistledown', 
               'harvestgain', 'leaffall', 'frostfall']
month_numbers = xrange(0, 12)
months = {}
for i,x in enumerate(month_names):
    months[x] = month_numbers[i]
    months[month_numbers[i]] = x

def split_and_strip(string, dlim, stripd=' '):
    return [x.strip(stripd) for x in string.split(dlim)]

def convert_date(date):
    month, date, year = split_and_strip(date, ' ', stripd=',')
    try: 
        month = int(month)
        month = month - 1
    except ValueError:
        month = months[month]
    return month, date, year

def make_js_date(month, date, year):
    date = 'goodDate({}, {}, {})'.format(year, 
                                         month, 
                                         date,
                                         year)
    return date
    
def make_event_date(date):
    month, date, year = split_and_strip(date, ' ', stripd=',')
    try:
        month = int(month)
        month = months[month - 1]
    except ValueError:
        pass
    return '{} {}, {}'.format(month, date, year)

def read_multiple_events(path=None, linelist=None, headersymbol='%%', 
                         expectlines=6, evbegin='event', prevpath=None):
    if path is not None:
        f = open(path, 'rb')
        linelist = [x for x in f.readlines()]
    else:
        path = prevpath
    events = []
    prev_lines = []
    lhs = len(headersymbol)
    for i, line in enumerate(linelist):
        head = line[:lhs] == headersymbol 
        event_beg = line[lhs:].strip(' ').lower()[:-1] == evbegin
        if head and event_beg:
            if len(prev_lines) >= expectlines:
                e = Event(linelist=prev_lines, prevpath=path, ind=len(events),
                          level=evbegin)
                events.append(e)
                prev_lines = []
        prev_lines.append(line)
    e = Event(linelist=prev_lines, prevpath=path, ind=len(events), 
              level=evbegin)
    events.append(e)
    return events
            
class Event(object):

    def __init__(self, linelist=None, path=None, headersymbol='%%',
                 prevpath=None, ind=None, level='event'):
        if path is not None:
            f = open(path, 'rb')
            linelist = [x for x in f.readlines()]
            loc = os.path.splitext(path)[0]
            self.html_path = loc + '.html'
        else: 
            prevp = os.path.splitext(prevpath)[0]
            h_path = '{}_{}.html'.format(prevp, ind)
            self.html_path = h_path
        descript = ''
        sublevel = 'sub'+level
        for i, line in enumerate(linelist):
            lhs = len(headersymbol)
            if line[:lhs] == headersymbol:
                # param, val = split_and_strip(line[lhs:], ':')
                out = split_and_strip(line[lhs:], ':')
                if len(out) == 2:
                    param, val = out
                    setattr(self, param.lower().strip('\n'), 
                            val.lower().strip('\n'))
                elif out[0][:-1].lower() == sublevel:
                    break
            else:
                descript = descript + line
        self.description = descript
        if i + 1 < len(linelist):
            es = read_multiple_events(linelist=linelist[i:], headersymbol=headersymbol,
                                      evbegin=sublevel, prevpath=self.html_path)
            self._add_events_to_timeline(es)
            
    def _add_events_to_timeline(self, events):
        t = self.get_timeline()
        if t is None:
            t = Timeline(event_list=events, html_name=self._html_name)
        else:
            t.add_events(events)
        self.timeline = t

    @property
    def _html_name(self):
        hname = os.path.splitext(self.html_path)[0]
        return hname

    def get_timeline(self):
        try:
            t = self.timeline
        except AttributeError:
            t = None
        else:
            try: 
                t.upper()
            except AttributeError:
                pass
            else:
                self.timeline = Timeline(source_folder=t, 
                                         html_name=self._html_name)
                t = self.timeline
        return t
        

    def get_html(self):
        t = self.get_timeline()
        if t is None:
            pretitle = ''
        else:
            pretitle = t.get_html()
        desc = mkd.markdown(self.description)
        e_start = make_event_date(self.start)
        e_end = make_event_date(self.end)
        full_html = event_display_template.substitute(pretitle=pretitle,
                                                      title=self.name,
                                                      type=self.type,
                                                      nations=self.nations,
                                                      start=e_start,
                                                      end=e_end,
                                                      description=desc)
        return full_html

    def save_html(self, path=None):
        if path is not None:
            self.html_path = path 
        else:
            path = self.html_path
        h = self.get_html()
        f = open(path, 'wb')
        f.write(h)
        return path

    def get_table_entries(self):
        categs = ['{} {}'.format(x, self.type) 
                  for x in split_and_strip(self.nations, ',')]
        entr_ev = "['{}', '{}', {}, {}]"
        entries = []
        sd = convert_date(self.start)
        js_start = make_js_date(*sd)
        ed = convert_date(self.end)
        js_end = make_js_date(*ed)
        for c in categs:
            # entr = entr_ev.format(c, self.name, js_start, js_end)
            entr = entr_ev.format(c, self.name, js_start, js_end)
            entries.append(entr)
        return entries
        
class Timeline(object):

    def __init__(self, source_folder=None, event_list=None, 
                 eventpatt='.*\.txt$', html_name='index'):
        self.html_path = os.path.splitext(html_name)[0] + '.html'
        if source_folder is not None:
            events = self._make_timeline_folder(source_folder, 
                                                eventpatt=eventpatt)
        elif event_list is not None:
            events = event_list
        self.events = events

    def _make_timeline_folder(self, source_folder, eventpatt='.*\.txt$'):
        event_files = os.listdir(source_folder)
        event_files = filter(lambda x: re.match(eventpatt, x) is not None, 
                             event_files)
        event_files = [os.path.join(source_folder, x) for x in event_files]
        events = []
        for f in event_files:
            # ev = Event(path=f)
            # events.append(ev)
            evs = read_multiple_events(path=f)
            events = events + evs
        return events

    def add_events(self, events):
        self.events = self.events + events

    def get_html(self):
        entries = []
        row_links = []
        for e in self.events:
            link = e.save_html()
            rellink = os.path.relpath(link, 
                                      os.path.split(self.html_path)[0])
            entries = entries + e.get_table_entries()
            row_links = row_links + [rellink]*len(entries)
        e_arr = '[' + ','.join(entries) + ']'
        thtml = timeline_template.substitute(row_array=e_arr, 
                                             event_links=row_links)
        return thtml

    def save_html(self, path=None):
        if path is not None:
            self.html_path = path
        else:
            path = self.html_path
        h = self.get_html()
        f = open(path, 'wb')
        f.write(h)
        return path
                
