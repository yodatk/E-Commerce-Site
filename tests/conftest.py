#
# conftest.py
import sys
from os.path import dirname as d
from os.path import abspath, join
root_dir = d(d(abspath(__file__)))
sys.path.append(root_dir)
def pytest_configure():
    print(root_dir)
