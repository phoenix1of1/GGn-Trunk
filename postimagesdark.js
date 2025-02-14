// ==UserScript==
// @name         PostImages Background Mod
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Dark mode to stop me being blinded!
// @match        https://postimages.org/*
// @match        https://postimg.cc/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Add custom CSS to change the background color of the #content div to a gradient, header, text color of the body, color of .bottom-menu a.active, background color of .panel, and styles for .thumb
    const style = document.createElement('style');
    style.innerHTML = `
        #content {
            background: linear-gradient(to bottom, #2C3E50, #000000) !important;
        }
        body {
            color: rgb(125, 125, 125) !important;
        }
        header {
            background: linear-gradient(to bottom, #2C3E50, #000000) !important;
        }
        .bottom-menu a.active {
            color: rgb(255, 255, 255) !important;
        }
        .panel {
            background-color:rgba(51, 51, 51, 0) !important;
        }
        .thumb {
            background-color: #000000 !important;
            border: 1px solid #4d4d4d !important;
        }
        .btn {
            background: #000000; !important;
            border-color: #000000; !important;
            color: #4d4d4d; !important;
        }
    `;
    document.head.appendChild(style);

    // Remove the first list item from the <ul> inside <nav class="mainmenu">
    const mainMenu = document.querySelector('nav.mainmenu ul');
    if (mainMenu && mainMenu.firstElementChild) {
        mainMenu.removeChild(mainMenu.firstElementChild);
    }

    // Replace the logo with text "Postimage" and retain the same href
    const logoLink = document.querySelector('a.logo');
    if (logoLink) {
        logoLink.innerHTML = 'Postimage';
        logoLink.style.color = 'rgb(125, 125, 125)'; // Ensure the text color matches the rest of the page
    }
})();
