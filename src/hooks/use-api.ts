import { useState, useEffect } from 'react';
import { AxiosResponse, AxiosError } from 'axios';

type ApiState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

type UseApiOptions = {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
};

export function useApi<T = any>(
  apiFunction: () => Promise<AxiosResponse<T>>,
  options: UseApiOptions = {}
) {
  const { immediate = true, onSuccess, onError } = options;
  
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await apiFunction();
      const data = response.data;
      
      setState({
        data,
        loading: false,
        error: null,
      });
      
      if (onSuccess) {
        onSuccess(data);
      }
      
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred';
      
      setState({
        data: null,
        loading: false,
        error: errorMessage,
      });
      
      if (onError) {
        onError(errorMessage);
      }
      
      throw error;
    }
  };

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate]);

  return {
    ...state,
    execute,
    refetch: execute,
  };
}

export function useMutation<T = any, P = any>(
  apiFunction: (params: P) => Promise<AxiosResponse<T>>,
  options: UseApiOptions = {}
) {
  const { onSuccess, onError } = options;
  
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const mutate = async (params: P) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await apiFunction(params);
      const data = response.data;
      
      setState({
        data,
        loading: false,
        error: null,
      });
      
      if (onSuccess) {
        onSuccess(data);
      }
      
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred';
      
      setState({
        data: null,
        loading: false,
        error: errorMessage,
      });
      
      if (onError) {
        onError(errorMessage);
      }
      
      throw error;
    }
  };

  return {
    ...state,
    mutate,
  };
}

// Pagination hook
export function usePagination(initialPage = 1, initialPageSize = 10) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  
  const goToPage = (newPage: number) => setPage(newPage);
  const nextPage = () => setPage(prev => prev + 1);
  const prevPage = () => setPage(prev => Math.max(1, prev - 1));
  const resetPage = () => setPage(1);
  
  return {
    page,
    pageSize,
    setPage,
    setPageSize,
    goToPage,
    nextPage,
    prevPage,
    resetPage,
  };
}