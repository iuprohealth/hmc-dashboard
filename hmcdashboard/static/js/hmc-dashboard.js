function toggle_spinner() {
    $('.circle-loader').toggleClass('load-complete');
    $('.checkmark').toggle();
}

function set_status_text(value) {
    document.getElementById("status-message").textContent = value;
}
