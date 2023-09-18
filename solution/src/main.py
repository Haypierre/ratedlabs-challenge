from fastapi import FastAPI

from src.etl import launch_etl
from src.routes import router


class App(FastAPI):
    def register_routers(self):
        self.include_router(router)


def start_application():
    launch_etl()
    return App()


app = start_application()
app.register_routers()
