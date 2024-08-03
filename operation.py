from .models import *
import logging
import random
from django.db.models import Avg
logger = logging.getLogger(__name__)

def weight_question(question_id):
    try:
        question = Question.objects.get(question_id=question_id)
        keywords = Keyword.objects.filter(topic=question.topic)
        answers = Answer.objects.filter(question=question)
        text = question.question_content
        for answer in answers:
            text += " " + answer.answer_content
        weight = 0
        for keyword in keywords:
            count = text.count(keyword.keyword)
            weight += count * keyword.value
        return weight
    except Exception as e:
        logger.error(f"Error in weight_question: {e}")
        return 0

def sum_weight_question(questions):
    weight = 0
    for question in questions:
        weight += weight_question(question.question_id)
    return weight

def weight_request(questions_T, questions_F):
    weight_T = sum_weight_question(questions_T)
    #logger.error(weight_T)
    weight_F = sum_weight_question(questions_F)
    
    if weight_T + weight_F == 0:  # To avoid division by zero
        return 0
    return 100*weight_T / (weight_T + weight_F)

def result_student(student_id):
    try:
        detail_results = Detail_Test_Student.objects.filter(result__student__student_id=student_id)
        topics = Topic.objects.all()
        questions_T = []
        questions_F = []
        for detail_result in detail_results:
            if detail_result.returned:
                questions_T.append(detail_result.question)
            else:
                questions_F.append(detail_result.question)

        for topic in topics:
            requests = Request.objects.filter(topic=topic)
            for request in requests:
                # Lấy tất cả các câu hỏi của yêu cầu
                question_requests = Question_Request.objects.filter(request=request)
                questions_R = Question.objects.filter(question_id__in=question_requests.values('question_id'))
                
                # Phân loại các câu hỏi đúng và sai theo yêu cầu
                questions_T_R = [qr for qr in questions_R if qr in questions_T]
                questions_F_R = [qr for qr in questions_R if qr in questions_F]
                
                # Tính trọng số
                
                weight_R_T = weight_request(questions_T_R, questions_F_R)
                
                # Update or create new record in Proportion_Student
                student = Student.objects.get(student_id=student_id)
                Proportion_Student.objects.update_or_create(
                    student=student,
                    request=request,
                    defaults={'percent': weight_R_T}
                )
    except Exception as e:
        logger.error(f"Error in result_student: {e}")

def get_questions_for_exam(lessons, total):
    selected_questions = []
    questions_potential = Question.objects.filter(question_lesson__lesson__in=lessons).distinct()
    for i in range(total):
        question = random.choice(list(questions_potential))
        selected_questions.append(question)
        # Xóa câu hỏi đã chọn khỏi ngân hàng câu hỏi
        questions_potential = questions_potential.exclude(question_id=question.question_id)
    return selected_questions

def Factor(percent, total):
    if percent == 0: 
        percent = 1
    return (total / percent) * 0.5

def calculate_question(total_questions, length, factor):
    return round((total_questions / length) * factor)

def selectQuestions(yccd, num_questions, levels, questions_potential):
    selected_questions = []
    for level in levels:
        if num_questions <= 0:
            break
        choices = questions_potential.filter(question_request__request=yccd, question_level=level)[:num_questions]
        selected_questions.extend(choices)
        num_questions -= len(choices)
        questions_potential = questions_potential.exclude(question_id__in=[q.question_id for q in choices])
    return selected_questions, questions_potential

def adjust_questions(questions, total_questions, questions_potential):
    if len(questions) > total_questions:
        questions = questions[:total_questions]
    elif len(questions) < total_questions:
        additional_questions_needed = total_questions - len(questions)
        potential_list = list(questions_potential)
        if additional_questions_needed > len(potential_list):
            additional_questions_needed = len(potential_list)
        new_questions = random.sample(potential_list, additional_questions_needed)
        questions.extend(new_questions)
    return questions

def get_questions_for_personalization(lessons, total_questions, student):
    questions = []
    yccd_list = Request.objects.filter(lesson_request__lesson__in=lessons).distinct()
    questions_potential = Question.objects.filter(question_request__request__in=yccd_list, question_lesson__lesson__in=lessons).distinct()
    percent_yccd_list = Proportion_Student.objects.filter(student=student, request__in=yccd_list).distinct()
    total_yccd = sum(yccd.percent for yccd in percent_yccd_list)
    
    for yccd in yccd_list:
        percent = percent_yccd_list.filter(request=yccd).first().percent if percent_yccd_list.filter(request=yccd).exists() else 0
        factor = Factor(percent, total_yccd)
        number = calculate_question(total_questions, len(yccd_list), factor)
        max_number = round(0.7 * number)
        min_number = number - max_number
        
        questions_choice = []
        if 0 <= percent <= 30:
            max_levels, min_levels = [1, 2], [3]
        elif 30 < percent <= 70:
            max_levels, min_levels = [2, 3], [4]
        else:  # 70 < percent <= 100
            max_levels, min_levels = [3, 4], [1, 2]

        max_questions, questions_potential = selectQuestions(yccd, max_number, max_levels, questions_potential)
        min_questions, questions_potential = selectQuestions(yccd, min_number, min_levels, questions_potential)
        
        questions_choice.extend(max_questions)
        questions_choice.extend(min_questions)
        questions.extend(questions_choice)
    
    questions = adjust_questions(questions, total_questions, questions_potential)
    return questions


def calculate_classroom_result(classroom, topic):
    # Lấy tất cả các học sinh trong lớp học
    students = Student.objects.filter(class_name=classroom)

    # Lấy tất cả các request liên quan đến topic
    requests = Request.objects.filter(topic=topic)

    # Lấy tất cả các Proportion_Student tương ứng với các học sinh và các request
    proportions = Proportion_Student.objects.filter(student__in=students, request__in=requests)

    # Tính giá trị trung bình của percent
    average_score = proportions.aggregate(Avg('percent'))['percent__avg'] or 0.0

    # Cập nhật hoặc tạo mới ClassroomResult
    classroom_result, created = ClassroomResult.objects.update_or_create(
        classroom=classroom,
        topic=topic,
        defaults={'average_score': round(average_score,2)}
    )

    return classroom_result

def calculate_all_classroom_results():
    # Lặp qua tất cả các lớp học
    classrooms = Classroom.objects.all()
    
    # Lặp qua tất cả các chủ đề
    topics = Topic.objects.all()
    
    for classroom in classrooms:
        for topic in topics:
            # Tính và cập nhật giá trị average_score cho từng classroom và topic
            classroom_result = calculate_classroom_result(classroom, topic)
    return 0