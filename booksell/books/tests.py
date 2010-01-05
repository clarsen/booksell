"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


"""
Some sample UPC codes:
978080184975690000
9780192860880
978052008940290000
9780520089402
007671400699700410
0076714006997
978039471618350900
9780394716183
978006096133690000
978089815644750995
978055306174151500
978055306174151500
978006017336490000
978067940773752750

"""