'use strict'

const params = new URLSearchParams(window.location.search);
const hostname = params.get('host');

document.getElementById('blockedHostname').textContent = hostname;
