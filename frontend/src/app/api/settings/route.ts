import { NextResponse } from 'next/server';

// Mock DB
let userSettings = {
    risk: {
        level: 'Medium', // Low, Medium, High
        maxDrawdown: 500, // USD
        riskPerTrade: 1.5, // %
        killSwitch: false
    },
    strategy: {
        aexiThreshold: 80,
        dreamThreshold: 70,
        activeTimeframes: ['H1', 'H4'],
        autoTrade: true
    },
    apiKeys: {
        capital: '********',
        alpaca: '********',
        deepseek: '********'
    }
};

export async function GET() {
    return NextResponse.json(userSettings);
}

export async function POST(request: Request) {
    try {
        const updates = await request.json();
        // Deep merge logic simplified
        userSettings = {
            ...userSettings,
            ...updates,
            risk: { ...userSettings.risk, ...updates.risk },
            strategy: { ...userSettings.strategy, ...updates.strategy }
        };

        return NextResponse.json({ success: true, settings: userSettings });
    } catch (e) {
        return NextResponse.json({ success: false, error: 'Update Failed' }, { status: 500 });
    }
}
