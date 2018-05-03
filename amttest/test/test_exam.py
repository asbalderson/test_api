from .base_test import BaseTest

from ..database import db
from ..database.tables.answer import Answer
from ..database.tables.question import Question
from ..database.tables.section import Section
from ..database.tables.exam import Exam
from ..errors import *
from ..routes import exam


class TestExam(BaseTest):

    def create_app(self):
        return BaseTest.create_app(self)


    def setUp(self):
        BaseTest.setUp(self)
        data = []
        data.append(Section(name='Rules of Play', examid=1, active_questions=2))
        data.append(Question(
            question='How many magic points does a caster get per level?',
            sectionid=1))
        data.append(Answer(answer='3', correct=False, questionid=1))
        data.append(Answer(answer='4', correct=False, questionid=1))
        data.append(Answer(answer='5', correct=True, questionid=1))
        data.append(Answer(answer='6', correct=False, questionid=1))
        data.append(Question(
            question='How many credits are required for level 4?',
            sectionid=1))
        data.append(Answer(answer='21', correct=True, questionid=2))
        data.append(Answer(answer='25', correct=False, questionid=2))
        data.append(Answer(answer='20', correct=False, questionid=2))
        data.append(Answer(answer='16', correct=False, questionid=2))

        data.append(Section(name='Safety', examid=1, active_questions=2))
        data.append(Question(
            question='When do shots count after a player is hit in the head?',
            sectionid=2))
        data.append(Answer(answer='All hits count even if the player is stunned', correct=False, questionid=3))
        data.append(Answer(answer='No hits count until the struck player says they are OK', correct=False, questionid=3))
        data.append(Answer(answer='No hits count and the striking player should remove hiimself from the field', correct=False, questionid=3))
        data.append(Answer(answer='All hits count, given the struck and striking players continue play, otherwise combat should be reset to before the strike', correct=True, questionid=3))
        data.append(Question(
            question='When should "Safety" be called?',
            sectionid=2))
        data.append(Answer(answer='When there is an injured player, or obstruction on the field', correct=True, questionid=4))
        data.append(Answer(answer='Never, "Hold" should be used instead', correct=False, questionid=4))
        data.append(Answer(answer='When there is a dispute of the rules', correct=False, questionid=4))
        data.append(Answer(answer='When a player feels that the game is unfair and wishes to leave', correct=False, questionid=4))
        self.add_obj_to_db(data)


    def tearDown(self):
        BaseTest.tearDown(self)


    def test_get_all_exams(self):
        exam = Exam(name='Reeves Test')
        exam2 = Exam(name='Corpora Test')
        self.default_get_all('amttest/api/exam', [exam, exam2])


    def test_get_randomized_test(self):
        exam = Exam(name='Reeves Test')
        self.add_obj_to_db([exam])
        response_dne = self.client.get('amttest/api/exam/42/take')
        self.assert400(response_dne, 'non existent id should return a 400')

        exam_response = self.client.get('amttest/api/exam/1/take')
        self.assert200(exam_response, 'successful test generation should return 200')
        self.assertEqual(len(exam_response.json['questions']), 4, 'not all questions present')
        answers = 0
        for question in exam_response.json['questions']:
            answers += len(question['answers'])
        self.assertEqual(answers, 16, 'some answers seem to be missing')

        question = Question.query.filter_by(questionid=1).first()
        question.archive = True
        section = Section.query.filter_by(sectionid=question.sectionid).first()
        section.active_questions = 1
        answer = Answer.query.filter_by(answerid=15).first()
        answer.archive = True
        db.session.commit()

        exam_archive = self.client.get('amttest/api/exam/1/take')
        self.assert200(exam_archive, 'when a question is archived, test generation does not return 200')
        self.assertEqual(len(exam_archive.json['questions']), 3, 'after archive, there should be 3 questions')
        for question in exam_archive.json['questions']:
            self.assertNotEqual(question['questionid'], 1, 'archived question appeared in questions')

        answers = 0
        for question in exam_archive.json['questions']:
            answers += len(question['answers'])
        self.assertEqual(answers, 11, 'there should be 11, there are %s' % answers)


    def test_get_exam(self):
        exam = Exam(name='Reeves Test')
        self.default_get('amttest/api/exam', exam)


    def test_create_exam(self):
        payload = {'name': 'Reeves Test'}
        self.default_post('amttest/api/exam', payload, Exam)


    def test_update_exam(self):
        payload = {'pass_percent': 101}
        exam = Exam(name='Reeves Test')
        self.default_put('amttest/api/exam', payload, exam, Exam)


    def test_delete_exam(self):
        exam1 = Exam(name='Reeves Test')
        self.default_delete('amttest/api/exam', exam1)