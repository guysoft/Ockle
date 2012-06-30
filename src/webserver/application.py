from wsgiref.simple_server import make_server

from pyramid.config import Configurator

def main():
    config = Configurator()
    
    #Add server view
    config.add_route('tree', '/server/{serverName}')
    #config.add_view(showTree, route_name='tree')
    
    config.scan("views")
    config.add_static_view('static', 'static/',
                           cache_max_age=86400)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8000, app)
    server.serve_forever()