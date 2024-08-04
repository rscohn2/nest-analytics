// This is for dynamically loaded content, we defer until after it is loaded
function afterLoad() {
  flatpickr(".datetimepicker", {
    enableTime : true,
    dateFormat : "Y-m-d H:i",
  });

  $('.electric-add-form').submit(function(e) { loadPostContent(e, this) });

  $('.structures-edit-form').submit(function(e) { loadPostContent(e, this) });

  $('.structures-edit-button').click(function(e) {
    e.preventDefault();
    loadGetContent($(this).data('url'));
  });
}

function loadPostContent(e, form) {
  e.preventDefault();

  var f = $(form);
  var url = f.attr('action');
  var formData = f.serialize();

  $.post(url, formData, function(response) {
    $('#main-content').html(response);
    afterLoad();
  });
}

// Get the content of the clicked link and load it in the main-content div
function loadGetContent(url) { $('#main-content').load(url, afterLoad); }

$(document).ready(function() {
  // This is initial page so we can add handlers immediately
  $('.sidebar-link').click(function(e) {
    e.preventDefault();
    loadGetContent($(this).data('url'));
  });
});
