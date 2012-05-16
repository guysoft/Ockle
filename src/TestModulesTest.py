from straight.plugin import load
import serviceTesters.TemplateTester

TEST_MODULES_DIR ="serviceTesters"
pluginLoadList=["PingTester"]



class Main():
    def __init__(self):
        self.plugins = []
        plugins = load(TEST_MODULES_DIR,subclasses=serviceTesters.TemplateTester.TemplateTester)
        print plugins
        for plugin in plugins:
            if plugin.__name__ in pluginLoadList:
                self.plugins.append(plugin(self))
        
        for plugin in self.plugins:
            plugin.test()

if __name__ == "__main__":
    a = Main()