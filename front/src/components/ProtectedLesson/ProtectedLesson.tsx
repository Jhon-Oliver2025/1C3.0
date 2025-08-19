import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Lock, ShoppingCart, AlertCircle, Loader } from 'lucide-react';
import { useCourseAccess } from '../../hooks/useCourseAccess';
import MercadoPagoCheckout from '../MercadoPagoCheckout/MercadoPagoCheckout';

// Styled Components
const AccessDeniedContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
  text-align: center;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 16px;
  margin: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const AccessDeniedIcon = styled.div`
  width: 80px;
  height: 80px;
  background: rgba(244, 67, 54, 0.1);
  border: 2px solid rgba(244, 67, 54, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  
  svg {
    color: #f44336;
  }
`;

const AccessDeniedTitle = styled.h2`
  color: #ffffff;
  font-size: 1.8rem;
  margin-bottom: 1rem;
  font-weight: 600;
`;

const AccessDeniedMessage = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  max-width: 500px;
`;

const CourseInfoCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  max-width: 400px;
  width: 100%;
  
  h3 {
    color: #ffffff;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
  }
`;

const ActionButton = styled.button`
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #00bcd4 100%);
  border: none;
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  gap: 1rem;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid #2196f3;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.1rem;
  }
`;

// Interfaces
interface ProtectedLessonProps {
  lessonId: string;
  children: React.ReactNode;
  showCheckout?: boolean;
  redirectToLogin?: boolean;
}

/**
 * Componente que protege o acesso às aulas
 * Verifica se o usuário tem permissão para acessar a aula específica
 * Administradores têm acesso direto, usuários logados veem indicador visual
 */
const ProtectedLesson: React.FC<ProtectedLessonProps> = ({
  lessonId,
  children,
  showCheckout = true,
  redirectToLogin = true
}) => {
  const navigate = useNavigate();
  const { 
    checkLessonAccess, 
    availableCourses, 
    hasAccessToLesson,
    isLoading: coursesLoading 
  } = useCourseAccess();
  
  const [isChecking, setIsChecking] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [courseInfo, setCourseInfo] = useState<{
    courseId: string;
    name: string;
    description: string;
    price: number;
  } | null>(null);

  // Verificar acesso à aula
  useEffect(() => {
    checkAccess();
  }, [lessonId]);

  /**
   * Verifica se o usuário tem acesso à aula
   * Administradores têm acesso direto
   */
  const checkAccess = async () => {
    try {
      setIsChecking(true);
      
      // Verificar se está logado
      const token = localStorage.getItem('token');
      if (!token) {
        if (redirectToLogin) {
          navigate('/login', { 
            state: { 
              returnUrl: window.location.pathname,
              message: 'Você precisa estar logado para acessar esta aula'
            }
          });
          return;
        }
        setHasAccess(false);
        setIsChecking(false);
        return;
      }

      // Verificar se é admin primeiro
      try {
        const adminResponse = await fetch('/api/auth/check-admin', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (adminResponse.ok) {
          const adminData = await adminResponse.json();
          if (adminData.is_admin) {
            setIsAdmin(true);
            setHasAccess(true);
            setIsChecking(false);
            return;
          }
        }
      } catch (error) {
        console.error('Erro ao verificar admin:', error);
      }

      // Para usuários não-admin, verificar acesso ao curso
      // Se está logado, sempre permitir acesso (mostrar indicador visual)
      setHasAccess(true);
      
      // Verificar se tem acesso real ao curso para mostrar indicador
      const localAccess = hasAccessToLesson(lessonId);
      if (!localAccess) {
        // Buscar informações do curso para o indicador
        findCourseInfo();
      }
    } catch (error) {
      console.error('Erro ao verificar acesso:', error);
      setHasAccess(false);
    } finally {
      setIsChecking(false);
    }
  };

  /**
   * Encontra informações do curso baseado na aula
   */
  const findCourseInfo = () => {
    for (const [courseId, course] of Object.entries(availableCourses)) {
      if (course.lessons && course.lessons.includes(lessonId)) {
        setCourseInfo({
          courseId,
          name: course.name,
          description: course.description,
          price: course.price
        });
        break;
      }
    }
  };

  /**
   * Redireciona para a página de login
   */
  const handleLoginRedirect = () => {
    navigate('/login', { 
      state: { 
        returnUrl: window.location.pathname,
        message: 'Faça login para acessar esta aula'
      }
    });
  };

  /**
   * Redireciona para a vitrine de cursos
   */
  const handleBrowseCourses = () => {
    navigate('/vitrine-alunos');
  };

  // Loading state
  if (isChecking || coursesLoading) {
    return (
      <LoadingContainer>
        <div className="spinner" />
        <p>Verificando acesso à aula...</p>
      </LoadingContainer>
    );
  }

  // Se tem acesso, renderizar o conteúdo
  if (hasAccess) {
    return <>{children}</>;
  }

  // Se não tem acesso, mostrar tela de bloqueio
  return (
    <AccessDeniedContainer>
      <AccessDeniedIcon>
        <Lock size={40} />
      </AccessDeniedIcon>
      
      <AccessDeniedTitle>
        Acesso Restrito
      </AccessDeniedTitle>
      
      <AccessDeniedMessage>
        Esta aula faz parte de um curso pago. Para acessar este conteúdo, 
        você precisa adquirir o curso correspondente.
      </AccessDeniedMessage>

      {courseInfo && (
        <CourseInfoCard>
          <h3>{courseInfo.name}</h3>
          <p>{courseInfo.description}</p>
        </CourseInfoCard>
      )}

      {/* Verificar se está logado */}
      {!localStorage.getItem('token') ? (
        <>
          <ActionButton onClick={handleLoginRedirect}>
            <AlertCircle size={20} />
            Fazer Login
          </ActionButton>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem' }}>
            Já tem uma conta? Faça login para verificar seus cursos.
          </p>
        </>
      ) : (
        <>
          {/* Mostrar checkout se disponível */}
          {showCheckout && courseInfo ? (
            <MercadoPagoCheckout
              courseId={courseInfo.courseId}
              course={{
                name: courseInfo.name,
                description: courseInfo.description,
                price: courseInfo.price
              }}
              onSuccess={() => {
                // Recarregar a página após compra bem-sucedida
                window.location.reload();
              }}
              onError={(error) => {
                console.error('Erro no checkout:', error);
              }}
            />
          ) : (
            <>
              <ActionButton onClick={handleBrowseCourses}>
                <ShoppingCart size={20} />
                Ver Cursos Disponíveis
              </ActionButton>
              <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem' }}>
                Explore nossos cursos e encontre o que você precisa.
              </p>
            </>
          )}
        </>
      )}
    </AccessDeniedContainer>
  );
};

export default ProtectedLesson;