import { useState, useEffect, useCallback } from 'react';

// Interface para dados do curso
interface Course {
  course_id: string;
  name: string;
  description: string;
  price: number;
  lessons: string[];
  granted_at?: string;
}

// Interface para retorno do hook
interface UseCourseAccessReturn {
  // Estados
  userCourses: Course[];
  availableCourses: Record<string, Course>;
  isLoading: boolean;
  error: string | null;
  
  // Funções
  checkCourseAccess: (courseId: string) => Promise<boolean>;
  checkLessonAccess: (lessonId: string) => Promise<boolean>;
  refreshUserCourses: () => Promise<void>;
  hasAccessToCourse: (courseId: string) => boolean;
  hasAccessToLesson: (lessonId: string) => boolean;
}

/**
 * Hook personalizado para gerenciar acesso aos cursos
 * Fornece funcionalidades para verificar acesso, buscar cursos do usuário, etc.
 */
export const useCourseAccess = (): UseCourseAccessReturn => {
  const [userCourses, setUserCourses] = useState<Course[]>([]);
  const [availableCourses, setAvailableCourses] = useState<Record<string, Course>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Busca cursos que o usuário tem acesso
   */
  const fetchUserCourses = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = localStorage.getItem('token');
      if (!token) {
        setUserCourses([]);
        return;
      }

      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/user-courses`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUserCourses(data.courses || []);
        }
      } else if (response.status === 401) {
        // Token inválido, limpar dados
        localStorage.removeItem('token');
        setUserCourses([]);
      }
    } catch (err) {
      console.error('Erro ao buscar cursos do usuário:', err);
      setError('Erro ao carregar seus cursos');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Busca cursos disponíveis para compra
   */
  const fetchAvailableCourses = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/courses`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAvailableCourses(data.courses || {});
        }
      }
    } catch (err) {
      console.error('Erro ao buscar cursos disponíveis:', err);
    }
  }, []);

  /**
   * Verifica se o usuário tem acesso a um curso específico
   */
  const checkCourseAccess = useCallback(async (courseId: string): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return false;

      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/check-access/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.success && data.has_access;
      }
      
      return false;
    } catch (err) {
      console.error('Erro ao verificar acesso ao curso:', err);
      return false;
    }
  }, []);

  /**
   * Verifica se o usuário tem acesso a uma aula específica
   */
  const checkLessonAccess = useCallback(async (lessonId: string): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return false;

      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/check-lesson-access/${lessonId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.success && data.has_access;
      }
      
      return false;
    } catch (err) {
      console.error('Erro ao verificar acesso à aula:', err);
      return false;
    }
  }, []);

  /**
   * Verifica localmente se o usuário tem acesso a um curso
   */
  const hasAccessToCourse = useCallback((courseId: string): boolean => {
    return userCourses.some(course => course.course_id === courseId);
  }, [userCourses]);

  /**
   * Verifica localmente se o usuário tem acesso a uma aula
   */
  const hasAccessToLesson = useCallback((lessonId: string): boolean => {
    return userCourses.some(course => 
      course.lessons && course.lessons.includes(lessonId)
    );
  }, [userCourses]);

  /**
   * Atualiza a lista de cursos do usuário
   */
  const refreshUserCourses = useCallback(async () => {
    await fetchUserCourses();
  }, [fetchUserCourses]);

  // Carregar dados iniciais
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserCourses();
      fetchAvailableCourses();
    }
  }, [fetchUserCourses, fetchAvailableCourses]);

  // Escutar mudanças no token de autenticação
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        if (e.newValue) {
          // Token adicionado/alterado
          fetchUserCourses();
          fetchAvailableCourses();
        } else {
          // Token removido
          setUserCourses([]);
          setAvailableCourses({});
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [fetchUserCourses, fetchAvailableCourses]);

  return {
    userCourses,
    availableCourses,
    isLoading,
    error,
    checkCourseAccess,
    checkLessonAccess,
    refreshUserCourses,
    hasAccessToCourse,
    hasAccessToLesson
  };
};

export default useCourseAccess;