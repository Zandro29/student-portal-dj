
function printSchedule() {
    var printContents = document.getElementById('schedule-section').innerHTML;
    var originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
    location.reload();  // para ma-reload ang full layout
}