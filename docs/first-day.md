# Your first study session

Example only. Exact responses and pace depend on your answers. No system-design knowledge is required.

1. **Open a study folder in Cursor and start an Agent chat.**
   Type `/sd-learn`. The tutor asks how long you would like to study, not where you are weak.

2. **Give a simple answer.**
   "I have an hour and I know nothing about this."
   The tutor creates the full curriculum map in `.system-design/curriculum.md`. Every untested item starts unassessed. You do not have to recognize topic names or choose today's lesson.

3. **Try one everyday question.**
   "When you type a website address and a page appears, what do you think happened in between?"
   Say what you think, or say "I don't know." Either is enough to start.

4. **Get a foothold if you need it.**
   The tutor explains that a browser sends a request to a server and receives a response. It draws the two directions. Then it asks what might happen if the server cannot reply.
   You learn the words request, response and server through something you already use.

5. **Reason about one changed condition.**
   "The browser works, but the server is unreachable. What might you see?"
   You might say loading or an error. The tutor builds on that instead of demanding a networking definition.

6. **Connect the next idea.**
   "You save a note, close the app and return tomorrow. What would need to be kept?"
   This leads toward stored data and databases. It is not a database-knowledge test. The tutor explains missing pieces before expecting you to use them.

7. **Explain the first idea back.**
   Describe who sends the request, who sends the response and one reason a page might not appear. Then apply it to a different everyday app. If you need hints, the tutor records assisted progress and keeps teaching.

8. **Save without pretending you finished a whole subject.**
   Say "Stop and save." Check `.system-design/progress.md`, the readable view of your validated state. It should show the specific small concept practiced, your evidence, what remains unclear and the next question. Understanding one request does not mark all communication complete.

9. **Come back without planning another syllabus.**
   Run `/sd-learn`. It checks due recall, then selects the next unresolved microconcept in the map. `/sd-review` is there if you want a recall-only session. A fresh independent pass at least 24 hours later can earn retained status for that concept. Intro checks use simple correctness/application, not advanced tradeoff questions. Assisted attempts get repair too; a waiting provisional concept does not stop new learning.

The tutor owns the curriculum and next step. You own the reasoning. You do not need to know what you don't know.

No background timer or reminders run. The Markdown records learning attempts, not verified elapsed time. If saving fails, the tutor must say so.

Saving now uses a local Python helper with revision checks, a write lock, backups and atomic canonical JSON. State belongs only to your chosen study folder. Readable Markdown is a view; do not edit it to grant yourself a score. Errors are surfaced, and interrupted or conflicting writes require recovery instead of a claim that everything saved. Use one active chat per workspace.
