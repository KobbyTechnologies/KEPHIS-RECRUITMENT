from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime

# Create your views here.


# def canvas(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('images')
#         for image in images:
#             photo = Photo.objects.create(
#                 image=image,
#             )
#         return redirect('main')
#     return render(request, 'offcanvas.html')


def dashboard(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyCompanyJobs")
    year = request.session['years']
    try:
        response = session.get(Access_Point, timeout=10).json()
        res = response['value']
        print(res)
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "year": year, "res": res}
    return render(request, 'main/dashboard.html', ctx)
