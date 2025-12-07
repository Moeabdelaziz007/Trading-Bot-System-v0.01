import { NextResponse } from 'next/server';

export async function GET() {
    // Simulated Signal Data (In production, this comes from Telegram Webhook KV)
    const signals = [
        {
            id: 1,
            symbol: 'EURUSD',
            type: 'BUY',
            price: 1.0845,
            tp: 1.0900,
            sl: 1.0820,
            time: '2 mins ago',
            aexi: 82,
            dream: 75,
            status: 'ACTIVE'
        },
        {
            id: 2,
            symbol: 'XAUUSD',
            type: 'SELL',
            price: 2045.50,
            tp: 2030.00,
            sl: 2055.00,
            time: '15 mins ago',
            aexi: 88,
            dream: 62,
            status: 'ACTIVE'
        },
        {
            id: 3,
            symbol: 'GBPUSD',
            type: 'BUY',
            price: 1.2650,
            tp: 1.2720,
            sl: 1.2600,
            time: '1 hour ago',
            aexi: 76,
            dream: 70,
            status: 'CLOSED'
        }
    ];

    return NextResponse.json(signals);
}
