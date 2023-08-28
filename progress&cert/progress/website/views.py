from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Course, Module, Video, Comment, SubComment, Notes,Monitor, Tags, Quiz, Question, Answer, Enrollment
from user.models import Profile, Student, Organization, Teacher
from datetime import datetime, timedelta
from django.contrib.gis.geoip2 import GeoIP2
from django_user_agents.utils import get_user_agent
import requests
import json
from django.urls import reverse
from .utils import searchCourses
from django.shortcuts import redirect

# Create your views here.

def index(request):
    courses = Course.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'website/home.html', context)


def courseviewpage(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
        if enrollment:
            is_enrolled = True
    if is_enrolled:
        return render(request, 'website/courseviewpage.html', {'course': course})
    else:
        return redirect('course_detail',course_id=course.id)


def courseviewpagenote(request, course_id, note_id):
    course = get_object_or_404(Course, id=course_id)
    note = get_object_or_404(Notes, id=note_id)
    is_enrolled = False
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
        if enrollment:
            is_enrolled = True
    if is_enrolled:
        return render(request, 'website/courseviewnote.html', {'course': course, 'note': note})
    else:
        return redirect('course_detail', course_id=course.id)

    



def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('index')
    else:
        profile=Profile.objects.filter(user=request.user)
       
        if profile.exists():
            profile=Profile.objects.get(user=request.user)
            context={
            "profile": profile
            }
            return render(request, 'website/dashboard.html', context)
        else:
            return HttpResponse('Something went wrong')


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    monitor = None
    if request.user.is_authenticated:
        try:
            monitor = Monitor.objects.get(user=request.user, landing_page=request.META.get('HTTP_HOST') + request.META.get('PATH_INFO'), ip=request.META.get('REMOTE_ADDR'))
            monitor.frequency += 1
            monitor.save()
        except Monitor.DoesNotExist:
            pass
    else:
        monitor = Monitor()
        monitor.ip = request.META.get('REMOTE_ADDR')
        g = 'https://geolocation-db.com/jsonp/' + str(monitor.ip)
        response = requests.get(g)
        data = response.content.decode()
        data = data.split("(")[1].strip(")")
        location = json.loads(data)
        monitor.country = location['country_name']
        monitor.city = location['city']
        monitor.region = location['region']
        monitor.timeZone = location['time_zone']
        user_agent = get_user_agent(request)
        monitor.browser = user_agent.browser.family
        monitor.browser_version = user_agent.browser.version_string
        monitor.operating_system = user_agent.os.family
        monitor.device = user_agent.device.family
        monitor.language = request.headers.get('Accept-Language')
        monitor.screen_resolution = request.headers.get('X-Original-Request-Screen-Resolution')
        monitor.referrer = request.META.get('HTTP_REFERER')
        monitor.landing_page = request.META.get('HTTP_HOST') + request.META.get('PATH_INFO')
        monitor.frequency = 1
        monitor.save()
        
    if not request.user.is_authenticated:
        profile_context = {"status": "none"}
    else:
        profile=Profile.objects.filter(user=request.user)
       
        if profile.exists():
            profile=Profile.objects.get(user=request.user)
            profile_context=profile
    context = {"profile": profile_context, "course": course}        
    return render(request, 'website/course_detail.html', context)





def update_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if(course.teacher.profile == request.user.profile):
        if request.method == 'POST':
            course.name = request.POST.get('name')
            course.description = request.POST.get('description')
            course.price = request.POST.get('price')
            course.small_description = request.POST.get('small_description')
            course.learned = request.POST.get('learned')
            tags = request.POST.get('tags').split(',')
            course.update_at = datetime.today()

            for tag in tags:
                tag = tag.strip()
                if tag:
                    obj, created = Tags.objects.get_or_create(name=tag)
                    course.tags.add(obj)
            course.save()
            return redirect('course_detail', course_id=course.id)
        return render(request, 'website/update_course.html', {'course': course})
    else:
        return redirect('course_detail', course_id=course.id)


def course(request):
    teacher=get_object_or_404(Teacher,profile=request.user.profile)
    courses=Course.objects.filter(teacher=teacher)
    context={
        "courses":courses,
    }
    return render(request,'website/courses.html', context)




def course_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course)
    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'website/course_module_details.html', context=context)

def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated:
        return redirect('login')
    enrollment, created = Enrollment.objects.get_or_create(course=course, student=request.user)
    if created:
        messages.success(request, f"You have successfully enrolled in {course.name}.")
    else:
        messages.warning(request, f"You are already enrolled in {course.name}.")
    return redirect(reverse('courseviewpage', args=[course_id]))

def analytics(request):
    return render(request, 'website/analytics.html')