import { useState, useCallback } from 'react';

interface DialecticData {
  coreText: string;
  shadowText: string;
  synthesisText: string;
  decision: string | null;
  coreConfidence: number;
  shadowRegret: number;
  eScore: number;
  condition: string;
  phase: 'idle' | 'core' | 'shadow' | 'synthesis' | 'complete';
}

export const useDialecticStream = () => {
  const [dialecticData, setDialecticData] = useState<DialecticData>({
    coreText: '',
    shadowText: '',
    synthesisText: '',
    decision: null,
    coreConfidence: 0,
    shadowRegret: 0,
    eScore: 0,
    condition: '',
    phase: 'idle'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startStream = useCallback(() => {
    // Reset state
    setDialecticData({
      coreText: '',
      shadowText: '',
      synthesisText: '',
      decision: null,
      coreConfidence: 0,
      shadowRegret: 0,
      eScore: 0,
      condition: '',
      phase: 'idle'
    });
    setIsLoading(true);
    setError(null);

    const eventSource = new EventSource('/api/dialectic/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'SESSION_START':
            setDialecticData(prev => ({
              ...prev,
              condition: data.metadata?.condition || '',
              phase: 'idle'
            }));
            break;

          case 'PHASE_START':
            if (data.payload === 'CORE') {
              setDialecticData(prev => ({ ...prev, phase: 'core', coreText: '' }));
            } else if (data.payload === 'SHADOW') {
              setDialecticData(prev => ({ ...prev, phase: 'shadow', shadowText: '' }));
            } else if (data.payload === 'SYNTHESIS') {
              setDialecticData(prev => ({ ...prev, phase: 'synthesis', synthesisText: '' }));
            }
            break;

          case 'CORE_TOKEN':
            setDialecticData(prev => ({
              ...prev,
              coreText: prev.coreText + data.payload,
              coreConfidence: data.confidence || prev.coreConfidence
            }));
            break;

          case 'SHADOW_TOKEN':
            setDialecticData(prev => ({
              ...prev,
              shadowText: prev.shadowText + data.payload,
              shadowRegret: data.confidence || prev.shadowRegret
            }));
            break;

          case 'SYNTHESIS_TOKEN':
            setDialecticData(prev => ({
              ...prev,
              synthesisText: prev.synthesisText + data.payload
            }));
            break;

          case 'PHASE_END':
            if (data.payload === 'CORE') {
              setDialecticData(prev => ({ ...prev, coreConfidence: data.confidence || prev.coreConfidence }));
            } else if (data.payload === 'SHADOW') {
              setDialecticData(prev => ({ ...prev, shadowRegret: data.confidence || prev.shadowRegret }));
            }
            break;

          case 'DECISION':
            setDialecticData(prev => ({
              ...prev,
              decision: data.payload,
              eScore: data.metadata?.e_score || 0,
              phase: 'complete'
            }));
            break;

          case 'SESSION_END':
            setIsLoading(false);
            eventSource.close();
            break;
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err);
      }
    };

    eventSource.onerror = () => {
      setError('Failed to connect to dialectic stream');
      setIsLoading(false);
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  return {
    ...dialecticData,
    isLoading,
    error,
    startStream
  };
};