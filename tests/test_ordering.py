# -*- coding: utf-8 -*-
import re

import pytest

pytest_plugins = ['pytester']


@pytest.fixture
def item_names_for(testdir):

    def _item_names_for(tests_content):
        # some strange code to extract sorted items
        items = testdir.getitems(tests_content)
        hook = testdir.config.hook
        hook.pytest_collection_modifyitems(session=items[0].session,
                                           config=testdir.config, items=items)
        return [item.name for item in items]

    return _item_names_for


def test_no_marks(item_names_for):
    tests_content = """
    def test_1(): pass

    def test_2(): pass
    """

    assert item_names_for(tests_content) == ['test_1', 'test_2']


def test_first_mark(item_names_for):
    tests_content = """
    import pytest

    def test_1(): pass

    @pytest.mark.first
    def test_2(): pass
    """

    assert item_names_for(tests_content) == ['test_2', 'test_1']


def test_last_mark(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.last
    def test_1(): pass

    def test_2(): pass
    """

    assert item_names_for(tests_content) == ['test_2', 'test_1']


def test_first_last_marks(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.last
    def test_1(): pass

    @pytest.mark.first
    def test_2(): pass

    def test_3(): pass
    """

    assert item_names_for(tests_content) == ['test_2', 'test_3', 'test_1']


def test_order_marks(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=-1)
    def test_1(): pass

    @pytest.mark.run(order=-2)
    def test_2(): pass

    @pytest.mark.run(order=1)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ['test_3', 'test_2', 'test_1']


def test_non_contiguous_positive(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=10)
    def test_1(): pass

    @pytest.mark.run(order=20)
    def test_2(): pass

    @pytest.mark.run(order=5)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ['test_3', 'test_1', 'test_2']


def test_non_contiguous_negative(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=-10)
    def test_1(): pass

    @pytest.mark.run(order=-20)
    def test_2(): pass

    @pytest.mark.run(order=-5)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ['test_2', 'test_1', 'test_3']


def test_non_contiguous_inc_zero(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=10)
    def test_1(): pass

    @pytest.mark.run(order=20)
    def test_2(): pass

    @pytest.mark.run(order=5)
    def test_3(): pass

    @pytest.mark.run(order=-10)
    def test_4(): pass

    @pytest.mark.run(order=-20)
    def test_5(): pass

    @pytest.mark.run(order=-5)
    def test_6(): pass

    @pytest.mark.run(order=0)
    def test_7(): pass
    """

    assert item_names_for(tests_content) == ['test_7', 'test_3', 'test_1', 'test_2', 'test_5', 'test_4', 'test_6']


def test_non_contiguous_inc_none(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=5)
    def test_1(): pass

    @pytest.mark.run(order=0)
    def test_2(): pass

    @pytest.mark.run(order=1)
    def test_3(): pass

    @pytest.mark.run(order=-1)
    def test_4(): pass

    @pytest.mark.run(order=-5)
    def test_5(): pass

    def test_6(): pass
    """

    assert item_names_for(tests_content) == ['test_2', 'test_3', 'test_1', 'test_6', 'test_5', 'test_4']


def test_first_mark_class(item_names_for):
    tests_content = """
    import pytest

    def test_1(): pass


    @pytest.mark.first
    class TestSuite(object):

        def test_3(self): pass

        def test_2(self): pass

    """

    assert item_names_for(tests_content) == ['test_3', 'test_2', 'test_1']


def test_last_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.last
    class TestSuite(object):

        def test_1(self): pass

        def test_2(self): pass


    def test_3(): pass
    """

    assert item_names_for(tests_content) == ['test_3', 'test_1', 'test_2']


def test_first_last_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.last
    class TestLast(object):

        def test_1(self): pass

        def test_2(self): pass


    def test_3(): pass


    @pytest.mark.first
    class TestFirst(object):

        def test_4(self): pass

        def test_5(self): pass

    """

    assert item_names_for(tests_content) == ['test_4', 'test_5', 'test_3', 'test_1', 'test_2']


def test_order_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.run(order=-1)
    class TestLast(object):

        def test_1(self): pass

        def test_2(self): pass


    @pytest.mark.run(order=0)
    def test_3(): pass


    @pytest.mark.run(order=-2)
    class TestFirst(object):

        def test_4(self): pass

        def test_5(self): pass
    """

    assert item_names_for(tests_content) == ['test_3', 'test_4', 'test_5', 'test_1', 'test_2']

def test_run_ordinals(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.run('second_to_last')
    def test_three():
        pass

    @pytest.mark.run('last')
    def test_four():
        pass

    @pytest.mark.run('second')
    def test_two():
        pass

    @pytest.mark.run('first')
    def test_one():
        pass
    """

    assert item_names_for(test_content) == ['test_one', 'test_two', 'test_three', 'test_four']

def test_quickstart(item_names_for):
    test_content="""
    import pytest

    def test_foo():
        pass

    def test_bar():
        pass
    """
    assert item_names_for(test_content) == ['test_foo', 'test_bar']    

def test_quickstart2(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.order2
    def test_foo():
        pass

    @pytest.mark.order1
    def test_bar():
        pass
    """
    assert item_names_for(test_content) == ['test_bar', 'test_foo']    

def test_relative(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.run(after='test_second')
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.run(before='test_second')
    def test_first():
        pass
    """
    assert item_names_for(test_content) == ['test_first', 'test_second', 'test_third']


def test_relative2(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.run(after='test_second')
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.run(before='test_second')
    def test_first():
        pass

    def test_five():
        pass

    @pytest.mark.run(before='test_five')
    def test_four():
        pass

    """
    assert item_names_for(test_content) == ['test_first', 'test_second', 'test_third', 'test_four', 'test_five']

def test_relative3(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.run(after='test_second')
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.run(before='test_second')
    def test_first():
        pass

    def test_five():
        pass

    @pytest.mark.run(before='test_five')
    def test_four():
        pass

    """
    assert item_names_for(test_content) == ['test_first', 'test_second', 'test_third', 'test_four', 'test_five']

def test_false_insert(item_names_for):
    test_content="""
    import pytest

    @pytest.mark.run(after='test_a')
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.run(before='test_b')
    def test_first():
        pass
    """
    assert item_names_for(test_content) == ['test_first', 'test_second', 'test_third', 'test_four', 'test_five']

def test_run_marker_registered(capsys):
    pytest.main('--markers')
    out, err = capsys.readouterr()
    assert '@pytest.mark.run' in out

