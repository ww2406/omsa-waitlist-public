importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js');

var firebaseConfig = {
    apiKey: "redacted",
    authDomain: "redacted",
    projectId: "redacted",
    storageBucket: "redacted",
    messagingSenderId: "redacted",
    appId: "redacted",
    measurementId: "redacted"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();