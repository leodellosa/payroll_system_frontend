from django.shortcuts import get_object_or_404, redirect, render
from .forms import PayrollForm,PayrollUploadForm
from .models import Payroll
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from employee.models import Employee
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.contrib.staticfiles import finders
from django.db.models import Min, Max
from django.utils import timezone

from django.utils.dateparse import parse_date
from django.db import IntegrityError

from datetime import datetime
from django.core.exceptions import ValidationError
from decimal import Decimal
from payroll_system.config import PAYROLL_API_URL,EMPLOYEE_API_URL
import requests


def dashboard(request):
    return redirect('employee_list')

def generatePayroll(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        base_url = f"{PAYROLL_API_URL}/generate"

        if form.is_valid():
            try:
                employee = form.cleaned_data['employee']
                time_in = form.cleaned_data['time_in']
                time_out = form.cleaned_data['time_out']

                print("employee",employee)

                if isinstance(time_in, str) and time_in:
                    time_in = parse_datetime(time_in)
                if isinstance(time_out, str) and time_out:
                    time_out = parse_datetime(time_out)

                total_hours_worked = form.cleaned_data['total_hours_worked']
                deductions = form.cleaned_data['deductions']
                subtotal = form.cleaned_data['subtotal']
                net_salary = form.cleaned_data['net_salary']
                deduction_remarks = form.cleaned_data['deduction_remarks']
                project = form.cleaned_data['project']
                daily_rate = form.cleaned_data['daily_rate']
                overtime_pay = form.cleaned_data['overtime_pay']
                overtime_hour = form.cleaned_data['overtime_hour']
                night_differential_pay = form.cleaned_data['night_differential_pay']
                night_differential_hour = form.cleaned_data['night_differential_hour']
                allowance = form.cleaned_data['allowance']
                date = time_in.date() if time_in else None
            
                payroll = {
                    "employee_id": employee,
                    "time_in": time_in.isoformat() if time_in else None,
                    "time_out": time_out.isoformat() if time_out else None,
                    "total_hours_worked": float(total_hours_worked) if total_hours_worked else 0.0,
                    "deductions": float(deductions) if deductions else 0.0,
                    "subtotal": float(subtotal) if subtotal else 0.0,
                    "net_salary": float(net_salary) if net_salary else 0.0,
                    "deduction_remarks": deduction_remarks,
                    "project": project,
                    "daily_rate": float(daily_rate) if daily_rate else 0.0,
                    "overtime_pay": float(overtime_pay) if overtime_pay else 0.0,
                    "overtime_hour": float(overtime_hour) if overtime_hour else 0.0,
                    "night_differential_pay": float(night_differential_pay) if night_differential_pay else 0.0,
                    "night_differential_hour": float(night_differential_hour) if night_differential_hour else 0.0,
                    "allowance": float(allowance) if allowance else 0.0,
                    "date": date.isoformat() if date else None,
                }
                print("valid",payroll)
                print("base_url",base_url)
                print("employee",employee)
                response = requests.post(
                    base_url,
                    params={"employee_id": employee},  # Send employee_id as a query parameter
                    json=payroll  # Send payroll data in the body of the request
                )
                print("response",response)

                if response.status_code == 201:
                    messages.success(request, "Payroll has been successfully generated!")
                    # Optionally, you can pass additional context or data here if needed
                    context = {
                        'form': PayrollForm(),
                        'EMPLOYEE_API_URL': EMPLOYEE_API_URL
                    }
                    return render(request, 'generate_payroll.html', context=context)
                else:
                    messages.error(request, f"Failed to generate payroll: {response.text}")
                    context = {
                        'form': PayrollForm(),
                        'EMPLOYEE_API_URL': EMPLOYEE_API_URL
                    }
                    return render(request, 'generate_payroll.html', context=context)
                
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'generate_payroll.html', {'form': form})
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")
            return render(request, 'generate_payroll.html', {
                'form': form,
                'total_hours_worked': form.cleaned_data.get('total_hours_worked', 0),
                'EMPLOYEE_API_URL': EMPLOYEE_API_URL
            })

    else:
        context = {
                    'form': PayrollForm(),
                    'EMPLOYEE_API_URL': EMPLOYEE_API_URL
                }
        print("context",context)      
        return render(request,'generate_payroll.html',context=context)

def payrollSummary(request):
   
    selected_employee = None
    selected_employee_id = request.GET.get('employee')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    payrolls = []
    totals = {}
    employees = []

    base_url = f"{PAYROLL_API_URL}/summary"

    if request.method == 'GET':
        try:
            emp_response = requests.get(EMPLOYEE_API_URL)
            employees = emp_response.json()
            query_params = {}
            if selected_employee_id:
                selected_employee = next(
                (emp for emp in employees if str(emp["id"]) == str(selected_employee_id)),
                None)
                query_params['employee_id'] = selected_employee_id
                if start_date:
                    query_params['start_date'] = start_date
                if end_date:
                    query_params['end_date'] = end_date

                response = requests.get(base_url, params=query_params)
                if response.status_code == 200:
                    data = response.json()
                    payrolls = data.get("payrolls", [])
                    totals = data.get("totals", {})
                    return render(request, 'payroll_summary.html', {
                        'payrolls': payrolls,
                        'employees': employees,
                        'selected_employee': selected_employee,
                        'selected_employee_id': selected_employee_id,
                        'start_date': start_date,
                        'end_date': end_date,
                        'total_hours_worked': totals.get("total_hours_worked", 0),
                        'total_overtime_pay': totals.get("overtime_pay", 0),
                        'total_night_differential_pay': totals.get("night_differential_pay", 0),
                        'allowance': totals.get("allowance", 0),
                        'total_deductions': totals.get("deductions", 0),
                        'total_gross_salary': totals.get("gross_salary", 0),
                        'total_net_salary': totals.get("net_salary", 0),
                    })
                else:
                    messages.error(request, f"Failed to fetch payroll data: {response.text}")
          
        except Exception as err:
            messages.error(request, f"An unexpected error occurred: {err}")
        
    return render(request, 'payroll_summary.html', {
        'payrolls': payrolls,
        'employees': employees,
        'selected_employee': selected_employee,
        'selected_employee_id': selected_employee_id,
        'start_date': start_date,
        'end_date': end_date
    })

def editPayroll(request, payroll_id):
    base_url = f"{PAYROLL_API_URL}/update"
    try:
        response = requests.get(f"{PAYROLL_API_URL}/{payroll_id}")
        if response.status_code != 200:
            messages.error(request, f"Failed to load payroll data: {response.json().get('detail', 'Unknown error')}")
            return redirect('payroll_summary')
        payroll_data = response.json()['payroll']
        employee_id = payroll_data['employee_id']
        print("employee_id",employee_id)
        employee_response = requests.get(f"{EMPLOYEE_API_URL}/{employee_id}")
        daily_rate = employee_response.json()['salary']
       
    except Exception as e:
        messages.error(request, f"Error contacting payroll API: {e}")
        return redirect('payroll_summary')

    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            try:
                employee = form.cleaned_data['employee']
                time_in = form.cleaned_data['time_in']
                time_out = form.cleaned_data['time_out']
                total_hours_worked = form.cleaned_data['total_hours_worked']
                deductions = form.cleaned_data['deductions']
                subtotal = form.cleaned_data['subtotal']
                net_salary = form.cleaned_data['net_salary']
                deduction_remarks = form.cleaned_data['deduction_remarks']
                project = form.cleaned_data['project']
                daily_rate = form.cleaned_data['daily_rate']
                overtime_pay = form.cleaned_data['overtime_pay']
                overtime_hour = form.cleaned_data['overtime_hour']
                night_differential_pay = form.cleaned_data['night_differential_pay']
                night_differential_hour = form.cleaned_data['night_differential_hour']
                allowance = form.cleaned_data['allowance']

                # Send updated data to FastAPI
                payload = {
                    "id": payroll_id,
                    "employee_id": employee,
                    "time_in": time_in.isoformat() if time_in else None,
                    "time_out": time_out.isoformat() if time_out else None,
                    "total_hours_worked": float(total_hours_worked) if total_hours_worked else 0.0,
                    "deductions": float(deductions) if deductions else 0.0,
                    "subtotal": float(subtotal) if subtotal else 0.0,
                    "net_salary": float(net_salary) if net_salary else 0.0,
                    "deduction_remarks": deduction_remarks,
                    "project": project,
                    "daily_rate": float(daily_rate) if daily_rate else 0.0,
                    "overtime_pay": float(overtime_pay) if overtime_pay else 0.0,
                    "overtime_hour": float(overtime_hour) if overtime_hour else 0.0,
                    "night_differential_pay": float(night_differential_pay) if night_differential_pay else 0.0,
                    "night_differential_hour": float(night_differential_hour) if night_differential_hour else 0.0,
                    "allowance": float(allowance) if allowance else 0.0,
                }
                print("Payload being sent to API:", payload)
                put_response = requests.put(
                    f"{base_url}",
                    params={"employee_id": employee, "payroll_id": payroll_id},
                    json=payload
                )

                if put_response.status_code == 200:
                    messages.success(request, 'Payroll record updated successfully.')
                    return redirect('payroll_summary')
                else:
                    messages.error(request, f"Update failed: {put_response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                messages.error(request, f"Unexpected error: {e}")
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")
            return render(request, 'edit_payroll.html', {'form': form})
    else:
        # Pre-fill the form with data from FastAPI
        print("employee",payroll_data['employee_id'])
        form = PayrollForm(initial={
            'employee': employee_id,
            'daily_rate': daily_rate,
            'time_in': payroll_data['time_in'],
            'time_out': payroll_data['time_out'],
            'total_hours_worked': payroll_data['total_hours_worked'],   
            'deductions': payroll_data['deductions'],
            'subtotal': payroll_data['subtotal'],
            'net_salary': payroll_data['net_salary'],
            'deduction_remarks': payroll_data['deduction_remarks'],
            'project': payroll_data['project'],
            'overtime_pay': payroll_data['overtime_pay'],
            'overtime_hour': payroll_data['overtime_hour'],
            'night_differential_pay': payroll_data['night_differential_pay'],
            'night_differential_hour': payroll_data['night_differential_hour'],
            'allowance': payroll_data['allowance'],

        })

    return render(request, 'edit_payroll.html', {'form': form})


def deletePayroll(request, payroll_id):
    if request.method == 'POST':
        try:
            response = requests.delete(f"{PAYROLL_API_URL}/delete", params={"payroll_id": payroll_id})
            if response.status_code == 200:
                messages.success(request, 'Payroll record deleted successfully.')
            else:
                detail = response.json().get('detail', 'Unknown error')
                messages.error(request, f"Failed to delete payroll record: {detail}")
        except Exception as e:
            messages.error(request, f"Error deleting payroll: {e}")

    return redirect('payroll_summary')
       
def exportPayslipPdf(request, employee_id):
    """
    Calls FastAPI endpoint to generate PDF for the employee's payslip,
    and returns it directly to the user as a file download.
    """
    base_url = f"{PAYROLL_API_URL}/payslip/pdf"
    try:
        # Request PDF from FastAPI
        response = requests.get(
            base_url,
            params={"employee_id": employee_id},
            stream=True
        )

        if response.status_code == 200:
            # Use content-disposition to make it a file download
            filename = f"payslip_employee_{employee_id}.pdf"
            pdf_file = response.content

            response_django = HttpResponse(pdf_file, content_type='application/pdf')
            response_django['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response_django

        else:
            # Extract error message if available
            try:
                error_message = response.json().get('detail', 'Failed to generate PDF.')
            except Exception:
                error_message = 'Failed to generate PDF.'
            messages.error(request, error_message)
            return redirect('payroll_summary')

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error contacting FastAPI service: {e}")
        return redirect('payroll_summary')


def generatePayslipExcel(request, employee_id):
    """
    Call the FastAPI endpoint to generate and download the Excel payslip file.
    """
    base_url = f"{PAYROLL_API_URL}/payslip/excel"
    params = {"employee_id": employee_id}

    try:
        response = requests.get(base_url, params=params, stream=True)

        if response.status_code != 200:
            messages.error(request, f"Failed to generate Excel payslip: {response.text}")
            return redirect('payroll_summary')  # Or redirect to another relevant page

        # Extract filename from Content-Disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = "payslip.xlsx"
        if "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[-1].strip('";')

        # messages.success(request, "Payslip Excel file downloaded successfully.")

        return HttpResponse(
            response.content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except requests.RequestException as e:
        messages.error(request, f"An error occurred while contacting the API: {str(e)}")
        return redirect('payroll_summary')

def downloadTemplate(request):
    """
    Call FastAPI to download the payroll Excel template.
    """
    base_url = f"{PAYROLL_API_URL}/download-template" 

    try:
        response = requests.get(base_url, stream=True)

        if response.status_code != 200:
            messages.error(request, "Failed to download the payroll template.")
            return redirect("payroll_batch_upload")  # update with your desired redirect target

        # Extract filename from header
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = "payroll_template.xlsx"
        if "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[-1].strip('";')

        messages.success(request, "Payroll template downloaded successfully.")

        return HttpResponse(
            response.content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except requests.RequestException as e:
        messages.error(request, f"An error occurred while downloading the template: {str(e)}")
        return redirect("payroll_batch_upload")
    

def batchUpload(request):
    base_url = f"{PAYROLL_API_URL}/batch-upload"
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = request.FILES.get("file")
        try:
            files = {
                'excel_file': (excel_file.name, excel_file.read(), excel_file.content_type)
            }
            response = requests.post(base_url, files=files)

            if response.status_code == 200 and response.json().get("success"):
                messages.success(request, response.json().get("message"))
            else:
                messages.error(request, response.json().get("detail", "Upload failed."))

        except Exception as e:
            messages.error(request, f"Error uploading file: {str(e)}")

        return redirect("payroll_batch_upload")

    return render(request, "batch_upload.html")