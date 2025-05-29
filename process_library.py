import re
import json
import time
import os
from datetime import datetime
import unicodedata # Para normalização de strings

# --- Constantes de Caminho ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTES_DE_DADOS_DIR = os.path.join(BASE_DIR, "fontes_de_dados")
GENRE_FILES_DIR = os.path.join(FONTES_DE_DADOS_DIR, "generos")
CURATED_TITLES_DIR = os.path.join(FONTES_DE_DADOS_DIR, "titulos_curados")
ORIGINAL_TITLES_RAW_FILENAME = "My YouTube Library - Desorganizada.txt" # Arquivo com títulos originais/brutos
CORRECTED_TITLES_FOR_MAPPING_FILENAME = "Títulos Corrigidos.txt" # Arquivo com títulos curados correspondentes

def normalize_string_for_match(s):
    """Normaliza uma string para uma correspondência mais robusta."""
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize('NFC', s)
    s = s.lower()
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def parse_genre_file_content(file_content, genre):
    """Analisa o conteúdo de um arquivo de gênero e extrai as informações."""
    videos = []
    entries = file_content.split('###############################################################\n###############################################################')
    for entry in entries:
        if entry.strip() == "":
            continue
        video_data = {"genre": genre}
        lines = entry.strip().split('\n')
        for line in lines:
            if line.startswith("Title:"):
                video_data["original_youtube_title"] = line.replace("Title:", "").strip()
            elif line.startswith("Channel name:"):
                video_data["channel_name"] = line.replace("Channel name:", "").strip()
            elif line.startswith("Uploaded Time:"):
                video_data["upload_date"] = line.replace("Uploaded Time:", "").strip()
            elif line.startswith("Video url:"):
                video_data["youtube_url"] = line.replace("Video url:", "").strip()
        if "original_youtube_title" in video_data:
            videos.append(video_data)
    return videos

def load_original_to_curated_map(original_titles_filepath, corrected_titles_filepath):
    """
    Carrega títulos originais brutos e suas versões corrigidas/curadas correspondentes,
    criando um mapa do título original normalizado para o título curado.
    Assume uma correspondência de linha 1 para 1 entre os dois arquivos.
    """
    original_to_curated_map = {}
    try:
        with open(original_titles_filepath, 'r', encoding='utf-8') as f_orig, \
             open(corrected_titles_filepath, 'r', encoding='utf-8') as f_corr:
            
            original_lines = [line.strip() for line in f_orig if line.strip()]
            corrected_lines = [line.strip() for line in f_corr if line.strip()]

            if len(original_lines) != len(corrected_lines):
                print(f"AVISO: O número de linhas em '{os.path.basename(original_titles_filepath)}' ({len(original_lines)}) "
                      f"não corresponde ao de '{os.path.basename(corrected_titles_filepath)}' ({len(corrected_lines)}). "
                      "O mapeamento pode ser incompleto ou incorreto.")
            
            for i in range(min(len(original_lines), len(corrected_lines))):
                norm_original = normalize_string_for_match(original_lines[i])
                curated_title = corrected_lines[i] # Mantém o case original para o valor
                if norm_original not in original_to_curated_map:
                    original_to_curated_map[norm_original] = curated_title
                # else:
                #     print(f"Aviso: Título original normalizado duplicado encontrado e ignorado no mapeamento: '{norm_original}' para o curado '{curated_title}' (mantendo o anterior: '{original_to_curated_map[norm_original]}')")
                    
    except FileNotFoundError:
        print(f"Erro: Um ou ambos os arquivos de mapeamento não foram encontrados: '{original_titles_filepath}', '{corrected_titles_filepath}'")
    except Exception as e:
        print(f"Erro ao carregar o mapa de títulos originais para curados: {e}")
    return original_to_curated_map

def is_likely_music_video(title_info):
    """Determina se um título de vídeo provavelmente é um vídeo de música."""
    title_str = title_info.get('title', "").lower() 
    original_title_str = title_info.get('title', "")
    channel_name = title_info.get('channel_name', "").lower() # Adicionado para heurísticas baseadas no canal

    music_keywords = [
        'ft.', 'feat.', 'featuring', 'prod.', 'produced by', 'official video', 'music video',
        'lyric video', 'lyrics', 'official audio', 'audio', 'remix', 'live', 'album',
        'song', 'music', 'track', 'single', 'records', 'official visualizer', 'visualizer',
        'acústico', 'unplugged', 'cover', 'live session', 'tiny desk', 'colors show',
        'clipe oficial', 'pseudo vídeo', 'versão oficial', 'áudio oficial', '(ep)',
        'live at', 'tema de', 'soundtrack', 'ost', 'hd', 'opening', 'ending', 'op', 'ed',
        'parody', 'paródia', 'musical', 'animated music video', 'starbomb', 'the living tombstone',
        'amv', 'mv', 
        'mashup', 'remix', 'medley', 'concerto', 'symphony', 'ballad', 'serenade', 'rhapsody',
        'full version', 'full song', 'pancadão', 'axé music',
        'capoeira', 'ponto de umbanda', 'samba de roda', 'embolada', 'jazz cover', 'instrumental' # Novas keywords
    ]
    non_music_keywords_general = [
        'episode', 'review', 'gameplay', 'trailer', 'tutorial', 'vlog',
        'podcast', 'how to', 'unboxing', 'documentary', 'news',
        'commentary', 'preview', 'hfil', 'minecraft', 'tekken',
        'dragon ball', 'street fighter', 'photoshop', 'asmr', 
        'standup', 'explained', 'science', 'reaction', 'interview',
        'highlights', 'full cast', 'deep dive', 'analysis', 'showcase',
        'old is cool', 'dicas e curiosidades', 'gaveta', 'cortes do flow',
        'nerdologia', 'manual do mundo', 'einerd',
        'recipe', 'cooking', 'kitchen', 'cake', 'food', 'restaurant',
        'mod', 'modpack', 'speedrun', 'walkthrough', 'let\'s play',
        'tier list', 'ranking', # Removido 'vs' daqui, será tratado com mais cuidado
        'ufc', 'mma', 'wwe', 'workout', 'fitness', 'bodybuilding',
        'clash royale', 'yu-gi-oh', 'yugioh', 'pokemon', 'magic the gathering',
        'd&d', 'rpg', 'baldurs gate', 'skyrim', 'fallout', 'gta', 'witcher 3',
        'financial', 'stocks', 'crypto', 'diy', 'life hack',
        'ytpbr', 'análise', 'guia', 'dicas', 'segredos',
        'reel', 'efeito', 'redesign', 'prompts', 'features', 'updates',
        'platform', 'startup', 'workflow', 'hack', 'tricks',
        'plugin', 'intervalo', 'comerciais', 'coleção de comerciais',
        'aula', 'curso', 'palestra', 'webinar', 'behind the scenes',
        'erros de gravação', 'bloopers', 'deleted scenes',
        'compilado', 'reação', 'react', 'assistindo', 'jogando',
        'legendado'
    ]
    tech_design_non_music_keywords = [
        "davinci resolve", "framer", "chatgpt", "image generator", "openai",
        "ai agents", "comfyui", "gemini 2.5", "ai image/video platform",
        "photoshop running slow", "copy paste colors", "ai news", "text to speech",
        "flux", "n8n", "feedhive", "runway gen-3", "speed ramping", "collage video effect",
        "parallax", "llm in comfyui"
    ]

    # --- Regras de Alta Prioridade ---
    if original_title_str == "Michael Jackson - History": return True
    if "pink guy" in title_str and "teriyaki god" in title_str: return True
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str: return True
    if "mc twist e mc brinquedo" in title_str and "ela caiu caillou" in title_str: return True
    if "mc pikachu" in title_str and "tava no fluxo" in title_str: return True
    if "mc" in title_str and any(prod_kw in title_str for prod_kw in ['prod.', 'produced by']): return True
    if "paródia musical" in title_str: return True
    if "axé music" in title_str and "kame kame kame ha" in title_str and "dragon ball" in title_str: return True
    if "guile's theme" in title_str and "jazz cover" in title_str and "j-music pocket band" in title_str: return True # Específico para Guile's Theme

    if "narrando o clipe" in title_str:
        if " - " in title_str or "#" in original_title_str or \
           any(mkw in title_str for mkw in ['song', 'music', 'clipe', 'parody', 'paródia', 'remix', 'cover', 'ft.', 'feat.']):
            return True
        if "one direction" in title_str and "what makes you beautiful" in title_str: return True
        return True # Ser mais inclusivo para "Narrando o Clipe"

    if any(kw in title_str for kw in tech_design_non_music_keywords): return False
    if "pipoca e nanquim" in title_str or "kitinete hq" in title_str: return False
    if "neil gaiman" in title_str and any(kw in title_str for kw in ["sandman", "cost", "graphic novel", "explained", "interview", "documentary", "stories within us", "success of", "behind the scenes", "first look", "trailer", "audible", "changes from comic", "on netflix"]): return False
    if "virtual barber shop" in title_str or "o barbeiro virtual audio 3d" in title_str: return False
    if "ytpbr" in title_str : return False
    if title_str.startswith("como ganhar flexibilidade") or title_str.startswith("alongamento geral básico"): return False
    if "mrpoladoful" in title_str and not any(kw in title_str for kw in ["song", "clipe oficial", "paródia", "musical", "paródia musical"]): return False
    if "asmr" in title_str and not any(kw in title_str for kw in ["song", "music", "singing", "cover"]): return False
    if title_str.startswith("qual endereço você usou"): return False
    if "rogerinho se descontrola #choquedecultura" in title_str: return False
    if "vampire the masquerade" in title_str and "review" in title_str: return False
    if "the death and rebirth of vampire: bloodlines" in title_str: return False
    if "easy dreadlocks styles" in title_str: return False
    if original_title_str == "The Scariest Comic of All Time": return False

    if "starbomb" in title_str or "erB" in original_title_str or "epic rap battles of history" in title_str: return True
    if "the living tombstone" in title_str: return True
    if "paródia" in title_str and any(artist_parody in title_str for artist_parody in ["matuê", "hungria hip hop", "costa gold", "emicouto", "mc vv", "eminem", "rihanna", "pollo", "psy", "alicia keys", "bruno mars", "chainsmokers", "luan santana", "restart"]): return True
    if "leod" in title_str and any(kw in title_str for kw in ["|", "mashup", "remix", "anos 80", "anos 90", "pt.", "ft.", "version", "extended", "kawaii", "club"]): return True
    if any(poze_kw in title_str for poze_kw in ["mc poze nos anos", "say poze", "marlboro poze", "descobridor dos sete pozes", "cheiro de say so", "cheiro de daft punk", "cheiro de pneu queimado", "sopa de macaco"]): return True
    if "smosh" in title_str and "song" in title_str : return True
    if "asdfmovie" in title_str and "song" in title_str: return True
    if "(egoraptor)" in title_str and "minecraft is for everyone" in title_str: return True
    if "tetris rap animated" in title_str: return True
    if "cyberpunk 2077" in title_str and "never fade away" in title_str and "by samurai" in title_str : return True
    if "charlie brown jr" in title_str and "lutar pelo que é meu" in title_str : return True
    if "revelação" in title_str and "velocidade da luz" in title_str: return True
    if "os tincoas" in title_str and "cordeiro de nanã" in title_str : return True
    if "king harvest" in title_str and "dancing in the moonlight" in title_str: return True
    if "terezinha e roque josé" in title_str and "emboladores" in title_str: return True

    anime_op_ed_pattern = r'(?:opening|ending|op|ed)\s*\d*\s*(?:full|version|hd|creditless|ncorp|nced)?\s*(?:\[|﹝|『|「|<|\||$)'
    if re.search(anime_op_ed_pattern, title_str) or \
       (any(anime_name in title_str for anime_name in ["jojo's bizarre adventure", "noragami", "naruto", "one punch man", "toriko", "mirai nikki", "one piece", "death parade"]) and any(op_ed_kw in title_str for op_ed_kw in ["opening", "ending", "op", "ed", "theme"])):
        return True
    if "hello sleepwalkers" in title_str and "午夜の待ち合わせ" in original_title_str: return True
    if "the oral cigarettes" in title_str and "狂乱 hey kids!!" in original_title_str: return True

    common_music_pattern_strict = r"^\s*[^-\n\[\(/:·]{2,}\s*(?:-|–|—|:|·|\/)\s*[^-\n\[\(/:·]{2,}"
    common_music_pattern_spaced = r"^\s*[^-\n\[\(/:·]{2,}\s+(?:-|–|—|:|·|\/)\s+[^-\n\[\(/:·]{2,}"
    is_common_artist_song_pattern = re.match(common_music_pattern_spaced, title_str, flags=re.IGNORECASE) or \
                                   re.match(common_music_pattern_strict, original_title_str.replace(':', ' - ', 1).replace('/', ' / '), flags=re.IGNORECASE)
    has_music_keyword = any(keyword in title_str for keyword in music_keywords)
    has_non_music_keyword_general = any(keyword in title_str for keyword in non_music_keywords_general)

    if is_common_artist_song_pattern:
        strong_overriding_non_music = ['tutorial', 'review', 'gameplay', 'vlog', 'podcast', 'documentary', 'commentary', 'explained', 'episode', 'unboxing', 'how to', 'aula', 'curso', 'palestra', 'reação', 'react', 'análise', 'dicas']
        very_strong_music_indicators = ['official music video', 'clipe oficial', 'official song', 'album completo', 'full album', 'paródia musical', 'official audio', 'live session', 'acústico']
        if any(strong_nmk in title_str for strong_nmk in strong_overriding_non_music):
            if any(very_strong_mk in title_str for very_strong_mk in very_strong_music_indicators): return True
            return False
        return True

    if has_music_keyword:
        if has_non_music_keyword_general:
            # Se "vs" estiver no título, mas for de ERB, é música.
            if " vs " in title_str and ("epic rap battles of history" in title_str or "erb" in title_str):
                return True
            if any(specific_music_type in title_str for specific_music_type in ["paródia", "musical", "axé music", "capoeira", "ponto de umbanda", "samba de roda", "embolada"]):
                if not any(nmk_override in title_str for nmk_override in ['tutorial', 'review', 'how to make', 'gameplay', 'documentary', 'explained']): return True
            if "tutorial" in title_str and "plugin" in title_str: return False
            if "song" in title_str and any(nm_kw in title_str for nm_kw in ['tutorial', 'review', 'analysis', 'explained', 'how to make', 'ranking', 'behind the scenes']): return False
            if "album" in title_str and any(nm_kw in title_str for nm_kw in ['review', 'analysis', 'unboxing', 'explained']): return False
            if "audio" in title_str and not any(other_music_kw in title_str for other_music_kw in ['song', 'track', 'album', 'remix', 'official audio', 'music']):
                 if any(techy_kw in title_str for techy_kw in ['platform', 'generator', 'text to speech', 'ai news']): return False
            return False
        return True

    short_music_titles_map = {
        "noid": ("Yves Tumor", "Noid"), "not like us": ("Kendrick Lamar", "Not Like Us"), "sorry not sorry": ("Demi Lovato", "Sorry Not Sorry"), 
        "wharf talk": ("Tyler, The Creator", "Wharf Talk"), "heaven to me": ("Tyler, The Creator", "Heaven To Me"), 
        "dogtooth": ("Tyler, The Creator", "Dogtooth"), "corso (audio)": ("Tyler, The Creator", "Corso"),
        "lemonhead (audio)": ("Tyler, The Creator", "Lemonhead"), "wusyaname (audio)": ("Tyler, The Creator", "Wusyaname"),
        "i think": ("Tyler, The Creator", "I Think"), "a boy is a gun*": ("Tyler, The Creator", "A Boy Is A Gun*"),
        "o oitavo anjo": ("509-E", "O Oitavo Anjo"), "remember the time": ("Michael Jackson", "Remember The Time"),
        "that guy": ("Tyler, The Creator", "That Guy"), "squabble up": ("Central Cee", "Squabble Up"),
        "sincronizadamente":("AOM", "Sincronizadamente"), "feel this aom moment":("AOM", "Feel This AOM Moment"), 
        "teriyaki god": ("Pink Guy (Joji)", "Teriyaki God")
    }
    if title_str.strip() in short_music_titles_map or original_title_str.strip() in short_music_titles_map: return True
    if original_title_str == "DNCE - Cake By The Ocean": return True
    if original_title_str == "RITA LEE ERVA VENENOSA": return True
    if original_title_str == "Modjo - Lady (Hear Me Tonight) (Radio Edit) (HQ)": return True
    if any(umbanda_kw in title_str for umbanda_kw in ["canto para mãe iemanjá", "pontos de caboclo cobra coral", "frita no dênde", "ponto de tranca rua", "o sino da igrejinha", "festa do exu tiriri", "oxóssi - o rei das matas", "cabocla jurema"]): return True
    
    # Se o nome do canal indicar que é um canal de música (ex: VEVO, nome de artista)
    # e o título não tiver palavras-chave não musicais fortes, considerar música.
    if channel_name: # channel_name já está em minúsculas
        if "vevo" in channel_name or "official" in channel_name or "music" in channel_name or "records" in channel_name or "band" in channel_name or "dj" in channel_name or "mc" in channel_name:
            if not has_non_music_keyword_general:
                return True
    
    if has_non_music_keyword_general: return False
    return False
    # --- FIM da is_likely_music_video ---

def extract_song_artist_from_title(title_to_process, channel_name_hint=None):
    """
    Extrai o artista, título da música, artistas em destaque e produtores de uma string de título.
    Usa channel_name_hint como uma heurística se a extração do artista falhar.
    """
    # Funções auxiliares aninhadas para manter o escopo local
    def clean_common_tags_local(text_input):
        text = text_input
        if not isinstance(text, str): return text
        tags_to_remove = [
            'official video', 'music video', 'official audio', 'lyric video', 'lyrics',
            'audio', 'visualizer', 'official visualizer', 'hd', '4k remaster', '4k upgrade',
            'hq', 'full album', 'original version', 'official lyric video', 'official music video',
            'official', 'live', 'original mix', 'remastered', 'video clip', 'clipe oficial',
            'pseudo vídeo', 'versão oficial', 'áudio oficial', 'sub español', 'español',
            'subtitulado', 'legendado(?: pt-br)?', 'promo', 'tradução', 'emboladores',
            'dj kr3', 'dj felipe único', 'lyrics in both', 'the ultimate collection',
            'wshh exclusive', 
            'official music video', 
            'official lyric video',
            'official audio',
            'official visualizer',
            'extended mix',
            'live jazz cover' # Adicionado para Guile's Theme
        ]
        for tag in tags_to_remove:
            text = re.sub(r'\s*\[\s*' + re.escape(tag) + r'\s*\]\s*', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*\(\s*' + re.escape(tag) + r'\s*\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\|\s*(?:official video|music video|official audio|lyric video|lyrics|audio|visualizer|clipe oficial|legendado(?: pt-br)?|prod[^\)]*|wshh exclusive.*?)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*#shorts\s*$', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[\s*\]\s*|\s*\(\s*\)\s*', ' ', text)
        text = re.sub(r'\s*\(prod[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[prod[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(animated by[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(from the series[^\)]+\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(from[^\)]+\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[[^\]]*soundtrack[^\]]*\]', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\([^\)]*soundtrack[^\)]*\)', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*//\s*official music video\s*//.*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\((?!.*\b(?:feat|ft|prod|by|vs|remix|version|cover|parody|paródia)\b)[^)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\[(?!.*\b(?:feat|ft|prod|by|vs|remix|version|cover|parody|paródia)\b)[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\blive\b\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(wshh exclusive.*?\)\s*$', '', text, flags=re.IGNORECASE)
        text = text.replace('...', '').strip()
        # Remover "// J-MUSIC Pocket Band" do final
        text = re.sub(r'\s*//\s*J-MUSIC Pocket Band\s*$', '', text, flags=re.IGNORECASE).strip()
        return text.strip()

    def capitalize_name_local(name_input):
        name = name_input
        if not name or not isinstance(name, str): return None
        name = name.strip()
        if not name: return None
        words_to_upper = ["MC", "DJ", "JR", "SR", "DR", "AC", "DC", "EV", "MR", "MS", "MD", "XV", "RE", "ST", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XL", "MGMT", "J.I.D", "JID", "IDK", "ITR", "S.J.", "K.A.A.N", "B.A.R.F", "KRS-One", "6IX9INE"]
        lowercase_words = ["a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "in", "of", "e", "de", "do", "da", "dos", "das", "la", "le", "el", "los", "las", "du", "del", "vs"]
        parts = []
        for i, word_original_case in enumerate(name.split()):
            word = word_original_case.lower()
            if word_original_case == "S.J." : parts.append("S.J."); continue
            if word_original_case.upper() in words_to_upper: parts.append(word_original_case.upper())
            elif re.match(r"^[a-z]\.[a-z]\.(?:[a-z]\.)?[a-z]?$", word): parts.append(word.upper().replace('.', '.').strip('.'))
            elif re.match(r"^\d+[a-z]+[0-9]*$", word) or re.match(r"^[a-z]+\d+[a-z0-9]*$",word): parts.append(word_original_case)
            elif i > 0 and word in lowercase_words and word != "vs": parts.append(word) 
            elif word == "vs" and i > 0: parts.append("Vs")
            else:
                if "'" in word and len(word.split("'")[0]) == 1 and len(word) > 1:
                    sub_parts = word_original_case.split("'"); parts.append(sub_parts[0].lower() + "'" + sub_parts[1].capitalize())
                else: parts.append(word_original_case.capitalize())
        return ' '.join(parts)

    title_str_bkp_local = title_to_process
    title_str_proc = title_to_process.lower().replace('—', '-').replace('–', '-').replace('−', '-')
    artist = None; song_title = None; featured_artists = []; producers = []

    # --- Regras Específicas de Alta Prioridade ---
    if "eminem" in title_str_proc and "without me" in title_str_proc:
        artist = "Eminem"; song_title = "Without Me"
        return capitalize_name_local(artist), capitalize_name_local(song_title), featured_artists, producers
    
    if "armin van buuren vs vini vici" in title_str_proc and "great spirit" in title_str_proc:
        artist = "Armin van Buuren vs Vini Vici"
        song_title = "Great Spirit"
        if "hilight tribe" in title_str_proc: featured_artists.append("Hilight Tribe")
        return capitalize_name_local(artist), capitalize_name_local(song_title), featured_artists, producers

    if "epic rap battles of history" in title_str_proc or "erb" in title_str_proc:
        artist = "Epic Rap Battles of History"
        match_erb = re.match(r"(.+?)\s+vs\.?\s+(.+?)(?:\.|$|\s\(|\[)", title_str_bkp_local, re.IGNORECASE)
        if match_erb: song_title = f"{capitalize_name_local(match_erb.group(1).strip())} vs {capitalize_name_local(match_erb.group(2).strip())}"
        else: song_title = clean_common_tags_local(re.sub(r'\s*\.\s*epic rap battles of history.*$|\s*\(.*erb.*\)\s*$', '', title_str_bkp_local, flags=re.IGNORECASE).strip())
        return artist, capitalize_name_local(song_title), featured_artists, producers

    specific_artists_map_local = { "starbomb": "Starbomb", "the living tombstone": "The Living Tombstone", "egoraptor": "Egoraptor" }
    for key, art_name in specific_artists_map_local.items():
        if key in title_str_proc:
            artist = art_name
            temp_song_title_val = title_str_bkp_local
            if f"({key})" in temp_song_title_val.lower():
                temp_song_title_val = re.sub(r'\s*\(' + re.escape(key) + r'\)\s*', ' ', temp_song_title_val, flags=re.IGNORECASE)
            elif f"{key} -" in temp_song_title_val.lower():
                 temp_song_title_val = re.split(f"{key} -", temp_song_title_val, maxsplit=1, flags=re.IGNORECASE)[-1]
            temp_song_title_val = clean_common_tags_local(temp_song_title_val)
            song_title = temp_song_title_val.strip() 
            # Prioritize splitting by " - " if artist name is not in the first part
            if " - " in temp_song_title_val and art_name.lower() not in temp_song_title_val.split(" - ")[0].lower():
                 song_title = temp_song_title_val.split(" - ",1)[1] # Get the part after "Artist - "
            elif " - " in temp_song_title_val: # If artist name might be in the first part, take the first part
                 song_title = temp_song_title_val.split(" - ",1)[0]

            if key == "starbomb":
                if "by grind3h" in title_str_proc and "pokerap" in title_str_proc: song_title = "The New Pokerap"
                elif "animated by" in title_str_proc:
                     song_title_candidate = title_str_proc.split("animated by")[0].strip("- ")
                     if "starbomb -" in song_title_candidate: song_title = song_title_candidate.split("starbomb -",1)[-1].strip()
                     else: song_title = song_title_candidate
                if "overwatch rap music video" in title_str_proc: song_title = "Overwatch Rap"
                if "vegeta's serenade" in title_str_proc : song_title = "Vegeta's Serenade"
                if "robots in need of disguise" in title_str_proc: song_title = "Robots in Need of Disguise"
            elif key == "the living tombstone" and "no mercy" in title_str_proc and "overwatch" in title_str_proc:
                song_title = "No Mercy (Overwatch Song)"
            elif key == "egoraptor" and "minecraft is for everyone" in title_str_proc:
                song_title = "Minecraft Is For Everyone"
            if not song_title or song_title.lower() == key : song_title = "Unknown"
            return artist, capitalize_name_local(song_title), featured_artists, producers

    if any(k in title_str_proc for k in ["| leod", "leod -", "leod mashup", "leod remix", "leod anos", "mc poze nos anos", "say poze", "marlboro poze", "descobridor dos sete pozes", "doki doki mc poze", "doki doki popotão", "cheiro de kimi no toriko", "rei do kuduro", "sopa de macaco", "cheiro de pneu", "cheiro de say so", "cheiro de tame impala", "cheiro de daft punk", "cheiro de friends", "cheiro de ben 10", "vulgofk -", "bactéria get lucky", "blinding azeitona", "shake it bololô"]):
        artist = "LEOD"
        song_title_val = title_str_bkp_local
        song_title_val = re.sub(r'(\||-) leod.*$', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*pt\.\s*\w+', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*\(.*version\)', '', song_title_val, flags=re.IGNORECASE).strip()
        if "vulgofk -" in song_title_val.lower(): song_title_val = song_title_val.lower().split("vulgofk -",1)[-1].strip()
        if "bactéria get lucky" in song_title_val.lower(): song_title_val = "Bactéria Get Lucky"
        if "blinding azeitona" in song_title_val.lower(): song_title_val = "Blinding Azeitona"
        if "shake it bololô" in song_title_val.lower(): song_title_val = "Shake It Bololô"
        song_title = clean_common_tags_local(song_title_val)
        return artist, capitalize_name_local(song_title), [], []
    
    if "guile's theme" in title_str_proc and "j-music pocket band" in title_str_proc:
        artist = "J-MUSIC Pocket Band"
        song_title = "Guile's Theme (Street Fighter II)"
        if "insaneintherainmusic" in title_str_proc: featured_artists.append("insaneintherainmusic")
        return capitalize_name_local(artist), capitalize_name_local(song_title), featured_artists, producers

    match_artist_quoted_song = re.match(r'^([A-Za-z0-9\$\s_&.,\'-]+?)\s*"([^"]+)"(?:\s*\((.*?)\))?$', title_str_bkp_local)
    if match_artist_quoted_song:
        potential_artist = match_artist_quoted_song.group(1).strip("- ")
        potential_song = match_artist_quoted_song.group(2).strip()
        # Check if potential_artist is a known artist pattern (e.g., 6IX9INE, Cardi B)
        if potential_artist and potential_song and (potential_artist.replace(" ", "").isalnum() or "$" in potential_artist) and len(potential_artist.split()) < 4 :
            artist = potential_artist
            song_title = potential_song
            # Extract feats/prods from the rest of the original string
            remaining_part_for_feat = title_str_bkp_local[match_artist_quoted_song.end():]
            # (A lógica de extração de feat/prod precisaria ser aplicada aqui ao remaining_part_for_feat)
            # Esta parte é simplificada; a extração de feat/prod completa é mais abaixo.
            return capitalize_name_local(artist), capitalize_name_local(song_title), featured_artists, producers

    # --- Lógica Geral de Extração ---
    temp_title_for_feat_extraction = title_str_bkp_local
    feat_prod_pattern = r'(ft\.|feat\.|featuring|with|prod\.|produced by)\s*([\w\s,&\'./$+~-]+?(?=\s*\(|\s*\[|\s*\||$|\s+(?:ft\.|feat\.|featuring|prod\.|\s+prod by|with|vs\.)))'
    all_feat_prod_matches = []
    for match in re.finditer(feat_prod_pattern, temp_title_for_feat_extraction, flags=re.IGNORECASE):
        all_feat_prod_matches.append(match)
    all_feat_prod_matches.sort(key=lambda m: m.start())
    main_title_parts = []
    last_extraction_end = 0
    for match in all_feat_prod_matches:
        main_title_parts.append(temp_title_for_feat_extraction[last_extraction_end:match.start()])
        last_extraction_end = match.end()
        keyword_type = match.group(1).lower()
        items_str = match.group(2).strip()
        current_new_items = [it.strip() for it in re.split(r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+|\s+with\s+', items_str) if it.strip() and it.lower() not in ['x', 'vs']]
        if "prod" in keyword_type: producers.extend(current_new_items)
        else: featured_artists.extend(current_new_items)
    main_title_parts.append(temp_title_for_feat_extraction[last_extraction_end:])
    main_title_candidate = "".join(main_title_parts).strip()
    main_title_candidate_cleaned = clean_common_tags_local(main_title_candidate)

    if not artist: 
        parts = []
        separators_priority = [r"\s+-\s+", r"\s+–\s+", r"\s+—\s+", r"\s+:\s+", r"\s+\|\s+", r"\s+/\s+", r"\s+vs\s+"]
        for sep_regex in separators_priority:
            split_parts = re.split(sep_regex, main_title_candidate_cleaned, 1, flags=re.IGNORECASE)
            if len(split_parts) == 2:
                parts = [split_parts[0].strip(), split_parts[1].strip()]
                if sep_regex == r"\s+vs\s+": # "Artist1 vs Artist2"
                    artist = f"{parts[0]} vs {parts[1]}"
                    song_title = f"{parts[0]} vs {parts[1]}" # Assume a batalha é a música
                    # Se houver algo depois de "A vs B - C", C é a música
                    if " - " in parts[1]:
                        sub_parts = parts[1].split(" - ", 1)
                        artist = f"{parts[0]} vs {sub_parts[0].strip()}"
                        song_title = sub_parts[1].strip()
                    parts = [] # Processado
                break
        if not parts and "-" in main_title_candidate_cleaned and main_title_candidate_cleaned.count('-') == 1 and \
           not re.search(r"\s-\s", main_title_candidate_cleaned):
             parts = [p.strip() for p in main_title_candidate_cleaned.split("-", 1)]

        if len(parts) == 2:
            part1_raw, part2_raw = parts
            part1 = clean_common_tags_local(part1_raw); part2 = clean_common_tags_local(part2_raw)
            len_part1 = len(part1.split()); len_part2 = len(part2.split())
            if " by " in part1.lower() and not " by " in part2.lower(): artist, song_title = part2, part1
            elif " by " in part2.lower() and not " by " in part1.lower(): artist, song_title = part1, part2
            elif ("," in part1 or "&" in part1 or " e " in part1.lower()) and len_part1 > len_part2 and len_part2 < 5: artist, song_title = part1, part2
            elif ("," in part2 or "&" in part2 or " e " in part2.lower()) and len_part2 > len_part1 and len_part1 < 5: artist, song_title = part2, part1
            elif len_part1 <= len_part2 and len_part1 < 5 : artist, song_title = part1, part2
            elif len_part2 < len_part1 and len_part2 < 5 : artist, song_title = part2, part1
            else: artist, song_title = part1, part2
        
        elif main_title_candidate_cleaned and not artist:
            cleaned_lookup_title = clean_common_tags_local(title_to_process.lower())
            short_music_map_local = {
                "noid": ("Yves Tumor", "Noid"), "not like us": ("Kendrick Lamar", "Not Like Us"),
                "sorry not sorry": ("Demi Lovato", "Sorry Not Sorry"), "wharf talk": ("Tyler, The Creator", "Wharf Talk"),
                "heaven to me": ("Tyler, The Creator", "Heaven To Me"), "dogtooth": ("Tyler, The Creator", "Dogtooth"),
                "wusyaname": ("Tyler, The Creator", "Wusyaname"), "lemonhead": ("Tyler, The Creator", "Lemonhead"),
                "corso": ("Tyler, The Creator", "Corso"), "i think": ("Tyler, The Creator", "I Think"),
                "a boy is a gun*": ("Tyler, The Creator", "A Boy Is A Gun*"), "o oitavo anjo": ("509-E", "O Oitavo Anjo"),
                "remember the time": ("Michael Jackson", "Remember The Time"), "velocidade da luz": ("Revelação", "Velocidade da Luz"),
                "onda onda (olha a onda)": ("Tchakabum", "Onda Onda (Olha a Onda)"), "mr bombastic": ("Shaggy", "Boombastic"),
                "indian moonlight": ("S. J. Jananiy", "Indian Moonlight"), "teriyaki god": ("Pink Guy (Joji)", "Teriyaki God"),
                "o sino da igrejinha": ("Unknown", "O Sino da Igrejinha"), "st chroma x rah tah tah": ("ST CHROMA", "Rah Tah Tah"),
                "canto para mãe iemanjá e mãe oxum": ("Unknown", "Canto Para Mãe Iemanjá e Mãe Oxum"),
                "death to the world": ("Unknown", "Death To The World"), "dedo no cu e gritaria": ("Unknown", "Dedo no Cu e Gritaria"),
                "ly o lay ale loya (circle dance) ~ native song": ("Native Song Circle", "Ly O Lay Ale Loya (Circle Dance)"),
                "mademoiselle noir": ("Unknown", "Mademoiselle Noir"),
                "rock around the clock-bill haley-original song-1955": ("Bill Haley & His Comets", "Rock Around the Clock"),
                "tetris rap animated": ("Starbomb", "Tetris Rap")
            }
            if cleaned_lookup_title in short_music_map_local:
                artist, song_title = short_music_map_local[cleaned_lookup_title]
            elif "narrando o clipe" in main_title_candidate_cleaned.lower():
                if "one direction" in main_title_candidate_cleaned.lower() and "what makes you beautiful" in main_title_candidate_cleaned.lower():
                    artist = "One Direction"; song_title = "What Makes You Beautiful (Narrando o Clipe)"
                else:
                    artist = "Narrando o Clipe"; song_title = re.sub(r'narrando o clipe\s*', '', main_title_candidate_cleaned, flags=re.IGNORECASE).strip("- ")
            elif not artist: song_title = main_title_candidate_cleaned 
    
    artist_final = capitalize_name_local(artist) if artist else "Unknown"
    if song_title is None and main_title_candidate_cleaned:
        song_title_final = capitalize_name_local(main_title_candidate_cleaned)
    else:
        song_title_final = capitalize_name_local(song_title) if song_title else "Unknown"

    if artist_final == "Unknown" and channel_name_hint:
        potential_artist_from_channel = capitalize_name_local(channel_name_hint)
        potential_artist_from_channel = re.sub(r'\s*-\s*Topic$|\s*VEVO$|\s*Official$|\s*Music$', '', potential_artist_from_channel, flags=re.IGNORECASE).strip()
        if potential_artist_from_channel and len(potential_artist_from_channel.split()) < 5 and \
           potential_artist_from_channel.lower() not in ["various artists", "official", "music", "topic", "channel", "records", "canal", "gravadora", "soundtrack", "ost", "theme", "temas", "trilha sonora", "wshh exclusive", "worldstarhiphop"]:
            if song_title_final == "Unknown" or song_title_final.lower() == clean_common_tags_local(title_to_process.lower()).lower():
                new_song_title = clean_common_tags_local(title_to_process)
                if potential_artist_from_channel.lower() in new_song_title.lower():
                    new_song_title = re.sub(re.escape(potential_artist_from_channel), '', new_song_title, flags=re.IGNORECASE).strip(" -:")
                if new_song_title and len(new_song_title.split()) < 10 :
                    artist_final = potential_artist_from_channel
                    song_title_final = capitalize_name_local(new_song_title)
            elif song_title_final != "Unknown" and song_title_final.lower() != potential_artist_from_channel.lower():
                 artist_final = potential_artist_from_channel

    featured_artists_final = sorted(list(set(filter(None, [capitalize_name_local(fa) for fa in featured_artists if fa]))))
    producers_final = sorted(list(set(filter(None, [capitalize_name_local(p) for p in producers if p]))))

    if artist_final and artist_final != "Unknown":
        main_artist_names_list_local = [a.strip().lower() for a in re.split(r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+', artist_final)]
        featured_artists_final = [fa for fa in featured_artists_final if not (capitalize_name_local(fa) and capitalize_name_local(fa).lower() in main_artist_names_list_local)]
        producers_final = [p for p in producers_final if not (capitalize_name_local(p) and capitalize_name_local(p).lower() in main_artist_names_list_local)]

    if not song_title_final or song_title_final.lower() == "unknown" or song_title_final == "": song_title_final = "Unknown"
    if not artist_final or artist_final.lower() == "unknown" or artist_final == "":
        artist_final = "Unknown"
        if song_title_final == "Unknown" and title_to_process:
            song_title_final = capitalize_name_local(clean_common_tags_local(title_to_process))
    
    if " vs " in artist_final and song_title_final == "Unknown":
        cleaned_original = clean_common_tags_local(title_to_process)
        potential_song_from_vs = re.sub(re.escape(artist_final), '', cleaned_original, flags=re.IGNORECASE).strip(" :-")
        if potential_song_from_vs:
            song_title_final = capitalize_name_local(potential_song_from_vs)

    if artist_final == song_title_final and artist_final != "Unknown": artist_final = "Unknown"
    return artist_final, song_title_final, featured_artists_final, producers_final
    # --- FIM do Corpo de extract_song_artist_from_title ---

def enrich_track_details_with_search(track_info, concise_search_tool):
    artist = track_info.get("artist")
    song_title = track_info.get("song_title")
    if not artist or artist == "Unknown" or not song_title or song_title == "Unknown":
        return False
    return True

def concise_search(query: str, max_num_results: int = 3):
  pass

# --- Função de Processamento Principal Adaptada ---
def process_new_data_format(video_data_list, original_to_curated_map, concise_search_tool_func):
    start_time_proc = time.time()
    processed_music_list = []
    skipped_titles_list_proc = []
    
    total_vids_processed = 0; music_vids_identified = 0; vids_skipped_not_music = 0
    music_extract_successful = 0; music_extract_failed_artist = 0; music_extract_failed_song = 0
    music_extract_fully_failed = 0; passed_to_srch = 0; errors_proc = 0

    for entry_data in video_data_list:
        total_vids_processed += 1
        
        original_yt_title = entry_data.get("original_youtube_title", "")
        channel = entry_data.get("channel_name", "Unknown")
        url = entry_data.get("youtube_url", f"https://www.youtube.com/watch?v=placeholder_for_line_{total_vids_processed}")
        upload_dt = entry_data.get("upload_date")
        video_genre = entry_data.get("genre", "Unknown")

        if not original_yt_title:
            vids_skipped_not_music +=1
            skipped_titles_list_proc.append(f"[EMPTY ORIGINAL TITLE for entry in genre {video_genre}]")
            continue

        normalized_original_yt_title = normalize_string_for_match(original_yt_title)
        title_for_extraction = original_to_curated_map.get(normalized_original_yt_title, original_yt_title)
        
        video_info_for_check = {
            "title": original_yt_title,
            "original_title": original_yt_title,
            "channel_name": channel 
        }

        try:
            if is_likely_music_video(video_info_for_check):
                music_vids_identified += 1
                artist_ext, song_ext, ft_ext, prod_ext = extract_song_artist_from_title(title_for_extraction, channel)
                music_item = {
                    "original_youtube_title": original_yt_title,
                    "processed_title_for_extraction": title_for_extraction,
                    "artist": artist_ext if artist_ext else "Unknown",
                    "song_title": song_ext if song_ext else "Unknown",
                    "featured_artists": ft_ext,
                    "producers": prod_ext,
                    "genre": [video_genre] if video_genre and video_genre != "Unknown" else [],
                    "channel_name": channel, "youtube_url": url, "upload_date": upload_dt,
                    "album": None, "release_year": None, "spotify_url": None, 
                    "language": None, "country_of_origin": None, "other_info": {}
                }
                is_art_unknown = (music_item["artist"] == "Unknown")
                is_song_unknown = (music_item["song_title"] == "Unknown" or not music_item["song_title"])
                if not is_art_unknown and not is_song_unknown: music_extract_successful += 1
                else:
                    if is_art_unknown and is_song_unknown: music_extract_fully_failed +=1
                    if is_art_unknown: music_extract_failed_artist += 1
                    if is_song_unknown: music_extract_failed_song +=1
                if enrich_track_details_with_search(music_item, concise_search_tool_func): passed_to_srch +=1
                processed_music_list.append(music_item)
            else:
                vids_skipped_not_music += 1
                skipped_titles_list_proc.append(f"{original_yt_title} (Genre: {video_genre}, Channel: {channel})")
        except Exception as e_proc:
            errors_proc += 1
            skipped_titles_list_proc.append(f"[ERROR SKIPPING] {original_yt_title} (Error: {e_proc})")

    end_time_proc = time.time(); processing_duration_proc = end_time_proc - start_time_proc
    report_lines = [
        "--- SCRIPT EXECUTION REPORT (New Workflow v3) ---",
        f"Processing Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_proc))}",
        f"Processing End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time_proc))}",
        f"Total Processing Duration: {processing_duration_proc:.2f} seconds",
        "\n--- Video Processing Summary ---",
        f"Total video entries read from genre files: {total_vids_processed}",
        f"Videos identified as music: {music_vids_identified}",
        f"Videos skipped (classified as non-music, empty, or error): {vids_skipped_not_music}",
        "\n--- Music Information Extraction (for identified music videos) ---",
        f"Successfully extracted Artist AND Song title: {music_extract_successful}",
        f"Artist could not be determined (marked 'Unknown'): {music_extract_failed_artist}",
        f"Song title could not be determined (marked 'Unknown'): {music_extract_failed_song}",
        f"Both Artist AND Song title were 'Unknown' (extraction fully failed): {music_extract_fully_failed}",
        "Note: 'Artist/Song could not be determined' counts may overlap.",
        "\n--- Data Enrichment (Mock Search) ---",
        f"Music entries passed to MOCK search function: {passed_to_srch}",
        "IMPORTANT: The search function ('enrich_track_details_with_search') is currently a MOCK.",
        "\n--- Errors ---", f"Errors encountered during processing of individual entries: {errors_proc}",
        "\n--- Output ---", "Structured music data saved to: [output_folder_path]/music_data.json",
        "List of videos with 'Unknown' artist OR 'Unknown' song saved to: [output_folder_path]/unknown_extraction_videos.txt",
        "List of skipped videos saved to: [output_folder_path]/skipped_videos.txt",
        "This report saved to: [output_folder_path]/processing_report.txt",
        "\n--- Recommendations ---"
    ]
    if music_extract_failed_artist > 0 or music_extract_failed_song > 0 :
        report_lines.append("- Review titles where artist/song extraction failed (see 'unknown_extraction_videos.txt'). The 'extract_song_artist_from_title' function (especially channel name hint logic) might need refinement.")
    if vids_skipped_not_music > 0 :
         report_lines.append("- Review 'skipped_videos.txt'. If actual music videos were skipped, the 'is_likely_music_video' heuristics and keywords need adjustment.")
    report_lines.append("- For actual data enrichment, replace the mock 'concise_search' function with a real search implementation (e.g., Spotify API, MusicBrainz API).")
    return processed_music_list, "\n".join(report_lines), skipped_titles_list_proc

if __name__ == "__main__":
    all_videos_data_main = []
    original_titles_path = os.path.join(FONTES_DE_DADOS_DIR, "arquivos_originais_brutos", ORIGINAL_TITLES_RAW_FILENAME)
    corrected_titles_path = os.path.join(CURATED_TITLES_DIR, CORRECTED_TITLES_FOR_MAPPING_FILENAME)
    original_to_curated_map_main = load_original_to_curated_map(original_titles_path, corrected_titles_path)
    print(f"Loaded {len(original_to_curated_map_main)} mappings from original to curated titles.")

    if not os.path.exists(GENRE_FILES_DIR):
        print(f"ERRO: Diretório de arquivos de gênero não encontrado: {GENRE_FILES_DIR}")
        exit()

    for genre_filename in os.listdir(GENRE_FILES_DIR):
        if genre_filename.endswith(".txt"):
            genre_name = os.path.splitext(genre_filename)[0]
            genre_filepath = os.path.join(GENRE_FILES_DIR, genre_filename)
            print(f"Processing genre file: {genre_filepath} for genre: {genre_name}")
            try:
                with open(genre_filepath, 'r', encoding='utf-8') as f_genre:
                    genre_file_content = f_genre.read()
                parsed_videos_from_genre = parse_genre_file_content(genre_file_content, genre_name)
                for video_details in parsed_videos_from_genre:
                    all_videos_data_main.append(video_details)
                print(f"Found {len(parsed_videos_from_genre)} entries in {genre_filename}")
            except Exception as e_file:
                print(f"Error processing file {genre_filepath}: {e_file}")
    
    print(f"\nTotal de {len(all_videos_data_main)} vídeos coletados de todos os arquivos de gênero.")

    now_time = datetime.now()
    output_folder_name_main = now_time.strftime("%Y-%m-%d_%H-%M-%S") + "_run_v9_full_pipeline"
    output_root_dir_main = os.path.join(BASE_DIR, "output_script_principal")
    if not os.path.exists(output_root_dir_main):
        os.makedirs(output_root_dir_main)
    output_directory_path_main = os.path.join(output_root_dir_main, output_folder_name_main)

    if not os.path.exists(output_directory_path_main):
        os.makedirs(output_directory_path_main)
        print(f"Created output directory: {output_directory_path_main}")

    output_json_filename_main = os.path.join(output_directory_path_main, "music_data.json")
    unknown_extraction_filename_main = os.path.join(output_directory_path_main, "unknown_extraction_videos.txt")
    skipped_videos_filename_main = os.path.join(output_directory_path_main, "skipped_videos.txt")
    report_filename_main = os.path.join(output_directory_path_main, "processing_report.txt")

    music_data_final, report_string_final, skipped_titles_list_final = process_new_data_format(all_videos_data_main, original_to_curated_map_main, concise_search)
    report_string_final = report_string_final.replace("[output_folder_path]", output_directory_path_main)

    print("\n" + "="*50 + "\n"); print(report_string_final); print("\n" + "="*50 + "\n")
    
    unknown_extraction_output_titles = []
    for entry_item in music_data_final:
        if entry_item.get("artist") == "Unknown" or entry_item.get("song_title") == "Unknown":
            genre_list = entry_item.get('genre', [])
            genre_str = genre_list[0] if genre_list else "N/A"
            unknown_extraction_output_titles.append(f"Original: {entry_item.get('original_youtube_title')} | Processed: {entry_item.get('processed_title_for_extraction')} | Artist: {entry_item.get('artist')} | Song: {entry_item.get('song_title')} (Genre: {genre_str}, Channel: {entry_item.get('channel_name')})")

    if unknown_extraction_output_titles:
        try:
            with open(unknown_extraction_filename_main, 'w', encoding='utf-8') as f_unknown_out:
                for title_out in unknown_extraction_output_titles: f_unknown_out.write(title_out + "\n")
            print(f"Lista de vídeos com extração 'Unknown' salva em: {unknown_extraction_filename_main}")
        except Exception as e_save: print(f"ERROR saving unknown extraction list: {e_save}")

    if skipped_titles_list_final:
        try:
            with open(skipped_videos_filename_main, 'w', encoding='utf-8') as f_skipped_out:
                for title_out in skipped_titles_list_final: f_skipped_out.write(title_out + "\n")
            print(f"Lista de vídeos pulados salva em: {skipped_videos_filename_main}")
        except Exception as e_save: print(f"ERROR saving skipped videos list: {e_save}")

    try:
        with open(output_json_filename_main, 'w', encoding='utf-8') as f_json_out: json.dump(music_data_final, f_json_out, indent=2, ensure_ascii=False)
        print(f"\nData successfully saved to {output_json_filename_main}")
    except Exception as e_save: print(f"ERROR saving data to json: {e_save}")

    try:
        with open(report_filename_main, 'w', encoding='utf-8') as f_report_out: f_report_out.write(report_string_final)
        print(f"Report saved to {report_filename_main}")
    except Exception as e_save: print(f"ERROR saving report: {e_save}")

