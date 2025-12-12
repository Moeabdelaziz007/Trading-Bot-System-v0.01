import React from 'react';
import { TRANSACTIONS } from '../constants';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export const TransactionsTable: React.FC = () => {
  return (
    <div className="glass-panel rounded-2xl p-6 h-full">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-axiom-danger/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-axiom-danger"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
          </div>
          <h2 className="text-lg font-semibold">Recent Transactions</h2>
        </div>
        <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-axiom-primary animate-pulse"></span>
            <span className="text-xs text-gray-400">Live Feed</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-white/5">
              <th className="pb-3 pl-2">Asset</th>
              <th className="pb-3">Type</th>
              <th className="pb-3">Price</th>
              <th className="pb-3">Amount</th>
              <th className="pb-3">P/L</th>
              <th className="pb-3 text-right pr-2">Status</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {TRANSACTIONS.map((tx, idx) => (
              <tr key={idx} className="group hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                <td className="py-4 pl-2 font-bold font-mono text-white">{tx.asset}</td>
                <td className="py-4">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${tx.type === 'LONG' ? 'bg-axiom-primary/10 text-axiom-primary border-axiom-primary/20' : 'bg-axiom-danger/10 text-axiom-danger border-axiom-danger/20'}`}>
                    {tx.type === 'LONG' ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                    {tx.type}
                  </span>
                </td>
                <td className="py-4 font-mono text-gray-300">${tx.price.toLocaleString()}</td>
                <td className="py-4 text-gray-500">--</td>
                <td className="py-4 text-gray-500">--</td>
                <td className="py-4 text-right pr-2">
                  <span className="text-axiom-warning font-medium">{tx.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
