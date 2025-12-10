'use client';

import React, { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { motion } from 'framer-motion';
import { X, Check, CreditCard, Wallet } from 'lucide-react';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const tiers = [
  {
    name: 'Initiate',
    price: 'FREE',
    borderColor: 'border-gray-600',
    features: [
      'Basic signals',
      'Demo trading',
      'Limited AI chat',
      'Community access'
    ],
    cta: 'Current Plan',
    disabled: true
  },
  {
    name: 'Adept',
    price: '$29',
    period: '/mo',
    borderColor: 'border-axiom-neon-cyan',
    glowClass: 'shadow-glow-cyan',
    features: [
      'Full AI chat access',
      'Paper trading',
      '10 active bots',
      'Advanced signals',
      'Email support'
    ],
    cta: 'Upgrade to Adept',
    popular: false
  },
  {
    name: 'Grandmaster',
    price: '$99',
    period: '/mo',
    borderColor: 'border-axiom-neon-gold',
    glowClass: 'shadow-glow-gold',
    features: [
      'Live trading',
      'MT5 Forex integration',
      'Unlimited bots',
      'Custom agents',
      'Priority support',
      'API access'
    ],
    cta: 'Upgrade to Grandmaster',
    popular: true
  }
];

const paymentProviders = [
  {
    name: 'Coinbase',
    icon: Wallet,
    description: 'Crypto Payments',
    color: 'text-axiom-neon-blue'
  },
  {
    name: 'Stripe',
    icon: CreditCard,
    description: 'Card Payments',
    color: 'text-axiom-neon-purple'
  },
  {
    name: 'PayPal',
    icon: Wallet,
    description: 'Global Payments',
    color: 'text-axiom-neon-cyan'
  }
];

export const PaymentModal: React.FC<PaymentModalProps> = ({ isOpen, onClose }) => {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  const handleCheckout = () => {
    if (!selectedTier || !selectedProvider) return;
    
    // TODO: Implement actual payment flow
    console.log('Checkout:', { tier: selectedTier, provider: selectedProvider });
    alert(`Processing ${selectedTier} subscription via ${selectedProvider}`);
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-5xl transform overflow-hidden rounded-2xl bg-axiom-surface border border-glass-border p-8 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                  <Dialog.Title className="text-2xl font-mono font-bold text-white">
                    UPGRADE_YOUR_PLAN
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="text-text-muted hover:text-white transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Subscription Tiers */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  {tiers.map((tier) => (
                    <motion.div
                      key={tier.name}
                      whileHover={{ scale: tier.disabled ? 1 : 1.02 }}
                      onClick={() => !tier.disabled && setSelectedTier(tier.name)}
                      className={`relative bg-axiom-bg border-2 ${tier.borderColor} rounded-xl p-6 cursor-pointer transition-all ${
                        selectedTier === tier.name ? tier.glowClass : ''
                      } ${tier.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      {tier.popular && (
                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-axiom-neon-gold text-black text-xs font-mono font-bold rounded-full">
                          MOST POPULAR
                        </div>
                      )}

                      <div className="text-center mb-6">
                        <h3 className="text-xl font-mono font-bold text-white mb-2">
                          {tier.name}
                        </h3>
                        <div className="flex items-baseline justify-center gap-1">
                          <span className="text-4xl font-mono font-bold text-white">
                            {tier.price}
                          </span>
                          {tier.period && (
                            <span className="text-text-muted font-mono">
                              {tier.period}
                            </span>
                          )}
                        </div>
                      </div>

                      <ul className="space-y-3 mb-6">
                        {tier.features.map((feature, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <Check className="w-4 h-4 text-axiom-neon-green flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-text-muted font-mono">
                              {feature}
                            </span>
                          </li>
                        ))}
                      </ul>

                      <button
                        disabled={tier.disabled}
                        className={`w-full py-3 rounded-lg font-mono font-bold transition-all ${
                          tier.disabled
                            ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                            : selectedTier === tier.name
                            ? 'bg-axiom-neon-cyan text-black'
                            : 'bg-axiom-bg border border-glass-border text-white hover:border-axiom-neon-cyan'
                        }`}
                      >
                        {tier.cta}
                      </button>
                    </motion.div>
                  ))}
                </div>

                {/* Payment Providers */}
                {selectedTier && selectedTier !== 'Initiate' && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="border-t border-glass-border pt-6"
                  >
                    <h3 className="text-lg font-mono font-bold text-white mb-4">
                      SELECT_PAYMENT_METHOD
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      {paymentProviders.map((provider) => (
                        <motion.button
                          key={provider.name}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setSelectedProvider(provider.name)}
                          className={`bg-axiom-bg border-2 rounded-lg p-4 transition-all ${
                            selectedProvider === provider.name
                              ? 'border-axiom-neon-cyan shadow-glow-cyan'
                              : 'border-glass-border hover:border-glass-border/50'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <provider.icon className={`w-6 h-6 ${provider.color}`} />
                            <div className="text-left">
                              <p className="font-mono font-bold text-white">
                                {provider.name}
                              </p>
                              <p className="text-xs text-text-muted font-mono">
                                {provider.description}
                              </p>
                            </div>
                          </div>
                        </motion.button>
                      ))}
                    </div>

                    <button
                      onClick={handleCheckout}
                      disabled={!selectedProvider}
                      className="w-full bg-axiom-neon-cyan hover:bg-axiom-neon-cyan/90 text-black font-mono font-bold py-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      PROCEED_TO_CHECKOUT
                    </button>
                  </motion.div>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};