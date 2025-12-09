import {
  getMarketPrice,
  getMarketHistory,
  getSystemStatus,
  executeTrade,
  getPositions,
  flattenAll,
  getAILogs,
  analyzeAsset,
  tradingApi,
} from '../api';

const API_BASE = 'https://trading-brain-v1.amrikyy1.workers.dev';

// Helper to mock successful fetch
const mockFetchSuccess = (data: any) =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(data),
  } as Response);

// Helper to mock failed fetch
const mockFetchError = () =>
  Promise.resolve({
    ok: false,
    status: 500,
    statusText: 'Internal Server Error',
  } as Response);

describe('API Client', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  describe('getMarketPrice', () => {
    it('fetches market price successfully', async () => {
      const mockData = { symbol: 'BTC', price: 50000 };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await getMarketPrice('BTC');

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/market/BTC`);
      expect(result).toEqual(mockData);
    });

    it('throws error on failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchError());

      await expect(getMarketPrice('BTC')).rejects.toThrow('Failed to fetch BTC');
    });
  });

  describe('getMarketHistory', () => {
    it('fetches market history successfully', async () => {
      const mockData = [{ time: '2023-01-01', price: 100 }];
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await getMarketHistory('BTC', '1d', '1h');

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE}/api/market/BTC/history?period=1d&interval=1h`
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('getSystemStatus', () => {
    it('fetches system status successfully', async () => {
      const mockData = { status: 'online' };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await getSystemStatus();

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/status`);
      expect(result).toEqual(mockData);
    });
  });

  describe('executeTrade', () => {
    it('executes trade successfully', async () => {
      const mockOrder = { symbol: 'BTC', side: 'BUY', amount: 1 } as any;
      const mockResponse = { orderId: '123' };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockResponse));

      const result = await executeTrade(mockOrder);

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockOrder),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getPositions', () => {
    it('fetches positions successfully', async () => {
      const mockData = [{ symbol: 'BTC', size: 1 }];
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await getPositions();

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/positions`);
      expect(result).toEqual(mockData);
    });
  });

  describe('flattenAll', () => {
    it('flattens positions successfully', async () => {
      const mockData = { status: 'flattened' };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await flattenAll();

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/flatten`, {
        method: 'POST',
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('getAILogs', () => {
    it('fetches AI logs successfully', async () => {
      const mockData = [{ log: 'test' }];
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await getAILogs(10);

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/ai/logs?limit=10`);
      expect(result).toEqual(mockData);
    });
  });

  describe('analyzeAsset', () => {
    it('analyzes asset successfully', async () => {
      const mockData = { analysis: 'bullish' };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess(mockData));

      const result = await analyzeAsset('BTC');

      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'BTC' }),
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('tradingApi methods', () => {
    it('placeOrder works correctly', async () => {
      const mockOrder = { symbol: 'ETH', side: 'SELL' };
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess({}));
      await tradingApi.placeOrder(mockOrder);
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/trade`, expect.anything());
    });

    it('chatWithAI works correctly', async () => {
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess({ reply: 'Hello' }));
      await tradingApi.chatWithAI('Hi');
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/ai/chat`, expect.anything());
    });

    it('getBrainStatus works correctly', async () => {
      (global.fetch as jest.Mock).mockResolvedValue(mockFetchSuccess({ status: 'ok' }));
      await tradingApi.getBrainStatus();
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/api/brain/status`);
    });
  });
});
