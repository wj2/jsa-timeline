
## D&D Timelines ##
Simple timeline-maker based on the Google Charts Timeline visualization.

### Dependencies ###
* python 2.x
* markdown2

### Usage ###
There are two types objects: Timelines and Events. Events can have Timelines;
Timelines, in turn, have events. 

#### Events ####
Events are derived from text files with, at minimum, parameters give alone
on a line in the form:

    %% \<param\>: \<value\>

Necessary parameters are:
* Name -- name of the event, shown on the timeline and as the title of the event
  page.
* Type -- type of event, can be descriptive but should be short (eg, War, 
  Government)
* Nations -- comma delimited list of nations involved in the event, typically 
  it is a single nation except in the case of War type events -- for which all 
  belligerents should be listed.
* Start -- start date of the event, given as \<month\> \<day\>, \<year\>. The year 
  should be in PR (TODO: change to allow to specify dating scheme)
* End -- same as Start for the end of the event
Optional parameters:
* Timeline -- a folder with events from which to generate a timeline, that will 
  be displayed at the top of this event page

The remainder of the event text file should be a description of the event in 
markdown format.