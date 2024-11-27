document.addEventListener('DOMContentLoaded', function() {
    // Log message to confirm script loading
    console.log('JavaScript loaded successfully');

    // Initialize Patient Statistics Chart if canvas element exists
    const patientChartElement = document.getElementById('patientChart');
    if (patientChartElement) {
        new Chart(patientChartElement, {
            type: 'bar',
            data: {
                labels: JSON.parse(patientChartElement.getAttribute('data-labels')),
                datasets: [{
                    label: 'Number of Patients',
                    data: JSON.parse(patientChartElement.getAttribute('data-values')),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initialize Appointment Trends Chart if canvas element exists
    const appointmentChartElement = document.getElementById('appointmentChart');
    if (appointmentChartElement) {
        new Chart(appointmentChartElement, {
            type: 'line',
            data: {
                labels: JSON.parse(appointmentChartElement.getAttribute('data-labels')),
                datasets: [{
                    label: 'Number of Appointments',
                    data: JSON.parse(appointmentChartElement.getAttribute('data-values')),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initialize Appointment Trends Chart for Provider Analytics if canvas element exists
    const appointmentTrendsChartElement = document.getElementById('appointmentTrendsChart');
    if (appointmentTrendsChartElement) {
        new Chart(appointmentTrendsChartElement, {
            type: 'line',
            data: {
                labels: JSON.parse(appointmentTrendsChartElement.getAttribute('data-labels')),
                datasets: [{
                    label: 'Appointments',
                    data: JSON.parse(appointmentTrendsChartElement.getAttribute('data-values')),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initialize Patient Demographics Chart for Provider Analytics if canvas element exists
    const patientDemographicsChartElement = document.getElementById('patientDemographicsChart');
    if (patientDemographicsChartElement) {
        new Chart(patientDemographicsChartElement, {
            type: 'pie',
            data: {
                labels: JSON.parse(patientDemographicsChartElement.getAttribute('data-labels')),
                datasets: [{
                    label: 'Patient Demographics',
                    data: JSON.parse(patientDemographicsChartElement.getAttribute('data-values')),
                    backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(153, 102, 255, 0.2)'],
                    borderColor: ['rgba(255, 99, 132, 1)', 'rgba(75, 192, 192, 1)', 'rgba(255, 206, 86, 1)', 'rgba(153, 102, 255, 1)'],
                    borderWidth: 1
                }]
            }
        });
    }

    // Handle form submission with AJAX
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            // Extract form data
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');
            
            // AJAX form submission logic
            fetch(actionUrl, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Handle success (e.g., display a success message or redirect)
                console.log('Form submitted successfully', data);
            })
            .catch(error => {
                // Handle error (e.g., display an error message)
                console.error('Error submitting form', error);
            });
        });
    });
});
