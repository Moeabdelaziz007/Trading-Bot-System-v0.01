"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
    User,
    onAuthStateChanged,
    signInWithPopup,
    signOut as firebaseSignOut
} from "firebase/auth";
import { auth, googleProvider, isFirebaseAvailable } from "@/lib/firebase";

interface AuthContextType {
    user: User | null;
    loading: boolean;
    signInWithGoogle: () => Promise<void>;
    signInWithEmail: (email: string, pass: string) => Promise<void>;
    logOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    signInWithGoogle: async () => { },
    signInWithEmail: async () => { },
    logOut: async () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Only set up auth state listener if Firebase is available
        if (isFirebaseAvailable() && auth) {
            const unsubscribe = onAuthStateChanged(auth, (user) => {
                setUser(user);
                setLoading(false);
            });

            return () => unsubscribe();
        } else {
            // If Firebase is not available, set loading to false
            setLoading(false);
        }
    }, [auth]);

    const signInWithGoogle = async () => {
        if (!isFirebaseAvailable()) {
            console.warn('Firebase is not available. Cannot sign in with Google.');
            return;
        }
        try {
            await signInWithPopup(auth, googleProvider);
        } catch (error) {
            console.error("Error signing in with Google", error);
            throw error;
        }
    };

    const signInWithEmail = async (email: string, pass: string) => {
        if (!isFirebaseAvailable()) {
            console.warn('Firebase is not available. Cannot sign in with email.');
            return;
        }
        // Import dynamically to avoid unused import errors if not used elsewhere
        const { signInWithEmailAndPassword } = await import("firebase/auth");
        try {
            await signInWithEmailAndPassword(auth, email, pass);
        } catch (error) {
            console.error("Error signing in with email", error);
            throw error;
        }
    };

    const logOut = async () => {
        if (!isFirebaseAvailable()) {
            console.warn('Firebase is not available. Cannot sign out.');
            return;
        }
        try {
            await firebaseSignOut(auth);
        } catch (error) {
            console.error("Error signing out", error);
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, signInWithGoogle, signInWithEmail, logOut }}>
            {children}
        </AuthContext.Provider>
    );
};