from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    full_time = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    occupation = models.CharField(max_length=200, blank=True)
    social_link = models.URLField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    image = models.URLField(blank=True)
    description = models.TextField(blank=True)
    pub_date = models.DateField(auto_now_add=True)
    instructors = models.ManyToManyField(Instructor)

    def __str__(self):
        return self.name

    def total_enrollment(self):
        return self.enrollment_set.count()


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    content = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    grade = models.IntegerField(default=1)

    def is_get_score(self, selected_ids):
        correct = set(c.id for c in self.choice_set.filter(is_correct=True))
        selected = set(choice.id for choice in self.choice_set.filter(id__in=selected_ids))
        return correct == selected


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)