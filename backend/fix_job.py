from database.db import SessionLocal, create_tables
from database.models import Job
import json

create_tables()
db = SessionLocal()
job = db.query(Job).filter(Job.id == 'fb9bcb48-16dc-48c7-b091-7bf05deb81a7').first()
if job:
    job.status = 'completed'
    job.progress = 100
    job.result = json.dumps({"title": "Fixed Script", "hook": "Fixed hook", "scenes": [{"scene_number": 1, "visual_description": "Fixed visual", "voiceover_script": "Fixed voiceover", "duration_seconds": 10}], "cta": "Fixed CTA"})
    db.commit()
    print("Job updated")
else:
    print("Job not found")
db.close()