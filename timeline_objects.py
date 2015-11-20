
import os
import re
import markdown2 as mkd
from string import Template

tt_path = 'timeline_template.html'
timeline_template = Template(open(tt_path, 'rb').read())

ed_path = 'event_display_template.html'
event_display_template = Template(open(ed_path, 'rb').read())

month_names = ['coleve', 'snowreap', 'wintersebb', 'morningthaw', 'solclaim',
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

class Event(object):

    def __init__(self, path, headersymbol='%%'):
        f = open(path, 'rb')
        descript = ''
        for i, line in enumerate(f.readlines()):
            if line[:len(headersymbol)] == headersymbol:
                param, val = split_and_strip(line[len(headersymbol):], ':')
                setattr(self, param.lower().strip('\n'), 
                        val.lower().strip('\n'))
            else:
                descript = descript + line
        self.description = descript
        self.mkd_path = path
        loc = os.path.splitext(path)[0]
        self.html_path = loc + '.html'

    def get_html(self):
        desc = mkd.markdown(self.description)
        e_start = make_event_date(self.start)
        e_end = make_event_date(self.end)
        full_html = event_display_template.substitute(title=self.name,
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

    def __init__(self, source_folder, eventpatt='.*\.txt$', html_name='index'):
        event_files = os.listdir(source_folder)
        event_files = filter(lambda x: re.match(eventpatt, x) is not None, 
                             event_files)
        event_files = [os.path.join(source_folder, x) for x in event_files]
        self.html_path = os.path.splitext(html_name)[0] + '.html'
        self.events = []
        for f in event_files:
            ev = Event(f)
            self.events.append(ev)

    def get_html(self):
        entries = []
        row_links = []
        for e in self.events:
            link = e.save_html()
            entries = entries + e.get_table_entries()
            row_links = row_links + [link]*len(entries)
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
                
