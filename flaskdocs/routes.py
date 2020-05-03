
from flaskdocs import app, db, scheduler

@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    print(User.query.get(1))
