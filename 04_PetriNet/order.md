## 5.2.2.  The Petri Net steps and description


- **Micro1:** 
  - Output North may dissapear, clock goes up in either case
- **Micro2:** 
  - Output South may dissapear, clock goes up in either case 
- **Micro3:** 
  - North segment may move to West segment or Northern Outroad, clock goes up in either case
- **Micro4:** 
  - South segment may move to East segment or Southern Outroad, clock goes up in either case
- **Micro6:**
  - Eastern segment **MUST** move to the Northern segment if possible
  - -> Can only stay put if Northern segment is occupied
- **Micro7:** 
    - Western segment **MUST** move to the Southern segment if possible
    - -> Can only stay put if Southern segment is occupied
- **Micro8:** 
  - A vehicle on the Western inroad **MUST** enter the core (western segment) if possible
  - -> Can only stay put if Western segment is occupied
- **Micro9:** 
  - A vehicle on the Eastern inroad **MUST** enter the core (eastern segment) if possible
  - -> Can only stay put if Eastern segment is occupied
- **Micro10:** 
  - A vehicle may or may not enter western inroad.
- **Micro11:** 
  - A vehicle may or may not enter eastern inroad.

***
-  A vehicle on a West/East inro\ad should enter the core, if the corresponding core road segment is empty. However, preference should be given to a vehicle that is on the corresponding North/South core road segment if that vehicle wants to move to that East/West core segment. (You will only be able to implement this by choosing the correct sequence of events in your clock!)
- On every input, a new vehicle may appear or not (non-deterministically).
-  If there is a vehicle on either of the East or West road segments of the core, it has to move (deterministically) to the North or South road-segment of the core respectively, of-course only if the North/South road segment does not already contain a vehicle. 
- If there is a vehicle on either of the North or South road segments of the core, it may either move to the corresponding outroad (if empty) or to the next East-West road segment of the core, if empty (non-deterministic).
- On every output that contains a vehicle, the vehicle present can disappear or not (non-deterministically).

