import logging, os, sys
import asyncio

from aiohttp import web, ClientSession

# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("WEB_URL_PREFIX")
API_CONNECTION_STRING = os.getenv("API_WEB_CONNECTION_STRING")


class WebService():
    """
        Frontend class controls routes the frontend requests to backend API 
    """

    # Configure rotes table and all available methods
    routes = web.RouteTableDef()

    # Index webpage
    @routes.get('/dashboard')
    async def uploadPage(request):
        return web.FileResponse("./web/dashboard.html")

    # Find objects
    @routes.post('/find_objects')
    async def find_objects(request):
        log.info("## Find objects function called ##")
        try:
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/find_objects") as response:
                    if response.status == 200:
                        return web.json_response({"status": 200, "messsage": "POST /find_objects successfull"})
                    else:
                        return web.json_response({"status": 500, "messsage": "POST /find_objects failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! POST /find_objects failed !!")
    
    # Insert object
    @routes.post('/insert_object')
    async def insert_object(request):
        log.info("## Insert object function called ##")
        try:
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/insert_object") as response:
                    if response.status == 200:
                        return web.json_response({"status": 200, "messsage": "POST /insert_object successfull"})
                    else:
                        return web.json_response({"status": 500, "messsage": "POST /insert_object failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! POST /insert_object failed !!")

    # Pack object
    @routes.post('/pack_object')
    async def pack_object(request):
        log.info("## Pack object function called ##")
        try:
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/pack_object") as response:
                    if response.status == 200:
                        return web.json_response({"status": 200, "messsage": "POST /pack_object successfull"})
                    else:
                        return web.json_response({"status": 500, "messsage": "POST /pack_object failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! POST /pack_object failed !!")

    # Stop
    @routes.post('/stop')
    async def stop(request):
        log.info("## Stop function called ##")
        try:
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/stop") as response:
                    if response.status == 200:
                        return web.json_response({"status": 200, "messsage": "POST /stop successfull"})
                    else:
                        return web.json_response({"status": 500, "messsage": "POST /stop failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! POST /stop failed !!")
        
    # Scan QR code
    @routes.post('/scan_qr_code')
    async def scan_qr_code(request):
        log.info("## Scan QR code function called ##")
        try:
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/scan_qr_code") as response:
                    if response.status == 200:
                        return web.json_response({"status": 200, "messsage": "POST /scan_qr_code successfull"})
                    else:
                        return web.json_response({"status": 500, "messsage": "POST /scan_qr_code failed in DAL"})
        except:
            raise web.HTTPInternalServerError("!! POST /scan_qr_code failed !!")

    ############################################################################################################################################
    ############################################################################################################################################
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add global upload chunk array to application object
        self.subapp['uploadChunkedList'] = []

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
    server = WebService()
    loop.run_until_complete(server.initialize())

    # Start the server
    server.start_server(host='0.0.0.0', port=4000, loop=loop)