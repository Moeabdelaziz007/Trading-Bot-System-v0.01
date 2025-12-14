import { initializeApp, getApps, getApp } from "firebase/app";
import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    signOut,
    onAuthStateChanged,
    User
} from "firebase/auth";

// Check if all required Firebase environment variables are present
const requiredEnvVars = [
    'NEXT_PUBLIC_FIREBASE_API_KEY',
    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
    'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
    'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
    'NEXT_PUBLIC_FIREBASE_APP_ID'
];

const isFirebaseConfigured = requiredEnvVars.every(envVar =>
    process.env[envVar] && process.env[envVar].trim() !== ''
);

// Firebase configuration object
const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '',
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '',
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '',
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '',
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || ''
};

// Initialize Firebase only if configuration is complete
let app: any = null;
let auth: any = null;
let googleProvider: any = null;

if (isFirebaseConfigured) {
    try {
        // Initialize Firebase (singleton pattern)
        app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
        auth = getAuth(app);
        googleProvider = new GoogleAuthProvider();
        console.log('Firebase initialized successfully');
    } catch (error) {
        console.error('Error initializing Firebase:', error);
        console.warn('Firebase will be disabled due to initialization error');
    }
} else {
    console.warn('Firebase is disabled due to missing environment variables. Please set the following variables in your .env.local file:');
    requiredEnvVars.forEach(envVar => {
        if (!process.env[envVar] || process.env[envVar].trim() === '') {
            console.warn(`  - ${envVar}`);
        }
    });
}

// Export Firebase instances (will be null if not configured)
export { app, auth, googleProvider };

// Helper function to check if Firebase is available
export const isFirebaseAvailable = () => {
    return isFirebaseConfigured && app !== null && auth !== null;
};

// Helper functions with fallback behavior
export const signInWithGoogle = async () => {
    if (!isFirebaseAvailable()) {
        console.warn('Firebase is not available. Cannot sign in with Google.');
        return null;
    }
    try {
        return await signInWithPopup(auth, googleProvider);
    } catch (error) {
        console.error('Error signing in with Google:', error);
        return null;
    }
};

export const signOutUser = async () => {
    if (!isFirebaseAvailable()) {
        console.warn('Firebase is not available. Cannot sign out.');
        return;
    }
    try {
        await signOut(auth);
    } catch (error) {
        console.error('Error signing out:', error);
    }
};

export const onAuthStateChangedHelper = (callback: (user: User | null) => void) => {
    if (!isFirebaseAvailable()) {
        console.warn('Firebase is not available. Auth state changes will not be tracked.');
        callback(null);
        return () => {}; // Return unsubscribe function
    }
    return onAuthStateChanged(auth, callback);
};
