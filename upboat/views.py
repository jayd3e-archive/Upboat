from pyramid.view import view_config
from upboat.models import UsersObjectsModel
from upboat.models import ObjectsModel

class ToggleVoteHandler(object):
    def __init__(self, request):
        self.request = request
        self.here = request.environ['PATH_INFO']
        self.matchdict = request.matchdict
        
    @view_config(route_name='toggle_vote', renderer='json')
    def toggle_vote(self):
        user_id = self.matchdict['user_id']
        object_id = self.matchdict['object_id']
        vote = self.matchdict['vote']
        
        db = self.request.db
        voted_object = db.query(ObjectsModel).filter_by(id=object_id).first()
        if vote=='up':
            vote = 1
        elif vote=='down':
            vote = -1
        else:
            return {'status' : 'unchanged', 'score' : voted_object.score}
        
        users_objects = db.query(UsersObjectsModel).filter_by(user_id=user_id,
                                                              object_id=object_id).first()
        # Vote exists                                                             
        if users_objects:
            if users_objects.vote != vote:
                users_objects.vote = vote
                db.flush()
                status = 'changed'
            else:
                db.delete(users_objects)
                db.flush()
                status = 'deleted'
                
        # Vote doesn't exist
        else:
            users_objects = UsersObjectsModel(user_id=user_id,
                                              object_id=object_id,
                                              vote=vote)
            db.add(users_objects)
            db.flush()
            status = 'added'
        
        score = self.calculateScore(voted_object)
        voted_object.score = score
        db.flush()
        return {'status' : status, 'score' : score}
        
    def calculateScore(self, voted_object):
        score = 0
        for users_objects in voted_object.users_objects:
            score += users_objects.vote
        return score