from dash import html
from datetime import datetime, timedelta
import pandas as pd
from core.gerenciar_sinais import GerenciadorSinais
from core.database import Database

def create_signal_card(signal):
    try:
        print("Dados do sinal:", signal)

        required_fields = ['type', 'symbol', 'entry_price', 'entry_time']
        for field in required_fields:
            if field not in signal:
                print(f"Campo ausente: {field}")
                return None

        entry_time = pd.to_datetime(signal['entry_time'])
        dias_ativos = (datetime.now() - entry_time).days
        if dias_ativos >= 8:
            return None

        try:
            entry_price = float(signal['entry_price'])
        except (ValueError, TypeError):
            print(f"Erro ao converter entry_price: {signal['entry_price']}")
            entry_price = 0.0

        try:
            # Verificar se devemos usar target_price em vez de tp3
            if 'target_price' in signal:
                tp_price = float(signal['target_price'])
            else:
                tp_price = float(signal.get('tp3', 0))
        except (ValueError, TypeError):
            print("Erro ao converter tp_price")
            tp_price = 0.0

        card_style = {
            'background': 'linear-gradient(135deg, rgba(0,0,51,0.95), rgba(0,0,25,0.98))',
            'padding': '20px',
            'borderRadius': '15px',
            'border': '1px solid rgba(0,127,255,0.2)',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.3)',
            'backdropFilter': 'blur(10px)',
            'marginBottom': '15px',
            'transition': 'all 0.3s ease',
            'width': 'calc(100% - 10px)',
            'margin': '5px',
            'minHeight': '200px'
        }

        # Usar quality_score em vez de score para classificação
        quality_score = float(signal.get('quality_score', signal.get('score', 0)))

        # Verificação de scalping (manter se ainda for relevante para outro tipo de exibição)
        # is_scalping = signal.get('is_scalping', False) # Manter ou remover conforme necessidade

        # --- Início da Edição ---
        # Definir classificação baseada no quality_score (apenas para sinais 80+)
        if quality_score >= 110:
            classification_display = "Sinais ELITE+"
            signal_class_css = 'signal-class-elite-plus'
            classification_style = {
                'color': '#FFD700',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'left',
                'textShadow': '0 0 5px #FFD700, 0 0 10px #FFD700, 0 0 15px #FFD700'
            }
        elif quality_score >= 95:
            classification_display = "Sinais ELITE"
            signal_class_css = 'signal-class-elite'
            classification_style = {
                'color': '#FFD700',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'left',
                'textShadow': '0 0 5px #FFD700, 0 0 10px #FFD700'
            }
        elif quality_score >= 85:
            classification_display = "Sinais PREMIUM+"
            signal_class_css = 'signal-class-premium-plus'
            classification_style = {
                'color': '#C0C0C0',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'left',
                'textShadow': '0 0 5px #C0C0C0'
            }
        elif quality_score >= 80:
            classification_display = "Sinais PREMIUM"
            signal_class_css = 'signal-class-premium'
            classification_style = {
                'color': '#C0C0C0',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'left',
                'textShadow': '0 0 5px #C0C0C0'
            }
        else:
             # Se o score for menor que 80, não deve gerar card com o filtro atual
             # Mantemos fallback para dados antigos
            classification_display = "❌ Score Insuficiente"
            signal_class_css = 'signal-class-low' # Opcional: definir uma classe para scores baixos
            classification_style = {
                'color': '#FF0000',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'left'
            }

        classification = html.Div(
            classification_display,
            className=f'signal-class {signal_class_css}',
            style=classification_style # Aplicar estilo inline ou confiar apenas no CSS
        )
        # --- Fim da Edição ---

        # Calcular porcentagem de lucro potencial
        if signal['type'] == 'LONG':
            profit_percent = ((tp_price - entry_price) / entry_price) * 100
        else:  # SHORT
            profit_percent = ((entry_price - tp_price) / entry_price) * 100

        formatted_time = pd.to_datetime(signal['entry_time']).strftime('%d/%m/%Y %H:%M')

        return html.Div([
            html.Div([
                html.Div([
                    html.Div(signal['symbol'], style={
                        'color': '#FFFFFF',
                        'fontWeight': 'bold',
                        'fontSize': '22px',
                        'marginRight': '20px'
                    }),
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(
                    "COMPRA" if signal['type'] == 'LONG' else "VENDA",
                    style={
                        'color': '#00ff00' if signal['type'] == 'LONG' else '#ff4444',
                        'fontWeight': 'bold',
                        'fontSize': '18px',
                        'letterSpacing': '0.5px'
                    }
                )
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '15px'}),

            html.Div(classification, style={
                'fontSize': '14px',
                'marginBottom': '15px',
                'fontWeight': 'bold',
                'textAlign': 'left'
            }),

            html.Div([
                html.Div([
                    html.Span("💰 Entrada: ", style={
                        'color': '#007FFF',
                        'fontSize': '14px'
                    }),
                    html.Span(f"${entry_price:.8f}", style={
                        'color': '#FFFFFF',
                        'fontWeight': 'bold'
                    })
                ], style={'marginBottom': '8px'}),

                html.Div([
                    html.Div([
                        html.Span("🎯 Alvo: ", style={
                            'color': '#007FFF',
                            'fontSize': '14px'
                        }),
                        html.Span(f"${tp_price:.8f}", style={
                            'color': '#FFD700',
                            'fontWeight': 'bold'
                        }),
                        html.Span(f" ({profit_percent:+.1f}%)", style={
                            'color': '#00ff00' if profit_percent > 0 else '#ff4444',
                            'fontSize': '13px',
                            'marginLeft': '5px',
                            'fontWeight': 'bold'
                        })
                    ]),
                    html.Div([
                        html.Span("🕒 ", style={
                            'marginRight': '5px'
                        }),
                        html.Span(formatted_time, style={
                            'color': '#FFFFFF',
                            'fontSize': '13px',
                            'opacity': '0.9'
                        })
                    ], style={
                        'marginTop': '5px',
                        'display': 'flex',
                        'alignItems': 'center'
                    })
                ])
            ], style={
                'background': 'rgba(0,0,0,0.2)',
                'padding': '10px',
                'borderRadius': '8px',
                'marginBottom': '10px'
            })
        ], style=card_style)

    except Exception as e:
        print(f"Erro detalhado ao criar card: {str(e)}")
        print(f"Dados do sinal que causou erro: {signal}")
        return html.Div("Erro ao criar card", style={'color': '#FF0000'})

# --- Início da Edição ---
# REMOVA A PRIMEIRA DEFINIÇÃO DE create_signals_container ABAIXO
# O código comentado aqui era a primeira definição da função
# Ele está sendo removido para corrigir os erros de sintaxe
# --- Fim da Edição ---


# Adicione esta linha no final do arquivo
__all__ = ['create_signals_container']


def create_signals_container(signals_list): # Usar signals_list como na primeira definição
    """Cria o container principal para exibir os sinais."""
    try:
        print("Iniciando processamento dos sinais...")

        if not signals_list:
            print("Nenhum sinal na lista")
            # --- Início da Edição ---
            # Adicionar de volta o botão e o header quando não há sinais
            restart_button = html.Button(
                'Reiniciar Sinais',
                id='restart-signals-button',
                n_clicks=0, # Ensure n_clicks is followed by a comma or closing parenthesis
                style={
                    'backgroundColor': '#FF4444',
                    'color': 'white',
                    'padding': '10px 20px',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'marginTop': '10px',
                    'marginBottom': '20px',
                    'transition': 'background-color 0.3s ease',
                    'alignSelf': 'center'
                },
                className='restart-button'
            )
            # REMOVA A LINHA 'continua' QUE ESTÁ CAUSANDO O ERRO AQUI
            return html.Div([
                html.Div([ # ADICIONAR ESTE DIV (HEADER) DE VOLTA
                    html.H2("Sinais de Trading", style={'color': '#FFFFFF'}),
                    restart_button, # Adicionar o botão aqui
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginBottom': '20px'
                }), # ADICIONAR ESTE FECHAMENTO DE DIV DE VOLTA
                html.Div("Aguardando sinais...", style={
                    'color': '#FFFFFF',
                    'textAlign': 'center',
                    'padding': '20px'
                })
            ],
            id='signals-container-div', # Adicionar o ID aqui também
            className='signals-container',
            style={ # Adicionar estilo para ocupar 100% da largura
                'width': '100%',
                'height': '100%',
                'display': 'flex',
                'flexDirection': 'column', # Mudar para coluna para empilhar título/botão e mensagem
                'backgroundColor': 'rgba(0,0,0,0.2)',
                'borderRadius': '15px',
                'padding': '20px'
            })
            # --- Fim da Edição ---


        # Converter para DataFrame para facilitar manipulação
        df = pd.DataFrame(signals_list)
        df['entry_time'] = pd.to_datetime(df['entry_time'])

        # Identificar sinais de scalping no DataFrame (manter se relevante)
        df['is_scalping'] = df.apply(
            lambda x: (
                x.get('is_scalping', False) is True or
                x.get('type_signal') == 'SCALPING' or
                '300%' in str(x.get('signal_class', ''))
            ),
            axis=1
        )

        # --- Início da Edição ---
        # REMOVIDO: Filtrar apenas sinais do dia atual (manter removido)
        # hoje = datetime.now().date()
        # df = df[df['entry_time'].dt.date == hoje]
        # --- Fim da Edição ---

        # Ordenar por horário (mais recente primeiro)
        df = df.set_index('entry_time').sort_index(ascending=False).reset_index()

        # Manter apenas um sinal de cada tipo (LONG/SHORT) por moeda
        df = df.drop_duplicates(subset=['symbol', 'type'], keep='first')

        # Ordenar novamente após o drop_duplicates para garantir a ordem correta
        df = df.sort_values('entry_time', ascending=False)

        # Criar cards para os sinais filtrados
        cards = []
        for _, sinal in df.iterrows():
            try:
                card = create_signal_card(sinal.to_dict())
                if card is not None:
                    cards.append(card)
                    print(f"Card criado com sucesso para: {sinal['symbol']} - {sinal['type']}")
            except Exception as e:
                print(f"Erro ao criar card para {sinal.get('symbol', 'unknown')}: {e}")
                continue

        # Contar sinais de compra e venda
        total_compra = len(df[df['type'] == 'LONG'])
        total_venda = len(df[df['type'] == 'SHORT'])

        # --- Início da Edição ---
        # Adicionar de volta o botão de reiniciar sinais
        restart_button = html.Button(
            'Reiniciar Sinais',
            id='restart-signals-button', # ID para o callback
            n_clicks=0,
            style={
                'backgroundColor': '#FF4444', # Cor vermelha para ação de deletar/reiniciar
                'color': 'white',
                'padding': '10px 20px',
                'border': 'none',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'fontWeight': 'bold',
                'marginTop': '10px', # Espaço abaixo do cabeçalho
                'marginBottom': '20px', # Espaço antes dos cards de sinal
                'transition': 'background-color 0.3s ease',
                'alignSelf': 'center' # Centralizar o botão
            },
            className='restart-button' # Classe CSS opcional
        )
        # --- Fim da Edição ---

        # --- Início da Edição ---
        # Adicionar de volta o container principal que envolve o header e os cards
        return html.Div([
            # Header fixo com contadores (sem emojis)
            html.Div([
                html.Div([
                    html.Span(f"Sinais Total: {len(df)}", style={
                        'color': '#FFFFFF',
                        'marginRight': '20px',
                        'fontSize': '18px',
                        'fontWeight': 'bold'
                    }),
                    html.Span(f"Compra: {total_compra}", style={
                        'color': '#00ff00',
                        'marginRight': '20px',
                        'fontSize': '18px',
                        'fontWeight': 'bold'
                    }),
                    html.Span(f"Venda: {total_venda}", style={
                        'color': '#ff4444',
                        'fontSize': '18px',
                        'fontWeight': 'bold'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '15px',
                    'backgroundColor': 'rgba(0,0,51,0.95)',
                    'borderRadius': '10px',
                    'border': '1px solid rgba(0,127,255,0.3)',
                    'marginBottom': '20px',
                    'width': '100%'
                }),
                # Adicionar o botão aqui, abaixo dos contadores
                restart_button,

                # Container dos cards
                html.Div(
                    children=cards,
                    style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '15px',
                        'overflowY': 'auto',
                        'maxHeight': 'calc(100vh - 250px)', # Ajustar altura máxima (removendo espaço do header/botão)
                        'padding': '15px',
                        'width': '100%'
                    }
                )
            ], style={
                'width': '100%', # Alterado para 100%
                'display': 'flex',
                'flexDirection': 'column',
                'backgroundColor': 'rgba(0,0,51,0.95)',
                'borderRadius': '15px',
                'padding': '20px'
            }),
            # REMOVIDA: Coluna da direita com a imagem (manter removida)
        ], style={
            'width': '100%', # Alterado para 100%
            'height': '100%',
            'display': 'flex',
            'flexDirection': 'column', # Alterado para coluna para empilhar o conteúdo
            'backgroundColor': 'rgba(0,0,0,0.2)',
            'borderRadius': '15px',
            'padding': '20px'
        },
        id='signals-container-div') # Manter o ID ao container principal
        # --- Fim da Edição ---

    except Exception as e:
        print(f"❌ Erro ao criar container de sinais: {e}")
        return html.Div("Erro ao carregar sinais", style={'color': '#FF0000', 'textAlign': 'center'})

# --- Início da Edição ---
# REMOVA A SEGUNDA DEFINIÇÃO DE create_signals_container ABAIXO (manter removida)
# O código comentado aqui era uma segunda definição da função
# Ele está sendo removido para evitar duplicação e erros
# --- Fim da Edição ---