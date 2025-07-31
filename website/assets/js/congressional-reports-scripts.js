function enableGenerateReportsButtonIfPossible() {
    const reportTypeElement = document.getElementById("report-type");
    const reportType = reportTypeElement.value;

    const agencyCodeElement = document.getElementById("agency-code");
    const agencyCode = agencyCodeElement.value;

    const yearElement = document.getElementById("year");
    const year = yearElement.value;

    const generateReportButtonElement = document.getElementById("generate-congressional-report-button");
    generateReportButtonElement.disabled = reportType === '' || agencyCode === '' || year === '';
}

function generateReport() {
    const reportTypeElement = document.getElementById("report-type");
    const reportType = reportTypeElement.value;

    const agencyCodeElement = document.getElementById("agency-code");
    const agencyCode = agencyCodeElement.value;

    const yearElement = document.getElementById("year");
    const year = yearElement.value;

    window.location.href = '/resources/congressional-reports/' + 
        year + '_' + agencyCode + '_' + reportType;
}