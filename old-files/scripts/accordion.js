// accordion for the divs so they can open and close

function openAccordion(edu) {
  var x = document.getElementById(edu);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
}
