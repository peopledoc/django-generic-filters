function search_submit() {
    $("#search_form #id_query").val($("#query").val());
    $("#search_form").submit();
}
