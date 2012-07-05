from pyramid.config import Configurator
import akhet
import pyramid_beaker

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from hotp.models.model import groupfinder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # Here you can insert any code to modify the ``settings`` dict.
    # You can:
    # * Add additional keys to serve as constants or "global variables" in the
    #   application.
    # * Set default values for settings that may have been omitted.
    # * Override settings that you don't want the user to change.
    # * Raise an exception if a setting is missing or invalid.
    # * Convert values from strings to their intended type.

    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    # Create the Pyramid Configurator.
    config = Configurator(settings=settings,
                          root_factory='hotp.models.model.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy
                          )
    config.include("pyramid_handlers")
    config.include("akhet")


    # Configure Beaker sessions and caching
    session_factory = pyramid_beaker.session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    pyramid_beaker.set_cache_regions_from_settings(settings)

    # Configure renderers and event subscribers
    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    config.add_subscriber("hotp.subscribers.create_url_generator",
        "pyramid.events.ContextFound")
    config.add_subscriber("hotp.subscribers.add_renderer_globals",
                          "pyramid.events.BeforeRender")

    # Set up view handlers
    config.include("hotp.handlers")

    # Set up other routes and views
    # ** If you have non-handler views, create create a ``hotp.views``
    # ** module for them and uncomment the next line.
    #
    #config.scan("hotp.views")

    # Mount a static view overlay onto "/". This will serve, e.g.:
    # ** "/robots.txt" from "hotp/static/robots.txt" and
    # ** "/images/logo.png" from "hotp/static/images/logo.png".
    #
    config.add_static_route("hotp", "static", cache_max_age=3600)

    # Mount a static subdirectory onto a URL path segment.
    # ** This not necessary when using add_static_route above, but it's the
    # ** standard Pyramid way to serve static files under a URL prefix (but
    # ** not top-level URLs such as "/robots.txt"). It can also serve files from
    # ** third-party packages, or point to an external HTTP server (a static
    # ** media server).
    # ** The first commented example serves URLs under "/static" from the
    # ** "hotp/static" directory. The second serves URLs under 
    # ** "/deform" from the third-party ``deform`` distribution.
    #
    #config.add_static_view("static", "hotp:static")
    #config.add_static_view("deform", "deform:static")
    config.scan("hotp.handlers")

    return config.make_wsgi_app()
