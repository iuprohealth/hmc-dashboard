function toggle_spinner() {
    $('.circle-loader').toggleClass('load-complete');
    $('.checkmark').toggle();
}

function set_status_text(value) {
    document.getElementById("status-message").textContent = value;
}

$('#user').on('change', function() {
    toggle_spinner();
    $.ajax({
        url: "/update_view",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'user': document.getElementById('user').value,
            'view': document.getElementById('view').value
        },
        dataType:"json",
        success: function(data) {
            Plotly.react('visualization', data);
            set_status_text((data.data[0].y.length).toLocaleString("en-US") + " records loaded.");
            toggle_spinner();
        },
        error: function() {
            set_status_text("❌ An error occurred (probably a missing record, try another User or Record Type).");
            toggle_spinner();
        }
    });
})

$("#view").on("change", function() {
    toggle_spinner();
    $.ajax({
        url: "/update_view",
        type: "GET",
        contentType: "application/json;charset=UTF-8",
        data: {
            "user": document.getElementById("user").value,
            "view": document.getElementById("view").value
        },
        dataType: "json",
        success: function(data) {
            Plotly.react('visualization', data);
            set_status_text((data.data[0].y.length).toLocaleString("en-US") + " records loaded.");
            toggle_spinner();
        },
        error: function() {
            set_status_text("❌ An error occurred (probably a missing record, try another User or Record Type).");
            toggle_spinner();
        }
    });
})
