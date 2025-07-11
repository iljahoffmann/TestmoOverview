from collections.abc import Callable, Sequence, Mapping
from typing import Any, Union, List

# Define types for terminal JSON values and general JSON nodes
JsonValueType = Union[str, int, float, bool, None]
JsonNodeType = Union[JsonValueType, Mapping, Sequence]


class JsonCursor:
    """
    A class for navigating and querying JSON-like structures (dicts and lists).

    Features:
    - Track and return current path in the JSON tree
    - Access dict keys with dot notation
    - Index into lists safely
    - Extract terminal values
    - Recursively search the JSON tree
    - Visit all nodes in the JSON tree with entry/exit callbacks
    """

    def __init__(self, node: JsonNodeType, path: List[Union[str, int]] = None):
        """
        Initialize the JsonCursor.

        Args:
            node: The current JSON node.
            path: The path from the root to this node.
        """
        self.node = node
        self.path = path or []

    def __getattr__(self, name: str) -> 'JsonCursor':
        """
        Access a child node by dictionary key using attribute access.

        Args:
            name: The key name to access in the current dict node.

        Returns:
            A new JsonCursor pointing to the child node.

        Raises:
            AttributeError: If the node is not a dict or the key is missing.
        """
        if isinstance(self.node, dict):
            if name in self.node:
                return JsonCursor(self.node[name], self.path + [name])
            raise AttributeError(f"Key '{name}' not found in current node")
        raise AttributeError("Current node is not a JSON object (dict)")

    def __getitem__(self, index: int) -> 'JsonCursor':
        """
        Access a child node by list index.

        Args:
            index: The index to access in the current list node.

        Returns:
            A new JsonCursor pointing to the indexed element.

        Raises:
            IndexError: If the index is out of bounds.
            TypeError: If the current node is not a list.
        """
        if isinstance(self.node, list):
            if 0 <= index < len(self.node):
                return JsonCursor(self.node[index], self.path + [index])
            raise IndexError("List index out of range")
        raise TypeError("Current node is not a JSON array (list)")

    def value(self) -> JsonValueType:
        """
        Return the terminal value of the current node.

        Returns:
            The value at the current node.

        Raises:
            TypeError: If the node is not a terminal value.
        """
        if isinstance(self.node, (dict, list)):
            raise TypeError("Current node is not a terminal JSON value")

        return self.node

    def search(self, predicate: Callable[['JsonCursor'], bool]) -> Union['JsonCursor', None]:
        """
        Recursively search the JSON tree for a node matching a predicate.

        Args:
            predicate: A callable that returns True if a node matches the condition.

        Returns:
            A JsonCursor pointing to the matching node, or None if not found.
        """
        # This should use visit - right? Well... no. The visit handler's result is already used for pruning and
        # visit normally returns nothing in any case, because there's no good generic return type afaik.
        def _recursive_search(cursor: 'JsonCursor') -> Union['JsonCursor', None]:
            if predicate(cursor):
                return cursor

            if isinstance(cursor.node, Mapping):
                pass
                for key, value in cursor.node.items():
                    result = _recursive_search(JsonCursor(value, cursor.path + [key]))
                    if result:
                        return result

            elif isinstance(cursor.node, Sequence) and not isinstance(cursor.node, (str, bytes, bytearray)):
                for index, item in enumerate(cursor.node):
                    result = _recursive_search(JsonCursor(item, cursor.path + [index]))
                    if result:
                        return result

            return None

        return _recursive_search(self)

    def visit(self, handler: Callable[['JsonCursor', bool], Any]) -> None:
        """
        Recursively visit every node in the JSON tree.

        Calls the handler twice for each container-node
        - First with entering=True before visiting children
        - Then with entering=False after visiting children
        For value-nodes, the handler just get called once with entering=True.

        If the handler returns _exactly_ False on the entering call, the node's children
        are not visited and the exiting call is also skipped.

        Args:
            handler: A function that accepts (JsonCursor, entering).
        """
        def _recursive_visit(cursor: 'JsonCursor') -> None:
            continue_descent = handler(cursor, True)
            if continue_descent is False:
                return

            descended = False
            if isinstance(cursor.node, Mapping):
                descended = True
                for key, value in cursor.node.items():
                    _recursive_visit(JsonCursor(value, cursor.path + [key]))

            elif isinstance(cursor.node, Sequence) and not isinstance(cursor.node, (str, bytes, bytearray)):
                descended = True
                for index, item in enumerate(cursor.node):
                    _recursive_visit(JsonCursor(item, cursor.path + [index]))

            if descended:
                handler(cursor, False)

        _recursive_visit(self)

    def get_path(self) -> List[Union[str, int]]:
        """
        Get the path from the root to the current node.

        Returns:
            A list of keys and/or indices representing the path.
        """
        return self.path

    def on_dict(self):
        """
        Return True, if the current node is a Mapping (i.e. a dict)
        """
        return isinstance(self.node, Mapping)

    def on_list(self):
        """
        Return True, if the current node is a Sequence (i.e. a list), but not if it is a string- or byte-container.
        """
        n = self.node
        return isinstance(n, Sequence) and not isinstance(n, (str, bytes, bytearray))

    def on_data(self):
        return not (self.on_dict() or self.on_list())

    def __repr__(self):
        """
        Developer-friendly string representation showing current node and path.
        """
        return f"<JsonCursor node={self.node!r} path={self.path}>"


def main():
    data = [{
        "user": {
            "name": "Alice",
            "age": 30,
            "emails": ["alice@example.com", "a.smith@example.com"]
        },
        "active": True
    }]

    cursor = JsonCursor(data)

    # Accessing attributes
    name_cursor = cursor[0].user.name
    print("User name:", name_cursor.value())
    print("Path to name:", name_cursor.get_path())

    # Accessing array items
    first_email_cursor = cursor[0].user.emails[0]
    print("First email:", first_email_cursor.value())
    print("Path to first email:", first_email_cursor.get_path())

    # Searching
    def is_age_node(c: JsonCursor):
        return c.value() == 30 if isinstance(c.node, (int, float)) else False

    age_cursor = cursor[0].user.search(is_age_node)
    print("Found age:", age_cursor.value() if age_cursor else "Not found")
    print("Path to age:", age_cursor.get_path() if age_cursor else "-")

    alice = cursor.search(lambda c: c.on_dict() and 'name' in c.node and c.node.get('name') == 'Alice')
    print("Alice:", alice)
    pass

if __name__ == "__main__":
    main()
