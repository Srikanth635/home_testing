import ast
import os
import networkx as nx
import matplotlib.pyplot as plt

def get_class_dependencies(filepath, module_name, class_map):
    """Extracts class dependencies from a Python file."""
    dependencies = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except FileNotFoundError:
        return dependencies

    class DependencyVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_class = None

        def visit_ClassDef(self, node):
            self.current_class = f"{module_name}.{node.name}"
            class_map[self.current_class] = node
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in class_map:
                    dependencies.add(class_map[base.id])

            self.generic_visit(node)
            self.current_class = None

        def visit_Name(self, node):
            if self.current_class and node.id in class_map:
                dependencies.add(class_map[node.id])
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if self.current_class and isinstance(node.value, ast.Name) and node.value.id in class_map:
              dependencies.add(class_map[node.value.id])
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                if alias.name in class_map:
                  dependencies.add(class_map[alias.name])
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module:
                if node.module in class_map:
                    dependencies.add(class_map[node.module])

            for alias in node.names:
                if node.module and f"{node.module}.{alias.name}" in class_map:
                   dependencies.add(class_map[f"{node.module}.{alias.name}"])
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            if self.current_class and isinstance(node.annotation, ast.Name) and node.annotation.id in class_map:
                dependencies.add(class_map[node.annotation.id])
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if self.current_class:
                for arg in node.args.args:
                    if arg.annotation and isinstance(arg.annotation, ast.Name) and arg.annotation.id in class_map:
                        dependencies.add(class_map[arg.annotation.id])
                if node.returns and isinstance(node.returns, ast.Name) and node.returns.id in class_map:
                    dependencies.add(class_map[node.returns.id])
            self.generic_visit(node)

    visitor = DependencyVisitor()
    visitor.visit(tree)
    return dependencies

def build_class_dependency_graph(root_dir):
    """Builds a class dependency graph."""
    graph = nx.DiGraph()
    class_map = {} # class name -> class node
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                module_name = os.path.splitext(os.path.relpath(filepath, root_dir))[0].replace(os.sep, '.')
                get_class_dependencies(filepath, module_name, class_map)

    for class_name, node in class_map.items():
        graph.add_node(class_name)

    for module_name, node in class_map.items():
        dependencies = get_class_dependencies(os.path.join(root_dir, module_name.replace('.', os.sep) + ".py"), module_name, class_map)
        for dependency in dependencies:
            graph.add_edge(module_name, dependency)

    return graph

# Example Usage
project_dir = '/home/malineni/VC_Pools/cram_pycram'
if os.path.isdir(project_dir):
    class_dependency_graph = build_class_dependency_graph(project_dir)

    # Visualize the graph (requires matplotlib and networkx)

    nx.draw(class_dependency_graph, with_labels=True, node_size=1500, node_color="skyblue", arrowstyle='->', arrowsize=20)
    plt.show()
else:
    print(f"Directory '{project_dir}' not found.")