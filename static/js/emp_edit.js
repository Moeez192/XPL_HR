$(document).ready(function () {
    $('#editEmployeeModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var url = button.data('url');
        var modal = $(this);

        console.log('Modal is about to be shown. URL: ' + url);  // Debug log

        // Load form into modal
        $.get(url, function (data) {
            console.log('Data loaded successfully');  // Debug log
            modal.find('#modal-body-content').html(data);
        }).fail(function () {
            console.error('Error loading form');  // Debug log
            modal.find('#modal-body-content').html('<p>Error loading form. Please try again.</p>');
        });
    });

    // Handle form submission
 $(document).on('submit', '#employeeEditForm', function (e) {
        e.preventDefault();
        var form = $(this);

        console.log('Form is being submitted');  // Debug log

        $.ajax({
            url: form.attr('action'),
            method: form.attr('method'),
            data: form.serialize(),
            success: function (response) {
                console.log('Form submitted successfully', response);  // Debug log
                if (response.success) {
                    $('#editEmployeeModal').modal('hide');
                    location.reload();
                } else {
                    $('#modal-body-content').html(response.form);
                }
            },
            error: function () {
                alert('An error occurred. Please try again.');
            }
        });
    });
});
