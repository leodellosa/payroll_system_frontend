import os
from django.shortcuts import get_object_or_404, redirect, render
from .forms import EmployeeForm
from .models import Employee
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, Http404
import requests
from django.views.decorators.csrf import csrf_exempt
from payroll_system.config import EMPLOYEE_API_URL

# BASE_API_URL: str = "http://127.0.0.1:8001/api/v1"


def employeeList(request):
    base_url = f"{EMPLOYEE_API_URL}/employeeList"

    params = {
        "search": request.GET.get("search", ""),
        "hire_date_from": request.GET.get("hire_date_from"),
        "hire_date_to": request.GET.get("hire_date_to"),
        "status": request.GET.get("status"),
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            return render(request, "employee_list.html", {
                "employees": data,
                "search_query": params["search"],
                "hire_date_from": params["hire_date_from"],
                "hire_date_to": params["hire_date_to"],
                "status_filter": params["status"],
            })
        else:
            return HttpResponse(f"Error fetching data: {data.get('detail')}", status=response.status_code)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Backend error: {str(e)}", status=500)

from datetime import date, datetime
from decimal import Decimal
def serialize_data(data):
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            data[key] = float(value)
    return data

from django.contrib.messages import get_messages

@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        
        if form.is_valid():
            employee_data = serialize_data(form.cleaned_data)
            base_url = f"{EMPLOYEE_API_URL}/employee/add"
            try:
                response = requests.post(
                    base_url,
                    json=employee_data,
                    timeout=5
                )
                print("response", response)
                data = response.json()
                print("log", data)  
                if response.status_code == 200 and data.get("success"):
                    messages.success(request, "Employee added successfully!")
                    return redirect('add_employee')
                else:
                    messages.error(request, data.get("error", data.get("detail", "Failed to add employee.")))
                    return render(request, 'add_employee.html', {'form': form})
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to API: {str(e)}")
                return render(request, 'add_employee.html', {'form': form})
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")
            return render(request, 'add_employee.html', {'form': form})
    else:
        form = EmployeeForm()
        return render(request, 'add_employee.html', {'form': form})

def employeeDetails(request, employee_id):
    try:
        base_url = f"{EMPLOYEE_API_URL}/{employee_id}"
        response = requests.get(base_url)

        if response.status_code == 200:
            employee = response.json()
            return render(request, 'employee_details.html', {'employee': employee})
        else:
            return HttpResponse(f"Error fetching employee details: {response.text}", status=response.status_code)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Backend service error: {str(e)}", status=500)

def editEmployee(request, employee_id):
     # Capture the referrer URL
    referer = request.META.get('HTTP_REFERER', '/')

    # Get employee data from FastAPI
    try:
        base_url = f"{EMPLOYEE_API_URL}/{employee_id}"
        response = requests.get(base_url)
        if response.status_code == 404:
            raise Http404("Employee not found")
        elif response.status_code != 200:
            return HttpResponse("Error fetching employee data from API", status=response.status_code)
        
        employee_data = response.json()

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Backend service error: {str(e)}", status=500)

    # POST: update employee
    if request.method == 'POST' and request.POST.get('_method') == 'PUT':
        form = EmployeeForm(request.POST, initial=employee_data)
        if form.is_valid():
            try:
                print("form.cleaned_data", form.cleaned_data)
                payload = serialize_data(form.cleaned_data)
                print("Payload being sent to API:", payload)  
                update_response = requests.put(
                    f"{EMPLOYEE_API_URL}/employee/edit/{employee_id}",
                    json=payload,
                    headers={"Content-Type": "application/json"}, 
                    timeout=5
                )
                print("update_response", update_response)
                if update_response.status_code == 200:
                    messages.success(request, "Employee updated successfully!")
                    return redirect('employee_details', employee_id=employee_id)
                else:
                    print("API Response Content:", update_response.text)
                    api_error = update_response.json().get("error", update_response.json().get("detail", "Failed to update employee."))
                    messages.error(request, api_error)
                    return redirect('employee_details', employee_id=employee_id)
            except Exception as e:
                messages.error(request, f"An error occurred while updating: {str(e)}")
                return redirect('employee_details', employee_id=employee_id)
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")
            return render(request, 'edit_employee.html', {'form': form, 'employee': employee_data, 'referer': referer})
    else:
        form = EmployeeForm(initial=employee_data)

    return render(request, 'edit_employee.html', {
        'form': form,
        'employee': employee_data,
        'referer': referer
    })

def updateEmployeeStatus(request, employee_id):
    try:
        base_url = f"{EMPLOYEE_API_URL}/{employee_id}"
        response = requests.get(base_url)
        if response.status_code == 404:
            raise Http404("Employee not found")
        elif response.status_code != 200:
            return HttpResponse("Error fetching employee data", status=response.status_code)

        employee_data = response.json()

        new_status = "Inactive" if employee_data["status"] == "Active" else "Active"
        update_response = requests.put(
            f"{EMPLOYEE_API_URL}/employee/status/{employee_id}",
            params={"status": new_status},
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if update_response.status_code == 200:
            messages.success(request, f"Employee status updated to {new_status}.")
        else:
            error_msg = update_response.json().get("detail", "Failed to update employee status.")
            messages.error(request, error_msg)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error communicating with API: {str(e)}", status=500)

    return redirect('employee_list')
