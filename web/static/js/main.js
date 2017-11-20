var $modal = $(".modal-block");
var $slider = $("input[name='last-days']");
var $sliderTooltip = null;
var lastDays = 7;
var $rows = null;
var rowsLen = null;
var page = $("body").data("name");

function setSlider() {
  $rows = $("#stat-table tr");
  rowsLen = $rows.length;
  $slider.attr("min", -rowsLen);
  $slider.attr("max", -1);
  $slider.attr("value", -lastDays);
  showLastDays();
}

function showLastDays() {
  var minShow = rowsLen - lastDays;
  for (i = 0; i < rowsLen; i++) {
    if (i > 0 && i < minShow)
      $($rows[i]).hide();
    else
      $($rows[i]).show();
  }
}

function getAjaxOpts(url, doAfter) {
  return {
    url: url,
		beforeSend: function() {
      $modal.show();
		},
		success: function(data) {
      $modal.hide();
      $("#stat-table").html(data);
      doAfter();
		}
	};
}

$(".stat-member").click(function(ev) {
  var url, after;
  switch (page) {
    case "index":
      url = "stat/" + $(ev.target).data("name");
      doAfter = setSlider;
      break;
    default:
      url = "stat/" + $(ev.target).data("name");
      doAfter = function () {};
  }
  $.ajax(getAjaxOpts(url, doAfter));
});

$("#form-upload-submit").hide(); $("#upload-xlsx").change(function() {
	$("#form-upload").submit();
});

$(".list-group .list-group-item").click(function(ev) {
	$(".list-group .list-group-item").removeClass("active");
	$(ev.target).addClass("active");
});

$slider.hover(function(ev){
  if (ev.type == "mouseenter")
    $sliderTooltip = $slider.tooltip({
      placement: "bottom",
      title: lastDays,
    });
  else
    $sliderTooltip.remove();
});

$slider.on("input change", function(ev) {
  lastDays = -ev.target.value;
  showLastDays();
});

$(document).ready(function() {
  $(".navbar-nav .nav-item").removeClass("active");
  $("a[href$="+page+"]").addClass("active");
	$("#list-members .list-group-item").first().click();
});
