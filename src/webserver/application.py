from wsgiref.simple_server import make_server

from pyramid.config import Configurator

def main():
    config = Configurator(settings = {'pyramid.reload_templates':True})
    
    #Add server view
    config.add_route('serverView', '/server/{serverName}')
    config.add_route('serverEdit', '/server/{serverName}/edit')
    config.add_route('pduEdit', '/pdu/{pduName}/edit')
    config.add_route('testerEdit', '/tester/{testerName}/edit')
    config.add_route('controllerEdit', '/controller/{controllerName}/edit')
    config.add_route('servers_outlet_add_list_view', '/server/{serverName}/outletCreate')
    config.add_route('servers_test_add_list_view', '/server/{serverName}/testCreate')
    config.add_route('servers_control_add_list_view', '/server/{serverName}/controlCreate')    
    config.add_route('servers_outletCreate_view', '/server/{serverName}/outletCreate/{PDU}')
    config.add_route('servers_testCreate_view', '/server/{serverName}/testCreate/{tester}')
    config.add_route('servers_controlCreate_view', '/server/{serverName}/controlCreate/{controller}')
    config.add_route('servers_outletEdit_view', '/server/{serverName}/outlet/{outlet}/edit')
    config.add_route('servers_testEdit_view', '/server/{serverName}/test/{test}/edit')
    config.add_route('servers_controlEdit_view', '/server/{serverName}/control/{control}/edit')
    config.add_route('pduCreate', '/pduCreate/{pduType}')
    config.add_route('testerCreate', '/testerCreate/{testerType}')
    config.add_route('controllerCreate', '/controllerCreate/{controllerType}')
    
    config.scan("views")
    config.add_static_view('static', 'static/',
                           cache_max_age=86400)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8000, app)
    server.serve_forever()