
import timeline_objects as to

root_event = 'index.txt'

def make_site(root, outname='index.html'):
     root_t = to.Event(path=root)
     root_t.save_html(outname)

if __name__ == '__main__':
    make_site(root_event)
    
