import time
from concurrent.futures import Executor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

from bonobo.core.bags import Bag
from bonobo.core.strategies.base import Strategy
from bonobo.util.tokens import Begin, End


class ExecutorStrategy(Strategy):
    """
    Strategy based on a concurrent.futures.Executor subclass (or similar interface).

    """

    executor_factory = Executor

    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_context(graph, plugins=plugins)
        executor = self.executor_factory()

        for i in graph.outputs_of(Begin):
            context[i].recv(Begin)
            context[i].recv(Bag())
            context[i].recv(End)

        futures = []

        for plugin_context in context.plugins:
            futures.append(executor.submit(plugin_context.run))

        for component_context in context.components:
            futures.append(executor.submit(component_context.run))

        while context.running:
            time.sleep(0.2)

        for plugin_context in context.plugins:
            plugin_context.shutdown()

        executor.shutdown()

        #for component_context in context.components:
        #    print(component_context)


class ThreadPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ThreadPoolExecutor


class ProcessPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ProcessPoolExecutor
