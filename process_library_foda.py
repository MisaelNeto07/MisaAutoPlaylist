# --- START OF FILE process_library_foda.py ---

import re
import json
import time
import os
from datetime import datetime
import unicodedata # Para normalização de strings

# --- Constantes de Caminho (ajuste conforme necessário se o script não estiver na Raiz_do_Projeto) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTES_DE_DADOS_DIR = os.path.join(BASE_DIR, "fontes_de_dados")
GENRE_FILES_DIR = os.path.join(FONTES_DE_DADOS_DIR, "generos")
CURATED_TITLES_DIR = os.path.join(FONTES_DE_DADOS_DIR, "titulos_curados")
CURATED_TITLES_FILENAME = "My YouTube Library.txt" # Nome do seu arquivo com títulos curados

def normalize_string_for_match(s):
    """Normaliza uma string para uma correspondência mais robusta."""
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize('NFC', s) # Normaliza caracteres Unicode (ex: acentos)
    s = s.lower() # Converter para minúsculas para correspondência insensível a caixa
    s = re.sub(r'\s+', ' ', s)          # Substitui múltiplos espaços por um único espaço
    return s.strip()                   # Remove espaços no início/fim

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
        
        if "original_youtube_title" in video_data: # Apenas adiciona se o título foi encontrado
            videos.append(video_data)
    return videos

def load_curated_titles(curated_titles_path):
    """Carrega os títulos curados e os normaliza para lookup."""
    curated_map = {}
    try:
        with open(curated_titles_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line:
                    curated_map[normalize_string_for_match(stripped_line)] = stripped_line
    except FileNotFoundError:
        print(f"Arquivo de títulos curados não encontrado em: {curated_titles_path}")
    return curated_map

def is_likely_music_video(title_info):
    title_str = title_info.get('title', "").lower()
    original_title_str = title_info.get('title', "")

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
        'full version', 'full song', 'pancadão', 'axé music'
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
        'tier list', 'ranking', 'vs',
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

    if original_title_str == "Michael Jackson - History": return True
    if "pink guy" in title_str and "teriyaki god" in title_str: return True
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str: return True
    if "mc twist e mc brinquedo" in title_str and "ela caiu caillou" in title_str: return True
    if "mc pikachu" in title_str and "tava no fluxo" in title_str: return True
    if "mc" in title_str and any(prod_kw in title_str for prod_kw in ['prod.', 'produced by']): return True
    if "paródia musical" in title_str: return True
    if "axé music" in title_str and "kame kame kame ha" in title_str and "dragon ball" in title_str: return True

    if "narrando o clipe" in title_str:
        if " - " in title_str or "#" in original_title_str or \
           any(mkw in title_str for mkw in ['song', 'music', 'clipe', 'parody', 'paródia', 'remix', 'cover', 'ft.', 'feat.']):
            return True
        if "one direction" in title_str and "what makes you beautiful" in title_str: return True
        return True

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
            if any(specific_music_type in title_str for specific_music_type in ["paródia", "musical", "axé music"]):
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
    if has_non_music_keyword_general: return False
    return False

def extract_song_artist_from_title(title_to_process, channel_name_hint=None):
    title_str_bkp = title_to_process 
    title_str = title_to_process.lower()
    title_str = title_str.replace('—', '-').replace('–', '-').replace('−', '-')

    artist = None
    song_title = None
    featured_artists = []
    producers = []

    def clean_common_tags(text):
        if not isinstance(text, str): return text
        tags_to_remove = [
            'official video', 'music video', 'official audio', 'lyric video', 'lyrics',
            'audio', 'visualizer', 'official visualizer', 'hd', '4k remaster', '4k upgrade',
            'hq', 'full album', 'original version', 'official lyric video', 'official music video',
            'official', 'live', 'original mix', 'remastered', 'video clip', 'clipe oficial',
            'pseudo vídeo', 'versão oficial', 'áudio oficial', 'sub español', 'español',
            'subtitulado', 'legendado(?: pt-br)?', 'promo', 'tradução', 'emboladores',
            'dj kr3', 'dj felipe único', 'lyrics in both', 'the ultimate collection'
        ]
        for tag in tags_to_remove:
            text = re.sub(r'\s*\[\s*' + re.escape(tag) + r'\s*\]\s*', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*\(\s*' + re.escape(tag) + r'\s*\)\s*', ' ', text, flags=re.IGNORECASE)

        text = re.sub(r'\s*\|\s*(official video|music video|official audio|lyric video|lyrics|audio|visualizer|clipe oficial|legendado(?: pt-br)?|prod[^\)]*)\s*', ' ', text, flags=re.IGNORECASE)
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
        text = re.sub(r'\s+\((?!.*\b(?:feat|ft|prod)\b)[^)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\[(?!.*\b(?:feat|ft|prod)\b)[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\blive\b\s*$', '', text, flags=re.IGNORECASE)
        return text.strip()

    def capitalize_name(name):
        if not name or not isinstance(name, str): return None
        name = name.strip()
        if not name: return None

        words_to_upper = ["MC", "DJ", "JR", "SR", "DR", "AC", "DC", "EV", "MR", "MS", "MD", "XV", "RE", "ST", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XL", "MGMT", "J.I.D", "JID", "IDK", "ITR", "S.J."]
        lowercase_words = ["a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "in", "of", "e", "de", "do", "da", "dos", "das", "la", "le", "el", "los", "las", "du", "del"]

        parts = []
        for i, word_original_case in enumerate(name.split()):
            word = word_original_case.lower()
            if word_original_case == "S.J." :
                parts.append("S.J.")
                continue
            if word_original_case.upper() in words_to_upper:
                parts.append(word_original_case.upper())
            elif re.match(r"^[a-z]\.[a-z]\.(?:[a-z]\.)?[a-z]?$", word):
                 parts.append(word.upper().replace('.', '.').strip('.'))
            elif re.match(r"^\d+[a-z]+[0-9]*$", word) or re.match(r"^[a-z]+\d+[a-z0-9]*$",word):
                parts.append(word_original_case)
            elif i > 0 and word in lowercase_words:
                parts.append(word)
            else:
                if "'" in word and len(word.split("'")[0]) == 1 and len(word) > 1:
                    sub_parts = word_original_case.split("'")
                    parts.append(sub_parts[0].lower() + "'" + sub_parts[1].capitalize())
                else:
                    parts.append(word_original_case.capitalize())
        return ' '.join(parts)

    if "eminem" in title_str and "without me" in title_str and "official music video" in title_str:
        artist = "Eminem"
        song_title = "Without Me"
        return artist, song_title, featured_artists, producers

    if "epic rap battles of history" in title_str or "erb" in title_str:
        artist = "Epic Rap Battles of History"
        match_erb = re.match(r"(.+?)\s+vs\.?\s+(.+?)(?:\.|$)", title_to_process, re.IGNORECASE)
        if match_erb: song_title = f"{capitalize_name(match_erb.group(1).strip())} vs {capitalize_name(match_erb.group(2).strip())}"
        else: song_title = re.sub(r'\s*\.\s*epic rap battles of history.*$', '', title_to_process, flags=re.IGNORECASE).strip()
        return artist, song_title, [], []

    specific_artists_map = { "starbomb": "Starbomb", "the living tombstone": "The Living Tombstone", "egoraptor": "Egoraptor" }
    for key, art_name in specific_artists_map.items():
        if key in title_str:
            artist = art_name
            temp_song_title_val = title_to_process
            if f"({key})" in temp_song_title_val.lower():
                temp_song_title_val = re.sub(r'\s*\(' + re.escape(key) + r'\)\s*', ' ', temp_song_title_val, flags=re.IGNORECASE)
            elif f"{key} -" in temp_song_title_val.lower():
                 temp_song_title_val = temp_song_title_val.lower().split(f"{key} -",1)[-1]
            temp_song_title_val = clean_common_tags(temp_song_title_val)
            if " - " in temp_song_title_val: temp_song_title_val = temp_song_title_val.split(" - ",1)[0]
            song_title = temp_song_title_val.strip()
            if key == "starbomb":
                if "by grind3h" in title_str and "pokerap" in title_str: song_title = "The New Pokerap"
                elif "animated by" in title_str:
                     song_title = title_str.split("animated by")[0].strip("- ")
                     if "starbomb" in song_title.lower(): song_title = song_title.lower().split("starbomb -",1)[-1].strip()
                if "overwatch rap music video" in title_str: song_title = "Overwatch Rap"
                if "vegeta's serenade" in title_str : song_title = "Vegeta's Serenade"
                if "robots in need of disguise" in title_str: song_title = "Robots in Need of Disguise"
            elif key == "the living tombstone" and "no mercy" in title_str and "overwatch" in title_str:
                song_title = "No Mercy (Overwatch Song)"
            elif key == "egoraptor" and "minecraft is for everyone" in title_str:
                song_title = "Minecraft Is For Everyone"
            if not song_title or song_title == key : song_title = "Unknown"
            return artist, song_title, featured_artists, producers

    if any(k in title_str for k in ["| leod", "leod -", "leod mashup", "leod remix", "leod anos", "mc poze nos anos", "say poze", "marlboro poze", "descobridor dos sete pozes", "doki doki mc poze", "doki doki popotão", "cheiro de kimi no toriko", "rei do kuduro", "sopa de macaco", "cheiro de pneu", "cheiro de say so", "cheiro de tame impala", "cheiro de daft punk", "cheiro de friends", "cheiro de ben 10", "vulgofk -", "bactéria get lucky", "blinding azeitona", "shake it bololô"]):
        artist = "LEOD"
        song_title_val = title_to_process
        song_title_val = re.sub(r'(\||-) leod.*$', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*pt\.\s*\w+', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*\(.*version\)', '', song_title_val, flags=re.IGNORECASE).strip()
        if "vulgofk -" in song_title_val.lower(): song_title_val = song_title_val.lower().split("vulgofk -",1)[-1].strip()
        if "bactéria get lucky" in song_title_val.lower(): song_title_val = "Bactéria Get Lucky"
        if "blinding azeitona" in song_title_val.lower(): song_title_val = "Blinding Azeitona"
        if "shake it bololô" in song_title_val.lower(): song_title_val = "Shake It Bololô"
        song_title = clean_common_tags(song_title_val)
        return artist, song_title, [], []

    if "pink guy (joji)" in title_str and "teriyaki god" in title_str:
        artist = "Pink Guy (Joji)"; song_title = "Teriyaki God"; return artist, song_title, [], []
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str:
        artist = "MC Neguinho ITR e MC Digu"; song_title = "Forte pra Dar Sorte"
        if "(dj kr3)" in title_str: featured_artists.append("DJ KR3")
        return artist, song_title, featured_artists, producers
    if "mc pikachu" in title_str and "tava no fluxo" in title_str:
        artist = "MC Pikachu"; song_title = "Tava no Fluxo"
        if "(dj felipe único)" in title_str: featured_artists.append("DJ Felipe Único")
        return artist, song_title, featured_artists, producers
    if "mc twist e mc brinquedo" in title_str and "ela caiu caillou" in title_str:
        artist = "MC Twist e MC Brinquedo"; song_title = "Ela Caiu Caillou"; return artist, song_title, featured_artists, producers
    if "terezinha e roque josé" in title_str and "emboladores" in title_str and "dona terezinha e roque" in title_str:
        artist = "Terezinha e Roque José (Emboladores)"; song_title = "Dona Terezinha e Roque"; return artist, song_title, [], []

    if "michael jackson" in title_str and "the ultimate collection" in title_str:
        artist = "Michael Jackson"
        cleaned_for_mj = clean_common_tags(title_to_process.replace("[HD]", ""))
        song_cand_match1 = re.match(r"^\s*(?:\d+\s+)?(.+?)\s*-\s*michael jackson\s*-\s*the ultimate collection", cleaned_for_mj, re.IGNORECASE)
        if song_cand_match1: song_title = song_cand_match1.group(1).strip()
        else:
            song_cand_match2 = re.match(r"michael jackson\s*-\s*(.+?)\s*-\s*the ultimate collection", cleaned_for_mj, re.IGNORECASE)
            if song_cand_match2: song_title = song_cand_match2.group(1).strip()
        if song_title: return capitalize_name(artist), capitalize_name(clean_common_tags(song_title)), featured_artists, producers

    temp_title_str_main_extraction = title_to_process
    non_feat_prod_parts = []
    last_match_end = 0
    all_matches = []
    ft_pattern = r'(ft\.|feat\.|featuring|with)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$|\s+prod\.|\s+prod by|\s+x\s+[\w\s]|\s+vs\.))'
    prod_pattern = r'(prod\.|produced by)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$))'

    for match in re.finditer(ft_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match, 'type': 'feat'})
    for match in re.finditer(prod_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match, 'type': 'prod'})
    all_matches.sort(key=lambda m: m['match'].start())

    for item in all_matches:
        match_obj_iter = item['match'] # Renamed to avoid conflict with 'match' from outer scope if any
        match_type = item['type']
        non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:match_obj_iter.start()])
        last_match_end = match_obj_iter.end()
        items_str = match_obj_iter.group(2).strip()
        split_regex = r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+'
        if match_type == 'feat': split_regex += r'|\s+with\s+'
        new_items = [it.strip() for it in re.split(split_regex, items_str) if it.strip() and it.lower() not in ['x', 'vs']]
        if match_type == 'feat': featured_artists.extend(new_items)
        else: producers.extend(new_items)
    non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:])
    main_title_candidate = "".join(non_feat_prod_parts).strip()
    main_title_candidate_cleaned = clean_common_tags(main_title_candidate)

    if artist and song_title: pass 
    elif main_title_candidate_cleaned:
        parts = []
        separators_to_try = [r"\s+-\s+", r"\s+:\s+", r"\s+\|\s+", r"\s+/\s+", r"\s+X\s+"] 
        for sep_regex in separators_to_try:
            match_sep = re.match(r"(.+?)" + sep_regex + r"(.+)", main_title_candidate_cleaned, re.IGNORECASE) # Renamed match_obj
            if match_sep:
                parts = [match_sep.group(1).strip(), match_sep.group(2).strip()]
                break
        if not parts and "-" in main_title_candidate_cleaned and main_title_candidate_cleaned.count('-') == 1 and \
           re.match(r"^[^- \t\n\r\f\v]+-[^- \t\n\r\f\v]+$", main_title_candidate_cleaned):
             parts = [p.strip() for p in main_title_candidate_cleaned.split("-", 1)]

        if len(parts) == 2:
            part1, part2 = parts
            part1 = clean_common_tags(part1); part2 = clean_common_tags(part2)
            artist_keywords_list = ["band", "project", "dj", "mc", "squad", "trio", "duo", "ensemble", "orquestra", "choir", "group", "clan", "mob", "clvb", "vs"]
            song_keywords_strict_list = ["song", "track", "theme", "anthem", "concerto", "symphony", "ballad", "serenade", "interlude", "prelude", "overture", "rhapsody", "suite", "remix", "live", "version", "cover", "acoustic", "medley", "session", "parody", "paródia", "opening", "ending", "soundtrack", "ost", "mix", "legendado", "lyrics", "tradução"]
            part1_has_artist_ind = any(akw in part1.lower() for akw in [",", "&", " e ", " x ", " ft.", " feat.", " with"])
            part2_has_artist_ind = any(akw in part2.lower() for akw in [",", "&", " e ", " x ", " ft.", " feat.", " with"])

            if part1_has_artist_ind and not part2_has_artist_ind and len(part2.split()) < 6 : artist, song_title = part1, part2
            elif not part1_has_artist_ind and part2_has_artist_ind and len(part1.split()) < 6: artist, song_title = part2, part1
            else:
                p1_is_art_kw = any(akw in part1.split() for akw in artist_keywords_list)
                p2_is_art_kw = any(akw in part2.split() for akw in artist_keywords_list)
                p1_is_song_kw = any(skw in part1.lower() for skw in song_keywords_strict_list)
                p2_is_song_kw = any(skw in part2.lower() for skw in song_keywords_strict_list)
                if "yun li" in part1.lower(): artist, song_title = part1, part2
                elif "yun li" in part2.lower(): artist, song_title = part2, part1
                elif p1_is_art_kw and not p2_is_art_kw: artist, song_title = part1, part2
                elif p2_is_art_kw and not p1_is_art_kw: artist, song_title = part2, part1
                elif p2_is_song_kw and not p1_is_song_kw: artist, song_title = part1, part2
                elif p1_is_song_kw and not p2_is_song_kw: artist, song_title = part2, part1
                elif len(part1.split()) <= len(part2.split()) and len(part1.split()) <= 5 and not p1_is_song_kw : artist, song_title = part1, part2
                elif len(part2.split()) < len(part1.split()) and len(part2.split()) <= 5 and not p2_is_song_kw : artist, song_title = part2, part1
                else: artist, song_title = part1, part2
        elif not artist: 
            cleaned_lookup_title = clean_common_tags(main_title_candidate.lower())
            short_music_map = {
                "noid": ("Yves Tumor", "Noid"), "not like us": ("Kendrick Lamar", "Not Like Us"),
                "sorry not sorry": ("Demi Lovato", "Sorry Not Sorry"), "wharf talk": ("Tyler, The Creator", "Wharf Talk"),
                "heaven to me": ("Tyler, The Creator", "Heaven To Me"), "dogtooth": ("Tyler, The Creator", "Dogtooth"),
                "wusyaname": ("Tyler, The Creator", "Wusyaname"), "lemonhead": ("Tyler, The Creator", "Lemonhead"),
                "corso": ("Tyler, The Creator", "Corso"), "i think": ("Tyler, The Creator", "I Think"),
                "a boy is a gun*": ("Tyler, The Creator", "A Boy Is A Gun*"), "o oitavo anjo": ("509-E", "O Oitavo Anjo"),
                "remember the time": ("Michael Jackson", "Remember The Time"), "velocidade da luz": ("Revelação", "Velocidade da Luz"),
                "onda onda (olha a onda)": ("Tchakabum", "Onda Onda (Olha a Onda)"), "mr bombastic": ("Shaggy", "Boombastic"),
                "indian moonlight": ("S. J. Jananiy", "Indian Moonlight"), "bonfire/cursed images meme": ("Shikoku Meeting", "Bonfire"),
                "teriyaki god": ("Pink Guy (Joji)", "Teriyaki God"), "o sino da igrejinha": ("Unknown", "O Sino da Igrejinha"),
                "st chroma x rah tah tah": ("ST CHROMA", "Rah Tah Tah"), "canto para mãe iemanjá e mãe oxum": ("Unknown", "Canto Para Mãe Iemanjá e Mãe Oxum"),
                "death to the world": ("Unknown", "Death To The World"), "dedo no cu e gritaria": ("Unknown", "Dedo no Cu e Gritaria"),
                "ly o lay ale loya (circle dance) ~ native song": ("Native Song Circle", "Ly O Lay Ale Loya (Circle Dance)"),
                "mademoiselle noir": ("Unknown", "Mademoiselle Noir"),
                "rock around the clock-bill haley-original song-1955": ("Bill Haley & His Comets", "Rock Around the Clock"),
                "tetris rap animated": ("Starbomb", "Tetris Rap")
            }
            if cleaned_lookup_title in short_music_map: artist, song_title = short_music_map[cleaned_lookup_title]
            elif "narrando o clipe" in main_title_candidate.lower():
                if "one direction" in main_title_candidate.lower() and "what makes you beautiful" in main_title_candidate.lower():
                    artist = "One Direction"; song_title = "What Makes You Beautiful (Narrando o Clipe)"
                else:
                    artist = "Narrando o Clipe"; song_title = re.sub(r'narrando o clipe\s*', '', main_title_candidate, flags=re.IGNORECASE).strip("- ")
            elif not artist: song_title = main_title_candidate_cleaned; artist = "Unknown"
    elif not artist and not song_title: 
        song_title = clean_common_tags(title_to_process); artist = "Unknown"

    artist_final = capitalize_name(artist) if artist else "Unknown"
    song_title_final = capitalize_name(song_title) if song_title else "Unknown"

    if artist_final == "Unknown" and channel_name_hint:
        potential_artist_from_channel = capitalize_name(channel_name_hint) 
        if potential_artist_from_channel:
            _papc = potential_artist_from_channel 
            _papc = re.sub(r'\s*-\s*Topic$', '', _papc, flags=re.IGNORECASE).strip()
            _papc = re.sub(r'\s*VEVO$', '', _papc, flags=re.IGNORECASE).strip()
            _papc = re.sub(r'\s*Official$', '', _papc, flags=re.IGNORECASE).strip()
            _papc = re.sub(r'\s*Music$', '', _papc, flags=re.IGNORECASE).strip()
            
            generic_channel_keywords = ["various artists", "official", "music", "topic", "channel", "records", "canal", "gravadora", "official channel", "artist channel"]
            if _papc and len(_papc.split()) < 5 and \
               _papc.lower() not in generic_channel_keywords and \
               _papc.lower() != title_to_process.lower():

                cleaned_title_as_song = clean_common_tags(title_to_process)
                cleaned_title_as_song_capitalized = capitalize_name(cleaned_title_as_song)
                
                if cleaned_title_as_song_capitalized and cleaned_title_as_song_capitalized.lower() != _papc.lower():
                    current_song_candidate = cleaned_title_as_song_capitalized
                    if _papc.lower() in current_song_candidate.lower():
                        escaped_artist_for_regex = re.escape(_papc)
                        pattern_prefix = r"^{}\s*[-–—:]\s*".format(escaped_artist_for_regex)
                        pattern_suffix = r"\s*[-–—:]\s*{}$|\s*\({}\)$".format(escaped_artist_for_regex, escaped_artist_for_regex)
                        
                        removed_prefix_song = re.sub(pattern_prefix, "", current_song_candidate, flags=re.IGNORECASE).strip()
                        if removed_prefix_song != current_song_candidate and removed_prefix_song: 
                             current_song_candidate = removed_prefix_song
                        else: 
                            removed_suffix_song = re.sub(pattern_suffix, "", current_song_candidate, flags=re.IGNORECASE).strip()
                            if removed_suffix_song != current_song_candidate and removed_suffix_song:
                                current_song_candidate = removed_suffix_song
                        
                        if not current_song_candidate or current_song_candidate.lower() == _papc.lower() or current_song_candidate == cleaned_title_as_song_capitalized :
                             if _papc.lower() in cleaned_title_as_song_capitalized.lower():
                                 temp_song = cleaned_title_as_song_capitalized.lower().replace(_papc.lower(), "").strip(" -:()[]").strip()
                                 if temp_song and temp_song != _papc.lower():
                                     current_song_candidate = capitalize_name(temp_song)
                                 else: 
                                     current_song_candidate = cleaned_title_as_song_capitalized
                             else: 
                                 current_song_candidate = cleaned_title_as_song_capitalized
                        else: 
                            current_song_candidate = capitalize_name(current_song_candidate)

                    if current_song_candidate and len(current_song_candidate.split()) < 10 and current_song_candidate.lower() != "unknown" and current_song_candidate.lower() != _papc.lower():
                        artist_final = _papc
                        song_title_final = current_song_candidate
                    elif current_song_candidate and current_song_candidate.lower() == _papc.lower(): 
                        artist_final = _papc 
                        song_title_final = capitalize_name(clean_common_tags(title_to_process)) 
                        if song_title_final.lower() == artist_final.lower(): 
                            artist_final = "Unknown" 

    if isinstance(song_title_final, str):
        song_title_final = re.sub(r'\s*\((?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP|Emboladores|DJ KR3|DJ Felipe Único|The Ultimate Collection)\s*\)\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\[(?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP|Emboladores|The Ultimate Collection)\s*\]\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\(\s*\)\s*|\s*\[\s*\]\s*', '', song_title_final).strip()
        song_title_final = re.sub(r'\s+\blive\b\s*$', '', song_title_final, flags=re.IGNORECASE).strip()

    featured_artists_final = sorted(list(set(filter(None, [capitalize_name(fa) for fa in featured_artists if fa]))))
    producers_final = sorted(list(set(filter(None, [capitalize_name(p) for p in producers if p]))))

    if not song_title_final or song_title_final.lower() == "unknown": song_title_final = "Unknown"
    if not artist_final or artist_final.lower() == "unknown": artist_final = "Unknown"

    if artist_final == title_to_process and song_title_final == "Unknown":
        artist_final = "Unknown"; song_title_final = capitalize_name(clean_common_tags(title_to_process))

    if artist_final != "Unknown" and isinstance(song_title_final, str):
        pass 

    if artist_final == "Unknown" and isinstance(song_title_final, str) and song_title_final != "Unknown": 
        common_separators = [" - ", " : ", " | ", " / ", " X "] 
        for sep in common_separators:
            if sep in song_title_final:
                parts_fallback = song_title_final.split(sep, 1)
                if len(parts_fallback[0].split()) <= 5 and len(parts_fallback[0].split()) > 0 and len(parts_fallback[0]) < 35:
                    potential_artist = capitalize_name(parts_fallback[0].strip())
                    potential_song = capitalize_name(parts_fallback[1].strip())
                    if potential_artist and potential_song and potential_artist.lower() != "unknown":
                         artist_final = potential_artist; song_title_final = potential_song; break
    
    if artist_final and isinstance(artist_final, str) and " x " in artist_final.lower(): 
        if not (artist_final.lower() == "lil nas x" or (artist_final.lower().endswith(" x") and len(artist_final.split())==1)):
            sub_artists = [capitalize_name(sa.strip()) for sa in re.split(r'\s+x\s+', artist_final, flags=re.IGNORECASE)]
            if len(sub_artists) > 1 and all(sub_artists): artist_final = ", ".join(sub_artists)

    if isinstance(artist_final, str) and ", Unknown" in artist_final: artist_final = artist_final.replace(", Unknown", "").strip()
    if isinstance(artist_final, str) and "Unknown, " in artist_final: artist_final = artist_final.replace("Unknown, ", "").strip()

    if artist_final and artist_final != "Unknown":
        main_artist_names_list = [a.strip().lower() for a in re.split(r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+', artist_final)]
        featured_artists_final = [fa for fa in featured_artists_final if not (capitalize_name(fa) and capitalize_name(fa).lower() in main_artist_names_list)]
        producers_final = [p for p in producers_final if not (capitalize_name(p) and capitalize_name(p).lower() in main_artist_names_list)]

    if artist_final == "Unknown" and song_title_final != "Unknown" and " - " in song_title_final:
        parts_last_chance = song_title_final.split(" - ", 1)
        if len(parts_last_chance[0].split()) < 4 and len(parts_last_chance[0]) > 0 : 
            potential_artist_lc = capitalize_name(parts_last_chance[0])
            potential_song_lc = capitalize_name(parts_last_chance[1])
            if potential_artist_lc and potential_artist_lc.lower() not in ["unknown", "official video", "lyrics"] and len(potential_artist_lc) > 1 : 
                artist_final = potential_artist_lc
                song_title_final = potential_song_lc
            
    if artist_final != "Unknown" and (not song_title_final or song_title_final == "Unknown"):
        song_title_final = capitalize_name(clean_common_tags(title_to_process)) 
        if artist_final.lower() in song_title_final.lower():
            escaped_artist_final_regex = re.escape(artist_final)
            pattern_prefix_final = r"^{}\s*[-–—:]\s*".format(escaped_artist_final_regex)
            pattern_suffix_final = r"\s*[-–—:]\s*{}$|\s*\({}\)$".format(escaped_artist_final_regex, escaped_artist_final_regex)
            
            temp_song_final = song_title_final
            removed_prefix_song_final = re.sub(pattern_prefix_final, "", temp_song_final, flags=re.IGNORECASE).strip()
            if removed_prefix_song_final != temp_song_final and removed_prefix_song_final:
                 temp_song_final = removed_prefix_song_final
            else:
                removed_suffix_song_final = re.sub(pattern_suffix_final, "", temp_song_final, flags=re.IGNORECASE).strip()
                if removed_suffix_song_final != temp_song_final and removed_suffix_song_final:
                    temp_song_final = removed_suffix_song_final
            
            if temp_song_final and temp_song_final.lower() != artist_final.lower():
                song_title_final = capitalize_name(temp_song_final)

    if song_title_final == "Unknown" and artist_final == "Unknown":
         song_title_final = capitalize_name(clean_common_tags(title_to_process))

    return artist_final, song_title_final, featured_artists_final, producers_final

def enrich_track_details_with_search(track_info, concise_search_tool):
    artist = track_info.get("artist")
    song_title = track_info.get("song_title")
    if not artist or artist == "Unknown" or not song_title or song_title == "Unknown":
        return False
    return True

def concise_search(query: str, max_num_results: int = 3):
  return []


def process_new_data_format(video_data_list, concise_search_tool_func):
    start_time_proc = time.time()
    processed_music_list = []
    skipped_titles_list_proc = []
    
    total_vids_processed = 0; music_vids_identified = 0; vids_skipped_not_music = 0
    music_extract_successful = 0; music_extract_failed_artist = 0; music_extract_failed_song = 0
    music_extract_fully_failed = 0; passed_to_srch = 0; errors_proc = 0

    for entry_data in video_data_list:
        total_vids_processed += 1
        
        original_yt_title = entry_data.get("original_youtube_title", "")
        title_for_extract = entry_data.get("title_for_extraction", original_yt_title) 
        channel = entry_data.get("channel_name", "Unknown")
        url = entry_data.get("youtube_url", f"https://www.youtube.com/watch?v=placeholder_for_entry_{total_vids_processed}")
        upload_dt = entry_data.get("upload_date")
        video_genre = entry_data.get("genre", "Unknown")

        if not original_yt_title:
            vids_skipped_not_music +=1
            skipped_titles_list_proc.append(f"[EMPTY ORIGINAL TITLE for entry in genre {video_genre}]")
            continue

        video_info_for_check = {
            "title": original_yt_title, 
            "original_title": original_yt_title
        }

        try:
            if is_likely_music_video(video_info_for_check):
                music_vids_identified += 1
                
                artist_ext, song_ext, ft_ext, prod_ext = extract_song_artist_from_title(title_for_extract, channel)

                music_item = {
                    "original_youtube_title": original_yt_title,
                    "processed_title_for_extraction": title_for_extract,
                    "artist": artist_ext if artist_ext else "Unknown",
                    "song_title": song_ext if song_ext else "Unknown",
                    "featured_artists": ft_ext,
                    "producers": prod_ext,
                    "genre": [video_genre] if video_genre and video_genre != "Unknown" else [],
                    "channel_name": channel,
                    "youtube_url": url,
                    "upload_date": upload_dt,
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
        "--- SCRIPT EXECUTION REPORT (process_library_foda.py) ---",
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
    all_videos_data = []
    
    curated_titles_path = os.path.join(CURATED_TITLES_DIR, CURATED_TITLES_FILENAME)
    curated_titles_map = load_curated_titles(curated_titles_path)
    print(f"Loaded {len(curated_titles_map)} curated titles for lookup from '{curated_titles_path}'.")

    if not os.path.exists(GENRE_FILES_DIR):
        print(f"ERRO: Diretório de arquivos de gênero não encontrado: {GENRE_FILES_DIR}")
        if not all_videos_data: 
             exit()

    # Ensure GENRE_FILES_DIR exists before trying to list its contents
    if os.path.exists(GENRE_FILES_DIR):
        for filename in os.listdir(GENRE_FILES_DIR):
            if filename.endswith(".txt"):
                genre_from_filename = os.path.splitext(filename)[0] 
                filepath = os.path.join(GENRE_FILES_DIR, filename)
                print(f"Processing genre file: {filepath} for genre: {genre_from_filename}")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    parsed_videos = parse_genre_file_content(content, genre_from_filename)
                    
                    for video in parsed_videos:
                        original_title = video.get("original_youtube_title", "")
                        normalized_original = normalize_string_for_match(original_title)
                        
                        title_to_use_for_extraction = curated_titles_map.get(normalized_original, original_title)
                        
                        video_data_for_processing = {
                            "title_for_extraction": title_to_use_for_extraction,
                            "original_youtube_title": original_title,
                            "channel_name": video.get("channel_name"),
                            "youtube_url": video.get("youtube_url"),
                            "upload_date": video.get("upload_date"),
                            "genre": video.get("genre") 
                        }
                        all_videos_data.append(video_data_for_processing)
                    
                    print(f"Found {len(parsed_videos)} entries in {filename}")
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
    else:
        print(f"WARNING: Genre files directory '{GENRE_FILES_DIR}' does not exist. No genre files will be processed.")

    if not all_videos_data:
        print("No video data loaded. Exiting. Check GENRE_FILES_DIR and file contents, or if the directory exists.")
        exit()
    
    print(f"\nTotal de {len(all_videos_data)} vídeos coletados de todos os arquivos de gênero.")

    now = datetime.now()
    output_folder_name = now.strftime("%Y-%m-%d_%H-%M-%S") + "_run_foda"
    output_root_dir = os.path.join(BASE_DIR, "output_script_principal") 
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
    output_directory_path = os.path.join(output_root_dir, output_folder_name)

    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)
        print(f"Created output directory: {output_directory_path}")

    output_json_filename = os.path.join(output_directory_path, "music_data.json")
    unknown_extraction_filename = os.path.join(output_directory_path, "unknown_extraction_videos.txt")
    skipped_videos_filename = os.path.join(output_directory_path, "skipped_videos.txt")
    report_filename = os.path.join(output_directory_path, "processing_report.txt")

    music_data, report_string, skipped_titles_list = process_new_data_format(all_videos_data, concise_search)
    report_string = report_string.replace("[output_folder_path]", output_directory_path)

    print("\n" + "="*50 + "\n"); print(report_string); print("\n" + "="*50 + "\n")
    
    unknown_extraction_data_entries = []
    for entry in music_data:
        if entry.get("artist") == "Unknown" or entry.get("song_title") == "Unknown":
            genre_list = entry.get('genre', ['Unknown'])
            genre_str = genre_list[0] if genre_list else 'Unknown'
            unknown_extraction_data_entries.append(
                f"Original Title: {entry.get('original_youtube_title')}\n"
                f"  Processed Title: {entry.get('processed_title_for_extraction')}\n"
                f"  Extracted: Artist='{entry.get('artist')}', Song='{entry.get('song_title')}'\n"
                f"  Channel: {entry.get('channel_name')}, Genre: {genre_str}\n"
                f"  URL: {entry.get('youtube_url')}\n"
                f"--------------------------------------------------"
            )

    if unknown_extraction_data_entries:
        try:
            with open(unknown_extraction_filename, 'w', encoding='utf-8') as f_unknown:
                for item_str in unknown_extraction_data_entries: f_unknown.write(item_str + "\n")
            print(f"Lista de vídeos com extração 'Unknown' salva em: {unknown_extraction_filename}")
        except Exception as e: print(f"ERROR saving unknown extraction list: {e}")

    if skipped_titles_list:
        try:
            with open(skipped_videos_filename, 'w', encoding='utf-8') as f_skipped:
                for title in skipped_titles_list: f_skipped.write(title + "\n")
            print(f"Lista de vídeos pulados salva em: {skipped_videos_filename}")
        except Exception as e: print(f"ERROR saving skipped videos list: {e}")

    try:
        with open(output_json_filename, 'w', encoding='utf-8') as f_json: json.dump(music_data, f_json, indent=2, ensure_ascii=False)
        print(f"\nData successfully saved to {output_json_filename}")
    except Exception as e: print(f"ERROR saving data to json: {e}")

    try:
        with open(report_filename, 'w', encoding='utf-8') as f_report: f_report.write(report_string)
        print(f"Report saved to {report_filename}")
    except Exception as e: print(f"ERROR saving report: {e}")

# --- END OF FILE process_library_foda.py ---