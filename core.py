import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC, time
import os

from simple_plugin_loader import Loader
from simple_plugin_loader.sample_plugin import SamplePlugin
import structlog
import yaml

logger = structlog.get_logger()


@dataclass
class Payload:
    callsign: str
    payload_id: int
    time: time
    latitude: float
    longitude: float
    altitude: float
    temperature: float
    sats: int
    battery: float
    pressure: float
    speed: float
    ascent_rate: float
    other_fields: dict
    recieved_at: datetime = datetime.now(UTC)


class PluginBase:
    def __init__(self, config, core, loop):
        self.config = config
        self.core = core
        self.logger = logger.bind(plugin=self.__class__.__name__)
        self.loop = loop

    async def start(self):
        self.logger.info("Starting plugin with config", config=self.config)

    async def output(self, payload: Payload):
        self.logger.info("Outputting payload", payload=payload)

    def run(self):
        self.logger.info("Running plugin with config", config=self.config)


class ForgivingTaskGroup(asyncio.TaskGroup):
    _abort = lambda self: None


class Core:
    def __init__(self, config, loop):
        self.config = config
        self.input_plugins = []
        self.output_plugins = []
        self.loop = loop

    def load_plugins(self):
        loader = Loader()
        input_plugins = loader.load_plugins(
            "input", PluginBase, self.config["input_plugins"]
        )
        for k, v in input_plugins.items():
            logger.info("Loading input plugin", plugin=k)
            self.input_plugins.append(v(self.config.get(k), self, self.loop))
        output_plugins = loader.load_plugins(
            "output", PluginBase, self.config["output_plugins"]
        )
        for k, v in output_plugins.items():
            logger.info("Loading output plugin", plugin=k)
            self.output_plugins.append(v(self.config.get(k), self, self.loop))

    async def init_plugins(self):
        async with asyncio.TaskGroup() as tg:
            for plugin in self.input_plugins + self.output_plugins:
                tg.create_task(plugin.start())

    async def receive_payload(self, payload: Payload):
        logger.info("Received payload", payload=payload)
        try:
            async with ForgivingTaskGroup() as tg:
                for plugin in self.output_plugins:
                    tg.create_task(plugin.output(payload))
        except ExceptionGroup as eg:
            for err in eg.exceptions:
                logger.error("Error processing payload", error=str(err))

    def run(self):

        self.load_plugins()
        asyncio.run(self.init_plugins())

        logger.info("Running core with config", config=self.config)
        self.loop.run_forever()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)
    with open(os.environ.get("CONFIG", "config.yml  "), "r") as file:
        config = yaml.safe_load(file)
    core = Core(config, loop)
    core.run()
