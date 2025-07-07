document.addEventListener('DOMContentLoaded', function() {
    const logoutForms = document.querySelectorAll('form.logout-form');
    logoutForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            this.submit();
        });
    });
});