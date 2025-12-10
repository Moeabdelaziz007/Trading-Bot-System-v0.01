import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SignInPage from './page';

// Mock Clerk's SignIn component
jest.mock('@clerk/nextjs', () => ({
  SignIn: ({ appearance, afterSignInUrl, redirectUrl }: any) => (
    <div data-testid="mock-signin">
      <h1>Mock SignIn Component</h1>
      <div data-testid="signin-config">
        Redirect: {afterSignInUrl} | {redirectUrl}
      </div>
      <button className={appearance?.elements?.formButtonPrimary}>
        Sign In
      </button>
    </div>
  ),
}));

// Mock Suspense since we are testing the page component
jest.mock('react', () => ({
  ...jest.requireActual('react'),
  Suspense: ({ fallback, children }: any) => (
    <div data-testid="suspense-wrapper">
      {fallback}
      {children}
    </div>
  ),
}));

describe('SignIn Page', () => {
  it('renders the page title correctly', () => {
    render(<SignInPage />);
    expect(screen.getByText('Axiom Access')).toBeInTheDocument();
  });

  it('renders the Clerk SignIn component with correct configuration', () => {
    render(<SignInPage />);
    const signInComponent = screen.getByTestId('mock-signin');
    expect(signInComponent).toBeInTheDocument();

    const configDiv = screen.getByTestId('signin-config');
    expect(configDiv).toHaveTextContent('Redirect: /dashboard | /dashboard');
  });

  it('renders the loading fallback within Suspense', () => {
    render(<SignInPage />);
    // Since we mocked Suspense to render both fallback and children, we can check for the loading text
    expect(screen.getByText('Establishing Secure Connection...')).toBeInTheDocument();
  });

  it('applies correct styling classes to the container', () => {
    const { container } = render(<SignInPage />);
    // Check for the neon shadow class we added
    const card = container.querySelector('.shadow-neon-green\\/20');
    expect(card).toBeInTheDocument();
  });
});
