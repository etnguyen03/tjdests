$(document).ready(function(){
    $("select").each(function(){
        new TomSelect("#" + this.id, {allowEmptyOption: true, "plugins": ["change_listener"]});
    });
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })

    $("#id_publish_data").change(function () {
        if (this.checked) {
            var confirmreturn = confirm("You have indicated that you wish to publicize the data that you have entered. " +
                "Note that any current and future TJHSST student will be able to view your data. You may unpublish your data at any time.\n\n" +
                "By selecting the affirmative answer below, you declare that all data that you have entered and " +
                "will enter in the future is accurate to the best of your belief. ")
            $(this).prop("checked", confirmreturn)
        }
    })
})