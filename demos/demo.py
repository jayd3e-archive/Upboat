from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.decorator import reify
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from upboat.models import UsersModel
from upboat.models import UsersObjectsModel
from upboat.models import ObjectsModel
from upboat.models import initializeBase

# Custom request class that automatically obtains a new SQLAlchemy session,
# on each request.
class UpboatRequest(Request):
    @reify
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        return maker()

# Root factory
class Site(object):
    def __init__(self, request):
        pass

# Main set of views for the demo
class MainHandler(object):
    def __init__(self, request):
        self.request = request
        self.here = request.environ['PATH_INFO']
        self.matchdict = request.matchdict
        
    @view_config(route_name='index', renderer='index.mako')
    def index(self):
        db = self.request.db
        objects = db.query(ObjectsModel).order_by(desc(ObjectsModel.score)).all()
        return {'title' : 'Upboat',
                'here' : self.here,
                'objects' : objects}

# Configuration function
def main(global_config, **settings):
        '''Main config function'''
        engine = create_engine("sqlite://", pool_recycle=3600)
        initializeBase(engine)

        # Will later attach a DBSession to the Request
        maker = sessionmaker(bind=engine, autocommit=True)
        settings['db.sessionmaker'] = maker

        config = Configurator(settings=settings,
                              root_factory=Site,
                              request_factory=UpboatRequest)
         
        config.add_static_view(name='static', path='upboat:static')
                                        
        # Handler Routes
        config.add_route('index', '/')
        config.add_route('toggle_vote', '/toggle_vote/{user_id}/{comment_id}/{vote}')
        
        # Scans                  
        config.scan('.')
        config.scan('upboat')
        return config.make_wsgi_app()

if __name__ == '__main__':
    from paste.httpserver import serve
    serve(main(None), host="0.0.0.0", port="5432")
