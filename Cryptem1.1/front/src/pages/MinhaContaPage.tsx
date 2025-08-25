import React, { useState } from 'react';
import styles from './MinhaContaPage.module.css';

interface UserProfile {
  nome: string;
  nomePreferido: string; // Add this line
  email: string;
  senha: string;
  objetivos: string;
  interesses: string[];
  perfilFinanceiro: string;
}

const MinhaContaPage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>({
    nome: '',
    nomePreferido: '', // Ensure this is initialized
    email: '',
    senha: '',
    objetivos: '',
    interesses: [],
    perfilFinanceiro: 'moderado'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProfile(prev => ({ 
      ...prev, 
      [name]: value || '' // Ensure value is never undefined
    }));
  };

  const handleInteresseChange = (interesse: string) => {
    setProfile(prev => {
      const currentInteresses = prev.interesses || []; // Fallback for undefined
      const novosInteresses = currentInteresses.includes(interesse)
        ? currentInteresses.filter(i => i !== interesse)
        : [...currentInteresses, interesse];
      return { ...prev, interesses: novosInteresses };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('nomePreferido', profile.nomePreferido);
    localStorage.setItem('userInterests', JSON.stringify(profile.interesses));
    localStorage.setItem('financialProfile', profile.perfilFinanceiro);
    // Aqui você implementaria a lógica para salvar no backend
    console.log('Perfil atualizado:', profile);
    alert('Perfil atualizado com sucesso!');
  };

  return (
    <div className={styles.container}>
      <h1>Minha Conta</h1>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label>Nome Completo</label>
          <input
            type="text"
            name="nome"
            value={profile.nome}
            onChange={handleChange}
            required
          />
        </div>

        {/* Add this new form group */}
        <div className={styles.formGroup}>
          <label>Como quero ser chamado</label>
          <input
            type="text"
            name="nomePreferido"
            value={profile.nomePreferido}
            onChange={handleChange}
            placeholder="Nome que o Zion usará para se referir a você"
          />
        </div>

        <div className={styles.formGroup}>
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={profile.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label>Senha</label>
          <input
            type="password"
            name="senha"
            value={profile.senha}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label>Objetivos Financeiros</label>
          <textarea
            name="objetivos"
            value={profile.objetivos}
            onChange={handleChange}
            placeholder="Ex: Quero atingir 1 milhão em 5 anos..."
          />
        </div>

        <div className={styles.formGroup}>
          <label>Interesses</label>
          <div className={styles.checkboxGroup}>
            {['Tecnologia', 'Investimentos', 'Empreendedorismo', 'Criptomoedas', 'Imóveis'].map(item => (
              <label key={item}>
                <input
                  type="checkbox"
                  checked={profile.interesses.includes(item)}
                  onChange={() => handleInteresseChange(item)}
                />
                {item}
              </label>
            ))}
          </div>
        </div>

        <div className={styles.formGroup}>
          <label>Perfil Financeiro</label>
          <select
            name="perfilFinanceiro"
            value={profile.perfilFinanceiro}
            onChange={handleChange}
          >
            <option value="conservador">Conservador</option>
            <option value="moderado">Moderado</option>
            <option value="arrojado">Arrojado</option>
          </select>
        </div>

        <button type="submit" className={styles.submitButton}>
          Salvar Perfil
        </button>
      </form>
    </div>
  );
};

export default MinhaContaPage;