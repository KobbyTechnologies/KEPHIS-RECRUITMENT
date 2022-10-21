from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from datetime import date
from django.contrib import messages
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
    try:
        session = requests.Session()
        session.auth = config.AUTHS
        Access_Point = config.O_DATA.format("/QyRecruitmentRequests")
        submitted = config.O_DATA.format("/QyApplicantJobApplied")
        todays_date = date.today()
        year = todays_date.year

        try:
            responses = session.get(Access_Point, timeout=10).json()
            submitted_res = session.get(submitted, timeout=10).json()
            Job = []
            Sub = []
            for job in responses['value']:
                if job['Submitted_To_Portal'] == True:
                    output_json = json.dumps(job)
                    Job.append(json.loads(output_json))
            for subs in submitted_res['value']:
                if subs['Application_No_'] == request.session['No_']:
                    output_json = json.dumps(subs)
                    Sub.append(json.loads(output_json))
            count = len(Job)
            counter = len(Sub)
        except requests.exceptions.ConnectionError as e:
            print(e)
        my_name = request.session['E_Mail']

        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "year": year,
               "count": count, "counter": counter,
               "job": Job, "my_name": my_name}
    except KeyError as e:
        print(e)
        messages.error(request, "Session has expired, Login Again")
        return redirect("login")
    return render(request, 'main/dashboard.html', ctx)
