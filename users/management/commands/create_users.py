from django.core.management.base import BaseCommand
from users.models import User
from wp_party.models import Party
from wp_core.models import (
        Question,
        Answer,
        VoteQuestion,
        VoteAnswer,
        Tag,
    )
from faker import Factory
from slugify import slugify
from random import randint
import requests


class Command(BaseCommand):
    help = 'adds a couple of new Users to the database'

    def add_arguments(self, parser):
        parser.add_argument('model', nargs=1, type=str)

    def handle(self, *args, **options):
        model = options['model'][0]
        if(model == 'user' or model == 'all'):
            self.add_users()

        if(model == 'tag' or model == 'all'):
            self.add_tags()
        if(model == 'question' or model == 'all'):
            self.add_questions()
        if(model == 'party' or model == 'all'):
            self.add_parties()
        if(model == 'answer' or model == 'all'):
            self.add_answers()
        if(model == 'vote-question' or model == 'all'):
            self.add_votes_question()
        if(model == 'vote-answer' or model == 'all'):
            self.add_votes_answer()

    def add_users(self, number=20):
        fake = Factory.create('de_DE')

        for i in range(0, 20):
            first_name = fake.first_name()
            last_name = fake.last_name()
            first_name_slug = slugify(first_name)
            last_name_slug = slugify(last_name)
            email = '%s.%s@%s' % (
                    first_name_slug,
                    last_name_slug,
                    fake.free_email_domain()
                    )
            username = '%s%s' % (first_name_slug, last_name_slug)

            u = User.objects.create_user(
                        email=email,
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        zip_code=fake.random_number(digits=3),
                        year_of_birth=fake.year(),
                        gender=fake.profile()['sex'],
                        password='password',
                    )
            u.is_active = True
            u.save()

    def add_tags(self, number=40):
        fake = Factory.create('de_DE')
        for _ in range(0, number):
            t = Tag.objects.create(text=fake.domain_word())
            t.save()

    def add_questions(self, number=50):
        sou = "https://api.stackexchange.com/2.2/questions/featured?order=desc&sort=activity&site=stackoverflow"
        user_count = User.objects.count()
        tag_count = Tag.objects.count()
        stack_res = requests.get(sou).json()['items']
        for _ in range(0, number):
            user = User.objects.all()[randint(0, user_count-1)]
            tag_number = randint(1, 5)
            stack_index = randint(0, len(stack_res))
            text = stack_res[stack_index-1]['title']
            q = Question(text=text, user=user)
            q.save()
            for _ in range(0, tag_number-1):
                q.tags.add(Tag.objects.all()[randint(0, tag_count-1)])
            q.save()

    def add_parties(self, number=5):

        parties = { 'SPD': 'Sozialdemokratische Partei Deutschlands',
                'CDU': 'Christlich Demokratische Union',
                'FDP': 'Freie Demokratische Partei',
                'AfD': 'Alternative für Deutschland',
                'DIE GRÜNEN': 'Bündnis 90 / Die Grünen' }

        for short_name, name in parties.items():
            p = Party(short_name=short_name, name=name)
            p.save()

    def add_answers(self, number=70):
        fake = Factory.create('de_DE')
        user_count = User.objects.count()
        question_count = Question.objects.count()
        party_count = Party.objects.count()

        for _ in range(0, number):
            user = User.objects.all()[randint(0, user_count-1)]
            text = fake.text(max_nb_chars=300)
            question = Question.objects.all()[randint(0, question_count-1)]
            party = Party.objects.all()[randint(0, party_count-1)]
            Answer.objects.create(text=text, user=user, question=question, party=party)

    def add_votes_question(self, number_max=30):
        users = User.objects.all()
        question_count = Question.objects.count()

        print("Creating {:d} Votes on Questions".format(
            users.count() * question_count)
            )

        for user in users:
            for _ in range(0, randint(1, number_max)):
                question = Question.objects.all()[randint(0, question_count-1)]
                try:
                    VoteQuestion.objects.get(
                            user=user,
                            question=question
                            ).delete()
                except VoteQuestion.DoesNotExist:
                    pass
                up = randint(0, 1) == 1
                VoteQuestion.objects.create(
                        user=user,
                        question=question,
                        up=up
                        )

    def add_votes_answer(self, number_max=30):
        users = User.objects.all()
        answer_count = Answer.objects.count()
        print("Creating {:d} Votes on Answers".format(
            users.count() * answer_count
            )
        )
        for user in users:
            for _ in range(0, randint(1, number_max)):
                answer = Answer.objects.all()[randint(0, answer_count-1)]
                try:
                    VoteAnswer.objects.get(
                            user=user,
                            answer=answer
                            ).delete()
                except VoteAnswer.DoesNotExist:
                    pass

                VoteAnswer.objects.create(
                        user=user,
                        answer=answer,
                        up=randint(0, 1) == 1
                        )
