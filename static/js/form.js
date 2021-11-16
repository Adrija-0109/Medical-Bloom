// Your web app's Firebase configuration
  var firebaseConfig = {
    apiKey: "AIzaSyA11vaC3HFW7hUsM4LtfW2w1fFDTexI5dQ",
    authDomain: "meadical-image-analysis.firebaseapp.com",
    projectId: "meadical-image-analysis",
    storageBucket: "meadical-image-analysis.appspot.com",
    messagingSenderId: "508086214962",
    appId: "1:508086214962:web:de6ef33457d2738b11372b"
  };
  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);

const auth = firebase.auth();


function signup()
{
    var email = document.getElementById("email");
    var password = document.getElementById("password");
    
    const promise = auth.createUserWithEmailAndPassword(email.value, password.value);
    promise.catch(e => alert(e.messege));
    
    alert("Signed Up");
}

function signin()
{
    var email = document.getElementById("email");
    var password = document.getElementById("password");
    
   const promise = auth.signInWithEmailAndPassword(email.value, password.value);
   promise.catch(e => alert(e.messege));
    
    alert("Signed In");
}

function signout()
{   
    auth.signOut();
    
    alert("Signed Out");
}
