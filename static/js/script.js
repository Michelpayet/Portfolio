const toggleBtn = document.querySelector('.toggle_btn')
const toggleBtnIcon = document.querySelector('.toggle_btn i')
const dropDownMenu = document.querySelector('.dropdown_menu')

// dropdown menu
toggleBtn.onclick = function () {
    dropDownMenu.classList.toggle('open')
    const isOpen = dropDownMenu.classList.contains('open')

    toggleBtnIcon.classList = isOpen
    ? 'fas fa-xmark'
    : 'fas fa-bars'
}

document.addEventListener('DOMContentLoaded', function () {
    var inputFields = document.querySelectorAll('.input-box input');

    inputFields.forEach(function (input) {
        input.addEventListener('focus', function () {
            this.nextElementSibling.style.display = 'none';
        });

        input.addEventListener('blur', function () {
            if (this.value === '') {
                this.nextElementSibling.style.display = 'block';
            }
        });
    });
});

document.querySelectorAll('.profile-link').forEach(function(link) {
    link.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent default link behavior
      if (confirm('Are you sure you want to delete your profile?')) {
        document.getElementById('delete-profile-form').submit(); // Submit the form if confirmed
      }
    });
  });