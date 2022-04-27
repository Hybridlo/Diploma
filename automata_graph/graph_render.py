import typing
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

from automaton.base_automaton import AbstractAutomaton, AbstractState

_T = typing.TypeVar("_T", bound="AbstractAutomaton")

class RenderedAutomaton(typing.Generic[_T]):
    def __init__(self, automaton: _T) -> None:
        self.graph = nx.DiGraph()
        self.automaton = automaton

        visited_nodes = []

        def recursive_visit(node: AbstractState):
            if node.my_number in visited_nodes:
                return

            visited_nodes.append(node.my_number)
            self.graph.add_node(node.my_number)

            for key, value in node.transitions.items():
                next_node = value[0]
                recursive_visit(next_node)

                self.graph.add_edge(node.my_number, next_node.my_number, label=f" {key}{'/'+value[1] if value[1] else ''} ")

        recursive_visit(automaton.initial_state)

    def render(self, transition: typing.Optional[str] = None) -> typing.List[bytes]:
        dupe_graph = self.graph.copy()

        result: typing.List[bytes] = []

        if not self.automaton.current_state:
            raise Exception("Transition render failure!")

        nx.set_node_attributes(dupe_graph, {self.automaton.current_state.my_number: {'color': 'red', 'fontcolor': 'red'}})

        # render graph pic for active state
        agraph = to_agraph(dupe_graph)
        agraph.layout(prog="fdp")
        result.append(agraph.draw(format="png"))

        dupe_graph = self.graph.copy()

        if transition:
            target_node = self.automaton.current_state.transitions[transition][0]
            nx.set_edge_attributes(dupe_graph, {(self.automaton.current_state.my_number, target_node.my_number): {'color': 'red', 'fontcolor': 'red'}})

            # render pic for transition
            agraph = to_agraph(dupe_graph)
            agraph.layout(prog="fdp")
            result.append(agraph.draw(format="png"))

        return result