import copy
from operator import ne
import typing
import xml.etree.cElementTree as cET

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

from automaton.base_automaton import AbstractAutomaton, AbstractState

_T = typing.TypeVar("_T", bound="AbstractState")

class RenderedAutomaton(typing.Generic[_T]):
    def __init__(self, automaton: AbstractAutomaton[_T]) -> None:
        graph = nx.DiGraph()
        self.automaton = automaton

        visited_nodes = []

        def recursive_visit(node: AbstractState):
            if node.my_number in visited_nodes:
                return

            visited_nodes.append(node.my_number)
            if node.is_accepting:
                graph.add_node(node.my_number, id=f"node{node.my_number}", shape="doublecircle", width="0.5", fixedsize="true")
            else:
                graph.add_node(node.my_number, id=f"node{node.my_number}", shape="circle", width="0.75", fixedsize="true")

            reorganized_transitions: typing.Dict[AbstractState, typing.Dict[str, typing.Optional[str]]] = {}

            for key, value in node.transitions.items():
                next_node = value[0]
                recursive_visit(next_node)

                if next_node in reorganized_transitions:
                    reorganized_transitions[next_node][key] = value[1]
                else:
                    reorganized_transitions[next_node] = {key: value[1]}

            for next_node in reorganized_transitions:
                # combines input and output strings with "->" and combines all those strings with "\n"
                edge_label = "\\n".join(" " + ("->".join(str(b) for b in a) if a[1] else a[0]) + " " for a in reorganized_transitions[next_node].items())
                graph.add_edge(node.my_number, next_node.my_number, label=edge_label, id=f"edge{node.my_number}-{next_node.my_number}")

        recursive_visit(automaton.initial_state)

        agraph = to_agraph(graph)
        agraph.layout(prog="fdp")
        self.xml_root = cET.fromstring(agraph.draw(format="svg").decode('utf-8'))

    def render_step(self, transition: typing.Optional[str] = None) -> bytes:
        ns = {"ns":self.xml_root.tag.split("}")[0].strip("{")}
        dupe_xml = copy.deepcopy(self.xml_root)

        if not self.automaton.current_state:
            raise Exception("Transition render failure!")

        if not transition:
            dupe_xml.findall(f".//*[@id='node{self.automaton.current_state.my_number}']/ns:ellipse",ns)[0].attrib["stroke"] = "red"
            dupe_xml.findall(f".//*[@id='node{self.automaton.current_state.my_number}']/ns:text",ns)[0].attrib["fill"] = "red"
        else:
            target_node = self.automaton.current_state.transitions[transition][0]
            target_edge = str(self.automaton.current_state.my_number) + "-" + str(target_node.my_number)
            dupe_xml.findall(f".//*[@id='edge{target_edge}']/ns:path",ns)[0].attrib["stroke"] = "red"
            dupe_xml.findall(f".//*[@id='edge{target_edge}']/ns:polygon",ns)[0].attrib["stroke"] = "red"
            dupe_xml.findall(f".//*[@id='edge{target_edge}']/ns:polygon",ns)[0].attrib["fill"] = "red"
            dupe_xml.findall(f".//*[@id='edge{target_edge}']/ns:text",ns)[0].attrib["fill"] = "red"

        return cET.tostring(dupe_xml)