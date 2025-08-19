import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import logo from '../assets/logo.png';
import AccessIndicator from './AccessIndicator/AccessIndicator';

interface Course {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  progress?: string;
  price?: string;
  link: string;
}

interface Section {
  type: 'banner' | 'course_list' | 'promo_banners' | 'community_text';
  image?: string;
  title?: string;
  subtitle?: string;
  filter?: 'purchased' | 'recommended' | 'masterclass' | 'app_mentoria';
  courses?: Course[];
  banners?: {
    text: string;
    text_color: string;
    background_color: string;
  }[];
  text?: string;
}

interface Layout {
  sections: Section[];
}

interface CourseShowcaseProps {
  data: Layout;
  userAccess?: {
    hasDespertarCrypto: boolean;
    hasMasterclass: boolean;
    hasAppMentoria: boolean;
  };
  isAdmin?: boolean;
}

const ShowcaseContainer = styled.div`
  background-color: #000000;
  color: #fff;
  min-height: 100vh; /* Garante que o fundo escuro cubra toda a tela */
`;

const ContentWrapper = styled.div`
  padding: 0 20px; /* Padding lateral para o conteúdo */
  max-width: 1200px; /* Largura máxima para o conteúdo principal */
  margin: 0 auto; /* Centraliza o conteúdo */
`;

const Banner = styled.div<{ $imageUrl: string }>`
  background-image: url(${props => props.$imageUrl});
  background-size: cover;
  background-position: center;
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
`;

const BannerTitle = styled.h1`
  font-size: 3em;
  margin-bottom: 10px;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
`;

const BannerSubtitle = styled.p`
  font-size: 1.5em;
  color: #e5e5e5;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
`;

const ProgressContainer = styled.div`
  margin-top: 20px;
  width: 100%;
  max-width: 400px;
`;

const ProgressLabel = styled.p`
  font-size: 1em;
  margin-bottom: 10px;
  color: #00bcd4;
  font-weight: bold;
`;

const ProgressBarContainer = styled.div`
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
`;

const ProgressBarFill = styled.div<{ $progress: number }>`
  height: 100%;
  background: linear-gradient(90deg, #2196f3, #00bcd4);
  width: ${props => props.$progress}%;
  transition: width 0.3s ease;
`;

const SectionTitle = styled.h2`
  font-size: 2em;
  margin-bottom: 20px;
  color: #e5e5e5;
`;

const CourseRow = styled.div`
  display: flex;
  overflow-x: auto;
  gap: 15px;
  margin-bottom: 40px;
  padding-bottom: 10px;
  
  &::-webkit-scrollbar {
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #333;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #666;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #888;
  }
`;

const PromoBannerContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 40px;
  justify-content: center;
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
  }
`;

const PromoBanner = styled.div<{ $backgroundColor: string }>`
  width: 100%;
  height: 120px;
  background: linear-gradient(135deg, 
    ${props => props.$backgroundColor} 0%, 
    #1e293b 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  border: 1px solid #3b82f6;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 30% 70%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 70% 30%, rgba(147, 197, 253, 0.05) 0%, transparent 50%);
    pointer-events: none;
  }
  
  @media (max-width: 768px) {
     height: 100px;
     padding: 15px;
   }
`;

const PromoBannerText = styled.p<{ $textColor: string }>`
  color: ${props => props.$textColor};
  font-size: 1.4em;
  font-weight: 600;
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.7),
    0 0 8px rgba(59, 130, 246, 0.3);
  margin: 0;
  position: relative;
  z-index: 10;
  letter-spacing: 0.3px;
  line-height: 1.4;
  
  @media (max-width: 768px) {
    font-size: 1.2em;
    letter-spacing: 0.2px;
  }
`;

const CommunityTextContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 30px 20px;
  margin: 30px 0;
  background: transparent;
  text-align: center;
  
  @media (max-width: 768px) {
    gap: 20px;
    padding: 20px 15px;
    margin: 20px 0;
  }
`;

const CommunityText = styled.p`
  color: #ffffff;
  font-size: 2em;
  font-weight: 400;
  margin: 0;
  line-height: 1.4;
  font-family: Arial, sans-serif;
  
  @media (max-width: 768px) {
    font-size: 1.8em;
  }
`;

const CommunityLogo = styled.img`
  width: 240px;
  height: 240px;
  object-fit: contain;
  
  @media (max-width: 768px) {
    width: 160px;
    height: 160px;
  }
`;

const CourseCard = styled.div`
  background-color: #222;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
  cursor: pointer;
  min-width: 200px;
  flex-shrink: 0;
  position: relative;

  &:hover {
    transform: scale(1.05);
  }
`;

const CourseImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
`;

const CourseInfo = styled.div`
  padding: 15px;
`;

const CourseTitle = styled.h3`
  font-size: 1.2em;
  margin-bottom: 10px;
  color: #fff;
`;

const CourseDescription = styled.p`
  font-size: 0.9em;
  color: #aaa;
  margin-bottom: 10px;
`;

const CourseStatus = styled.p`
  font-size: 0.8em;
  color: #00b894; /* Cor para progresso */
  font-weight: bold;
`;

const CoursePrice = styled.p`
  font-size: 1em;
  color: #ffeaa7; /* Cor para preço */
  font-weight: bold;
`;

const CourseShowcase: React.FC<CourseShowcaseProps> = ({ data, userAccess, isAdmin }) => {
  
  // Função para verificar se o usuário tem acesso a uma seção
  const hasAccessToSection = (filter?: string) => {
    if (!userAccess || !filter) return true;
    
    switch (filter) {
      case 'purchased':
        return userAccess.hasDespertarCrypto;
      case 'masterclass':
        return userAccess.hasMasterclass;
      case 'app_mentoria':
        return userAccess.hasAppMentoria;
      default:
        return true;
    }
  };
  
  // Para admins, mostrar todas as seções. Para usuários normais, filtrar baseado no acesso
  const filteredSections = isAdmin ? data.sections : data.sections.filter(section => {
    if (section.type === 'course_list') {
      return hasAccessToSection(section.filter);
    }
    return true;
  });
  // Estado para armazenar o progresso dos vídeos
  const [videoProgressData, setVideoProgressData] = useState<{[key: string]: {currentTime: number, duration: number}}>({});
  
  // Carrega o progresso dos vídeos do localStorage
  useEffect(() => {
    const saved = localStorage.getItem('videoProgressData');
    if (saved) {
      setVideoProgressData(JSON.parse(saved));
    }
  }, []);
  
  /**
   * Calcula o progresso de uma aula específica
   */
  const calculateLessonProgress = (lessonId: string): number => {
    const progressData = videoProgressData[lessonId];
    if (progressData && progressData.duration > 0) {
      return Math.round((progressData.currentTime / progressData.duration) * 100);
    }
    return 0;
  };
  
  /**
   * Calcula o progresso geral do curso
   */
  const calculateCourseProgress = (): number => {
    let totalWatchedTime = 0;
    let totalDuration = 0;
    
    // Considera todas as aulas do curso Despertar Crypto (IDs 1-8)
    for (let i = 1; i <= 8; i++) {
      const progressData = videoProgressData[i.toString()];
      if (progressData) {
        totalWatchedTime += progressData.currentTime;
        totalDuration += progressData.duration;
      }
    }
    
    return totalDuration > 0 ? Math.round((totalWatchedTime / totalDuration) * 100) : 0;
  };
  
  return (
    <ShowcaseContainer>
      <ContentWrapper>
        {filteredSections.map((section, index) => {
          if (section.type === 'banner' && section.image) {
            return (
              <Banner key={index} $imageUrl={section.image}>
                <BannerTitle>{section.title}</BannerTitle>
                {section.subtitle && <BannerSubtitle>{section.subtitle}</BannerSubtitle>}
              </Banner>
            );
          } else if (section.type === 'promo_banners' && section.banners) {
            return (
              <PromoBannerContainer key={index}>
                {section.banners.map((banner, bannerIndex) => (
                  <PromoBanner key={bannerIndex} $backgroundColor={banner.background_color}>
                    <PromoBannerText $textColor={banner.text_color}>{banner.text}</PromoBannerText>
                  </PromoBanner>
                ))}
              </PromoBannerContainer>
            );
          } else if (section.type === 'course_list' && section.courses) {
            const courseProgress = section.filter === 'purchased' ? calculateCourseProgress() : null;
            return (
              <React.Fragment key={index}>
                <SectionTitle>{section.title}</SectionTitle>
                {courseProgress !== null && (
                  <ProgressContainer style={{ marginBottom: '20px', marginLeft: 'auto', marginRight: 'auto' }}>
                    <ProgressLabel>Progresso do Curso: {courseProgress}%</ProgressLabel>
                    <ProgressBarContainer>
                      <ProgressBarFill $progress={courseProgress} />
                    </ProgressBarContainer>
                  </ProgressContainer>
                )}
                <CourseRow>
                  {section.courses.map(course => (
                    <CourseCard key={course.id} onClick={() => window.location.href = course.link}>
                      <CourseImage src={course.thumbnail} alt={course.title} />
                      <AccessIndicator
                        hasAccess={hasAccessToSection(section.filter)}
                        isAdmin={isAdmin}
                        courseName={section.title}
                      />
                      <CourseInfo>
                        <CourseTitle>{course.title}</CourseTitle>
                        <CourseDescription>{course.description}</CourseDescription>
                        {course.progress && <CourseStatus>Progresso: {calculateLessonProgress(course.id)}%</CourseStatus>}
                        {course.price && <CoursePrice>{course.price}</CoursePrice>}
                      </CourseInfo>
                    </CourseCard>
                  ))}
                </CourseRow>
              </React.Fragment>
            );
          } else if (section.type === 'community_text' && section.text) {
            return (
              <CommunityTextContainer key={index}>
                <CommunityText>{section.text}</CommunityText>
                <CommunityLogo src={logo} alt="Logo 1Crypten" />
              </CommunityTextContainer>
            );
          }
          return null;
        })}
      </ContentWrapper>
    </ShowcaseContainer>
  );
};

export default CourseShowcase;