import random

import pytest

from dsa.graphs.analysis.traversal.dijkstra import dijkstra
from dsa.graphs.analysis.traversal.order import Order
from dsa.graphs.graph import Graph
from dsa.graphs.graph_factory import GraphFactory

# TODO why is this so slow with 2**big_number
MAX_TEST_GRAPH_SIZE = 2**8


@pytest.mark.parametrize("use_approach_1", (True, False))
def test_dijkstra(use_approach_1: bool) -> None:
    # non-comparable nodes
    g = Graph(nodes=(12, "blah"), edges=((12, "blah"),))
    with pytest.raises(TypeError):
        dijkstra(g, use_approach_1=use_approach_1, seed_order=Order.SORTED)

    ### simple graphs

    # empty graph
    g = Graph()
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1
    )
    assert parents == {}
    assert dists == {}
    assert distorder == []
    assert ccs == []
    assert not contains_cycle

    # singleton graph
    g = Graph(nodes=1)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1
    )
    assert parents == {0: None}
    assert dists == {0: 0}
    assert distorder == [0]
    assert ccs == [[0]]
    assert not contains_cycle

    # generally: n nodes, 0 edges
    for n in (2, 3, random.randint(4, MAX_TEST_GRAPH_SIZE)):
        g = Graph(nodes=n)
        # seeds in sorted order
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g, use_approach_1=use_approach_1, seed_order=Order.SORTED
        )
        assert parents == {u: None for u in range(n)}
        assert dists == {u: 0 for u in range(n)}
        assert distorder == list(range(n)), n
        assert ccs == [[i] for i in range(n)]
        assert not contains_cycle
        # seeds in reverse sorted order
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g, use_approach_1=use_approach_1, seed_order=Order.REVERSE_SORTED
        )
        assert parents == {u: None for u in range(n)}
        assert dists == {u: 0 for u in range(n)}
        assert distorder == list(range(n - 1, -1, -1)), n
        assert ccs == [[i] for i in range(n - 1, -1, -1)]
        assert not contains_cycle

    ### spindly trees

    # generally: n node spindly tree, same as BFS
    for n in (2, 3, random.randint(4, MAX_TEST_GRAPH_SIZE)):
        g = GraphFactory.create_spindly_tree(n)
        # in sorted order
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g, use_approach_1=use_approach_1, seed_order=Order.SORTED
        )
        assert parents == {0: None, **{u: u - 1 for u in range(1, n)}}
        assert dists == {u: u for u in range(0, n)}
        assert distorder == list(range(n)), n
        assert ccs == [distorder]
        assert not contains_cycle
        # in reverse sorted order
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g, use_approach_1=use_approach_1, seed_order=Order.REVERSE_SORTED
        )
        assert parents == {n - 1: None, **{u: u + 1 for u in range(n - 1)}}
        assert dists == {u: n - 1 - u for u in range(n)}
        assert distorder == list(range(n - 1, -1, -1)), n
        assert ccs == [distorder]
        assert not contains_cycle
        # branch from the middle
        dijkstra_root = random.randint(1, n - 1)
        to_left = list(range(dijkstra_root - 1, -1, -1))  # from middle to the left
        to_right = list(range(dijkstra_root + 1, n))  # from middle to the right
        # important that dijkstra_root is first; everything else is irrelevant
        # explore left then right
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g,
            use_approach_1=use_approach_1,
            seed_order=dijkstra_root,
            neighbor_order=Order.SORTED,
        )
        exp_parents = {
            dijkstra_root: None,
            **{u: u + 1 for u in range(dijkstra_root)},
            **{u: u - 1 for u in range(dijkstra_root + 1, n)},
        }
        exp_dists = {
            dijkstra_root: 0,
            **{u: dijkstra_root - u for u in range(dijkstra_root)},
            **{u: u - dijkstra_root for u in range(dijkstra_root + 1, n)},
        }
        assert parents == exp_parents
        assert dists == exp_dists
        exp_distorder = [dijkstra_root]
        for dist in range(1, len(g)):
            left, right = dijkstra_root - dist, dijkstra_root + dist
            if left in g:
                exp_distorder.append(left)
            if right in g:
                exp_distorder.append(right)
        assert distorder == exp_distorder
        assert ccs == [distorder]
        assert not contains_cycle
        # explore right then left
        parents, dists, distorder, ccs, contains_cycle = dijkstra(
            g,
            use_approach_1=use_approach_1,
            seed_order=dijkstra_root,
            neighbor_order=Order.REVERSE_SORTED,
        )
        assert parents == exp_parents
        assert dists == exp_dists
        exp_distorder = [dijkstra_root]
        for dist in range(1, len(g)):
            left, right = dijkstra_root - dist, dijkstra_root + dist
            if right in g:
                exp_distorder.append(right)
            if left in g:
                exp_distorder.append(left)
        assert distorder == exp_distorder
        assert ccs == [distorder]
        assert not contains_cycle

    ### binary trees

    # simple binary tree (see create_b_ary_tree docstring for example)
    g = GraphFactory.create_b_ary_tree(2, 2)
    # starting from 0, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    exp_parents = {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    assert parents == exp_parents
    exp_dists = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}
    assert dists == exp_dists
    assert distorder == [0, 1, 2, 3, 4, 5, 6]
    assert ccs == [distorder]
    assert not contains_cycle
    # change (0,1) weight to 2 and try again - it's a tree, so only dists should change not parents
    g.set_weight((0, 1), 2)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == exp_parents
    exp_dists[1] += 1
    exp_dists[3] += 1
    exp_dists[4] += 1
    assert dists == exp_dists
    assert distorder == [0, 2, 1, 5, 6, 3, 4]
    assert ccs == [distorder]
    assert not contains_cycle
    g.set_weight((0, 1), 1)
    exp_dists[1] -= 1
    exp_dists[3] -= 1
    exp_dists[4] -= 1
    # starting from 0, neighbors in reverse order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [0, 2, 1, 6, 5, 4, 3]
    assert ccs == [distorder]
    assert not contains_cycle
    # starting from 6, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.REVERSE_SORTED,
        neighbor_order=Order.SORTED,
    )
    exp_parents = {6: None, 2: 6, 5: 2, 0: 2, 1: 0, 3: 1, 4: 1}
    exp_dists = {6: 0, 2: 1, 5: 2, 0: 2, 1: 3, 3: 4, 4: 4}
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [6, 2, 0, 5, 1, 3, 4]
    assert ccs == [distorder]
    assert not contains_cycle
    # starting from 6, neighbors in reverse order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.REVERSE_SORTED,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [6, 2, 5, 0, 1, 4, 3]
    assert ccs == [distorder]
    assert not contains_cycle
    # starting from 1
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=1,
        neighbor_order=Order.SORTED,
    )
    exp_parents = {1: None, 3: 1, 4: 1, 0: 1, 2: 0, 5: 2, 6: 2}
    exp_dists = {1: 0, 3: 1, 4: 1, 0: 1, 2: 2, 5: 3, 6: 3}
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [1, 0, 3, 4, 2, 5, 6]
    assert ccs == [distorder]
    assert not contains_cycle
    # now neighbors in reverse order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=1,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [1, 4, 3, 0, 2, 6, 5]
    assert ccs == [distorder]
    assert not contains_cycle
    # change (0,1) weight to 2 and try again - it's a tree, so only dists should change not parents
    g.set_weight((0, 1), 2)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=1,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == exp_parents
    exp_dists[0] += 1
    exp_dists[2] += 1
    exp_dists[5] += 1
    exp_dists[6] += 1
    assert dists == exp_dists
    assert distorder == [1, 4, 3, 0, 2, 6, 5]
    assert ccs == [distorder]
    assert not contains_cycle

    ### nearly spindly trees

    # See 8 node binary example in create_nearly_spindly_b_ary_tree docstring
    g = GraphFactory.create_nearly_spindly_b_ary_tree(2, 8)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 3, 6: 3, 7: 5}
    assert dists == {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
    assert distorder == list(range(8))
    assert ccs == [distorder]
    assert not contains_cycle
    # set (0,2)'s weight to 100, so it appears at the end of distorder
    g.set_weight((0, 2), 100)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 3, 6: 3, 7: 5}
    assert dists == {0: 0, 1: 1, 2: 100, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
    assert distorder == [*range(2), *range(3, 8), 2]
    assert ccs == [distorder]
    assert not contains_cycle
    g.set_weight((0, 2), 1)

    # start from node 3 (arbitrarily chosen), neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=3,
        neighbor_order=Order.SORTED,
    )
    exp_parents = {3: None, 5: 3, 6: 3, 1: 3, 7: 5, 4: 1, 0: 1, 2: 0}
    exp_dists = {3: 0, 5: 1, 6: 1, 1: 1, 7: 2, 4: 2, 0: 2, 2: 3}
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [3, 1, 5, 6, 0, 4, 7, 2]
    assert ccs == [distorder]
    assert not contains_cycle
    # now with neighbors in reverse order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=3,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == [3, 6, 5, 1, 7, 4, 0, 2]
    assert ccs == [distorder]
    assert not contains_cycle

    # Same with 9 nodes
    g = GraphFactory.create_nearly_spindly_b_ary_tree(2, 9)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 3, 6: 3, 7: 5, 8: 5}
    assert dists == {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}
    assert distorder == list(range(9))
    assert ccs == [distorder]
    assert not contains_cycle
    # start from node 8, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=8,
        neighbor_order=Order.SORTED,
    )
    assert parents == {8: None, 5: 8, 7: 5, 3: 5, 6: 3, 1: 3, 4: 1, 0: 1, 2: 0}
    assert dists == {8: 0, 5: 1, 7: 2, 3: 2, 6: 3, 1: 3, 4: 4, 0: 4, 2: 5}
    assert distorder == [8, 5, 3, 7, 1, 6, 0, 4, 2]
    assert ccs == [distorder]
    assert not contains_cycle

    # See 10 node 3-ary example in create_nearly_spindly_b_ary_tree docstring
    g = GraphFactory.create_nearly_spindly_b_ary_tree(3, 10)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    exp_parents = {0: None, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 4, 8: 4, 9: 4}
    exp_dists = {0: 0, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3}
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == list(range(10))
    assert ccs == [distorder]
    assert not contains_cycle

    # Same with 11 nodes
    g = GraphFactory.create_nearly_spindly_b_ary_tree(3, 11)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    exp_parents[10] = 7
    assert parents == exp_parents
    exp_dists[10] = 4
    assert dists == exp_dists
    assert distorder == list(range(11))
    assert ccs == [distorder]
    assert not contains_cycle

    # Same with 12 nodes
    g = GraphFactory.create_nearly_spindly_b_ary_tree(3, 12)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    exp_parents[11] = 7
    assert parents == exp_parents
    exp_dists[11] = 4
    assert dists == exp_dists
    assert distorder == list(range(12))
    assert ccs == [distorder]
    assert not contains_cycle
    # set (1,4)'s weight to 1.5 and (0,1)'s weight to 0.5
    g.set_weight((1, 4), 1.5)
    g.set_weight((0, 1), 0.5)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == exp_parents
    assert dists == {**exp_dists, 1: 0.5, 5: 1.5, 6: 1.5}
    assert distorder == [0, 1, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11]
    assert ccs == [distorder]
    assert not contains_cycle
    g.set_weight((1, 4), 1)
    g.set_weight((0, 1), 1)

    ### arbitrary custom tree
    g = Graph(
        nodes=range(10),
        edges=((0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (0, 8), (8, 9)),
    )
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 5: 0, 8: 0, 2: 1, 3: 2, 4: 3, 6: 5, 7: 6, 9: 8}
    assert dists == {0: 0, 1: 1, 5: 1, 8: 1, 2: 2, 3: 3, 4: 4, 6: 2, 7: 3, 9: 2}
    assert distorder == [0, 1, 5, 8, 2, 6, 9, 3, 7, 4]
    assert ccs == [distorder]
    assert not contains_cycle

    # complete graphs (fully connected, so node 0 should just recurse fully in one pass)
    k = random.randint(4, 10)
    g = GraphFactory.create_complete_graph(k)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, **{i: 0 for i in range(1, k)}}
    assert dists == {0: 0, **{i: 1 for i in range(1, k)}}
    assert distorder == list(range(k))
    assert ccs == [distorder]
    assert contains_cycle

    # look ahead graph (see example in create_look_ahead_graph docstring)
    g = GraphFactory.create_look_ahead_graph(5, 2)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 2: 0, 3: 1, 4: 2}
    assert dists == {0: 0, 1: 1, 2: 1, 3: 2, 4: 2}
    assert distorder == [0, 1, 2, 3, 4]
    assert ccs == [distorder]
    assert contains_cycle
    # now start from 2
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1, seed_order=2, neighbor_order=Order.SORTED
    )
    assert parents == {2: None, 0: 2, 1: 2, 3: 2, 4: 2}
    assert dists == {2: 0, 0: 1, 1: 1, 3: 1, 4: 1}
    assert distorder == [2, 0, 1, 3, 4]
    assert ccs == [distorder]
    assert contains_cycle
    # now start from 3
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1, seed_order=3, neighbor_order=Order.SORTED
    )
    assert parents == {3: None, 1: 3, 2: 3, 4: 3, 0: 1}
    assert dists == {3: 0, 1: 1, 2: 1, 4: 1, 0: 2}
    assert distorder == [3, 1, 2, 4, 0]
    assert ccs == [distorder]
    assert contains_cycle
    # set weights so that look-ahead edges are worse than two hop
    g.set_weight((0, 2), 3)
    g.set_weight((1, 3), 3)
    g.set_weight((2, 4), 3)
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1, seed_order=3, neighbor_order=Order.SORTED
    )
    assert parents == {3: None, 1: 2, 2: 3, 4: 3, 0: 1}
    assert dists == {3: 0, 1: 2, 2: 1, 4: 1, 0: 3}
    assert distorder == [3, 2, 4, 1, 0]
    assert ccs == [distorder]
    assert contains_cycle

    # cycles
    g = GraphFactory.create_cycle(4)
    # start at 0, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 3: 0, 2: 1}
    assert dists == {0: 0, 1: 1, 3: 1, 2: 2}
    assert distorder == [0, 1, 3, 2]
    assert ccs == [distorder]
    assert contains_cycle
    # start at 1, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1, seed_order=1, neighbor_order=Order.SORTED
    )
    assert parents == {1: None, 0: 1, 2: 1, 3: 0}
    assert dists == {1: 0, 0: 1, 2: 1, 3: 2}
    assert distorder == [1, 0, 2, 3]
    assert ccs == [distorder]
    assert contains_cycle
    # start at 3, neighbors in sorted order
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g, use_approach_1=use_approach_1, seed_order=3, neighbor_order=Order.SORTED
    )
    assert parents == {3: None, 0: 3, 2: 3, 1: 0}
    assert dists == {3: 0, 0: 1, 2: 1, 1: 2}
    assert distorder == [3, 0, 2, 1]
    assert ccs == [distorder]
    assert contains_cycle

    ### custom cylic graphs
    # two uneven cycles with 0 at center. I.e., a lopsided figure-8
    g = Graph(
        nodes=range(9),
        edges=(
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (0, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 0),
        ),
    )
    # neighbors in order, so shorter cycle first
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 3: 0, 4: 0, 8: 0, 2: 1, 5: 4, 7: 8, 6: 5}
    assert dists == {0: 0, 1: 1, 3: 1, 4: 1, 8: 1, 2: 2, 5: 2, 7: 2, 6: 3}
    assert distorder == [0, 1, 3, 4, 8, 2, 5, 7, 6]
    assert ccs == [distorder]
    assert contains_cycle
    # neighbors in reverse order, so larger cycle first, and in the opposite direction
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == {0: None, 8: 0, 4: 0, 3: 0, 1: 0, 7: 8, 5: 4, 2: 3, 6: 7}
    assert dists == {0: 0, 8: 1, 4: 1, 3: 1, 1: 1, 7: 2, 5: 2, 2: 2, 6: 3}
    assert distorder == [0, 8, 4, 3, 1, 7, 5, 2, 6]
    assert ccs == [distorder]
    assert contains_cycle
    # now start at 8
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=8,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == {8: None, 7: 8, 0: 8, 6: 7, 4: 0, 3: 0, 1: 0, 5: 6, 2: 3}
    assert dists == {8: 0, 7: 1, 0: 1, 6: 2, 4: 2, 3: 2, 1: 2, 5: 3, 2: 3}
    assert distorder == [8, 7, 0, 6, 4, 3, 1, 5, 2]
    assert ccs == [distorder]
    assert contains_cycle

    # add node 9, add 0-9 edge, start at 9
    g.add_node(9)
    g.add_edge((0, 9))
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.REVERSE_SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {9: None, 0: 9, 1: 0, 3: 0, 4: 0, 8: 0, 2: 1, 5: 4, 7: 8, 6: 5}
    assert dists == {9: 0, 0: 1, 1: 2, 3: 2, 4: 2, 8: 2, 2: 3, 5: 3, 7: 3, 6: 4}
    assert distorder == [9, 0, 1, 3, 4, 8, 2, 5, 7, 6]
    assert ccs == [distorder]
    assert contains_cycle

    # graph with a main line with cycles coming off of it
    # we already have the current example, we can just add to that
    # 9 - 0
    # 0 has two cycles coming off it, using up nodes 1 through 8
    # add nodes 10 and 11
    # add a 3-cycle off of 11, using nodes 12 and 13
    # add node 14;
    # add 7-cycle off 14, using nodes 15, 16, 17, 18, 19, 20
    g.add_nodes(range(10, 21))
    g.add_edges(
        (
            (0, 10),
            (10, 11),
            (11, 12),  # start 3-cycle
            (12, 13),
            (13, 11),
            (11, 14),
            (14, 15),  # start 7-cycle
            (15, 16),
            (16, 17),
            (17, 18),
            (18, 19),
            (19, 20),
            (20, 14),
        )
    )
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=9,
        neighbor_order=Order.SORTED,
    )
    assert parents == {
        9: None,
        0: 9,
        1: 0,
        3: 0,
        4: 0,
        8: 0,
        10: 0,
        2: 1,
        5: 4,
        7: 8,
        11: 10,
        6: 5,
        12: 11,
        13: 11,
        14: 11,
        15: 14,
        20: 14,
        16: 15,
        19: 20,
        17: 16,
        18: 19,
    }
    assert dists == {
        9: 0,
        0: 1,
        1: 2,
        3: 2,
        4: 2,
        8: 2,
        10: 2,
        2: 3,
        5: 3,
        7: 3,
        11: 3,
        6: 4,
        12: 4,
        13: 4,
        14: 4,
        15: 5,
        20: 5,
        16: 6,
        19: 6,
        17: 7,
        18: 7,
    }
    assert distorder == [
        9,
        0,
        1,
        3,
        4,
        8,
        10,
        2,
        5,
        7,
        11,
        6,
        12,
        13,
        14,
        15,
        20,
        16,
        19,
        17,
        18,
    ]
    assert ccs == [distorder]
    assert contains_cycle

    # "nested" cycles
    # 0-1-2-3-4-5-6-7-0
    # 2-8-9-10-2
    # 10-11-12-13-10
    g = Graph(
        nodes=range(14),
        edges=(
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 0),
            (2, 8),
            (8, 9),
            (9, 10),
            (10, 2),
            (10, 11),
            (11, 12),
            (12, 13),
            (13, 10),
        ),
    )
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {
        0: None,
        1: 0,
        7: 0,
        2: 1,
        6: 7,
        3: 2,
        8: 2,
        10: 2,
        5: 6,
        4: 3,
        9: 8,
        11: 10,
        13: 10,
        5: 6,
        12: 11,
    }
    assert dists == {
        0: 0,
        1: 1,
        7: 1,
        2: 2,
        6: 2,
        3: 3,
        8: 3,
        10: 3,
        5: 3,
        4: 4,
        9: 4,
        11: 4,
        13: 4,
        5: 3,
        12: 5,
    }
    assert distorder == [0, 1, 7, 2, 6, 3, 8, 10, 5, 4, 9, 11, 13, 12]
    assert ccs == [distorder]
    assert contains_cycle
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.REVERSE_SORTED,
    )
    assert parents == {
        0: None,
        7: 0,
        1: 0,
        6: 7,
        2: 1,
        5: 6,
        10: 2,
        8: 2,
        3: 2,
        4: 5,
        13: 10,
        11: 10,
        9: 10,
        12: 13,
    }
    assert dists == {
        0: 0,
        7: 1,
        1: 1,
        6: 2,
        2: 2,
        5: 3,
        10: 3,
        8: 3,
        3: 3,
        4: 4,
        13: 4,
        11: 4,
        9: 4,
        12: 5,
    }
    assert distorder == [0, 7, 1, 6, 2, 5, 10, 8, 3, 4, 13, 11, 9, 12]
    assert ccs == [distorder]
    assert contains_cycle

    # test disjoint graphs (disconnected components)
    g_spindly = GraphFactory.create_spindly_tree(3)
    exp_parents_spindly = {0: None, 1: 0, 2: 1}
    exp_dists_spindly = {0: 0, 1: 1, 2: 2}
    exp_distorder_spindly = list(range(3))
    g_b_ary = GraphFactory.create_b_ary_tree(2, 2)
    exp_parents_b_ary = {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    exp_dists_b_ary = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}
    exp_distorder_b_ary = [0, 1, 2, 3, 4, 5, 6]
    # See 8 node binary example in create_nearly_spindly_b_ary_tree docstring
    g_nearly_spindly_b_ary = GraphFactory.create_nearly_spindly_b_ary_tree(2, 8)
    exp_parents_nearly_spindly_b_ary = {
        0: None,
        1: 0,
        2: 0,
        3: 1,
        4: 1,
        5: 3,
        6: 3,
        7: 5,
    }
    exp_dists_nearly_spindly_b_ary = {
        0: 0,
        1: 1,
        2: 1,
        3: 2,
        4: 2,
        5: 3,
        6: 3,
        7: 4,
    }
    exp_distorder_nearly_spindly_b_ary = list(range(8))
    g_custom = g  # above custom example
    exp_parents_custom = {
        0: None,
        1: 0,
        7: 0,
        2: 1,
        6: 7,
        3: 2,
        8: 2,
        10: 2,
        5: 6,
        4: 3,
        9: 8,
        11: 10,
        13: 10,
        5: 6,
        12: 11,
    }
    exp_dists_custom = {
        0: 0,
        1: 1,
        7: 1,
        2: 2,
        6: 2,
        3: 3,
        8: 3,
        10: 3,
        5: 3,
        4: 4,
        9: 4,
        11: 4,
        13: 4,
        5: 3,
        12: 5,
    }
    exp_distorder_custom = [0, 1, 7, 2, 6, 3, 8, 10, 5, 4, 9, 11, 13, 12]
    gs = (g_spindly, g_b_ary, g_nearly_spindly_b_ary, g_custom)
    g_combined = GraphFactory.concat_int_graphs(gs)
    exp_parents_seq = (
        exp_parents_spindly,
        exp_parents_b_ary,
        exp_parents_nearly_spindly_b_ary,
        exp_parents_custom,
    )
    exp_dists_seq = (
        exp_dists_spindly,
        exp_dists_b_ary,
        exp_dists_nearly_spindly_b_ary,
        exp_dists_custom,
    )
    exp_distorders = (
        exp_distorder_spindly,
        exp_distorder_b_ary,
        exp_distorder_nearly_spindly_b_ary,
        exp_distorder_custom,
    )
    lengths = [len(g) for g in gs]
    exp_parents = {}
    exp_dists = {}
    exp_distorder = []
    exp_ccs = []
    for i, (distorder, parents, dists) in enumerate(
        zip(exp_distorders, exp_parents_seq, exp_dists_seq)
    ):
        offset = sum(lengths[:i])
        exp_parents.update(
            {
                offset + node: offset + parent if parent is not None else None
                for node, parent in parents.items()
            }
        )
        exp_dists.update({offset + node: dist for node, dist in dists.items()})
        exp_distorder.extend([offset + node for node in distorder])
        exp_ccs.append([offset + node for node in distorder])
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g_combined,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == exp_parents
    assert dists == exp_dists
    assert distorder == exp_distorder
    assert ccs == exp_ccs
    assert contains_cycle

    # most of the above test that dijkstra gives the same as BFS for even weights, though there are a few tests with weights
    # now here are some custom tests specifically for dijkstra's
    g = Graph(
        nodes=7,
        edges={
            (0, 1): 2,
            (0, 2): 1,
            (1, 2): 5,
            (1, 3): 11,
            (1, 4): 3,
            (2, 4): 1,
            (2, 5): 15,
            (3, 4): 2,
            (3, 6): 1,
            (4, 5): 4,
            (4, 6): 5,
            (5, 6): 1,
        },
    )
    parents, dists, distorder, ccs, contains_cycle = dijkstra(
        g,
        use_approach_1=use_approach_1,
        seed_order=Order.SORTED,
        neighbor_order=Order.SORTED,
    )
    assert parents == {0: None, 1: 0, 2: 0, 4: 2, 3: 4, 6: 3, 5: 4}
    assert dists == {0: 0, 1: 2, 2: 1, 4: 2, 3: 4, 6: 5, 5: 6}
    assert distorder == [0, 2, 1, 4, 3, 6, 5]
    assert ccs == [distorder]
    assert contains_cycle
