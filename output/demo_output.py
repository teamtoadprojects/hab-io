from core import PluginBase


class demo_output(PluginBase):
    def run(self):
        super().run()
        print("Demo plugin running with config: {}".format(self.config))
        return 42
