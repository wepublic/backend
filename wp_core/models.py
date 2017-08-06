from django.db import models
from users.models import User
from wp_party.models import Party


class Tag(models.Model):
    text = models.CharField(max_length=64)

    def __str__(self):
        return "#%s" % self.text


class Question(models.Model):
    text = models.TextField(max_length=500)
    tags = models.ManyToManyField(Tag, related_name="questions")
    time_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    votes = models.ManyToManyField(
            User,
            through="VoteQuestion",
            related_name='votes'
        )
    user = models.ForeignKey(User)

    class Meta:
        get_latest_by = 'time_created'

    def __str__(self):
        return "%s: \"%s\", %s " % (self.pk, self.text, self.user.email)

    def vote_by(self, user, up):
        try:
            vote = VoteQuestion.objects.get(question=self, user=user)
        except VoteQuestion.DoesNotExist:
            vq = VoteQuestion(question=self, user=user, up=up)
            vq.save()
            return
        if vote.up != up:
            vote.up = up
            vote.save()


class VoteQuestion(models.Model):
    class Meta:
        unique_together = ['question', 'user']
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    up = models.BooleanField(default=True)


class Answer(models.Model):
    text = models.TextField(max_length=5000)
    time_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(
            Question,
            on_delete=models.CASCADE,
            related_name='answers'
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, null=True)
    votes = models.ManyToManyField(
            User,
            through="VoteAnswer",
            related_name='votes_answer'
        )

    def __str__(self):
        return "%s: %s -> %s" % (self.pk, self.text, self.question.pk)


class VoteAnswer(models.Model):
    class Meta:
        unique_together = ['answer', 'user']
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    up = models.BooleanField()
