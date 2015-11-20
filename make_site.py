
import timeline_objects as to

root_folder = 'events'

def make_site(root, outname='index.html'):
     root_t = to.Timeline(root)
     root_t.save_html(outname)

if __name__ == '__main__':
    make_site(root_folder)
    
