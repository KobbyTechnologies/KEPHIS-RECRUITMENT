from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime

# Create your views here.


def CompanyJobs(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyCompanyJobs")
    year = request.session['years']
    try:
        response = session.get(Access_Point, timeout=10).json()
        res = response['value']
    except requests.exceptions.ConnectionError as e:
        print(e)
    count = len(res)
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "year": year,
           "count": count, "res": res}
    return render(request, 'job.html', ctx)


def JobDetail(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyCompanyJobs")
    Qualifications = config.O_DATA.format("/QyJobAcademicQualifications")
    Experience = config.O_DATA.format("/QyJobExperienceQualifications")
    Industry = config.O_DATA.format("/QyJobIndustries")
    Memberships = config.O_DATA.format("/QyProfessionalMemberships")
    res = ''
    E_response = ''
    try:
        response = session.get(Access_Point, timeout=10).json()
        Qualifications_res = session.get(Qualifications, timeout=10).json()
        Experience_res = session.get(Experience, timeout=10).json()
        Industry_res = session.get(Industry, timeout=10).json()
        Memberships_res = session.get(Memberships, timeout=10).json()

        All_Industry = Industry_res['value']
        All_Memberships = Memberships_res['value']
        for job in response['value']:
            if job['Job_ID'] == pk:
                res = job
        for Qualifications in Qualifications_res['value']:
            if Qualifications['Job_ID'] == pk:
                response = Qualifications
        for Experience in Experience_res['value']:
            if Experience['Job_ID'] == pk:
                E_response = Experience
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "Qualifications": response, "experience": E_response,
           "industry": All_Industry, "member": All_Memberships}
    return render(request, 'jobDetail.html', ctx)
