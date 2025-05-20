# Django Frontend for Payroll System

This is the frontend for the Payroll System built with **Django**. It serves as the UI layer that communicates with a **FastAPI** backend to manage employee and payroll data.

---

## Features

- List employees with filters (name, hire date, status)
- Add, view, update, and delete employees
- Update employee status (active/inactive)
- Download payroll Excel templates
- Batch upload payroll entries via Excel
- Integrates with a FastAPI backend using HTTP API calls

---

## Setup Instructions

- git clone https://github.com/leodellosa/payroll_system_frontend.git "django"
- cd django
- python -m venv .venv
- source .venv/scripts/activate
- pip install -r requirements.txt
- cd payroll_system
- py manage.py makemigrations 
- py manage.py migrate
- py manage.py collectstatic
- py manage.py runserver


## API Integration
This frontend communicates with your FastAPI backend using:

### Employee Management
- GET /api/v1/employees - List employees
- GET /api/v1/employees/employeeList?search={name}&hire_date_from={hire_date_from}&hire_date_to={hire_date_to}&status={status} - Filter employee
- POST /api/v1/employees/employee/add - Add employee
- GET /api/v1/employees/{id} - Get employee detail
- PUT /api/v1/employees/employee/edit/{id} - Update employee
- PUT /api/v1/employees/employee/status/{id}?status={status} - Toggle employee status

### Payroll
- GET /api/v1/payroll – List payroll records
- GET /api/v1/payroll/payslip/pdf?employee_id={id} – Download individual payslip in PDF format
- GET /api/v1/payroll/payslip/excel?employee_id={id} – Download individual payslip in Excel format
- GET /api/v1/payroll/summary?employee_id={id} - Get Payroll summary
- POST /api/v1/payroll/generate?employee_id={id} - Generate payroll
- PUT /api/v1/payroll/update?employee_id={id}&payroll_id={payrol_id} - Update payroll details
- DEL /api/v1/payroll/delete?payroll_id={payroll_id} - Delete payroll
- GET /api/v1/payroll/{id} - Get payroll details
- GET /api/v1/payroll/download-template – Download Excel template for batch upload
- POST /api/v1/payroll/batch-upload – Upload payroll records via Excel








