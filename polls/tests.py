# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Questions
# Create your tests here.

class QuestionModeTests(TestCase):
	"""docstring for QuestionModeTests"""
	def test_was_published_recently_with_future_question(self):
		time = timezone.now() - datetime.timedelta(days = 30);
		future_question = Questions(pub_date = time);
		self.assertIs(future_question.was_published_recently(), False);

	def test_was_published_recently_with_old_question(self):
		time = timezone.now() - datetime.timedelta(days = 1, seconds = 1);
		old_question = Questions(pub_date = time);
		self.assertIs(old_question.was_published_recently(),False);

	def test_was_published_recently_with_recent_question(self):
		time = timezone.now() - datetime.timedelta(hours = 23, minutes = 59, seconds = 59);
		recent_question = Questions(pub_date = time);
		self.assertIs(recent_question.was_published_recently(), True);

def create_question(question_text, days):
	time = timezone.now() + datetime.timedelta(days = days);
	return Questions.objects.create(question_text = question_text,pub_date = time);

class QuestionIndexViewTests(TestCase):
	def test_no_question(self):
		response = self.client.get(reverse('polls:index'));
		self.assertEqual(response.status_code, 200);
		self.assertContains(response, "No polls are Available.");
		self.assertQuerysetEqual(response.context['latest_question_list'],[]);

	def test_past_question(self):
		create_question(question_text='Past questions.', days = -30);
		response = self.client.get(reverse("polls:index"));
		self.assertContains(response, "No polls are available.");
		self.assertQuerysetEqual(response.context['latest_question_list'],[]);

	def test_future_question_and_past_question(self):
		create_question(question_text = "Past questions.", days = -30);
		create_question(question_text = "Future questions", days = 30);
		response = self.client.get(reverse('polls:index'));
		self.assertQuerysetEqual(response.context[['latest_question_list'],['<Question: Past question.>']]);

	def test_two_past_questions(self):
		create_question(question_text="Past question 1.", days=-30)
		create_question(question_text="Past question 2.", days=-5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question 2.>', '<Question: Past question 1.>']);

	def test_past_quesion(self):
		past_question = create_question(question_text='Past Question.', days=-5);
		url = reverse('polls:detail', args=(past_question.id,));
		response = self.client.get(url);
		self.assertContains(response, past_question.question_text);

	def test_future_question(self):
		future_question = create_question(question_text='Future question.', days=5);
		url = reverse('polls:detail', args=(future_question.id,));
		response = self.client.get(url);
		self.assertEqual(response.status_code, 404);