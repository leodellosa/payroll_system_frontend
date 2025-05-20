document.addEventListener("DOMContentLoaded", function () {
    employeeSelect = document.getElementById('id_employee').addEventListener('change',getEmployeeSalary);
    
    function getEmployeeSalary() {
        const employeeId = document.getElementById('id_employee').value;
        console.log('Selected employee ID:', employeeId);
        console.log("Url:", `${EMPLOYEE_API_URL}/${employeeId}`);
        if (employeeId) {
            fetch(`${EMPLOYEE_API_URL}/${employeeId}`)
                .then(response => response.json())
                .then(data => {
                    if (data && data.salary) {
                        document.getElementById('id_daily_rate').value = data.salary;
                    } else {
                        document.getElementById('id_daily_rate').value = '';
                    }
                })
                .catch(error => console.error('Error fetching employee data:', error));
        } else {
            document.getElementById('id_daily_rate').value = '';
        }
    }
});
