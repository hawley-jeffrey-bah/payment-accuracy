function downloadDataset() {
    var fiscalYear = document.getElementById("fiscal-year").value;

    var formattedFiscalYear = fiscalYear.replace(/\s+/g, '');
    var fileName = "FY" + formattedFiscalYear + "_Dataset.xlsx";
    var filePath = "/assets/files/" + fileName;

    // Create a temporary link to trigger the download
    var a = document.createElement("a");
    a.href = filePath;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function selectYear(prefix, val) {
    window.location.href = prefix + val;
}

// makes entire th element trigger uswds sort
function initSortableHeaders() {
    document.querySelectorAll("th[data-sortable]").forEach(
        th => th.addEventListener('click', (e) => {
            // prevent triggering twice when clicking sort button directly
            if (e.target === e.currentTarget) {
                th.querySelector('.usa-table__header__button:first-child').click();
            }
        })
    );
}

document.addEventListener('DOMContentLoaded', () => {
    initSortableHeaders();
});