
from dataclasses import dataclass
from common_imports import *

from nodes.node_types import NodeId


@dataclass
class BreadCrumb:
    root_node_id: NodeId
    selected_node_id: NodeId


class NodePath:

    def __init__(self):
        self.node_ids: List[NodeId] = []
        self.breadcrumbs: List[BreadCrumb] = []

    def get_breadcrumb_path(self) -> List[NodeId]:
        return [bc.root_node_id for bc in self.breadcrumbs]

    def _truncate_after(self, node_id: NodeId):
        index = self.node_ids.index(node_id)
        self.node_ids = self.node_ids[:index + 1]

    def push(self, breadcrumb: BreadCrumb, node_ids: List[NodeId]):
        self.node_ids.extend(node_ids)
        self.breadcrumbs.append(breadcrumb)

    def pop(self) -> BreadCrumb:
        assert self.breadcrumbs
        last_breadcrumb = self.breadcrumbs.pop()
        self._truncate_after(last_breadcrumb.root_node_id)
        return last_breadcrumb
