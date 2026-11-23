// Wicketle site settings, shared by the home page and every game. Edit this one file.
window.WICKETLE_CONFIG = {
  // Your email for corrections. Leave "" to hide the "report a mistake" lines.
  contactEmail: "",

  // Sign-in (Google, email link, Apple): paste your Firebase web app config here to switch it on (see README), e.g.
  // {apiKey: "...", authDomain: "your-project.firebaseapp.com", projectId: "your-project", appId: "..."}
  firebase: null,
  // Apple sign-in also needs an Apple Developer account and setup in Firebase. Set to true once that's done.
  appleSignIn: false,

  // Donations, shown in the profile panel. Fill in either or both; leave both "" to hide the section.
  donate: {
    upi: "",            // your UPI ID, e.g. "yourname@okaxis" (opens GPay / PhonePe / Paytm on phones)
    url: "",            // a donation page, e.g. Buy Me a Coffee, Ko-fi or a Razorpay payment page
    urlLabel: "Donate online",
    name: "Wicketle",   // name shown in the UPI app
    message: ""         // optional custom message; leave "" for the default
  }
};
