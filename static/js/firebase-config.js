// TODO: Replace with your Firebase project configuration
// You can get this from the Firebase Console > Project Settings > General > Your apps > SDK setup and configuration
const firebaseConfig = {
    apiKey: "AIzaSyDS2nQh6Nscyyu48YaMmay3b9A4hDY71ME",
    authDomain: "phovite-7ae18.firebaseapp.com",
    projectId: "phovite-7ae18",
    storageBucket: "phovite-7ae18.firebasestorage.app",
    messagingSenderId: "47949518574",
    appId: "1:47949518574:web:563db370644499bc0185ff"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const googleProvider = new firebase.auth.GoogleAuthProvider();
