var $modal = $(".modal-block");
var $slider = $("input[name='last-days']");
var $sliderTooltip = null;
var lastDays = 7;
var $rows = null;
var rowsLen = null;
var $tableFooter = null;
var page = $("body").data("name");

function sum(arr) {
  return arr.reduce(function(a, b) { return a + b; }, 0);
}

function avg(arr) {
  return sum(arr) / arr.length;
}

function getInt(str) {
  return parseInt(str.replace(" ", ""));
}

function separateThousands(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function formatFloat(fl) {
  return fl.toFixed(2).toString();
}

function updateTable () {
  $rows = $("#stat-table tbody tr");
  $tableFooter = $("#stat-table tfoot tr").children();
  fillSummary();
}

function setSlider() {
  updateTable();
  rowsLen = $rows.length;
  $slider.attr("min", -rowsLen);
  $slider.attr("max", -1);
  $slider.attr("value", -lastDays);
  showLastDays();
}

function showLastDays() {
  var minShow = rowsLen - lastDays;
  $("#date-from").html($($($rows[minShow]).children()[0]).html());
  $("#date-to").html($($($rows[$rows.length - 1]).children()[0]).html());
  for (i = 0; i < rowsLen; i++) {
    if (i < minShow)
      $($rows[i]).hide();
    else
      $($rows[i]).show();
  }
  fillSummary();
}

function fillSummary() {
  var shows = [], starts = [], clicks = [], percents = [];
  $rows.each(function(index) {
      var $r = $($rows[index]);
      if ($r.css("display") != "none") {
        row = $r.children();
        shows.push(getInt($(row[1]).html()));
        starts.push(getInt($(row[2]).html()));
        clicks.push(getInt($(row[3]).html()));
        percents.push(parseFloat($(row[4]).html()));
      }
  });
  $($tableFooter[1]).html(separateThousands(sum(shows)));
  $($tableFooter[2]).html(separateThousands(sum(starts)));
  $($tableFooter[3]).html(separateThousands(sum(clicks)));
  $($tableFooter[4]).html(formatFloat(avg(percents)));
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
      doAfter = updateTable;
  }
  $.ajax(getAjaxOpts(url, doAfter));
});

$("#form-upload-submit").hide();

$("#upload-xlsx").change(function() {
  $("#upload-file-name").html(this.files[0].name);
	$("#form-upload").submit();
});

$(".list-group .list-group-item").click(function(ev) {
	$(".list-group .list-group-item").removeClass("active");
	$(ev.target).addClass("active");
});

$slider.on("input change", function(ev) {
  lastDays = -ev.target.value;
  showLastDays();
});

$("#fetch").click(function() {
  var progressBar = $("#progress-bar");
  var progressBarLabel = $("#progress-bar .progress-bar-label");
  var button = $(this);
  var logger = $("#logger");
  var logLines = $(".error-log-window").children();
  // clear log
  logLines.each(function(index) {
    if (!$(logLines[index]).is(logger)) {
      logLines[index].remove();
    }
  });
  var oldText = button.html();
  button.html("Загружается...");
  button.prop("disabled", true);
  if(typeof(EventSource) !== "undefined") {
    var stream = new EventSource("fetchdata");
    stream.onmessage = function(event) {
      if (event.data.indexOf("Error:") != -1)
        logger.before("<p>" + event.data + "</p>");
      splitted = event.data.split("|");
      progressBar.css('width', splitted[1]+'%').attr('aria-valuenow', splitted[1]);
      progressBarLabel.text(splitted[0]);
      if(splitted[1] == 100) {
        stream.close();
        button.html(oldText);
        button.prop("disabled", false);
      }
    };
  } else {
    // no server-sent events support
  }
});

$(document).ready(function() {
  $(".navbar-nav .nav-item").removeClass("active");
  $("a[href$=" + page + "]").addClass("active");
	$("#list-members .list-group-item").first().click();
  $(".navbar-nav .disabled a").click(function() {return false;});
});
