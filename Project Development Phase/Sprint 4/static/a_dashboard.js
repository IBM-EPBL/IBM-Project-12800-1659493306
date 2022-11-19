$(function () {
    $("#dialg").dialog({
        autoOpen: false,
    });
    $("body").on("click", "#assign_agent", function () {
        $("#dialg").dialog("open");
    });
});
$(document).ready(function () {
    $("body").on("click", "#assign_agent", function () {
        var layout = $(this).data('rep');
        $.ajax({
            url: "/setcid",
            type: "get",
            data: { layout: layout }
        });
    });
    $("body").on("click", "#complete", function () {
        var lay = $(this).data('rep');
        $.ajax({
            url: "/setstatus",
            type: "get",
            data: { compl_id: lay }
        });
    });
})