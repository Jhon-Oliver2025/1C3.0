import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaUsers, FaShoppingCart, FaDollarSign, FaEye, FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';

// Interfaces
interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  last_login?: string;
  status: 'active' | 'inactive';
}

interface Purchase {
  id: string;
  user_id: string;
  course_id: string;
  payment_id: string;
  status: 'pending' | 'approved' | 'rejected';
  amount: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

interface CourseAccess {
  id: string;
  user_id: string;
  course_id: string;
  purchase_id: string;
  granted_at: string;
  expires_at?: string;
  status: 'active' | 'expired' | 'revoked';
}

// Styled Components
const CRMContainer = styled.div`
  background-color: #000000;
  min-height: 100vh;
  color: white;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 12px;
  border: 1px solid #3b82f6;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const Logo = styled.img`
  height: 40px;
  width: auto;
`;

const Title = styled.h1`
  color: #64FFDA;
  font-size: 2.5em;
  margin: 0;
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #3b82f6;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-2px);
  }
`;

const StatIcon = styled.div`
  font-size: 2em;
  color: #64FFDA;
  margin-bottom: 10px;
`;

const StatValue = styled.div`
  font-size: 2em;
  font-weight: bold;
  color: white;
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  color: #94a3b8;
  font-size: 0.9em;
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #1e293b;
`;

const Tab = styled.button<{ $active: boolean }>`
  background: ${props => props.$active ? '#3b82f6' : 'transparent'};
  color: ${props => props.$active ? 'white' : '#94a3b8'};
  border: none;
  padding: 15px 25px;
  cursor: pointer;
  font-size: 1em;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$active ? '#3b82f6' : '#1e293b'};
    color: white;
  }
`;

const TableContainer = styled.div`
  background: #1e293b;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  background: #334155;
  padding: 15px;
  text-align: left;
  color: #64FFDA;
  font-weight: 600;
  border-bottom: 2px solid #3b82f6;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background: #2d3748;
  }

  &:hover {
    background: #374151;
  }
`;

const TableCell = styled.td`
  padding: 12px 15px;
  border-bottom: 1px solid #374151;
`;

const StatusBadge = styled.span<{ $status: string }>`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  background: ${props => {
    switch (props.$status) {
      case 'active': case 'approved': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'inactive': case 'rejected': case 'expired': case 'revoked': return '#ef4444';
      default: return '#6b7280';
    }
  }};
  color: white;
`;

const ActionButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin: 0 2px;
  font-size: 0.9em;
  transition: background 0.2s ease;

  &:hover {
    background: #2563eb;
  }

  &.danger {
    background: #ef4444;

    &:hover {
      background: #dc2626;
    }
  }

  &.success {
    background: #10b981;

    &:hover {
      background: #059669;
    }
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.2em;
  color: #64FFDA;
`;

/**
 * Página de CRM para gerenciamento de usuários, compras e acessos
 */
const CRMPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'users' | 'purchases' | 'access'>('users');
  const [isLoading, setIsLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [courseAccess, setCourseAccess] = useState<CourseAccess[]>([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPurchases: 0,
    totalRevenue: 0,
    activeAccess: 0
  });

  // Verificar se é admin
  useEffect(() => {
    const checkAdminAccess = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login', {
          state: {
            returnUrl: '/crm',
            message: 'Faça login para acessar o CRM'
          }
        });
        return;
      }

      try {
        // Verificar se o usuário é admin
        const response = await fetch('/api/auth/check-admin', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.is_admin) {
            // Usuário é admin, carregar dados
            loadData();
          } else {
            // Usuário não é admin, redirecionar para dashboard
            navigate('/dashboard', {
              state: {
                message: 'Acesso negado: Apenas administradores podem acessar o CRM'
              }
            });
          }
        } else {
          // Token inválido ou erro, redirecionar para login
          localStorage.removeItem('token');
          navigate('/login', {
            state: {
              returnUrl: '/crm',
              message: 'Sessão expirada. Faça login novamente'
            }
          });
        }
      } catch (error) {
        console.error('Erro ao verificar permissão de admin:', error);
        navigate('/dashboard', {
          state: {
            message: 'Erro ao verificar permissões. Tente novamente'
          }
        });
      }
    };

    checkAdminAccess();
  }, [navigate]);

  /**
   * Carrega todos os dados do CRM
   */
  const loadData = async () => {
    setIsLoading(true);
    try {
      // Simular dados por enquanto - em produção, fazer chamadas para API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Dados simulados
      const mockUsers: User[] = [
        {
          id: '1',
          email: 'usuario1@example.com',
          name: 'João Silva',
          created_at: '2024-01-15T10:30:00Z',
          last_login: '2024-01-20T14:22:00Z',
          status: 'active'
        },
        {
          id: '2',
          email: 'usuario2@example.com',
          name: 'Maria Santos',
          created_at: '2024-01-16T09:15:00Z',
          last_login: '2024-01-19T16:45:00Z',
          status: 'active'
        }
      ];

      const mockPurchases: Purchase[] = [
        {
          id: '1',
          user_id: '1',
          course_id: 'despertar_crypto',
          payment_id: 'MP_001',
          status: 'approved',
          amount: 197.00,
          currency: 'BRL',
          created_at: '2024-01-15T11:00:00Z',
          updated_at: '2024-01-15T11:05:00Z'
        },
        {
          id: '2',
          user_id: '2',
          course_id: 'masterclass',
          payment_id: 'MP_002',
          status: 'pending',
          amount: 497.00,
          currency: 'BRL',
          created_at: '2024-01-16T10:30:00Z',
          updated_at: '2024-01-16T10:30:00Z'
        }
      ];

      const mockAccess: CourseAccess[] = [
        {
          id: '1',
          user_id: '1',
          course_id: 'despertar_crypto',
          purchase_id: '1',
          granted_at: '2024-01-15T11:05:00Z',
          status: 'active'
        }
      ];

      setUsers(mockUsers);
      setPurchases(mockPurchases);
      setCourseAccess(mockAccess);
      
      // Calcular estatísticas
      setStats({
        totalUsers: mockUsers.length,
        totalPurchases: mockPurchases.length,
        totalRevenue: mockPurchases.reduce((sum, p) => p.status === 'approved' ? sum + p.amount : sum, 0),
        activeAccess: mockAccess.filter(a => a.status === 'active').length
      });
      
    } catch (error) {
      console.error('Erro ao carregar dados do CRM:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Formata data para exibição com timezone correto do Brasil
   */
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString('pt-BR', {
          timeZone: 'America/Sao_Paulo',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      }
    } catch (error) {
      console.error('Erro ao formatar data:', error);
    }
    return 'Data inválida';
  };

  /**
   * Formata valor monetário
   */
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  /**
   * Renderiza tabela de usuários
   */
  const renderUsersTable = () => (
    <TableContainer>
      <Table>
        <thead>
          <tr>
            <TableHeader>ID</TableHeader>
            <TableHeader>Email</TableHeader>
            <TableHeader>Nome</TableHeader>
            <TableHeader>Criado em</TableHeader>
            <TableHeader>Último Login</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Ações</TableHeader>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <TableRow key={user.id}>
              <TableCell>{user.id}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.name || '-'}</TableCell>
              <TableCell>{formatDate(user.created_at)}</TableCell>
              <TableCell>{user.last_login ? formatDate(user.last_login) : '-'}</TableCell>
              <TableCell>
                <StatusBadge $status={user.status}>{user.status}</StatusBadge>
              </TableCell>
              <TableCell>
                <ActionButton><FaEye /> Ver</ActionButton>
                <ActionButton><FaEdit /> Editar</ActionButton>
                <ActionButton className="danger"><FaTrash /> Excluir</ActionButton>
              </TableCell>
            </TableRow>
          ))}
        </tbody>
      </Table>
    </TableContainer>
  );

  /**
   * Renderiza tabela de compras
   */
  const renderPurchasesTable = () => (
    <TableContainer>
      <Table>
        <thead>
          <tr>
            <TableHeader>ID</TableHeader>
            <TableHeader>Usuário</TableHeader>
            <TableHeader>Curso</TableHeader>
            <TableHeader>Valor</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Data</TableHeader>
            <TableHeader>Ações</TableHeader>
          </tr>
        </thead>
        <tbody>
          {purchases.map(purchase => {
            const user = users.find(u => u.id === purchase.user_id);
            return (
              <TableRow key={purchase.id}>
                <TableCell>{purchase.id}</TableCell>
                <TableCell>{user?.email || purchase.user_id}</TableCell>
                <TableCell>{purchase.course_id}</TableCell>
                <TableCell>{formatCurrency(purchase.amount)}</TableCell>
                <TableCell>
                  <StatusBadge $status={purchase.status}>{purchase.status}</StatusBadge>
                </TableCell>
                <TableCell>{formatDate(purchase.created_at)}</TableCell>
                <TableCell>
                  <ActionButton><FaEye /> Ver</ActionButton>
                  {purchase.status === 'pending' && (
                    <>
                      <ActionButton className="success">Aprovar</ActionButton>
                      <ActionButton className="danger">Rejeitar</ActionButton>
                    </>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </tbody>
      </Table>
    </TableContainer>
  );

  /**
   * Renderiza tabela de acessos
   */
  const renderAccessTable = () => (
    <TableContainer>
      <Table>
        <thead>
          <tr>
            <TableHeader>ID</TableHeader>
            <TableHeader>Usuário</TableHeader>
            <TableHeader>Curso</TableHeader>
            <TableHeader>Concedido em</TableHeader>
            <TableHeader>Expira em</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Ações</TableHeader>
          </tr>
        </thead>
        <tbody>
          {courseAccess.map(access => {
            const user = users.find(u => u.id === access.user_id);
            return (
              <TableRow key={access.id}>
                <TableCell>{access.id}</TableCell>
                <TableCell>{user?.email || access.user_id}</TableCell>
                <TableCell>{access.course_id}</TableCell>
                <TableCell>{formatDate(access.granted_at)}</TableCell>
                <TableCell>{access.expires_at ? formatDate(access.expires_at) : 'Nunca'}</TableCell>
                <TableCell>
                  <StatusBadge $status={access.status}>{access.status}</StatusBadge>
                </TableCell>
                <TableCell>
                  <ActionButton><FaEye /> Ver</ActionButton>
                  {access.status === 'active' && (
                    <ActionButton className="danger">Revogar</ActionButton>
                  )}
                  {access.status === 'revoked' && (
                    <ActionButton className="success">Reativar</ActionButton>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </tbody>
      </Table>
    </TableContainer>
  );

  if (isLoading) {
    return (
      <CRMContainer>
        <LoadingSpinner>Carregando dados do CRM...</LoadingSpinner>
      </CRMContainer>
    );
  }

  return (
    <CRMContainer>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Gerencie seu ecossistema com precisão e transforme dados em resultados.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
      <div className="mobile-safety-gap"></div>
    </div>

    {/* CONTEÚDO DA PÁGINA CRM */}
    <Header>
        <LogoContainer>
          <Title>CRM - Gestão Completa</Title>
        </LogoContainer>
        <div>
          <span style={{ color: '#94a3b8', fontSize: '0.9em' }}>
            {new Date().toLocaleDateString('pt-BR')}
          </span>
        </div>
      </Header>

      {/* Estatísticas */}
      <StatsContainer>
        <StatCard>
          <StatIcon><FaUsers /></StatIcon>
          <StatValue>{stats.totalUsers}</StatValue>
          <StatLabel>Total de Usuários</StatLabel>
        </StatCard>
        <StatCard>
          <StatIcon><FaShoppingCart /></StatIcon>
          <StatValue>{stats.totalPurchases}</StatValue>
          <StatLabel>Total de Compras</StatLabel>
        </StatCard>
        <StatCard>
          <StatIcon><FaDollarSign /></StatIcon>
          <StatValue>{formatCurrency(stats.totalRevenue)}</StatValue>
          <StatLabel>Receita Total</StatLabel>
        </StatCard>
        <StatCard>
          <StatIcon><FaPlus /></StatIcon>
          <StatValue>{stats.activeAccess}</StatValue>
          <StatLabel>Acessos Ativos</StatLabel>
        </StatCard>
      </StatsContainer>

      {/* Tabs */}
      <TabContainer>
        <Tab 
          $active={activeTab === 'users'} 
          onClick={() => setActiveTab('users')}
        >
          <FaUsers /> Usuários
        </Tab>
        <Tab 
          $active={activeTab === 'purchases'} 
          onClick={() => setActiveTab('purchases')}
        >
          <FaShoppingCart /> Compras
        </Tab>
        <Tab 
          $active={activeTab === 'access'} 
          onClick={() => setActiveTab('access')}
        >
          <FaPlus /> Acessos
        </Tab>
      </TabContainer>

      {/* Conteúdo das tabs */}
    {activeTab === 'users' && renderUsersTable()}
    {activeTab === 'purchases' && renderPurchasesTable()}
    {activeTab === 'access' && renderAccessTable()}
  </CRMContainer>
);
};

export default CRMPage;