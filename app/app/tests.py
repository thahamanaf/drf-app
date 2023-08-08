"""Sample test"""

from django.test import SimpleTestCase

from app import calc

class CalcTest(SimpleTestCase):
  """Test the calc module"""
    
  def test_add_numbers(self):
    """Test adding numbers together"""
    result = calc.add(5,6)
    self.assertEqual(result, 11)
        
  def test_sub_num(self):
    """Substracting numbers"""
    res = calc.sub(15, 10)
    self.assertEqual(res, 5)