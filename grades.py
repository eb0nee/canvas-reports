from datetime import datetime
import math

import numpy as np
import pandas as pd

"""
Code format: '00.00-C- Description'
"""

class Gradebook:
    """
    A class that represents the gradebook.
    """
    def __init__(self, filename, practice_code='-P-', test_code='-T-', method='outcome') -> None:
        self.filename = filename
        self.df = self._fetch_grades_dataframe()
        self.students = []
        self.practice_code = practice_code
        self.test_code = test_code
        self.method = method

        for _, row in self.df.iterrows():
            student = Student(row['Student name'], row['Student ID'], row['Student SIS ID'], row.drop(labels=['Student name', 'Student ID', 'Student SIS ID']).to_dict(), self)
            self.students.append(student)

    def get_class_grade_report(self):
        data = [student.report for student in self.students]

        return data

    def save_report(self):
        df = pd.DataFrame(self.get_class_grade_report())

        report_filename = f'{datetime.now().strftime("%Y-%m-%d")}_report.csv'
        df.to_csv(report_filename, index=False, encoding='utf-8')

    def _fetch_grades_dataframe(self):
        """
        Fetches the current gradebook either locally or using the Canvas API.

        parameters:
        - update (bool): If True, will fetch from the Canvas API if there is no grade report saved or if the report is older than a day.
            If False, will use local file, or throw an error if the local file does not exist or is invalid.
        """
        df = pd.read_csv(f'outcome_reports/{self.filename}')
        cols = [column for column in df.columns if not column.endswith('mastery points')]
        return df[cols]



class Student:
    """
    A class that represents an individual student.
    """
    def __init__(self, name, id, user_id, outcomes, gradebook) -> None:
        self.name = name
        self.id = id
        self.user_id = user_id
        self.outcomes = outcomes
        self.gradebook = gradebook
        self.report = self.calculate_individual_grade_report(gradebook.method)

    def calculate_individual_grade_report(self, method='outcome'):
        """
        Returns the individual grade report for the student.

        parameters:
        - method: one of 'outcome' or 'assignment_type'. denotes how the assignments are first sorted.
        """
        def calculate_average_percentage(num, den):
            return round(num / den * 100, 1) if den != 0 else 0
        
        def filter_outcomes(outcomes, func):
            return sum(1 for outcome, rating in outcomes.items() if func(outcome, rating))
        
        def practice(outcomes, value):
            return sum(1 for outcome, rating in outcomes.items() if self.gradebook.practice_code in outcome and rating == value)

        def test(outcomes, value):
            return sum(1 for outcome, rating in outcomes.items() if self.gradebook.test_code in outcome and rating == value)
        
        def weighted_average(practice, test):
            return 0.6*test + 0.4*practice

        def parse_code(code):
            """Parse a single code in the format 'number-C-description'."""
            # Split the string into parts separated by '-'
            parts = code.split('-')

            number = float(parts[0])
            assignment_type = parts[1]
            description = '-'.join(parts[2:]).strip()

            return number, assignment_type, description

        def match_codes(outcomes):
            """
            Match practice and test codes, returning a dictionary with weighted averages.
            """
            def valid_num(n):
                if n is None:
                    return False
                elif np.isnan(n):
                    return False
                return True
            
            assignment_dict = {}

            for code, rating in outcomes.items():
                code = code.split('>')[-1][:-7]
                number, assignment_type, description = parse_code(code)
                
                if number not in assignment_dict:
                    assignment_dict[number] = {'P': None, 'T': None}

                assignment_dict[number][assignment_type] = rating

            result = {}
            for description, values in assignment_dict.items():
                P = values["P"]
                T = values["T"]
                if valid_num(P) and valid_num(T):
                    result[description] = weighted_average(P, T)
                elif valid_num(P):
                    result[description] = P
                elif valid_num(T):
                    result[description] = T

            return result
    
        
        def convert_to_EMRN(value):
            if value >= 2.6:
                return 'E'
            elif  2.6 > value >= 1.6:
                return 'M'
            elif 1.6 > value >= 1:
                return 'R'
            elif value >= 0:
                return 'N'

        def calculate_final_grade(report):
            if report['N'] > 0.05:
                return 'NR'
            elif report['E'] >= 0.15 and report['E'] + report['M'] >= 0.90:
                return '95'
            elif report['E'] >= 0.02 and report['E'] + report['M'] >= 0.79:
                return '85'
            elif report['M'] >= 0.65:
                return '75'
            return '65'
        
        cumulative_test_ratings = sum(1 for outcome, rating in self.outcomes.items() if not math.isnan(rating) and self.gradebook.test_code in outcome)
        cumulative_practice_ratings = sum(1 for outcome, rating in self.outcomes.items() if not math.isnan(rating) and self.gradebook.practice_code in outcome)

        EMRN = {outcome: convert_to_EMRN(value) for outcome, value in self.outcomes.items()}

        practice_e = practice(EMRN, 'E')
        practice_m = practice(EMRN, 'M')
        practice_r = practice(EMRN, 'R')
        practice_n = practice(EMRN, 'N')

        test_e = test(EMRN, 'E')
        test_m = test(EMRN, 'M')
        test_r = test(EMRN, 'R')
        test_n = test(EMRN, 'N')

        report = {
            'pE': calculate_average_percentage(practice_e, cumulative_practice_ratings),
            'pM': calculate_average_percentage(practice_m, cumulative_practice_ratings),
            'pR': calculate_average_percentage(practice_r, cumulative_practice_ratings),
            'pN': calculate_average_percentage(practice_n, cumulative_practice_ratings),
            'tE': calculate_average_percentage(test_e, cumulative_test_ratings),
            'tM': calculate_average_percentage(test_m, cumulative_test_ratings),
            'tR': calculate_average_percentage(test_r, cumulative_test_ratings),
            'tN': calculate_average_percentage(test_n, cumulative_test_ratings)

        }
        if method == 'outcome':
            codes = match_codes(self.outcomes)
            codes = {outcome: convert_to_EMRN(rating) for outcome, rating in codes.items()}
            print(codes)
            report |= {letter: list(codes.values()).count(letter) for letter in ['E', 'M', 'R', 'N']}
        elif method == 'assignment_type':
            report |= {letter: 0.6 * report[f'p{letter}'] + 0.4 * report[f't{letter}'] for letter in ['E', 'M', 'R', 'N']}

        report['final_grade'] = calculate_final_grade(report)

        report = (
            {"Student": self.name, "ID": self.id, "SIS User ID": self.user_id, "SIS Login ID": '', "Section": '', "Expected Final Grade": report['final_grade']} |
            {f"Practice % of {letter}s so far": report[f'p{letter}'] for letter in ['E', 'M', 'R', 'N']} |
            {f"Test % of {letter}s so far": report[f't{letter}'] for letter in ['E', 'M', 'R', 'N']}
        )

        return report

