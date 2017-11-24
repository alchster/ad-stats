var $modal = $(".modal-block");
var $slider = $("input[name='last-days']");
var $sliderTooltip = null;
var lastDays = 7;
var $rows = null;
var rowsLen = null;
var $tableFooter = null;
var page = $("body").data("name");
var $currentStatMember =  null;
var $filterIcon = $("#stat-member-clear-filter i");
var $statMember = $(".stat-member");
var statMembers = {};
var year = null;
var month = null;
var graph = null;

var panelActive = false;

// utils

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

// stat-member

function fillStatMembers() {
  var memberObj;
  $("#list-members .stat-member").toArray().forEach(function (el) {
    memberObj = $(el);
    statMembers[memberObj.html().toLowerCase()] = memberObj;
  });
}

function filterStatMembers(str) {
  $("#list-members .stat-member").hide();
  for (var name in statMembers) {
    if (name.indexOf(str.toLowerCase()) != -1)
      statMembers[name].show();
  }
}

// helpers

function toggleSidePanel(visible) {
  $(".row-offcanvas").toggleClass("active");
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
  $(".label-date-from").html($($($rows[minShow]).children()[0]).html());
  $(".label-date-to").html($($($rows[$rows.length - 1]).children()[0]).html());
  for (i = 0; i < rowsLen; i++) {
    if (i < minShow)
      $($rows[i]).hide();
    else
      $($rows[i]).show();
  }
  fillSummary();
}

function fillSummary() {
  var data = {
    dates: [],
    shows: [],
    starts: [],
    clicks: [],
    percents: []
  };
  $rows.each(function(index) {
      var $r = $($rows[index]);
      if ($r.css("display") != "none") {
        row = $r.children();
        data.dates.push($(row[0]).html());
        data.shows.push(getInt($(row[1]).html()));
        data.starts.push(getInt($(row[2]).html()));
        data.clicks.push(getInt($(row[3]).html()));
        data.percents.push(parseFloat($(row[4]).html()));
      }
  });
  $($tableFooter[1]).html(separateThousands(sum(data.shows)));
  $($tableFooter[2]).html(separateThousands(sum(data.starts)));
  $($tableFooter[3]).html(separateThousands(sum(data.clicks)));
  $($tableFooter[4]).html(formatFloat(avg(data.percents)));
  createGraph(data);
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

function createGraph(data) {
  var shows = [], starts = [], clicks = [];
  var len = data.shows.length;
  for (var i = 0; i < len; i++) {
    shows.push({
      label: data.dates[i],
      y: data.shows[i]
    });
    starts.push({
      label: data.dates[i],
      y: data.starts[i]
    });
    clicks.push({
      label: data.dates[i],
      y: data.clicks[i]
    });
  }
  graph = new CanvasJS.Chart("data-graph", {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      verticalAlign: "top",
      horizontalAlign: "right",
    },
    data: [
      {
        type: "line",
        name: "Показы",
        color: "blue",
        indexLabelOrientation: "vertical",
        toolTipContent: "{label}: {y} ",
        dataPoints: shows,
        showInLegend: true,
      },
      {
        type: "line",
        name: "Старты",
        color: "red",
        indexLabelOrientation: "vertical",
        toolTipContent: "{label}: {y}",
        dataPoints: starts,
        showInLegend: true,
      },
      {
        type: "line",
        name: "Клики",
        color: "green",
        indexLabelOrientation: "vertical",
        toolTipContent: "{label}: {y}",
        dataPoints: clicks,
        showInLegend: true,
      },
    ],
  });
  graph.render();
}

// events


$("#stat-member-filter").on("change keyup paste", function () {
  var val = $(this).val();
  $statMember.unmark();
  if (val != "") {
    $filterIcon.removeClass("fa-filter").addClass("fa-eraser");
    $statMember.mark(val);
  } else {
    $filterIcon.removeClass("fa-eraser").addClass("fa-filter");
  }
  filterStatMembers(val);
});

$("#stat-member-clear-filter").click(function () {
  $("#stat-member-filter").val("");
  $("#stat-member-filter").change();
  $("#list-members .stat-member").show();
});

$("#graph-tab").click(function () {
  window.setTimeout(function() { 
    window.dispatchEvent(new Event('resize'));
  }, 0); 
});

$("#list-members .stat-member").click(function(ev) {
  if ($currentStatMember)
    $currentStatMember.removeClass("active");
  $currentStatMember = $(this);
  $currentStatMember.addClass("active");
  panelActive = false;
  $(".row-offcanvas").removeClass("show-md-panel").addClass("hide-md-panel").removeClass("hide-md-panel");
  var url = "stat/" + $currentStatMember.data("name");
  var after;

  switch (page) {
    case "index":
      doAfter = setSlider;
      break;
    case "months":
      if (year) {
        url += "/" + year;
        if (month)
          url += "/" + month;
      }
      doAfter = updateTable;
      break;
    default:
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
  var val = $(this).val();
  $slider.val(val);
  lastDays = -val;
  showLastDays();
});

/*
$("#list-members .list-group-item").click(function(){
});
*/

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

$(".row-offcanvas").swipe({
  swipeLeft: function () {
    if (panelActive) {
      panelActive = false;
      $(this).removeClass("show-md-panel").addClass("hide-md-panel").removeClass("hide-md-panel");
    }
  },
  swipeRight: function () {
    if (!panelActive) {
      panelActive = true;
      $(this).removeClass("hide-md-panel").addClass("show-md-panel");
    }
  },
  excludedElements: "input"
});

$(document).ready(function() {
  $(".navbar-nav .nav-item").removeClass("active");
  $("a[href$=" + page + "]").addClass("active");
  $("#list-members .stat-member").first().click();
  $(".navbar-nav .disabled a").click(function() {return false;});
  fillStatMembers();
});
