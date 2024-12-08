
    document.addEventListener('DOMContentLoaded', function () {
        const searchInput = document.getElementById('employeeSearch');
        const departmentFilter = document.getElementById('tableFilter');
        const employeeTable = document.getElementById('employeeTable');
        const rows = employeeTable.querySelectorAll('tbody tr');
    
        
        function filterTable() {
            const searchValue = searchInput.value.toLowerCase();
            const selectedDepartment = departmentFilter.value.toLowerCase();
    
            rows.forEach(row => {
                const columns = row.querySelectorAll('td');
                const employeeName = `${columns[0].textContent} ${columns[1].textContent} ${columns[3].textContent}`.toLowerCase(); 
                const employeeDepartment = columns[1].textContent.toLowerCase(); 
    
                
                const matchesSearch = employeeName.includes(searchValue);
                const matchesDepartment = selectedDepartment ? employeeDepartment === selectedDepartment : true;
    
                
                if (matchesSearch && matchesDepartment) {
                    row.style.display = ''; 
                } else {
                    row.style.display = 'none'; 
                }
            });
        }
    
        
        searchInput.addEventListener('input', filterTable);
        departmentFilter.addEventListener('change', filterTable);
    });
