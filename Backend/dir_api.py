import logging, os, sys

import asyncio, asyncpg
import aiohttp_sqlalchemy as ahsa

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine

from db_model import metadata
from nativeApp_DAL import nativeApp_DAL


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("API_URL_PREFIX")
DB_URI = str(os.getenv("API_DB_CONNECTION_STRING"))
DB_MAX_CONNECTIONS = int(os.getenv("API_DB_MAX_CONNECTIONS"))
DB_POOL_RECYCLE = int(os.getenv("API_DB_POOL_RECYCLE"))
DB_MAX_OVERFLOW = int(os.getenv("API_DB_MAX_OVERFLOW"))
DB_POOL_TIMEOUT = int(os.getenv("API_DB_POOL_TIMEOUT"))


#########################################################################
### API CLASS ###
class API_Server():
    """
    API_Server class controls the behaviour of API server
    """
    
    # Configure routes table and all available methods
    routes = web.RouteTableDef()

    # Healthcheck
    @routes.get('/healthz')
    async def health_check(request):
        log.info("Api test running\n")
        return web.Response(text="## API test successfull ##\n")
    

    @routes.get('/find_objects')
    async def find_objects(request):
        log.info("## Find objects function called ##")
        try:
            if nativeApp_DAL.find_objects() == True:
                return web.json_response({"status": 200, "messsage": "GET /find_objects successfull"})
            else:
                return web.json_response({"status": 500, "messsage": "GET /find_objects failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! GET /find_objects failed !!")

    @routes.get('/insert_object')
    async def insert_object(request):
        log.info("## Insert object function called ##")
        try:
            if nativeApp_DAL.insert_object() == True:
                return web.json_response({"status": 200, "messsage": "GET /insert_object successfull"})
            else:
                return web.json_response({"status": 500, "messsage": "GET /insert_object failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! GET /insert_object failed !!")

    
    @routes.get('/pack_object')
    async def pack_object(request):
        log.info("## Pack object function called ##")
        try:
            if nativeApp_DAL.pack_object() == True:
                return web.json_response({"status": 200, "messsage": "GET /pack_object successfull"})
            else:
                return web.json_response({"status": 500, "messsage": "GET /pack_object failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! GET /pack_object failed !!")
        
    
    @routes.get('/stop')
    async def stop(request):
        log.info("## Stop function called ##")
        #TODO insert code from nativeApp/main.py and generate a status response, so either 200 or 500
        try:
            if nativeApp_DAL.stop() == True:
                return web.json_response({"status": 200, "messsage": "GET /stop successfull"})
            else:
                return web.json_response({"status": 500, "messsage": "GET /stop failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! GET /stop failed !!")
    
    
    @routes.get('/scan_qr')
    async def scan_qr(request):
        log.info("## Scan QR function called ##")
        #TODO insert code from nativeApp/main.py and generate a status response, so either 200 or 500
        try:
            if nativeApp_DAL.scan_qr() == True:
                return web.json_response({"status": 200, "messsage": "GET /scan_qr successfull"})
            else:
                return web.json_response({"status": 500, "messsage": "GET /scan_qr failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! GET /scan_qr failed !!")
    
    ############################################################################################################################################
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

        log.info("Configuring API SQLAlchemy engine")
        self.subapp['engine'] = create_async_engine(DB_URI, 
                                                    echo = (False if APP_CONFIG == 'prod' else True),
                                                    connect_args={"server_settings": {"jit": "off"}},
                                                    pool_pre_ping=True, 
                                                    pool_size=DB_MAX_CONNECTIONS,
                                                    pool_recycle=DB_POOL_RECYCLE,
                                                    max_overflow=DB_MAX_OVERFLOW,
                                                    pool_timeout=DB_POOL_TIMEOUT)
        
        log.info("Binding SQLAlchemy engine to application object")
        ahsa.setup(self.subapp, [ahsa.bind(DB_URI)])

        log.info("Creating DB tables")
        await ahsa.init_db(self.subapp, metadata)

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add sub-app to set the IP/recognition-api request
        self.app = web.Application()
        self.app.add_subapp(URL_PREFIX, self.subapp)

        log.info("API initialization complete")

    # Run API
    def start_server(self, host, port, loop):
        log.info("Server starting on address: http://{}:{}".format(host, port))
        web.run_app(self.app, host=host, port=port, loop=loop)


if __name__ == '__main__':
    # Set up operation mode for server
    if APP_CONFIG == 'dev':
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        DB_MAX_CONNECTIONS = 10
        DB_POOL_RECYCLE = 3600
        DB_MAX_OVERFLOW = 0
        DB_POOL_TIMEOUT = 60
        log = logging.getLogger()
        log.info("Running in development config")

    elif APP_CONFIG == 'prod':
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Running in production config")

    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable APP_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(APP_CONFIG))
        sys.exit(1)

    # Get asyncio loop
    loop = asyncio.get_event_loop()

    # Create WebServer object and initialize it
    server = API_Server()
    loop.run_until_complete(server.initialize())

    # Start the server
    server.start_server(host='0.0.0.0', port=5000, loop=loop)
