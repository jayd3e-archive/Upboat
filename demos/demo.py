from pyramid.view import view_config
from upboat.models import initializeBase

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

def main(global_config, **settings):
        '''Main config function'''
        engine = create_engine("sqllite://", pool_recycle=3600)
        initializeBase(engine)
         
        config.add_static_view(name='static', path='reprap:static')
                                        
        #Handler Root Routes
        config.add_route('index', '/')
                          
        config.scan('upboat')
        return config.make_wsgi_app()

if __name__ == '__main__':
    from paste.httpserver import serve
    serve(main(), host="0.0.0.0", port="5432")
