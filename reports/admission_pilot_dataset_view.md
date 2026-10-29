# Dataset used for the first NeuroBrain training trial

80 fictional assistant-authored records: 50 train, 15 validation, 15 test. Only the 50 training records were used for gradient updates. Validation selected the checkpoint and threshold; test measured the frozen result.

**All labels are draft labels pending human review.** Label 1 = useful to remember; label 0 = not useful to remember. No personal notes or public datasets were used. The model trained was the admission MLP, not Qwen.

The source JSONL also records IDs, timestamps, scenario and template groups, annotation status and fictional provenance. The tables below show every candidate and its intended label/rationale.

## Train

### Database

Context: The fictional Alder team is selecting storage for an offline notes tool.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-00-00 | Concurrent imports still produce a reproducible locked-database error. | 1 | Specific unresolved issue. |
| pilot-00-01 | We settled on SQLite because this prototype has one local user. | 1 | Durable architecture decision. |
| pilot-00-02 | Many thanks for taking a look at those storage options. | 0 | Acknowledgment without durable information. |
| pilot-00-03 | The progress spinner moved a little while I watched it. | 0 | Transient observation. |
| pilot-00-04 | The import transaction must include its full text search update. | 1 | Reusable consistency requirement. |

### Accessibility

Context: A fictional designer reviews the Cedar interface.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-01-00 | Please remember that I navigate primarily using the keyboard. | 1 | Stable accessibility preference. |
| pilot-01-01 | I am moving the pointer over the left side of the window now. | 0 | Temporary interaction. |
| pilot-01-02 | The focus indicator disappears after closing the confirmation dialog. | 1 | Actionable unresolved defect. |
| pilot-01-03 | Every delete control needs an accessible name describing its source. | 1 | Reusable interface requirement. |
| pilot-01-04 | That sounds fine, let us continue with the walkthrough. | 0 | Conversational transition. |

### Research

Context: A fictional student organizes a literature review.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-02-00 | I have just scrolled past the heading we already read. | 0 | Temporary activity. |
| pilot-02-01 | There are three tabs visible at this exact moment. | 0 | Incidental session state. |
| pilot-02-02 | My supervisor requires a primary source for each factual claim. | 1 | Durable review requirement. |
| pilot-02-03 | The citation export drops authors whose names contain accents. | 1 | Specific unresolved problem. |
| pilot-02-04 | The proposal submission deadline is November 18. | 1 | Future milestone. |

### Cooking

Context: A fictional household plans reusable meal preferences.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-03-00 | Yes, I can see the recipe title on this page. | 0 | Acknowledgment. |
| pilot-03-01 | For future meal plans, exclude peanuts from my dishes. | 1 | Persistent dietary constraint. |
| pilot-03-02 | Replace the old servings estimate: our household now has four people. | 1 | Explicit lasting correction. |
| pilot-03-03 | Our regular grocery collection happens on Saturday mornings. | 1 | Reusable schedule. |
| pilot-03-04 | The kettle is boiling while we type this sentence. | 0 | Ephemeral status. |

### Study

Context: A fictional learner sets up a recurring study routine.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-04-00 | I am stretching my arms before the next paragraph. | 0 | Transient unrelated action. |
| pilot-04-01 | The cursor blinked twice in the search field. | 0 | Incidental observation. |
| pilot-04-02 | I still confuse validation loss with final test performance. | 1 | Specific learning gap for later sessions. |
| pilot-04-03 | Reserve Tuesday evenings for the weekly revision session. | 1 | Recurring plan. |
| pilot-04-04 | Worked numerical examples help me more than long definitions. | 1 | Reusable learning preference. |

### Travel

Context: A fictional traveler prepares an upcoming conference trip.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-05-00 | I need step-free access when choosing accommodation. | 1 | Durable accessibility constraint. |
| pilot-05-01 | The conference venue changed from Harbor Hall to Birch Center. | 1 | Correction of an important planned location. |
| pilot-05-02 | A person outside just walked past the window. | 0 | Irrelevant temporary event. |
| pilot-05-03 | The hotel reservation remains unconfirmed despite two attempts. | 1 | Unresolved task relevant to the trip. |
| pilot-05-04 | Let me take a sip of water before we carry on. | 0 | Transient chatter. |

### Writing

Context: A fictional author describes editorial conventions.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-06-00 | Oh, right, I see what you were referring to. | 0 | Acknowledgment. |
| pilot-06-01 | The main character was renamed from Lio to Soren. | 1 | Durable correction. |
| pilot-06-02 | Chapter six still contradicts the timeline established in chapter two. | 1 | Specific unresolved continuity issue. |
| pilot-06-03 | Use British spelling throughout this manuscript. | 1 | Reusable project convention. |
| pilot-06-04 | I highlighted the first word for a moment and cleared it. | 0 | Temporary editor state. |

### Garden

Context: A fictional club records gardening plans.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-07-00 | The northern bed receives shade all afternoon. | 1 | Stable fact relevant to future planting. |
| pilot-07-01 | The west irrigation valve leaks whenever the pump starts. | 1 | Persistent actionable fault. |
| pilot-07-02 | The wheelbarrow rattled once as I moved past it. | 0 | Incidental noise without ongoing issue. |
| pilot-07-03 | A small cloud crossed the sun just now. | 0 | Fleeting observation. |
| pilot-07-04 | We chose drip irrigation for the greenhouse. | 1 | Durable decision. |

### Music

Context: A fictional musician arranges weekly practice.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-08-00 | I tapped the table twice while waiting for the page. | 0 | Transient action. |
| pilot-08-01 | That was an interesting sentence, anyway let us move on. | 0 | Chatter without a durable fact. |
| pilot-08-02 | The audio interface disconnects consistently when recording starts. | 1 | Reproducible unresolved defect. |
| pilot-08-03 | I tune this guitar a whole step below standard tuning. | 1 | Reusable instrument setup. |
| pilot-08-04 | The recital is scheduled for December 7. | 1 | Future milestone. |

### Workshop

Context: A fictional maker organizes a woodwork project.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-09-00 | The cabinet opening is 82 centimetres wide. | 1 | Project dimension needed later. |
| pilot-09-01 | I clicked away from the toolbar and then clicked back. | 0 | Temporary interface action. |
| pilot-09-02 | The window reflection shifted while I read the sketch. | 0 | Incidental visual observation. |
| pilot-09-03 | Use water-based finish for this cabinet. | 1 | Durable material choice. |
| pilot-09-04 | The hinge alignment is still off by three millimetres. | 1 | Specific unresolved issue. |

## Validation

### Volunteer

Context: A fictional volunteer group coordinates a library event.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-10-00 | Nera is now responsible for coordinating the book collection. | 1 | Lasting responsibility update. |
| pilot-10-01 | I am checking the time on my watch this second. | 0 | Temporary action. |
| pilot-10-02 | The pickup driver has not confirmed the accessible van yet. | 1 | Unresolved dependency. |
| pilot-10-03 | Drop-off closes at noon on the event day. | 1 | Relevant deadline. |
| pilot-10-04 | Okay, understood, we can proceed to the next point. | 0 | Acknowledgment. |

### Photography

Context: A fictional photographer maintains project requirements.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-11-00 | Thank you, that explanation answers my immediate question. | 0 | Acknowledgment. |
| pilot-11-01 | Deliver the exhibition images in monochrome. | 1 | Durable output requirement. |
| pilot-11-02 | Exported files consistently lose their capture timestamps. | 1 | Reproducible unresolved issue. |
| pilot-11-03 | The thumbnail flashed briefly when I opened the folder. | 0 | Temporary interface observation. |
| pilot-11-04 | The client changed the required print width to 40 centimetres. | 1 | Explicit dimension correction. |

### Language

Context: A fictional language learner records tutoring preferences.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-12-00 | Correct my pronunciation after I finish the sentence. | 1 | Reusable feedback preference. |
| pilot-12-01 | Our oral assessment takes place on January 12. | 1 | Future milestone. |
| pilot-12-02 | I still mix up past and present forms in spoken replies. | 1 | Specific persistent learning gap. |
| pilot-12-03 | I am turning the page in the workbook right now. | 0 | Transient action. |
| pilot-12-04 | Hmm, let us pause for a second before moving ahead. | 0 | Temporary conversational pause. |

## Test

### Fitness

Context: A fictional runner organizes a training diary, without medical advice.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-13-00 | I can see the next section now, thanks. | 0 | Acknowledgment. |
| pilot-13-01 | The club moved its weekly meeting point to Pine Gate. | 1 | Lasting location update. |
| pilot-13-02 | The diary importer counts the same activity twice after a restart. | 1 | Persistent reproducible application issue. |
| pilot-13-03 | A bicycle passed the bench while I waited. | 0 | Irrelevant transient event. |
| pilot-13-04 | I prefer morning runs to evening runs. | 1 | Durable scheduling preference. |

### Museum

Context: A fictional curator plans a small exhibition.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-14-00 | I adjusted my chair before looking at the layout. | 0 | Transient unrelated action. |
| pilot-14-01 | The selection border appeared when I clicked the map. | 0 | Temporary interface state. |
| pilot-14-02 | The display inventory still lacks a location for object K17. | 1 | Specific unresolved inventory issue. |
| pilot-14-03 | Keep the original object labels alongside their translations. | 1 | Durable curatorial requirement. |
| pilot-14-04 | Opening day was postponed to March 9. | 1 | Explicit schedule correction. |

### Robotics

Context: A fictional school club documents its robot build.

| ID | Candidate | Label | Rationale |
|---|---|---:|---|
| pilot-15-00 | Sure, I follow the explanation so far. | 0 | Acknowledgment. |
| pilot-15-01 | The left motor reverses direction whenever the controller reboots. | 1 | Reproducible unresolved fault. |
| pilot-15-02 | The wheel encoder produces 360 pulses per revolution. | 1 | Stable technical specification. |
| pilot-15-03 | We changed the control link from Bluetooth to a wired connection. | 1 | Durable design change. |
| pilot-15-04 | My sleeve brushed the desk while I opened the notebook. | 0 | Incidental action. |

