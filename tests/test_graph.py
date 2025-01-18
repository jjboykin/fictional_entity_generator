import unittest
import os, sys
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)

from graph import Graph

class TestGraph(unittest.TestCase):
    test_cases = [
        (
            [
                (0, 1),
                (2, 0),
            ],
            (
                [
                    (1, 0),
                    (1, 2),
                    (2, 0),
                ],
                [True, False, True],
            ),
        ),
        (
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 5),
            ],
            (
                [
                    (0, 1),
                    (1, 2),
                    (0, 4),
                    (2, 5),
                    (5, 0),
                ],
                [True, True, False, False, False],
            ),
        ),
        (
            [
                (0, 1),
                (2, 4),
                (2, 1),
                (3, 1),
                (4, 5),
            ],
            (
                [
                    (5, 4),
                    (1, 5),
                    (0, 4),
                    (2, 5),
                    (1, 3),
                ],
                [True, False, False, False, True],
            ),
        ),
    ]

    def test_edges(self):
        for test_case in self.test_cases:
            edges_to_add, edges_to_check = test_case
            graph = Graph()
            for edge in edges_to_add:
                graph.add_edge(edge[0], edge[1])
            try:
                actual = []
                for i, edge in enumerate(edges_to_check[0]):
                    exists = graph.edge_exists(edge[0], edge[1])
                    actual.append(exists)
                self.assertEqual(
                    actual,
                    edges_to_check[1],
                )
            except Exception as e:
                return False        
    
if __name__ == "__main__":
    unittest.main()