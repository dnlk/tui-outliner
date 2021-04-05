
from typing import *

from containers_ext import BijectiveMap
from enums import TreeLink
import func


Id = TypeVar('Id')
Link = TypeVar('Link')
Node = TypeVar('Node')


class UniqueNodeLinks(Generic[Id, Link]):

    node_links: BijectiveMap[Tuple[Id, Link], Id]

    def __init__(self):
        self.node_links = BijectiveMap()

    def add_link(self, previous_id: Id, _id: Id, link_type: Link):
        self.node_links.set_mapping((previous_id, link_type), _id)

    def get_previous(self, _id: Id) -> Optional[Tuple[Id, Link]]:
        return self.node_links.rget(_id)

    def get_closest_previous_of_type(self, _id: Id, link_type: Link) -> Optional[Id]:
        this_id = _id
        while previous := self.get_previous(this_id):
            this_id, this_link_type = previous
            if this_link_type == link_type:
                return this_id

    def get_next(self, _id: Id, link_type: Link) -> Optional[Id]:
        return self.node_links.lget((_id, link_type))

    def get_next_group_of_type(self, _id: Id, link_type: Link) -> List[Id]:
        group = []
        this_id = _id
        while (this_id := self.get_next(this_id, link_type)) is not None:
            group.append(this_id)
        return group

    def pop_previous_link(self, _id: Id) -> Optional[Tuple[Id, Link]]:
        return self.node_links.rpop(_id)

    def pop_next_link(self, _id: Id, link_type: Link) -> Optional[Id]:
        return self.node_links.lpop((_id, link_type))

    def switch_previous_node(self, _id: Id, new_previous_id: Id, new_link_type: Link):
        self.pop_previous_link(_id)
        self.add_link(new_previous_id, _id, new_link_type)

    def _insert_after(self, _id: Id, previous_id: Id, link_type: Link, bumped_link_type: Link):
        next_id = self.node_links.lpop((previous_id, link_type))
        self.add_link(previous_id, _id, link_type)
        if next_id is not None:
            self.add_link(_id, next_id, bumped_link_type)

    def _splice(self, _id: Id, link_type_to_patch_through: Optional[Link]):
        id_to_patch_through = None
        if link_type_to_patch_through:
            id_to_patch_through = self.node_links.lpop((_id, link_type_to_patch_through))
        previous_link = self.node_links.rpop(_id)
        if id_to_patch_through is not None and previous_link is not None:
            previous_id, previous_link_type = previous_link
            self.add_link(previous_id, id_to_patch_through, previous_link_type)

    def _move_after(
            self, _id: Id,
            link_type_to_patch_though: Optional[Link],
            previous_id: Id,
            link_type: Link,
            bumped_link_type: Link
    ):
        self._splice(_id, link_type_to_patch_though)
        self._insert_after(_id, previous_id, link_type, bumped_link_type)


class Tree(UniqueNodeLinks[Id, TreeLink]):
    def get_children(self, _id: Id) -> List[Id]:
        children = []
        first_child = self.get_next(_id, TreeLink.Parent)
        if first_child is not None:
            children.append(first_child)
            children.extend(self.get_next_group_of_type(first_child, TreeLink.Sibling))

        return children

    def get_parent(self, _id: Id) -> Id:
        return self.get_closest_previous_of_type(_id, TreeLink.Parent)

    def get_ancestors(self, _id: Id) -> List[Id]:
        return func.iterate(
            func=self.get_parent,
            exit_condition=lambda id_it: id_it is None,
            initial_value=_id,
            include_first=True,
            include_last=False
        )

    def get_depth_relative_to(self, _id: Id, ancestor_id: Id) -> int:
        ancestors = self.get_ancestors(_id)
        return ancestors.index(ancestor_id)

    def get_next_sibling(self, _id: Id) -> Id:
        return self.get_next(_id, TreeLink.Sibling)

    def get_next_uncle(self, _id: Id) -> Optional[Id]:
        """
        Funny method name. It tries to find the next sibling. Failing that, the parent's next sibling. Failing that,
        the grandparent's next sibling. Etc.
        """
        ancestors = self.get_ancestors(_id)
        for ancestor in ancestors:
            if next_sibling := self.get_next_sibling(ancestor):
                return next_sibling

    def get_previous_sibling(self, _id: Id) -> Id:
        previous = self.get_previous(_id)
        if previous is not None:
            node_id, link_type = previous
            if link_type == TreeLink.Sibling:
                return node_id

    def get_first_child(self, _id: Id) -> Optional[Id]:
        return self.get_next(_id, TreeLink.Parent)

    def get_last_child(self, _id: Id) -> Optional[Id]:
        children = self.get_children(_id)
        if children:
            return children[-1]

    def insert_after(self, _id: Id, previous_id: Id, link_type: Link) -> None:
        bumped_link_type = TreeLink.Sibling
        self._insert_after(_id, previous_id, link_type, bumped_link_type)

    def splice(self, _id: Id) -> None:
        link_type_to_patch_through = TreeLink.Sibling
        self._splice(_id, link_type_to_patch_through)

    def move_after(self, _id: Id, previous_id: Id, link_type: Link) -> None:
        link_type_to_patch_though = TreeLink.Sibling
        bumped_link_type = TreeLink.Sibling
        self._move_after(_id, link_type_to_patch_though, previous_id, link_type, bumped_link_type)

    def move_after_as_sibling(self, _id: Id, previous_id: Id):
        self.move_after(_id, previous_id, TreeLink.Sibling)

    def move_after_as_child(self, _id: Id, parent_id: Id):
        self.move_after(_id, parent_id, TreeLink.Parent)


class Nodes(Dict[Id, Node]):
    def __setitem__(self, key, value):
        assert key not in self
        return super().__setitem__(key, value)


class NodeContext(Generic[Id, Node]):
    id: Id
    node: Node
    previous_id: Id
    link_type: TreeLink

    def __init__(self, _id: Id, node: Node, previous_id: Id, link_type: TreeLink):
        self.id = _id
        self.node = node
        self.previous_id = previous_id
        self.link_type = link_type


class NodeTree(Generic[Id, Node]):

    tree: Tree[Id]
    nodes: Nodes[Id, Node]

    def __init__(self, node_data: Optional[Iterable[NodeContext[Id, Node]]]=None):
        self.tree = Tree()
        self.nodes = Nodes()

        if node_data is not None:
            self._init_nodes(node_data)

    def _init_nodes(self, nodes: Iterable[NodeContext[Id, Node]]):
        for node_context in nodes:
            self.add_node(node_context)

    def get_node(self, _id: Id) -> Optional[Node]:
        return self.nodes.get(_id)

    def add_orphan_node(self, _id: Id, node: Node):
        self.nodes[_id] = node

    def add_node(self, node_context: NodeContext):
        self.add_orphan_node(node_context.id, node_context.node)
        self.tree.add_link(node_context.previous_id, node_context.id, node_context.link_type)

    def add_node_as_next_sibling(self, _id: Id, node: Node, sibling_id: Id):
        node_context = NodeContext[Id, Node](_id, node, sibling_id, TreeLink.Sibling)
        self.add_node(node_context)

    def add_node_as_first_child(self, _id: Id, node: Node, parent_id: Id):
        node_context = NodeContext[Id, Node](_id, node, parent_id, TreeLink.Parent)
        self.add_node(node_context)

    def insert_node(self, node_context: NodeContext):
        self.add_orphan_node(node_context.id, node_context.node)
        self.tree.move_after(node_context.id, node_context.previous_id, node_context.link_type)

    def delete_node(self, _id: Id):
        self.tree.splice(_id)
        self.nodes.pop(_id)

    def print_tree(self, _id, left_padding=''):
        node = self.nodes[_id]
        print(left_padding, _id, node)
        for child in self.tree.get_children(_id):
            self.print_tree(child, left_padding + '  ')
