import argparse

from grades import Gradebook, Student

parser = argparse.ArgumentParser(description="Create grade report")
parser.add_argument('filename', type=str, help='The filename of the gradebook obtained from Canvas')
parser.add_argument('--method', type=str, default='outcome', help='The first sort method')
args = parser.parse_args()

grades = Gradebook(args.filename, method=args.method)
grades.save_report()