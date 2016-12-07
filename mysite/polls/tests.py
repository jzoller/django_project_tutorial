import datetime

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Question
# Create your tests here.

def create_question(question_text, days):
    """
    Creates a question with the given question_text and published on a given number of days
    offset to now(negative values indicate the past, positive for questions that have yet to be 
    published, zero for now)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestoinMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False forquestions whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for question with pub_date older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_ws_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for question published within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionViewTests(TestCase):

    def test_index_view_wtih_no_questions(self):
        """
        If not questions exist, a message should be displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index page
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_index_view_with_a_future_question(self):
        """
        Questions witha pub_date in the future should not be displayed on index page
        """
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Only past Question should be displayed.
        """
        create_question(question_text="Past Question.", days=-30)
        create_question(question_text="Future Question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                response.context['latest_question_list'], 
                ['<Question: Past Question.>'])

    def test_index_view_with_two_psat_questions(self):
        """
        Questions index should display multiple questions.
        """
        create_question(question_text='Past question 1.', days=-30)
        create_question(question_text='Past question 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                response.context['latest_question_list'],
                ['<Question: Past question 2.>', '<Question: Past question 1.>'])

class QuestionIndexDetailTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should return
        a 404.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view ofa questionin the past should display the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
