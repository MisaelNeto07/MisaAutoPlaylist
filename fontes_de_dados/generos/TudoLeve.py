import re

def otimizar_para_gemini(arquivo_entrada="TudoJunto.txt", arquivo_saida="TudoJunto_Gemini_Minimo.txt"):
    """
    Lê um arquivo com informações de vídeos, extrai os dados relevantes,
    remove duplicatas e os salva em um novo arquivo no formato mais enxuto
    possível para leitura por LLMs como o Gemini.
    """
    separador_original_blocos = "###############################################################\n###############################################################"
    novo_separador_registros = "~~~" # Separador curto e distinto entre registros

    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in:
            conteudo_completo = f_in.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo de entrada: {e}")
        return

    blocos_videos = conteudo_completo.split(separador_original_blocos)
    
    registros_unicos_formatados = []
    # Usaremos um set de tuplas para rastrear vídeos únicos e manter a ordem de aparição
    # (embora o set em si não garanta ordem, a lista registros_unicos_formatados sim)
    videos_ja_processados = set() 

    for bloco_bruto in blocos_videos:
        bloco_limpo = bloco_bruto.strip()
        if not bloco_limpo:
            continue

        # Regex para extrair os valores de forma mais robusta
        # O (.*?) é não-ganancioso para pegar o mínimo possível até a próxima label ou fim da linha
        title_match = re.search(r"Title:\s*(.*?)(?:\nChannel name:|\Z)", bloco_limpo, re.IGNORECASE | re.DOTALL)
        channel_match = re.search(r"Channel name:\s*(.*?)(?:\nUploaded Time:|\Z)", bloco_limpo, re.IGNORECASE | re.DOTALL)
        time_match = re.search(r"Uploaded Time:\s*(.*?)(?:\nVideo url:|\Z)", bloco_limpo, re.IGNORECASE | re.DOTALL)
        url_match = re.search(r"Video url:\s*(.*)", bloco_limpo, re.IGNORECASE | re.DOTALL) # URL é geralmente o último

        title = title_match.group(1).strip() if title_match else "N/A"
        channel = channel_match.group(1).strip() if channel_match else "N/A"
        uploaded_time = time_match.group(1).strip() if time_match else "N/A"
        video_url = url_match.group(1).strip() if url_match else "N/A"

        # Considera um vídeo único pela combinação de todos os seus campos
        # Se a URL sozinha for suficiente para definir unicidade, pode simplificar
        identificador_video = (title, channel, uploaded_time, video_url)

        if video_url != "N/A" and identificador_video not in videos_ja_processados:
            videos_ja_processados.add(identificador_video)
            
            # Formata para o novo arquivo: cada campo em uma nova linha
            registro_formatado = f"{title}\n{channel}\n{uploaded_time}\n{video_url}"
            registros_unicos_formatados.append(registro_formatado)
        elif video_url == "N/A" and bloco_limpo:
             print(f"Aviso: Bloco ignorado por falta de URL ou dados incompletos:\n{bloco_limpo[:100]}...")


    # Escreve os dados processados no arquivo de saída
    try:
        with open(arquivo_saida, 'w', encoding='utf-8') as f_out:
            # Junta os registros formatados com o novo separador
            # O separador será inserido ENTRE os registros
            # Cada registro já termina com \n da URL
            # Adiciona \n antes do separador para que ele fique em sua própria linha.
            texto_saida = f"\n{novo_separador_registros}\n".join(registros_unicos_formatados)
            f_out.write(texto_saida)
            # Adiciona uma nova linha no final do arquivo, se houver registros
            if registros_unicos_formatados:
                f_out.write("\n") 
        
        print(f"Arquivo '{arquivo_saida}' criado com sucesso com {len(registros_unicos_formatados)} registros únicos.")

    except Exception as e:
        print(f"Erro ao escrever o arquivo de saída: {e}")

# Para executar a função:
if __name__ == "__main__":
    otimizar_para_gemini()