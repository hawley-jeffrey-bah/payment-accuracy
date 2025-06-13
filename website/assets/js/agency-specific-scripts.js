function unclampExecutiveSummary() {
    var element = document.getElementById('executive-summary-text');
    element.classList.add('expanded');

    var button = document.getElementById('show-full-executive-summary');
    button.style.display = 'none';
}

function showCompliantPrograms() {
    const toggle = document.querySelector('.toggle-visibility-compliant-programs');
    toggle.style.display = 'none';
    const toggled = document.querySelector('.toggled-visibility-compliant-programs');
    toggled.classList.remove('hide');
}