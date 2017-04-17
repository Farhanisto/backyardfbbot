
from index import app,db
from flask_script import Manager,prompt_bool

manager=Manager(app)
@manager.command
def initdb():
    db.create_all()



    print "Db created"



@manager.command
def dropdb():
    if prompt_bool("Are you sure ?"):
        db.drop_all()
        print "Db dropped"

if __name__=='__main__':

    manager.run()


