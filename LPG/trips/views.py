from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from trips.models import *
from random import randint
from .forms import *
from django.contrib import auth, messages
from django.core.serializers import serialize
import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3
import io

def hello_world(request):
# return HttpResponse("Hello World!")
  return render(request, 'hello.html', {
      'current_time': str(datetime.now()),
})

def test_img(request):
	book = Booklist.objects.all()[1]
	img_url = str(book.picturename)
	aws_access_key_id = settings.AWS_ACCESS_KEY_ID 
	aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
	s3 = boto3.resource('s3', region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
	obj = s3.Object('fjulpg',img_url)
	file_stream = io.BytesIO()
	obj.download_fileobj(file_stream)
	image_data = file_stream.getvalue()
	return HttpResponse(image_data, content_type="image/png")


def index(request):
	return render(request, 'index.html')

	
def game(request):
	return render(request, 'game.html')

def app(request):
	test_num = 3
	test_list = Test.objects.all().order_by('?')[:test_num]
	choice_list = Choice.objects.all()
	type_list = Type.objects.all()
	book_list = Booklist.objects.all()

	return render(request, 'app.html', {
		'test_list': test_list, 'choice_list': choice_list, 'type_list': type_list, 'book_list': book_list, 'test_num':test_num,
		})

def administration(request):
	question_num = Test.objects.all().count()
	book_num = Booklist.objects.all().count()
	pointrecord_num = PointRecord.objects.all().count()
	return render(request, 'administration.html', {'question_num': question_num, 'book_num':book_num, 'pointrecord_num':pointrecord_num})

def booklist(request):
	book_list = Booklist.objects.all()
	
	return render(request, 'booklist.html', {
		'book_list': book_list
		})

def pointrecord_list(request):
	pointrecord_list = PointRecord.objects.all()
	
	return render(request, 'pointrecord_list.html', {
		'pointrecord_list': pointrecord_list
		})

def testlist(request):
	test_list = Test.objects.all()
	choice_list = Choice.objects.all()
	type_list = Type.objects.all()

	return render(request, 'testlist.html', {
		'test_list': test_list, 'choice_list': choice_list, 'type_list': type_list
		})

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/administration/')
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect('/administration/')
    else:
        return render(request, 'login.html', locals())

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/administration/')

def lucky_draw(request):
	pointrecord_list = PointRecord.objects.all()
	pointrecord_num = pointrecord_list.count()
	return render(request, 'lucky_draw.html', {
		'pointrecord_list':pointrecord_list, 'pointrecord_num': pointrecord_num,
		})

def test_new(request):
	if request.method == "POST":
		form = TestForm(request.POST)
		if form.is_valid():
			test = form.save(commit=False)
			test.save()
			return redirect('administration', pk=test.pk)
	else:
		form = TestForm()
	return render(request, 'test_edit.html', {'form':form})

def test_edit(request, pk):
	test = get_object_or_404(Test, pk=pk)
	if request.method == "POST":
		form = TestForm(request.POST, instance=test)
		if form.is_valid():
			test = form.save(commit=False)
			test.save()
			return redirect('administration', pk=test.pk)
	else:
		form = TestForm(instance=test)
	return render(request, 'test_edit.html', {'form': form})
##########未完成
def single_new_test(request):
	test_list = Test.objects.all()
	new_test_id = test_list.order_by('-id')[0]
	new_test_num = new_test_id.id + 1
	return render(request, 'single_new_test.html', {'new_test_num':new_test_num})
##########

def single_new_book(request):
	if request.method == "POST":
		form = BooklistForm(request.POST,request.FILES)
		if form.is_valid():
			book = form.save(commit=False)
			book.created_date = timezone.now()
			book.save()
			return redirect('/booklist/', pk=book.pk)
	else:
		form = BooklistForm()
	return render(request, 'book_edit.html', {'form':form})

def book_edit(request, pk):
	book = get_object_or_404(Booklist, pk=pk)
	if request.method == "POST":
		form = BooklistForm(request.POST, request.FILES, instance=book)
		if form.is_valid():
			book = form.save(commit=False)
			book.created_date = timezone.now()
			book.save()
			return redirect('booklist', pk=book.pk)
	else:
		form = BooklistForm(instance=book)
	return render(request, 'book_edit.html', {'form': form})

def pointrecord_new(request):
	pointrecord_list = PointRecord.objects.all()
	recent_pointrecord_list = pointrecord_list.order_by('-date')[:3]
	if request.method == "POST":
		form = PointRecordForm(request.POST)
		if form.is_valid():
			pointrecord = form.save(commit=False)
			if not pointrecord_list.filter(studentID=pointrecord.studentID , ISBN=pointrecord.ISBN):
				pointrecord.date = timezone.now()
				pointrecord.save()
				messages.success(request, '成功紀錄!')
				return redirect('/pointrecord/new/', pk=pointrecord.pk)
			else:
				messages.error(request, '重複的紀錄無法輸入')
	else:
		form = PointRecordForm()
	return render(request, 'pointrecord_edit.html', {'form':form, 'recent_pointrecord_list': recent_pointrecord_list})

def pointrecord_edit(request, pk):
	pointrecord_list = PointRecord.objects.all()
	pointrecord = get_object_or_404(PointRecord, pk=pk)
	if request.method == "POST":
		form = PointRecordForm(request.POST, instance=pointrecord)
		if form.is_valid():
			pointrecord = form.save(commit=False)
			if not pointrecord_list.filter(studentID=pointrecord.studentID , ISBN=pointrecord.ISBN):
				pointrecord.date = timezone.now()
				pointrecord.save()
				messages.success(request, '成功紀錄!')
	else:
		form = PointRecordForm(instance=pointrecord)
	return render(request, 'pointrecord_edit.html', {'form': form,})

def process_result_from_client(request):
	book_num = 3
	result = int(request.POST.get('result'))
	book_list = Booklist.objects.filter(typeof=result)
	
	library_url = "https://library.lib.fju.edu.tw:444/search*cht/?searchtype=i&searcharg="
	exclude_id_list = list()
	for book in book_list:
		book_library_url = "https://library.lib.fju.edu.tw:444/search*cht/?searchtype=i&searcharg="+ str(book.ISBN)
		res_text = requests.get(book_library_url).text
		soup = BeautifulSoup(res_text , 'html.parser')
		find_soup = soup.find_all('td',width="16%")
		available_bool = 0
		if len(find_soup) > 1:
			for i in find_soup:
				if '可外借' in i.text:
					available_bool = 1
					break
		else:
			if '可外借' in find_soup[0].text:
				available_bool = 1
		if available_bool == 0:
			exclude_id_list.append(book.id)
	result_book_list = book_list.exclude(id__in=exclude_id_list).order_by('?')
	if len(result_book_list) >= book_num:
		result_book_list = result_book_list[:book_num]

	c = 0
	for book in result_book_list:
		result_book_list[c].picturename = result_book_list[c].picturename.url
		c += 1

	serialized_book_list = serialize('json', result_book_list)
	return JsonResponse(serialized_book_list, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json")


def upload_test_file(request):
	test_list = Test.objects.all()
	choice_list = Choice.objects.all()
	type_list = Type.objects.all()
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			print(request.FILES['file'])
			df = pd.read_csv(request.FILES['file'])
			data = df.values.tolist()
			for i in data:
				if not test_list.filter(question=i[0]):
					Test.objects.create(question=i[0])
				i_test = test_list.filter(question=i[0])
				i_choice = Choice.objects.create(question=i_test[0], choice_number=i[1], text=i[2])
				Type.objects.create(choice=i_choice,text=i[3])
			messages.info(request, '上傳成功!')
			return HttpResponseRedirect('/testlist/')
	else:
		form = UploadFileForm()
	return render(request, 'upload_test_file.html', {'form': form})

def upload_booklist_file(request):
	book_list = Booklist.objects.all()
	if request.method == 'POST':
		form = UploadBooklistFileForm(request.POST, request.FILES)
		if form.is_valid():
			print(request.FILES)
			print(request.FILES['file'])
			for i in request.FILES.getlist('image'):
				print(type(i))
				print(str(i))
			
			df = pd.read_csv(request.FILES['file'])
			data = df.values.tolist()
			for i in data:
				book = Booklist.objects.create(title=i[0],author=i[1],publisher=i[2],callnumber=i[3],location=i[4],ISBN=i[5],created_date=timezone.now(),typeof=i[7])
				for j in request.FILES.getlist('image'):
					if str(i[6]) == str(j):
						book.picturename = j
						book.save()
			messages.info(request, '上傳成功!')
			return HttpResponseRedirect('/booklist/')
	else:
		form = UploadBooklistFileForm()
	return render(request, 'upload_booklist_file.html', {'form': form})


def process_share_image(img):
	print(123)