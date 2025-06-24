function toggleClamp(index) {
    let element = document.getElementById('desc-' + index);
    element.classList.toggle('expanded');

    element = document.getElementById('date-' + index);
    element.classList.toggle('expanded');
}