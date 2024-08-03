from django.shortcuts import render, get_object_or_404,redirect

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, decorators, logout
from django.views import View
from .models import*
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .operation import*
import logging
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum

logger = logging.getLogger(__name__)
# Create your views here.
@decorators.login_required(login_url="login")
def index(request):
    user = request.user
    for group in user.groups.all():
        if group.name == "Teacher":
            classrooms = Classroom.objects.all()
            classroom_results = ClassroomResult.objects.select_related('classroom', 'topic').all()
            request_totals = Proportion_Student.objects.values('request').annotate(total_percent=Sum('percent'))
            contents = {
                'classrooms': classrooms,
                'classroom_results': classroom_results,
                'user_name': user.username,
            }
            return render(request, "HeThongHoTroLT/index_gv.html", contents)
    
    try:
        student = Student.objects.get(student_id=user.username)
    except Student.DoesNotExist:
        return HttpResponse("Không tồn tại học sinh này.")
    
    proportion_students = Proportion_Student.objects.filter(student=student)
    
    pro_topics = {
        'A': 0.0,
        'B': 0.0,
        'D': 0.0,
        'F': 0.0,
        'G': 0.0,
        'E': 0.0,
    }
    
    def convert_to_float(value):
        if isinstance(value, str):
            try:
                value = value.replace(',', '.')
                return float(value)
            except ValueError:
                return 0.0
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return 0.0
    
    main_suggest = []
    suggest_more = []
    
    for proportion in proportion_students:
        request_topic = proportion.request.topic.topic_id
        request_percent = convert_to_float(proportion.request.percent)
        proportion_percent = convert_to_float(proportion.percent)
        
        pro_topics[request_topic] += proportion_percent * request_percent
        
        if proportion_percent == 0:
            suggest_more.append(proportion.request)
        elif proportion_percent < 60:
            main_suggest.append({
                'request': proportion.request,
                'lesson': Lesson.objects.filter(lesson_request__request=proportion.request).distinct()
            })
    
    topics = [{'name': key, 'percent': round(value, 2)} for key, value in pro_topics.items()]
    # Tính tổng tất cả các percent theo request và lấy 10 đối tượng thấp nhất, không tính các giá trị bằng 0
    request_totals = (
                    Proportion_Student.objects.values('request')
                    .annotate(total_percent=Sum('percent'))
                    .filter(total_percent__gt=0)
                    .order_by('total_percent')[:5]
                    )
    # Lấy danh sách request_id từ 10 request có tổng percent thấp nhất
    request_ids = [total['request'] for total in request_totals]

    # Lấy các đối tượng Request tương ứng và giữ nguyên thứ tự sắp xếp theo tổng percent
    general_suggest = Request.objects.filter(request_id__in=request_ids).order_by('request_id')
    contents = {
        'user_name': user.username,
        'topics': topics,
        'main_suggest': main_suggest,
        'suggest_more': suggest_more,
        'general_suggest':general_suggest
    }
    return render(request, "HeThongHoTroLT/index_hs.html", contents)

@decorators.login_required(login_url='login')
def _classes(request):
    classrooms = Classroom.objects.all()
    contents={'classrooms': classrooms}
    return render(request, "HeThongHoTroLT/_classes.html",contents)
@decorators.login_required(login_url='login')
def exam(request):
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break
    exams = Inf_Exam_Framework.objects.all()
    contents = {'pos': pos, 'exams': exams}
    return render(request, "HeThongHoTroLT/exam.html", contents)
@decorators.login_required(login_url='login')
def practice(request):
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break

    student = request.user.username
    # Lấy tất cả các bài kiểm tra của học sinh hiện tại
    tests = Test.objects.filter(student__student_id=student)
    # Lấy tất cả các bài kiểm tra có exam không null và của học sinh hiện tại
    tests_with_exam = Test.objects.filter(exam__isnull=False)
    
    # Hợp nhất hai QuerySet
    combined_tests = tests.union(tests_with_exam)

    contents = {'pos': pos, 'tests': combined_tests}
    return render(request, "HeThongHoTroLT/practice.html", contents)
@decorators.login_required(login_url='login')
def forgot_password(request):
    return render(request, "HeThongHoTroLT/forgot-password.html")
@decorators.login_required(login_url='login')
def register(request):
    return render(request, "HeThongHoTroLT/register.html")
@decorators.login_required(login_url='login')
def utilities_animation(request):
    return render(request, "HeThongHoTroLT/utilities-animation.html")
@decorators.login_required(login_url='login')
def utilities_color(request):
    return render(request, "HeThongHoTroLT/utilities-color.html")
@decorators.login_required(login_url='login')
def utilities_other(request):
    return render(request, "HeThongHoTroLT/utilities-other.html")
@decorators.login_required(login_url='login')
def detail_exam(request, exam_id):
    pos = 'HeThongHoTroLT/base_student.html'
    
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break
    
    # Lấy exam từ exam_id
    # exam = Inf_Exam_Framework.objects.get(exam_id=exam_id)
    
    tests = Test.objects.filter(exam=exam_id)
    if tests.exists():
        test = tests.first()
    else:
        test = None  # Hoặc xử lý khi không tìm thấy test nào
    
    # Lấy tất cả bài học liên quan đến exam
    test_lessons = Test_Lesson.objects.filter(test=exam_id).distinct()
    lessons = Lesson.objects.filter(lesson_id__in=test_lessons.values_list('lesson_id', flat=True)).distinct()
    
    # Lấy tất cả các yêu cầu (Request) liên quan đến danh sách các bài học
    requests = Request.objects.filter(lesson_request__lesson__in=lessons).distinct()
    contents = {'pos': pos,'test': test,'lessons': lessons,'requests': requests,'exam': test}
    return render(request, "HeThongHoTroLT/detail_exam.html", contents)
class class_login(View):
    def get(self,request):
        return render(request, "HeThongHoTroLT/login.html")
    def post(self,request):
        user_name = request.POST.get('username')
        Password = request.POST.get('password')
        my_user = authenticate(username=user_name,password=Password)
        if my_user is None:
            return HttpResponse("Lỗi đăng nhập")
        login(request,my_user)
        return redirect('index')
def _404(request):
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break
    return render(request, "HeThongHoTroLT/404.html",{'pos':pos})
def blank(request):
    return render(request, "HeThongHoTroLT/blank.html")
def detail_class(request, classroom_id):
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break

    # Lấy đối tượng Classroom dựa trên classroom_id
    classroom = get_object_or_404(Classroom, classroom_id=classroom_id)
    
    # Lấy danh sách học sinh thuộc lớp đó
    students = Student.objects.filter(class_name=classroom)

    return render(request, "HeThongHoTroLT/detail_class.html", {
        'pos': pos,
        'classroom': classroom,
        'students': students
    })
def add_exam(request):
    pos = 'student'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'teacher'
            break
    lessons = Lesson.objects.all()
    contents = {'pos':pos, 'lessons':lessons}
    return render(request, "HeThongHoTroLT/add_exam.html",contents)
def add_practice(request):
    pos = 'student'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'teacher'
            break
    lessons = Lesson.objects.all()
    contents = {'pos':pos, 'lessons':lessons}
    return render(request, "HeThongHoTroLT/add_practice.html",contents)
logger = logging.getLogger(__name__)
def save_a_practice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info("Received data: %s", data)  # Kiểm tra dữ liệu nhận được
            student = get_object_or_404(Student, student_id=request.user.username)
            # Lấy danh sách mã kiểm tra của các bài kiểm tra mà học sinh đã tạo
            test_ids = Test.objects.filter(student=student).values_list('test_id', flat=True)
            test_name = data.get('practice_name')
            time_limit = data.get('time_limit')
            question_limit = data.get('question_limit')
            now = timezone.now()
            # Tạo ID cho bài kiểm tra mới
            id_prefix_map = {
                "Luyện tập Chủ đề A": "A",
                "Luyện tập Chủ đề B": "B",
                "Luyện tập Chủ đề D": "D",
                "Luyện tập Chủ đề E": "E",
                "Luyện tập Chủ đề F": "F",
                "Luyện tập Chủ đề G": "G",
                "Bài luyện tập tự chọn": now.strftime("%Y%m%d"),
            }

            id = "LT" +id_prefix_map.get(test_name) + student.student_id

            if id in test_ids:
                # Cập nhật lại date_update, numer_q, test_time
                test = Test.objects.get(test_id=id)
                test.date_update = now
                test.numer_q = question_limit
                test.test_time = time_limit
                test.save()
                
            else:
                # Tạo một bài luyện tập mới
                test = Test.objects.create(
                    test_id=id, 
                    test_name=test_name, 
                    date_update=now, 
                    date_create=now, 
                    factor=1, 
                    numer_q=question_limit, 
                    test_time=time_limit, 
                    student=student
                )
            lessons_data = Lesson.objects.filter(topic_id=id_prefix_map.get(test_name)).values_list('lesson_id', flat=True)
            if not lessons_data:
                lessons_data = data.get('lessons', [])
            # Lưu các bài học được chọn
            for lesson_id in lessons_data:
                lesson_instance = get_object_or_404(Lesson, lesson_id=lesson_id)
                Test_Lesson.objects.create(test=test, lesson=lesson_instance)

            return JsonResponse({'success': True})

        except Lesson.DoesNotExist:
            logger.error("Lesson does not exist")
            return JsonResponse({'error': 'Lesson không tồn tại'}, status=400)
        except Exception as e:
            logger.error("Error occurred: %s", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức POST'}, status=405)
def detail_practice(request,test_id):
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            break
    test = Test.objects.get(test_id=test_id) 
    # Lấy tất cả bài học liên quan đến exam
    test_lessons = Test_Lesson.objects.filter(test=test_id).distinct()
    lessons = Lesson.objects.filter(lesson_id__in=test_lessons.values_list('lesson_id', flat=True)).distinct()
    
   # Lấy tất cả các yêu cầu (Request) liên quan đến danh sách các bài học 
    requests = Request.objects.filter(lesson_request__lesson__in=lessons).distinct()
    contents= {'pos':pos,'test':test,'lessons': lessons,'requests':requests}
    return render(request, "HeThongHoTroLT/detail_practice.html",contents)
def do(request, test_id):
    referer = request.META.get('HTTP_REFERER', '')
    pos = 'HeThongHoTroLT/base_student.html'
    for group in request.user.groups.all():
        if group.name == "Teacher":
            pos = 'HeThongHoTroLT/base_teacher.html'
            # khi là giáo viên, tập kiểm tra được chọn chỉ đơn giản là câu hỏi và số lượng câu hỏi
            test = get_object_or_404(Test, test_id=test_id)
            test_lessons = Test_Lesson.objects.filter(test=test_id).distinct()
            lessons = Lesson.objects.filter(lesson_id__in=test_lessons.values_list('lesson_id', flat=True)).distinct()
            questions = get_questions_for_exam(lessons, test.numer_q)
            question_answer_list = []
            for question in questions:
                answers = Answer.objects.filter(question=question)
                question_answer_list.append({'question': question, 'answers': answers})
            contents = {'pos': pos, 'test': test, 'question_answer_list': question_answer_list}
            return render(request, "HeThongHoTroLT/do.html", contents)
    
    test = get_object_or_404(Test, test_id=test_id)
    test_lessons = Test_Lesson.objects.filter(test=test_id).distinct()
    lessons = Lesson.objects.filter(lesson_id__in=test_lessons.values_list('lesson_id', flat=True)).distinct()
    # xác định bài tập và số lượng câu hỏi cho các loại bài kiểm tra
    student = Student.objects.get(student_id=request.user.username)
    if 'exam' in referer:
        questions = get_questions_for_exam(lessons, test.numer_q)
    else:
        questions = get_questions_for_personalization(lessons, test.numer_q, student)
    question_answer_list = []
    for question in questions:
        answers = Answer.objects.filter(question=question)
        question_answer_list.append({'question': question, 'answers': answers})
    contents = {'pos': pos, 'test': test, 'question_answer_list': question_answer_list}
    return render(request, "HeThongHoTroLT/do.html", contents)
            
def result_test(request):
    pos = 'HeThongHoTroLT/base_student.html'
    if request.user.groups.filter(name="Teacher").exists():
        pos = 'HeThongHoTroLT/base_teacher.html'
    
    if request.method == "POST":
        test_id = request.POST.get('test_id')
        test = Test.objects.get(test_id=test_id)
        student = Student.objects.get(student_id=request.user.username)
        result_now = f"{test_id}_{request.user.username}?1"
        result_all = Student_result.objects.values_list('result_id', flat=True)
        
        times = 1
        for result_id in result_all:
            if result_now in result_id:
                times = int(result_id.split('?')[1]) + 1
                result_now = f"{result_id.split('?')[0]}?{times}"
                
        student_result = Student_result.objects.create(
            result_id=result_now,
            student=student,
            test=test,
            score=0.0,
            times=times
        )
        
        total_score = 0
        total_questions = 0
        question_results = []
        
        for question_id, answer_id in request.POST.items():
            if question_id.startswith('answers[') and question_id.endswith(']'):
                question_id = question_id[8:-1]
                question = Question.objects.get(question_id=question_id)
                answer = Answer.objects.get(answer_id=answer_id)

                is_correct = answer.answer_right
                if is_correct:
                    total_score += 1
                total_questions += 1

                Detail_Test_Student.objects.create(
                    result=student_result,
                    question=question,
                    chose=answer.answer_content,
                    returned=is_correct
                )
                question_results.append({
                    'question': question,
                    'chosen_answer': answer,
                    'is_correct': is_correct,
                    'answers': Answer.objects.filter(question=question)
                })

        student_result.score = (total_score / total_questions) * 10 if total_questions > 0 else 0
        student_result.save()

        contents = {
            'pos': pos,
            'test': test,
            'question_results': question_results,
            'total_score': student_result.score
        }
        return render(request, "HeThongHoTroLT/result_test.html", contents)

    return render(request, "HeThongHoTroLT/result_test.html", {'pos': pos})

@csrf_exempt
def save_exam_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_name = data.get('test_name')
            lessons = data.get('lessons', [])
            exam_framework = Inf_Exam_Framework.objects.filter(exam_name=test_name).first()
            factor = 1
            numer_q = 15
            now = timezone.now()
            time_test=15
            if exam_framework:
                # Xóa các bài học hiện tại của bài kiểm tra
                Test_Lesson.objects.filter(exam=exam_framework).delete()
                test = Test.objects.filter(test_id=exam_framework.exam_id).first()
                if test:
                    test.date_update = now
                    test.save()
            else:
                # Tạo ID cho bài kiểm tra mới
                if test_name == "Kiểm tra 15' HK1 lần 1":
                    id = "15'HK1_1"
                elif test_name == "Kiểm tra 15' HK1 lần 2":
                    id = "15'HK1_2"
                elif test_name == "Kiểm tra 15' HK1 lần 3":
                    id = "15'HK1_3"
                elif test_name == "Kiểm tra 15' HK2 lần 1":
                    id = "15'HK2_1"
                elif test_name == "Kiểm tra 15' HK2 lần 2":
                    id = "15'HK2_2"
                elif test_name == "Kiểm tra 15' HK2 lần 3":
                    id = "15'HK2_3"
                elif test_name == "Kiểm tra 1 tiết HK1":
                    id = "1'HK1_1"
                    factor = 2
                    numer_q = 40
                    time_test=45
                elif test_name == "Kiểm tra 1 tiết HK2":
                    id = "1'HK2_1"
                    factor = 2
                    numer_q = 40
                    time_test=45
                elif test_name == "Kiểm tra cuối KH1":
                    id = "CK'HK1"
                    factor = 3
                    numer_q = 40
                    time_test=45
                elif test_name == "Kiểm tra cuối KH2":
                    id = "CK'HK2"
                    factor = 3
                    numer_q = 40
                    time_test=45
                else:
                    id = "UNKNOWN"

                # Tạo đối tượng Inf_Exam_Framework và Test mới
                exam_framework = Inf_Exam_Framework.objects.create(exam_id=id, exam_name=test_name)
                test = Test.objects.create(test_id=id, test_name=test_name, date_update=now, date_create=now, factor=factor, exam=exam_framework, numer_q=numer_q, test_time=time_test)

            # Lưu các bài học được chọn
            for lesson in lessons:
                lesson_instance = Lesson.objects.get(lesson_id=lesson['id'])
                Test_Lesson.objects.create(test=test, lesson=lesson_instance)

            return redirect(exam)

        except Lesson.DoesNotExist:
            return JsonResponse({'error': 'Lesson không tồn tại'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức POST'}, status=405)

@require_POST
def reload_results(request):
    student_id = request.user.username
    result_student(student_id)
    return redirect('index')
@require_POST
def reload_classroom_results(request):
    calculate_all_classroom_results()
    print('vào được rồi!')
    return redirect('index')
def user_logout(request):
    logout(request)
    return redirect('login')