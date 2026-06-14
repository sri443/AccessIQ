import networkx as nx
from typing import Dict, Any, List
from app.services.data_processor import DataProcessor

class IdentityGraph:
    def __init__(self): self.graph = nx.Graph()

    def build_graph(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.graph = nx.Graph(); nodes = []; edges = []
        systems_set = set(); departments_set = set(); roles_set = set()

        for user in users:
            user_id = user['id']; user_systems = user.get('systems', []); department = user.get('department', ''); role = user.get('role', '')
            
            self.graph.add_node(user_id, type='user', label=user.get('name', user_id))
            nodes.append({'id': user_id, 'type': 'user', 'label': user.get('name', user_id), 'risk_level': user.get('risk_level', 'Low')})

            if department:
                dept_id = f"dept_{department}"
                if dept_id not in departments_set:
                    departments_set.add(dept_id)
                    self.graph.add_node(dept_id, type='department', label=department)
                    nodes.append({'id': dept_id, 'type': 'department', 'label': department})
                self.graph.add_edge(user_id, dept_id, type='belongs_to')
                edges.append({'source': user_id, 'target': dept_id, 'type': 'belongs_to'})

            if role:
                role_id = f"role_{role}"
                if role_id not in roles_set:
                    roles_set.add(role_id)
                    self.graph.add_node(role_id, type='role', label=role)
                    nodes.append({'id': role_id, 'type': 'role', 'label': role})
                self.graph.add_edge(user_id, role_id, type='has_role')
                edges.append({'source': user_id, 'target': role_id, 'type': 'has_role'})

            expected_systems = DataProcessor.get_expected_systems(role)
            for system in user_systems:
                sys_id = f"sys_{system}"
                if sys_id not in systems_set:
                    systems_set.add(sys_id)
                    self.graph.add_node(sys_id, type='system', label=system)
                    nodes.append({'id': sys_id, 'type': 'system', 'label': system})
                
                edge_type = 'unexpected_access' if system not in expected_systems else 'standard_access'
                self.graph.add_edge(user_id, sys_id, type=edge_type)
                edges.append({'source': user_id, 'target': sys_id, 'type': edge_type, 'anomalous': system not in expected_systems})

        return {'nodes': nodes, 'edges': edges}

    def get_user_subgraph(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.graph: return {'nodes': [], 'edges': []}
        subgraph = nx.ego_graph(self.graph, user_id, radius=2)
        nodes = [{'id': n, 'type': self.graph.nodes[n].get('type', 'unknown'), 'label': self.graph.nodes[n].get('label', n)} for n in subgraph.nodes()]
        edges = [{'source': u, 'target': v, 'type': d.get('type', 'unknown'), 'anomalous': d.get('anomalous', False)} for u, v, d in subgraph.edges(data=True)]
        return {'nodes': nodes, 'edges': edges}