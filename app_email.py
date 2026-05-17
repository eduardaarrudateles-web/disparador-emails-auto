import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import time

# Configuração da página da web
st.set_page_config(page_title="Disparador de E-mails", page_icon="✉️")

st.title("✉️ Robô de Disparos Automáticos")
st.write("Suba a lista de contatos para processar os envios em lote diretamente pela nuvem.")

# Área para upload da planilha
arquivo_subido = st.file_uploader("Selecione a planilha de contatos (.xlsx)", type=["xlsx"])

if arquivo_subido is not None:
    tabela = pd.read_excel(arquivo_subido)
    colunas = tabela.columns.tolist()
    
    # Mapeamento dinâmico de colunas caso mude o padrão da planilha
    col_email = st.selectbox("Qual coluna contém os e-mails?", colunas, 
                             index=colunas.index('Email') if 'Email' in colunas else 0)
    col_cpf = st.selectbox("Qual coluna contém os CPFs?", colunas, 
                           index=colunas.index('CPF') if 'CPF' in colunas else 0)

    if st.button("🚀 Iniciar Disparo em Massa"):
        total = len(tabela)
        
        # Interface de progresso visual
        barra = st.progress(0)
        status_texto = st.empty()
        log_container = st.container() # Caixa para exibir o histórico de envios ao vivo
        
        # Configurações de autenticação salvas com segurança
        remetente = "eduarda.arruda.teles@gmail.com"
        
        # Recomenda-se usar st.secrets para proteger senhas se o GitHub for público
        if "gmail_password" in st.secrets:
            senha_app = st.secrets["gmail_password"]
        else:
            senha_app = "ebeosrbsjkwjsytg" # Sua senha de aplicativo atual
        
        sucessos = 0
        erros = 0

        try:
            status_texto.text("🔗 Conectando ao servidor de e-mail do Gmail...")
            
            # Abre a conexão com o servidor SMTP apenas UMA vez antes do loop (deixa o processo muito mais rápido)
            servidor = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            servidor.login(remetente, senha_app)
            
            status_texto.text(f"✅ Conectado! Iniciando o envio de {total} mensagens...")
            
            for index, linha in tabela.iterrows():
                email_cliente = str(linha[col_email]).strip()
                cpf_cliente = str(linha[col_cpf]).strip()
                
                # Valida se a linha possui um e-mail preenchido
                if pd.notna(linha[col_email]) and email_cliente != 'nan':
                    assunto = f"Aviso sobre o CPF {cpf_cliente}"
                    
                    msg = EmailMessage()
                    msg['Subject'] = assunto
                    msg['From'] = remetente
                    msg['To'] = email_cliente
                    msg.set_content("Olá! Este é um e-mail automático disparado pelo nosso novo sistema em Python.")
                    
                    try:
                        servidor.send_message(msg)
                        sucessos += 1
                        with log_container:
                            st.caption(f"✅ E-mail entregue com sucesso para: {email_cliente}")
                    except Exception as e:
                        erros += 1
                        with log_container:
                            st.error(f"❌ Erro ao enviar para {email_cliente}: {e}")
                
                # Atualização da barra de progresso do site em tempo real
                progresso = (index + 1) / total
                barra.progress(progresso)
                status_texto.text(f"Processando: {index + 1} de {total} contatos")
                
                # Pausa estratégica para evitar bloqueios anti-spam do Gmail
                time.sleep(0.5)
                
            # Fecha a conexão após concluir o loop
            servidor.quit()
            st.success(f"🏁 Processamento Concluído! Envios realizados com sucesso: {sucessos} | Falhas: {erros}")
            
        except Exception as e:
            st.error(f"❌ Falha crítica na autenticação com o servidor SMTP: {e}")
