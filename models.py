from django.db import models

# Create your models here.
from django.db import models

class Topic(models.Model):
  topic_id = models.CharField(max_length=10, primary_key=True)
  content = models.TextField()

class Request(models.Model):
  request_id = models.CharField(max_length=10, primary_key=True)
  topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
  content = models.TextField()
  percent = models.FloatField()

class Inf_Exam_Framework(models.Model):
  exam_id = models.CharField(max_length=10, primary_key=True)
  exam_name =  models.CharField(max_length=255) 

class Classroom(models.Model):
    classroom_id = models.CharField(max_length=10, primary_key=True)
    classroom_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)

class Student(models.Model):
  student_id = models.CharField(max_length=10, primary_key=True)
  student_name = models.TextField()
  class_name = models.ForeignKey(Classroom, on_delete=models.CASCADE) 
  picture = models.BinaryField(null=True)

class Test(models.Model):
  test_id = models.CharField(max_length=10, primary_key=True)
  test_name = models.TextField()
  date_update = models.DateTimeField()
  date_create = models.DateTimeField()
  factor = models.IntegerField()
  exam = models.ForeignKey(Inf_Exam_Framework, on_delete=models.CASCADE, null=True)
  numer_q = models.IntegerField()
  test_time = models.IntegerField()
  student = models.ForeignKey(Student,on_delete=models.CASCADE, null=True)

class Student_result(models.Model):
  result_id = models.CharField(max_length=10, primary_key=True)
  student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
  test = models.ForeignKey(Test, on_delete=models.CASCADE)
  score = models.FloatField()
  times = models.IntegerField(default=1)

class Proportion_Student(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  request = models.ForeignKey(Request, on_delete=models.CASCADE)
  percent = models.FloatField()
  class Meta:
    unique_together = (('student', 'request'),)

class Booktype(models.Model):
  book_id = models.CharField(max_length=10, primary_key=True)
  book_name = models.TextField()

class Lesson(models.Model):
  lesson_id = models.CharField(max_length=10, primary_key=True)
  topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
  book = models.ForeignKey(Booktype, on_delete=models.CASCADE)
  lesson_name = models.TextField()

class Question(models.Model):
  question_id = models.AutoField(primary_key=True)
  question_content = models.TextField()
  question_level = models.IntegerField()
  topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
  date_update = models.DateTimeField(null=True)
  date_create = models.DateTimeField(null=True)
  picture = models.BinaryField(null=True)
  form = models.IntegerField()

class Answer(models.Model):
  answer_id = models.CharField(max_length=10, primary_key=True)
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  answer_content = models.TextField()
  answer_right = models.BooleanField(default=False)

class Question_BookType(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
  class Meta:
    unique_together = (('question', 'topic'),)

class Question_Lesson(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
  class Meta:
    unique_together = (('question', 'lesson'),)

class Question_Request(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  request = models.ForeignKey(Request, on_delete=models.CASCADE)
  class Meta:
    unique_together= (('question', 'request'),)


class Lesson_Request(models.Model):
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
  request = models.ForeignKey(Request, on_delete=models.CASCADE)
  class Meta:
    unique_together = (('lesson', 'request'),)

class Parameter(models.Model):
  parameter_id = models.CharField(max_length=10, primary_key=True)
  parameter_name = models.TextField()
  parameter_value = models.TextField()

class Detail_Test_Student(models.Model):
  result = models.ForeignKey(Student_result, on_delete=models.CASCADE)  # Update Student_result to result
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  chose = models.TextField()
  returned = models.BooleanField()  # Update "Return" to returned

class Test_Lesson(models.Model):
  test = models.ForeignKey(Test, on_delete=models.CASCADE)
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
  class Meta:
    unique_together = (('test', 'lesson'),)

class Keyword(models.Model):
  keyword = models.CharField(max_length=40)  # Change to TextField if needed for longer keywords
  topic = models.ForeignKey(Topic, on_delete=models.CASCADE)  # Replace with your actual topic model name
  value = models.IntegerField()
  class Meta:
    unique_together = (('keyword', 'topic'),)

class ClassroomResult(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    average_score = models.FloatField()
    class Meta:
        unique_together = (('classroom', 'topic'),)