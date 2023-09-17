from fastapi import FastAPI

from etl import launch_etl
from routes import router


class App(FastAPI):
    def register_routeers(self):
        self.include_router(router)


def start_application():
    launch_etl()
    return App()


app = start_application()