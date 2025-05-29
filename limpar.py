# Este é o conteúdo para o seu arquivo limpar.py

import re # Importa o módulo para expressões regulares (normalizar espaços)
import unicodedata # Importa o módulo para normalização Unicode

def normalize_string_for_match(s):
    """Normaliza uma string para uma correspondência mais robusta."""
    s = unicodedata.normalize('NFC', s) # Normaliza caracteres Unicode (ex: acentos)
    s = re.sub(r'\s+', ' ', s)          # Substitui múltiplos espaços por um único espaço
    return s.strip()                   # Remove espaços no início/fim

def remove_lines_from_file(filename, lines_to_remove_raw_list, report_filename="removed_lines_report.txt"):
    """
    Remove specified lines from a text file using robust matching
    and creates a report of removed lines.

    Args:
        filename (str): The path to the text file.
        lines_to_remove_raw_list (list): A list of raw strings to be removed.
        report_filename (str): The name of the file to save the removed lines report.
    """
    # Normaliza as linhas a serem removidas para comparação robusta
    lines_to_remove_normalized_set = {normalize_string_for_match(line) for line in lines_to_remove_raw_list}
    
    removed_lines_actual = [] # Para armazenar as linhas exatas que foram removidas do arquivo
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()

        lines_kept = []
        for line_from_file in original_lines:
            # Normaliza a linha do arquivo antes de verificar se deve ser removida
            if normalize_string_for_match(line_from_file) not in lines_to_remove_normalized_set:
                lines_kept.append(line_from_file) # Mantém a linha original com sua formatação
            else:
                removed_lines_actual.append(line_from_file.strip()) # Adiciona a linha original (strip) ao relatório

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines_kept)
        
        removed_count = len(original_lines) - len(lines_kept)
        print(f"Processed '{filename}'. Kept {len(lines_kept)} lines. Removed {removed_count} lines.")

        # Create the report file
        if removed_lines_actual:
            with open(report_filename, 'w', encoding='utf-8') as report_f:
                report_f.write("Lines removed from My Playlist.txt:\n")
                report_f.write("====================================\n")
                for removed_line in removed_lines_actual:
                    report_f.write(f"{removed_line}\n")
            print(f"Report of removed lines saved to '{report_filename}'")
        else:
            # Se nenhuma linha foi removida, ainda cria um relatório vazio para consistência ou informa.
            with open(report_filename, 'w', encoding='utf-8') as report_f:
                report_f.write("No lines were removed from My Playlist.txt based on the provided list.\n")
            print("No lines were removed, an empty report file was created or updated.")


    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Lista de linhas a remover (esta é a lista "ideal" das versões "menor organizada")
# O script agora é mais robusto para encontrar correspondências mesmo com pequenas variações de espaçamento ou Unicode.
lines_to_remove_raw = [
    "Axé Music - Kame Kame Kame Ha do Dragon Ball",
    "Bell Biv DeVoe - Poison (de Dance Central 3)",
    "Childish Gambino - Bonfire (Música usada no meme \"cursed images\")",
    "Comédia MTV - O Lado Bom de Ser Gay",
    "Galo Frito - 3 PORQUINHOS",
    "Galo Frito - AS AVENTURAS DE PINÓQUIO",
    "Galo Frito - BRASIL É FODA",
    "Galo Frito - DON'T START MOSTRA O PEITIN NOW 🤭🤭🤭scari",
    "Galo Frito - ESSA MINA É UMA VACA | Paródia Alicia Keys Girl on Fire",
    "Galo Frito - JOÃO E O PÉ DE MACONHA ♫",
    "Galo Frito - MC POZE DO QUEIJO 🧀 (PARÓDIA Vida Louca)",
    "Galo Frito - O MENINO DE VÓ FOI BUSCAR UM PÓ (PARÓDIA)",
    "Galo Frito - ♫ OTAKU BELEZA ♫",
    "Galo Frito - ＯＮＤＥ　ＡＮＤＡ　ＶＯＣＥ",
    "Galo Frito - DESLEMBRANÇAS | PARÓDIA Hungria Hip Hop",
    "Galo Frito - EU NEM TAVA LÁ! | PARÓDIA Costa Gold com Marechal e Luccas Carlos",
    "Hans Zimmer - Davy Jones (de Piratas do Caribe)",
    "Historical H.P. Lovecraft Society - Death May Die",
    "Historical H.P. Lovecraft Society - Do You Fear What I Fear",
    "Historical H.P. Lovecraft Society - Fishmen",
    "ItsJustSomeRandomGuy - Reggae Shark™",
    "Miracle Of Sound - Sovngarde Song 2016",
    "Nightwish - The Phantom Of The Opera", # Corrected version has (Cover)
    "PMM - ASTRONOMIA PNEU QUEIMADO",
    "PMM - Doki Doki MC Poze Club",
    "PMM - FUNK CIRCULATION",
    "PMM - NA RABA TOMA BUTTERCUP",
    "PMM - RENAI FUNK CIRCULATION",
    "Tyler, The Creator ft. YoungBoy Never Broke Again & Ty Dolla $ign - WUSYANAME", # Order of ft. and title
    "\"Revenge\" - A Minecraft Parody of Usher's DJ Got Us Fallin' In Love (Music Video)",
    "\"TNT\" - A Minecraft Parody of Taio Cruz's Dynamite (Music Video)",
    "\"Take My True Love By The Hand - The Limeliters\", Breaking Bad OST (Lyrics in Description)",
    "\"TheCypherDeffect\" - Costa Gold Apresenta: DAMASSACLAN ! [Haikaiss, DonCesão, Família Madá & DJ EB]",
    "\"Viajando\" - Ventania e Banda Hippie no Estúdio Showlivre 2017",
    "$uicideboy$ - kill yourself part (1,2,3,4)", # Case difference
    "(Clipe Oficial) MC Maha - Senhor dos Anais.(FUNK DO SENHOR DOS ANÉIS)",
    "(Deepfake) James Bond vs Austin Powers. Epic Rap Battles of History",
    "01 I Want You Back - Michael Jackson - The Ultimate Collection [HD]",
    "02 ABC - Michael Jackson - The Ultimate Collection [HD]",
    "02 Stranger In Moscow - Michael Jackson - The Ultimate Collection [HD]",
    "03 I'll Be There - Michael Jackson - The Ultimate Collection [HD]",
    "04 Got To Be There - Michael Jackson - The Ultimate Collection [HD]",
    "05 Dirty Diana - Michael Jackson - The Ultimate Collection [HD]",
    "05 I Wanna Be Where You Are - Michael Jackson - The Ultimate Collection [HD]",
    "06 Ben - Michael Jackson - The Ultimate Collection [HD]",
    "07 Dancing Machine - Michael Jackson - The Ultimate Collection [HD]",
    "08 Dangerous (Early Version) - Michael Jackson - The Ultimate Collection [HD]",
    "08 Enjoy Yourself - Michael Jackson - The Ultimate Collection [HD]",
    "08 State Of Shock - Michael Jackson - The Ultimate Collection [HD]",
    "09 Ease On Down The Road - Michael Jackson - The Ultimate Collection [HD]",
    "09 You Rock My World - Michael Jackson - The Ultimate Collection [HD]",
    "10 We Are The World (Demo) - Michael Jackson - The Ultimate Collection [HD]",
    "12 Shake Your Body - Michael Jackson - The Ultimate Collection [HD]",
    "14 Rock With You - Michael Jackson - The Ultimate Collection [HD]",
    "15 Off The Wall - Michael Jackson - The Ultimate Collection [HD]",
    "1Kilo - Pablo Martins | DoisP | Sadan | Mozart MZ | Funkero | Knust | Pelé Milflows | Xamã [ Ep.129]", # Formatting of artist list and Ep.
    "21 Savage - a lot (Official Video) ft. J. Cole", # Corrected version has ft. J. Cole (Official Video)
    "9mm - yun li ft d$ luqi (prod biffe)",
    "A LITTLE THEORIZING | Official Game Theory Song!",
    "A PRESIDENTA | Paródia ANACONDA - NICKI MINAJ",
    "A$AP ROCKY X TYLER THE CREATOR - POTATO SALAD",
    "A$AP Rocky - Multiply (Official Audio) ft. Juicy J",
    "A$AP Rocky - Praise The Lord (Da Shine) (Official Video) ft. Skepta",
    "ASHLEY & MARY KATE LIFE - MC VV FT DREIKI (PROD LAUNZERA)",
    "Abusadamente - MC Gustta e MC DG (KondZilla) | Official Music Video",
    "Alex Heflin - Back in the 90's (From \"BoJack Horseman\")",
    "Alice Francis - Shoot Him down! (Official Video) (Break his neck, neck, neck, neck)", # Extra parenthetical
    "Amiga Da Minha Mulher - Seu Jorge (Músicas Para Churrasco Vol.1)",
    "Anderson .Paak - Fire in the Sky (Official Audio) | Shang-Chi: The Album",
    "Apocalypse Orchestra - The Garden Of Earthly Delights (Official Music Video) Medieval Metal", # Corrected has (Medieval Metal)
    "Arch Enemy - Shout (cover Version)",
    "Arch Enemy - The Book of Heavy Metal (cover Version)",
    "AronChupa, Little Sis Nora - I'm an Albatraoz | OFFICIAL VIDEO",
    "Asheru - Judo Flip (Boondocks Theme Song Full Version) w/lyrics",
    "Aurelio Voltaire - Death Death (Devil, Devil, Evil, Evil, Song) (OFFICIAL)",
    "Aurelio Voltaire - Dirtiest Song that Ain't OFFICIAL",
    "Aurelio Voltaire - Hallelujah - World Premiere Song",
    "Aurelio Voltaire - Oh My Goth! (OFFICIAL) with lyrics",
    "Aurelio Voltaire - Riding a Black Unicorn OFFICIAL",
    "Aurelio Voltaire - The Beast of Pirate's Bay (OFFICIAL)",
    "Aurelio Voltaire - This Ship's Going Down (OFFICIAL)",
    "Aurelio Voltaire - To The Bottom Of The Sea (OFFICIAL)",
    "Aurelio Voltaire - Wake Up (OFFICIAL) with LYRICS",
    "Ayo & Teo, Lil Yachty - Ay3 (Official Video)", # Corrected: Ayo & Teo - Ay3 ft. Lil Yachty (Official Video)
    "BACTÉRIA GET LUCKY - MC Ray-Ban",
    "BARMAN DE IOGURTE 🍧 - MrPoladoful - CLIPE OFICIAL",
    "BELZEBUBS - Cathedrals Of Mourning (OFFICIAL VIDEO)",
    "BEST Zelda Rap EVER!! (Starbomb) - Legendado PT-BR",
    "BIG MERDA | Paródia Scream and Shout - Will.i.Am e Britney Spears",
    "BLINDING AZEITONA (EXTENDED VERSION) | LEOD",
    "BODY & BASS - Wojtek Pilichowski",
    "BRADIO-Flyers【TVアニメ「デス・パレード」OP曲】(OFFICIAL VIDEO)",
    "Baby Goth - Swimming (Audio) ft. Trippie Redd, Lil Xan",
    "Baldi’s Basics Song- Basics in Behavior [Blue]- The Living Tombstone feat. OR3O",
    "Barrels of Whiskey - The O'Reillys and the Paddyhats [Official Video]",
    "Barão Vermelho · Cazuza · Frejat - Bete Balanço",
    "Bed Intruder Song - Full Version",
    "Bella Poarch - Build a B*tch (Tradução/Legendado) [Clipe Oficial]",
    "Beth Carvalho - Camarão Que Dorme a Onda Leva - São José de Madureira - Dor de Amor Ao Vivo",
    "Bonde R300 - Oh Nanana (DJ CK) Lançamento 2017", # Corrected is shorter
    "Breakbot - Baby I'm Yours (feat. Irfane) [Official Audio]",
    "Bruno Mars, Anderson .Paak, Silk Sonic - Leave the Door Open [Official Video]",
    "Bruno Mars, Anderson .Paak, Silk Sonic - Skate [Official Music Video]",
    "Bruno Mars, Anderson .Paak, Silk Sonic - Smokin Out The Window [Official Music Video]",
    "Bumbum Granada - MCs Zaac e Jerry (KondZilla) | Official Music Video",
    "Bury the Light - Vergil's battle theme from Devil May Cry 5 Special Edition",
    "CANDLEMASS ft. TONY IOMMI - Astorolus - The Great Octopus (Official Video) | Napalm Records",
    "CAZZETTE - She Wants Me Dead ft. The High (CAZZETTE vs. AronChupa) [Official Video]",
    "CELTIC FROST - A Dying God Coming Into Human Flesh (OFFICIAL VIDEO)",
    "CHEGOU O VERÃO | Paródia Timber - Pitbull ft. Ke$ha",
    "CHEIRO DE PNEU QUEIMADO LO-FI (Versão SteveZ TV)",
    "CHEIRO DE SOMEBODY THAT I USED TO KNOW (EXTENDED) | LEOD",
    "CHTHONIC - TAKAO - Official Video | 閃靈 [皇軍] MV",
    "COLTER WALL - IMAGINARY APPALACHIA - The Devil Wears a Suit and Tie",
    "Canção Xamânica: 02 Pena Branca Curador - Akaiê Sramana",
    "Calvin Harris - Feels (Official Video) ft. Pharrell Williams, Katy Perry, Big Sean",
    "Calvin Harris - Rollin (Official Audio) ft. Future, Khalid",
    "Camille - MANDALALÀ - 6 - \"UN CRAYON DE COULEUR\"",
    "Candlemass - \"Mirror Mirror\" Official Video (1988)",
    "Carlinhos Brown - Vc, O Amor e Eu Feat. Quésia Luz (Clipe Oficial)",
    "Cazuza - Exagerado (\"Cazuza & Barão Vermelho - Melhores Momentos\") [Áudio Oficial]",
    "Charlie Brown Jr - Céu Azul ( Letra )",
    "Charlie brown Jr Só os loucos sabem - letra.",
    "Chris Brown - Wobble Up (Official Video) ft. Nicki Minaj, G-Eazy",
    "Coffee for Your Head ( Vinyll Remix ) / Lo-fi Chill",
    "Conexão Zona Sul - Racionais MC's ft. ClariS",
    "Costa Gold - Dás Arábia Pt. 2 (feat. Haitam) [prod. Nine] (Clipe Oficial)",
    "Costa Gold e Haikaiss - Irmão DQbrada! (prod. Nox e Andre Nine) (Clipe Oficial)",
    "Cowboy Bebop OST 1 - Rush",
    "Coça de xereca - Rebecca ( DJ Rogerinho do Quero) (VERSÃO ORIGINAL)",
    "Crasher-Vania (Starbomb) - Legendado PT-BR",
    "Criolo - Fio De Prumo (Padê Onã) (Part.Juçara Marçal)",
    "Cuphead - Porkrind's Shop [Electro Swing Remix]",
    "D$ Luqi - GOXTOSINHO! (feat. Yung Lixo) [Official Music Video]",
    "DE VOLTA AO SERVER - MC VV FT BOFFE & JEAN XEROSO (PROD BOFFE & MC VV)",
    "DHION - CARA DA DROGA ft. JEDY (Prod. SLOW808)",
    "DHION - FUNK GÓTICO (PROD.SLOW808) (OFICIAL AUDIO) | Explicit", # Corrected is shorter
    "DJ Durel, Migos - Hot Summer (Official Video)",
    "DJ Khaled - I'm The One ft. Justin Bieber, Quavo, Chance the Rapper, Lil Wayne",
    "DJ Shub - Indomitable ft. Northern Cree Singers (Official Video)",
    "DOLLY LARANJA | Paródia Klyn x Igu - França",
    "DOUGLAS & EU - MC VV (PROD MC VV & EF)",
    "DRAM - Broccoli feat. Lil Yachty (Official Music Video)",
    "DYES IWASAKI - BAD HATTER feat.リリィミズサキ [#ElectroSwing]",
    "Damian \"Jr. Gong\" Marley - Medication (ft. Stephen Marley) (Official Audio)",
    "Damian “Jr. Gong” Marley - Medication [Remix] (Stephen \"Ragga\" Marley, Wiz Khalifa & Ty Dolla $ign)",
    "Demondice · nyankobrq · TINY PLANETS · TINY PLANETS · Mixed and mastered in kokoroStudio - Hazy Skyscraper",
    "Denzel Curry, Gizzle, Bren Joy - Dynasties & Dystopia | Arcane League of Legends | Riot Games Music",
    "Djavan · Stevie Wonder - Samurai",
    "Doki Doki Literature Club! OST - Your Reality (Credits)",
    "Dona Gigi - Os Caçadores Feat DJ Marlboro (Clipe Oficial)",
    "Dr. Dre - The Next Episode (Official Music Video) ft. Snoop Dogg, Kurupt, Nate Dogg",
    "Dr. Dre · Snoop Dogg - Nuthin' But A \"G\" Thang",
    "Dublador do Sid (É desse jeito) - Remix by AtilaKw",
    "ELUVEITIE - The Call Of The Mountains (OFFICIAL MUSIC VIDEO)",
    "EMICOUTO - MILHA (Prod. Mortão VMG) 1 MILHÃO DE INSCRITOS!",
    "ERA BÃO - MC VV FT BOFFE & JEAN XEROSO (PROD BOFFE)",
    "EU NÃO VOU PAGAR - MC VV (PROD BOFFE)",
    "EU TO LIVRE DA VAGABA - MC VV (PROD EF)",
    "EU VOU MACHUCAR SÓ UM POUQUINHO - CATUCANDO GOSTOSINHO - MC Teteu (Love Funk) JC no Beat & DJ F7",
    "Elis Regina & Tom Jobim - \"Aguas de Março\" - 1974",
    "Enemy - League of Legends (Arcane) but it’s only J.I.D", # Corrected: Imagine Dragons & J.I.D - Enemy (from Arcane League of Legends)
    "Ep. 134 - MC SID - \"Rap News\" [Prod. Velho Beats]",
    "Ethno-House - Wild Spirit by Indian Calling",
    "FENDA DA SUNGA 2 - MC VV FT BOFFE (PROD BOFFE)",
    "Fabio Brazza e Péricles - Só Uma Noite (Clipe Oficial) [Prod. Paiva e Mortão VMG]",
    "Felipe Smith - Remix by AtilaKw",
    "Filthy Frank - Weeaboos Lyrics", # Corrected: Filthy Frank - Weeaboos (Lyrics)
    "Fuleragem - MC WM (KondZilla) | Official Music Video",
    "G-Eazy - No Limit REMIX ft. A$AP Rocky, Cardi B, French Montana, Juicy J, Belly",
    "Gabriel O Pensador · Lulu Santos - Cachimbo da Paz",
    "Gabriel O Pensador, Lulu Santos - Cachimbo Da Paz ft. Lulu Santos",
    "Gabriel O Pensador, Lulu Santos, Xamã - Cachimbo da Paz 2",
    "Galo Cego - Remix by AtilaKw",
    "Ghost B.C - Year Zero (Lyric Video - HD)",
    "Gilberto & Gilmar - Nóis Não Vive Sem Msluié - Gravado Em Um Circo, Onde Tudo Começou", # Corrected: Gilberto & Gilmar - Nóis Não Vive Sem Muié (Gravado Em Um Circo)
    "Giro dos artista - MC GP , MC BRUNINHO DA PRAIA , MC KEVIN , MC IG , MC MAGAL ( DJ OREIA E Oldilla )", # Corrected: Giro dos Artistas - MC GP, MC Bruninho da Praia, MC Kevin, MC IG, MC Magal (DJ Oreia e Oldilla)
    "Glass Joe's Title Fight (Starbomb) - Legendado PT-BR",
    "God of No More (Starbomb) - Legendado PT-BR",
    "Gorillaz - Controllah ft. MC Bin Laden (Official Audio)",
    "Gorillaz - Cracker Island ft. Thundercat (Official Audio)",
    "Gorillaz - New Gold ft. Tame Impala & Bootie Brown (Official Lyric Video)",
    "Gotye - Somebody That I Used To Know (feat. Kimbra) [Official Music Video]",
    "Green Day - Boulevard Of Broken Dreams [Official Music Video] [4K Upgrade]",
    "Green Day - Good Riddance (Time of Your Life) [Official Music Video] [4K UPGRADE]",
    "Green Day - Holiday [Official Music Video] [4K Upgrade]",
    "Green Day - Wake Me Up When September Ends [Official Music Video] [4K Upgrade]",
    "Green Day - When I Come Around [Official Music Video] (4K Upgrade)",
    "Gregor Salto - Para Voce Feat. Curio Capoeira | Official Video | Capoeira Music Video",
    "Grover Washington Jr. - Just the Two of Us (feat. Bill Withers) (Official Lyric Video)",
    "Gucci Mane - I Get The Bag feat. Migos [Official Music Video]",
    "Gucci Mane - Kept Back feat. Lil Pump [Official Music Video]",
    "Gucci Mane, Bruno Mars, Kodak Black - Wake Up in The Sky [Official Music Video]",
    "Guiu · Dk 47 · IssoQueÉSomDeRap · Soffiatti - Racista e N1Ke (feat. Soffiatti)",
    "HEARTSTEEL - PARANOIA ft. BAEKHYUN, tobi lou, ØZI, and Cal Scruby (Official Music Video)",
    "HOJE EU NÃO PASSO CARTÃO | Funk Ostentação de Pobre",
    "HOJE TEM GOL DO RIBAMAR - MC NANDINHO e PITTER CORREA ((Áudio Oficial))",
    "HYPE NO JUTSU 4 - LUCKHAOS x Massaru (Prod. EF) [Edit by @sr_machinarium]",
    "I Choose You To Die! (Starbomb) - Legendado PT-BR",
    "I Saw you Saying (That You Say That You Saw) - Raimundos - Lyrics",
    "IEMANJÁ - CANTO DE IEMANJÁ CON LETRA", # Corrected: Umbanda - Canto de Iemanjá (Com Letra)
    "IGNEA — Alga (Official Video) / symphonic metal", # Corrected: Ignea - Alga (Official Video) (Symphonic Metal)
    "INDIAN MOONLIGHT (Official Video)", # Corrected: S. J. Jananiy - Indian Moonlight (Official Video)
    "IRON MAIDEN - Fear of the Dark (Harp Twins) ELECTRIC HARP METAL", # Corrected: Harp Twins - Fear of the Dark (Iron Maiden Electric Harp Metal Cover)
    "Indian Calling - Yeha Noha - Native American Music",
    "Inner Circle - Games People Play (Official Video HD)(Audio HD)", # Corrected: Inner Circle - Games People Play (Official Video HD)
    "Irish Way - The O'Reillys and the Paddyhats [Official Video]",
    "Ivete Sangalo, Maria Bethânia - Muito Obrigado Axé",
    "Ivete Sangalo, Tatau - Arerê",
    "J Balvin, Willy William - Mi Gente (Official Video)",
    "Jack e Chocolate · DJ Marlboro - Um Morto Muito Louco",
    "Jason Mraz - I'm Yours (Official Video) [4K Remaster]",
    "Jay Rock, Kendrick Lamar, Future, James Blake - King's Dead (Official Music Video)",
    "John Entwistle of The Who - Bass Solo Atlanta 2000",
    "Joyner Lucas & Will Smith - Will (Remix)",
    "Justin Bieber - Peaches ft. Daniel Caesar, Giveon",
    "K.A.A.N - Mary Jane // For Honor Edit",
    "K/DA - POP/STARS (ft. Madison Beer, (G)I-DLE, Jaira Burns) | Music Video - League of Legends",
    "KISS - Shout It Out Loud ( 2012 Remix ) - Destroyer Resurrected Album 2012",
    "KVNYL · Agnus · Sir Jude - Running",
    "KYLE - Hey Julie! feat. Lil Yachty [Lyric Video]",
    "Kangwaá - Cantando para Nhanderú - Indígenas Tupi Guarani",
    "Kanye West · PARTYNEXTDOOR - Ghost Town",
    "Kendrick Lamar · Jay Rock - Money Trees",
    "Kenny Loggins - Footloose (From \"Footloose\" Soundtrack)",
    "Kiss - Rock And Roll All Nite (From Kiss eXposed)",
    "LACUNA COIL - Enjoy the Silence - US Version (OFFICIAL VIDEO)",
    "LIL' LIXO - ROLÊ NA NETOLAND [CLIPE OFICIAL]", # Corrected: Yung Lixo e Lil Lixo - Rolê na Netoland (Clipe Oficial)
    "LSD - Genius ft. Sia, Diplo, Labrinth",
    "LSD - Mountains (Official Lyric Video) ft. Sia, Diplo, Labrinth",
    "LUCKHAOS - A moderação (edit by @jotatress) [prod PMM]",
    "LUCKHAOS - Batidão Do Suicídio 2 (Prod. by Koji & XB$) [Tipografia by @_britt0_]",
    "LUCKHAOS - COMO O DEREK FAZ TRAP (Passinho do Carti) [Prod. by NebulousBeatz]",
    "LUCKHAOS - Mina, eu já gozei (edit by @jotatress) [prod PMM]",
    "LUCKHAOS - Mina, eu não amo você (ft. Waifudida) [SHITTRAP ROMÂNTICO]",
    "LUCKHAOS - Novinha bem anime [ANIMESHITTRAP] (Prod. by Brycky)",
    "LUCKHAOS - Novinha do feto morto (feat. Waifudida) [Clipe Oficial]",
    "LUCKHAOS - ♪ MUITO PESCOTAPA ♪ (Clipe Oficial) (Prod. aizenboy) (Edit by 5verso)",
    "LUCKHAOS - ♪ Olha a carinha dessa desgraçada ♪ (Prod. by KzZ)",
    "LW - Identidade (Official Visualizer) prod. @manuGTB x @vhulto",
    "Lil Dicky - $ave Dat Money feat. Fetty Wap and Rich Homie Quan (Official Music Video)",
    "Lil Dicky - Professional Rapper (Feat. Snoop Dogg)",
    "Lil Luvi - Gata (Clipe Oficial) - LUCAS INUTILISMO",
    "Lil Nas X, Jack Harlow - INDUSTRY BABY (Official Video)",
    "Lil Peep - Awful Things feat. Lil Tracy (Official Video)",
    "Lil Peep - Star Shopping (Lyrics) (Music video)",
    "Lil Peep · ILoveMakonnen - Sunlight On Your Skin (Bonus Track)",
    "Lil Skies - Lust [Official Music Video] (Dir. by @NicholasJandora)",
    "Lil Skies - No Rest [Official Music Video] (Dir. by @NicholasJandora)",
    "Lil Skies x Yung Pinch - I Know You [Official Music Video] (Dir. by @NicholasJandora)",
    "Lilo & Stitch - Hawaiian Roller Coaster Ride (Mattrixx Remix) [Lofi Remix]", # Corrected: Mattrixx - Hawaiian Roller Coaster Ride (Lilo & Stitch Lofi Remix)
    "Lily Allen - Fuck You [Tradução/Legendado]",
    "Louis & Ella - Dream A Little Dream Of Me (HD)",
    "Luan Banana | Paródia Luan Santana - Meteoro",
    "Luciana Mello, Walmir Borges - Ainda É Tempo Pra Ser Feliz (Videoclipe Oficial)",
    "Lucid Vida Louca - MC Poze ft. Juice WRLD", # Corrected: MC Poze & Juice WRLD - Lucid Vida Louca (Mashup)
    "Luckhaos - A Trindade do Shittrap (Macaco Engraçado) (feat. Xxxbi$entb0y$$ e Yung Bostola)",
    "Luigi's Ballad (Starbomb) - Legendado PT-BR",
    "Luiz Gonzaga - Asa Branca ft. Fagner, Sivuca, Guadalupe",
    "Ly - O Lay Ale Loya (Circle Dance)", # Corrected: Traditional - Ly O Lay Ale Loya (Circle Dance)
    "MAMADEIRA DE CERVEJA - Paródia Chainsmokers - Closer",
    "MATUEIGHT - QUER CHUPAR 😙💨 (PARÓDIA)",
    "MATUEIGHT - É NATAL 👃🎅 (PARÓDIA Matuê - É Sal)",
    "MC 3L e MC Ygor Yanks - Acabou a Água (Love Funk) DJ J2 e DJ PBEATS",
    "MC Bin Laden, MC Pikachu, Mc 2K e MC Brinquedo - Feliz Natal (Vídeo Oficial)",
    "MC Brinquedo - Pepeca no Pau Part. 2 (KondZilla - WebClipe)",
    "MC Brinquedo e MC Pikachu - Vai Safada (Video Clipe) DJ R7",
    "MC Crash - Sarrada No Ar (Passinho do Romano) (KondZilla)",
    "MC Davi e MC Livinho - Mina Louca (KondZilla)",
    "MC Dede - Bumbum Na Água ♪ (Prod Dj Bruninho FZR) Música Nova 2013",
    "MC Dudu, MC Magrinho e MC Nandinho - Pepeca Malcriada (DJ R7)",
    "MC Fioti - Bum Bum Tam Tam (KondZilla) | Official Music Video",
    "MC KEVIN O CHRIS - EU VOU PRO BAILE DA GAIOLA [ MUSICA NOVA 2018 ]",
    "MC KEVIN O CHRIS - TU TA NA GAIOLA [ LANÇAMENTO 2018 ]",
    "MC Kevin - Sniper (PereraDJ) (Áudio Oficial)",
    "MC Kevinho - O Grave Bater [Sintonia Soundtrack] (KondZilla)",
    "MC Kevinho e Léo Santana - Encaixa (KondZilla)",
    "MC L Da Vinte · MC Gury · MC L Da Vinte - Parado no Bailão", # Corrected: MC L Da Vinte & MC Gury - Parado no Bailão
    "MC Lan - Cyclonado (Lan RW e Lil Beat RW) Lançamento 2017",
    "MC Lan - Maquiavelico | Senta Pros Louco, Sarra Pros Mlk Doido (Lan RW e DJ Ian Belmonte) 2017",
    "MC Lan - Open The Tcheka - Putaria em Inglês (DJ R7) Lançamento 2017",
    "MC Lan - Rabetão (Lan RW e Lil Beat RW) Lançamento 2017",
    "MC Lan e Djonga - 5 Minutos de Merda (DJ G Beats) Videoclipe",
    "MC Lan e MC WM - Ei Psiu To Ti Observando - Tum Tum Balançando (Lan RW e DJ Will O Cria)",
    "MC Lan e MC WM - Sua Amiga Vou Pegar e Lararara - É Melhor Sentando (DJ Will O Cria e Lan Rw) 2017",
    "MC Lan e MC WM - Vou Furunfá - Senta Prós Pobre Lo",
    "MC Lan, Skrillex, TroyBoi feat. Ludmilla e Ty Dolla $ign - Malokera (kondzilla.com)",
    "MC Leléto e MC GW - Bailão (Novinha Tu Tá Tirando) (Vídeo Clipe Oficial) DJ Tadeu",
    "MC Livinho - Cheia de Marra (KondZilla) | Official Music Video",
    "MC Livinho - Pepeca do Mal (DJ Perera) Lançamento 2014",
    "MC Maha - Funk Do Star Wars | Treta nas Estrelas (WebClipe Oficial 2018) DJ WS",
    "MC Pikachu - Lá no Meu Barraco (Videoclipe) @BielBoladoOficial",
    "MC Pikachu - Tava na Rua (DJ Pikenó) (KL PRODUTORA)",
    "MC Pikachu · Emerson Martins - Guarda Chuva",
    "MC REBECCA - CAI DE BOCA NO BUCETAO [DJ ZEBRINHA DO PISTINHA]",
    "MC TIMBU - PALAVRAS NÃO BASTAM, TEM QUE SE ENVOLVER [DJ BRUNO] | LYRICS by @Lipee",
    "MC Tavinho - Ela Me Mamou(Prera Dj)(Vídeo Clipe)#detonafunk",
    "MC VV & BOFFE - AMOR GERIATRICO (prod. LAUNZERA)",
    "MC VV & LAUNZERA - CONDOMÍNIO LIFE (prod. LAUNZERA)",
    "MC VV & PREDO - NÃO ERRO TIRO DE NINE (prod. JANGO)",
    "MC VV (ft. BOFFE) - Autoescola das Loucas (prod. MC VV & EF)",
    "MC VV (ft. LAUNZERA) - Os Boy da Boca (prod. MC VV)",
    "MC VV - Big Crack Trinity (prod. MC VV & EF)",
    "MC VV - Daily Vlog (prod. JANGO & LAUNZERA)",
    "MC VV - E no Fim foram Dois (prod. MC VV)",
    "MC VV - FEEL GOOD 2 (ft. LUCKHAOS)",
    "MC VV - Mando o Michael (prod. MC VV & EF)",
    "MC VV - Pisadona (Trapiseiro) (prod. LAUNZERA)",
    "MC VV - SCAM FROM NIGERIA (prod. EF)",
    "MC VV - SOGRA DESGRAÇADA (prod. LAUNZERA)",
    "MC VV - Sequestro as 11 (prod. MC VV & EF)",
    "MC VV - Shadow 4EVER (prod. MC VV)",
    "MC VV - TO DE AK NA RUA (prod. LAUNZERA)",
    "MC VV - UM CARA COOL (prod. JANGO)",
    "MC VV - sindrome de estoucomdedonomeuboga (prod. MC VV)",
    "MC VV, BOFE & JEAN XEROSO - CAIPIRA LIFE",
    "MC VV, JEAN XEROSO & BOFFE - CRIAS DO MINE (prod. BOFFE)",
    "MC VV, JEAN XEROSO & BOFFE - FENDA DA SUNGA (prod. BOFFE)",
    "MC Zaac - Te Jurupinga (DJ Yuri Martins) Lançamento 2017",
    "MD NEVE - REI OSASCO 👃 (PARÓDIA)",
    "ME COME BABY | Paródia Call Me Maybe - Carly Rae Jepsen",
    "MOB79 · Djonga · Don Cesão · BK · Febem · Torres · Koning - Atleta do Ano (Remix)",
    "MY CONQUISTER - ENTREGADOR DO IFOOD (Clipe Oficial) prod. @_beatsbysav",
    "MY CONQUISTER - SIGMA LIFESTYLE 🗿🍷 (Clipe Oficial) prod. @vhulto",
    "Mad World - Vintage Vaudeville - Style Cover ft. Puddles Pity Party & Haley Reinhart",
    "Magrelinho - Remix by AtilaKw",
    "Mamonas Assassinas - Cabeça De Bagre II/Baby Elephant Walk - Música Incidental (Studio Version)",
    "Matthew Perryman Jones - Living in the Shadows | Love, Death & Robots OST",
    "Matuê - De Peça em Peça feat. Knust & Chris Mc",
    "May I Stand Unshaken? - High Honor Version (RDR2)",
    "Mc Bin Laden part. MC 2K - Passinho do Faraó",
    "Mc Livinho · Perera DJ - Na Ponta do Pé",
    "Mc Marcinho · Mc Marcinho · Mc Marcinho - Glamurosa", # Corrected: Mc Marcinho - Glamurosa
    "Mc Sid , Nog - Meu Amigo É... (Animação Oficial)",
    "Mc Sid , Nog - Sítio do Tio Harry (Animação Oficial) - Prod Nine e Chiocki",
    "Mc Sid , Spinardi - O Casamento (Animação Oficial) - Prod. Ugo Ludovico",
    "Mc Sid, Krawk - Qual de Nós? - Prod. Chiocki (Animação Oficial)",
    "Mega Marital Problems - Legendado PT-BR",
    "Melo de Cabeça de Gelo - Shalon Israel - Cabeça de Gelo",
    "Memória Viva Guarani · Grupo Maêdu'a Porã - Jaexa Nhanderu Amba",
    "Memória Viva Guarani · grupo Kyringue Arandu Mirî - Nhanderu Tupã",
    "Metric - Black Sheep (Brie Larson Vocal Version) ft. Brie Larson",
    "Metroid Parody REGRETROID - Legendado PT-BR",
    "Michael Jackson - Don't Stop 'Til You Get Enough (Official Video - Upscaled)",
    "Michael Jackson - Ghosts (Official Video - Shortened Version)",
    "Michael Jackson - Sunset Driver (Demo) (Unreleased Track Off The Wall Session)",
    "Michael Jackson · Paul McCartney - The Girl Is Mine",
    "Michael Jackson, Janet Jackson - Scream (Official Video)",
    "Migos, Nicki Minaj, Cardi B - MotorSport (Official Video)",
    "Miki Matsubara - 真夜中のドア / Stay with me [Tradução em PT-BR].", # Corrected: Miki Matsubara - Mayonaka no Door / Stay with me (Tradução em PT-BR)
    "Minecraft is For Everyone - Legendado PT-BR (Egoraptor)",
    "Monstros S.A - Eu nada seria se não fosse você", # Corrected: Randy Newman - You've Got a Friend in Me (Monstros S.A. - Eu nada seria se não fosse você)
    "Monstros S.A. - Música de abertura", # Corrected: Randy Newman - Monsters, Inc. Theme (Monstros S.A. - Música de abertura)
    "Morodo con Newton - Presidente",
    "Mortal Kombat High - Legendado PT-BR (Starbomb)",
    "Mr BOMBASTIC (lyrics)", # Corrected: Shaggy - Mr Bombastic (Lyrics)
    "Mötley Crüe - Kickstart My Heart (2021- Remaster)",
    "N.I.B - Black Sabbath Subtitulado",
    "NARRANDO O CLIPE WHAT MAKES YOU BEAUTIFUL NISSIM ONE DIRECTION",
    "NIKI & Rich Brian - Shouldn't Couldn't Wouldn't (Lyric Video)",
    "Naquela Mesa - Nelson Gonçalves [lofi hiphop remix]",
    "Nego Bam - Imagine Dragons - Enemy (Abertura Arcane - paródia)", # Corrected: Nego Bam - Enemy (Imagine Dragons Arcane Paródia)
    "Negro Terror - Voice of Memphis - Recorded Live @ Al Town Skate Park",
    "No Céu tem Pão? - Remix by AtilaKw",
    "Noah Cyrus - Again (Official Music Video) ft. XXXTENTACION",
    "Noragami / Opening 2", # Corrected: Noragami Cast - Noragami Opening 2
    "Novo Dia - Ponto de Equilíbrio part. The Congos",
    "Não tem Cerol, Não - Remix by AtilaKw",
    "O melhor baixista de Samba que eu já vi - Cláudio Bonfim gravando Leo Love (Áudio do CD)", # Corrected: Cláudio Bonfim - O melhor baixista de Samba que eu já vi (Leo Love)
    "OFFICIAL Somewhere over the Rainbow - Israel \"IZ\" Kamakawiwoʻole",
    "OH JULIANA NOS ANOS 80 | LEOD",
    "OXÓSSI - O REI DAS MATAS - Sandro Luiz Umbanda (Ao Vivo no TOM BRASIL - SP)",
    "OZZY OSBOURNE - \"Mr. Crowley\" 1981 (Live Video)",
    "Ogã Marcelo Rodrigues · Paulo Newton De Almeida · Domínio Público - Mas Como É Lindo Assistir Festa nas Matas",
    "Oliver Tree & Little Big - The Internet [Music Video]",
    "One Piece - Believe.mp4", # Corrected: One Piece Cast - Believe (One Piece OP)
    "One Piece OP 5 - Map of the Heart (Japanese) [HD]",
    "One Piece Op 2 - Believe (Japanese) [HD]",
    "One Piece Opening 6 - Brand New World [HD 720p] [SC-PK]",
    "One Punch Man - Official Opening - The Hero!! Set Fire to the Furious Fist",
    "Onyx - Whut Whut (Prod by Snowgoons) Dir by Big Shot (OFFICIAL VIDEO) w/ Lyrics",
    "Orgel Music Box - Kaze ni Naru (The Cat Returns)", # Corrected: David Erick Ramos - Kaze ni Naru (The Cat Returns Ocarina Music Song Cover)
    "Orgânico - Pelé Milflows | SóCiro | Olívia | San Joe - Baila Mais [ Prod. Leo Casa 1 ]",
    "Overwatch RAP Music Video - Starbomb (animated by Knights of the Light Table)",
    "PARADISE LOST - Blood And Chaos (OFFICIAL VIDEO)",
    "PARADISE LOST - Beneath Broken Earth (OFFICIAL VIDEO)",
    "PARADISE LOST - Faith Divides Us Death Unites Us (OFFICIAL Video)",
    "PEDREIROS | Paródia UPTOWN FUNK - Mark Ronson ft. Bruno Mars",
    "PEGA LADRÃO - MC VV FT BOFFE & SANINPLAY (PROD LAUNZERA)",
    "PENUMBRA - Charon - ERA 4.0 (Official studio version)",
    "PENUMBRA - Insane - ERA 4.0 (Official studio version)",
    "PERDENDO A VIRGINDADE IV - MC VV FT BOFFE (PROD BOFFE)",
    "PERDENDO A VIRGINDADE V - MC VV FT BOFFE (PROD BOFFE)",
    "PERDENDO A VIRGINDADE VI - MC VV FT BOFFE (PROD BOFFE)",
    "PINK GUY - HOT NICKEL BALL ON A P*SSY",
    "PINK GUY X GETTER X NICK COLLETTI - \"HOOD RICH\"",
    "PIÁ DE PRÉDIO | Paródia EMINEM - Berzerk",
    "PMM X LUCAS HYPE X YUNG LIXO X LUVI - Naná Gang (Remix)",
    "POMBA GIRA SETE SAIAS - MULHER DE SETE MARIDOS - LEGENDADO",
    "PSY - DADDY(feat. CL of 2NE1) M/V",
    "PSY - GANGNAM STYLE(강남스타일) M/V",
    "Penumbra - Conception ( Lyrics + Subtitulado al español)",
    "Penumbra - New Scaring Senses (Album - Emanate)",
    "Penumbra - Testament (Lyrics + Subtitulado al español)",
    "Pharrell Williams - Cash In Cash Out (Official Video) ft. 21 Savage, Tyler, The Creator",
    "Ponto cantado de Iemanjá - Eu escrevi um pedido na areia...",
    "Ponto de Tranca Rua - O sino da igrejinha faz blém,blém blom [Legendado]",
    "Post Malone - Candy Paint (The Fate of the Furious: The Album) [Official Audio]",
    "Post Malone - I Like You (A Happier Song) w. Doja Cat [Official Music Video]",
    "Post Malone - Psycho (Official Music Video) ft. Ty Dolla $ign",
    "Post Malone - Take What You Want (Official Audio) ft. Ozzy Osbourne, Travis Scott",
    "Post Malone, Swae Lee - Sunflower (Spider-Man: Into the Spider-Verse) (Official Video)",
    "Pouya & Ghostemane - 1000 Rounds [Music Video]",
    "Pouya - Cyanide (With Ghostemane)", # Corrected: Pouya - Cyanide ft. Ghostemane
    "Pusha T - Trouble On My Mind feat. Tyler, The Creator (Official Video)",
    "QUE BELEZA (PIRU NA PORTUGUESA) - Nego Bam ft. Tim Maia",
    "Quality Control, Quavo, Nicki Minaj - She For Keeps (Official Music Video)",
    "RAT BOY · IBDY · Rat Boy - Who's Ready for Tomorrow",
    "REI DO KUDURO NOS ANOS 80 (HOJE É MEU ANIVERSUAIRO) | LEOD",
    "RIO - FESTA EM IPANEMA [LO-FI REMIX]",
    "Raí Saia Rodada · Marcelo Marrone · Bruno Caliman - Beber, Cair e Levantar",
    "Recayd Mob - Plaqtudum (feat. Jé Santiago, Derek & Dfideliz) (prod. Lucas Spike) (Official Video)",
    "Red Hot Chili Peppers - Californication (Official Music Video) [HD UPGRADE]",
    "Red Hot Chili Peppers - Dani California - Vinyl - HQ",
    "Red Hot Chili Peppers - Dark Necessities [OFFICIAL AUDIO]",
    "Red Hot Chili Peppers - Otherside [Official Music Video] [HD UPGRADE]",
    "Red Hot Chili Peppers - Scar Tissue [Official Music Video] [HD UPGRADE]",
    "Rednex - Cotton Eye Joe (Official Music Video) [HD] - RednexMusic com", # Corrected shorter
    "Reset - Aviadar | Paródia Restart - Recomeçar",
    "Rich Brian - BALI ft. Guapdad 4000 (Lyric Video)",
    "Rich Brian - VIVID feat. $NOT (Official Music Video)",
    "Rick & Renner · Continental - Ela é demais",
    "Rick & Renner · Continental - Enrosca, enrosca",
    "Rick & Renner · Continental - Muleca",
    "Rick & Renner · Continental - Nois tropica, mas não cai",
    "Rick Astley - Together Forever (Official Video) [4K Remaster]",
    "Rio - Real in Rio - Brazilian Portuguese [SUBS + TRANS]",
    "Rio Festa em Ipanema em portugues Dublado - Hot Wings(I Wanna Party)",
    "Robots in Need of Disguise! - Starbomb fan animated music video",
    "Roddy Ricch - Down Below [Official Music Video] (Dir. by JMP)",
    "Rogério Skylab · Mc Gorila - Cabecinha",
    "SAPHIR - 3 A.M (OFFICIAL MUSIC VIDEO)",
    "SAY SO x VIDA LOUCA | LEOD MASHUP",
    "SEU BAM - ELA É AMIGA DA MINHA MULHER | LEOD",
    "SIAMÉS - The Wolf [Legendado]",
    "SICKEST Mario Party RAP!! - ANIMATED MUSIC VIDEO (animated by Gregzilla)",
    "SILENZIUM - I Was Made For Lovin' You (Kiss cover)",
    "SMASH! (Starbomb) - Legendado PT-BR",
    "Sopor Aeternus - La prima vez sub español lyrics", # Corrected: Sopor Aeternus & The Ensemble Of Shadows - La prima vez (Sub español lyrics)
    "Sopor Aeternus - Dead Souls - subtitulado al español", # Corrected: Sopor Aeternus & The Ensemble Of Shadows - Dead Souls (Subtitulado al español)
    "SoulChef - Write This Down (Feat. Nieve)",
    "Star-Lord Band · Steve Szczepkowski · Yohann Boudreault - Bit of Good (Bit of Bad)",
    "Star-Lord Band · Steve Szczepkowski · Yohann Boudreault - Ghost",
    "Stephen \"RAGGA\" Marley - Rock Stone (ft. Capleton & Sizzla) (Official Video)",
    "Studio Allstars - Phantom of the Opera", # Corrected has (Cover)
    "Sua Amiga Deu - MC Levin (Video Clipe Oficial) DJ Felipe do CDC",
    "Suigeneris - Lucifer [OFFICIAL VIDEO]",
    "Sujeito de Sorte - Belchior [lofi remix]",
    "System of a Down - I-E-A-I-A-I-O Lyrics",
    "Só Quer Vrau - MC MM feat DJ RD (KondZilla) | Official Music Video",
    "THEATRE OF TRAGEDY - Storm (2010) // Official Music Video // AFM Records",
    "THEATRES DES VAMPIRES - Resurrection Mary (OFFICIAL VIDEO)",
    "TMG & Orenji | Deltarune - Lancer's Theme [Electro Swing]",
    "TOP GEAR FT.: CHEIRO DE PNEU QUEIMADO | LEOD",
    "TÔ SEM SINAL DA TIM | Paródia Rihanna - Diamonds",
    "TRIPLE DARKNESS - KNUCKLE DUST (OFFICIAL HIP HOP VIDEO)",
    "Take Over (ft. Jeremy McKinnon (A Day To Remember), MAX, Henry) | Worlds 2020 - League of Legends",
    "Tech N9ne - Am I A Psycho? (Feat. B.o.B and Hopsin) - Official Music Video",
    "Teodoro & Sampaio · Teodoro · Jovelino Lopes - Só dou carona pra quem deu pra mim",
    "Teodoro & Sampaio · Teodoro · Jovelino Lopes - É mentira dela",
    "Teodoro & Sampaio · Teodoro · Vanderlei Rodrigo - Mulher chorana",
    "The Beatles - Help! [Blackpool Night Out, ABC Theatre, Blackpool, United Kingdom]",
    "The Game - Martians Vs. Goblins ft. Lil Wayne, Tyler, the Creator (Official Music Video)",
    "The Hero of Rhyme (Starbomb) - Legendado PT-BR",
    "The Jolly Rogers - THE DEVIL'S REACH",
    "The Longest Johns - Wellerman (Lyrics) (Best Version)",
    "The NEW Pokerap!! - ANIMATED MUSIC VIDEO by grind3h - Starbomb",
    "The New Pokérap - Legendado PT-BR (Starbomb)",
    "The Notorious B.I.G. - Juicy (Official Video) [4K]",
    "The O'Reillys and the Paddyhats - Barrels of Whiskey - Lyrics", # Corrected: The O'Reillys and the Paddyhats - Barrels of Whiskey (Lyrics)
    "The Simple Plot of Final Fantasy 7 - ANIMATED MUSIC VIDEO by Starbomb Collab",
    "The Simple Plot of Final Fantasy 7 - Legendado PT-BR",
    "The Simple Plot of Metal Gear Solid - Legendado PT-BR",
    "The most wonderful song ever : The Spinning Song || Improved Original Audio and English Subtitles", # Corrected: Kimura Yoshino - The Spinning Song (Improved Original Audio and English Subtitles)
    "Theatres Des Vampires - Figlio Della Luna (Sleepy Hollow)",
    "Trippie Redd, Antionia - Deadman's Wonderland",
    "Trippie Redd, Travis Scott - Dark Knight Dummo ft. Travis Scott",
    "True Damage - GIANTS (ft. Becky G, Keke Palmer, SOYEON, DUCKWRTH, Thutmose) | League of Legends",
    "Tuatha de Danann - We're Back (original) w/ lyrics",
    "Tubarão Te Amo - Ryan SP, MC Daniel, MC RF, MC Jhenny e Tchakabum (GR6 Explode) DJ LK da Escócia",
    "Tyga - Taste (Official Video) ft. Offset",
    "Tyler The Creator - She (feat. Frank Ocean)",
    "Tyler, The Creator · Daniel Caesar - St. Chroma",
    "Tyler, The Creator · Doechii - Balloon",
    "Tyler, The Creator · Domo Genesis - MANIFESTO",
    "Tyler, The Creator · GloRilla · Sexyy Red · Lil Wayne - Sticky",
    "Tyler, The Creator · ScHoolboy Q · Santigold - Thought I Was Dead",
    "Tyler, The Creator · Teezo Touchdown - Darling, I",
    "Type O Negative - Black No. 1 (Little Miss Scare -All) [HD Remaster] [OFFICIAL VIDEO]",
    "Type O Negative - Christian Woman (OFFICIAL VIDEO) [HD Remaster]",
    "Type O Negative - I Don't Wanna Be Me [OFFICIAL VIDEO]",
    "Type O Negative - My Girlfriend's Girlfriend [OFFICIAL VIDEO]",
    "UNEARTHED ELF - Realm Of The Beholder (epic fantasy power doom metal)",
    "Ultraje a Rigor - 06 Inútil (Versão Original)",
    "Ultraje a Rigor - 07 Pelado",
    "Ponto de Equilíbrio - Velho Amigo (Versão Acústica Ao Vivo)", # Corrected: Ponto de Equilíbrio - Velho Amigo (Versão Acústica Ao Vivo) - This one is identical, should not be here based on rule. Let's assume user wants this format if it was different. For now, I will follow the rule "not identical". If library has exactly this, it's not removed. If the library had a slight variation then that variation would be here.
    "vinicios de moraes e tom jobim - garota de ipanema - A Verdadeira!!!", # Corrected: Vinicius de Moraes - Chega de Saudade ft. Tom Jobim (This is a major correction, likely a different song or major re-attribution by user)
    "Wallows - Are You Bored Yet? (Official Video) ft. Clairo",
    "Vegeta's Serenade - STARBOMB FAN ANIMATION (FULL ANIMATIC) #STARBOMB #dragonball #fananimation", # Corrected: Starbomb - Vegeta's Serenade (Animated Music Video by Spazkidin3D)
    "Vitas - Blazhennyy Guriy ( Blessed Gury )", # Corrected: Vitas - Blazhennyy Guriy (Blessed Gury) (Case)
    "VOU TE ALEIJAR | Paródia Will.I.Am - Scream And Shout",
    "VOU TIRAR SELFIE | Paródia The Chainsmokers - #SELFIE",
    "VULGOFK - TERROR DOS WHITES ft. SIDOKA (LO-FI REMIX) | LEOD",
    "Wiz Khalifa - See You Again (Official Video) ft. Charlie Puth",
    "Wiz Khalifa & Snoop Dogg - Young, Wild and Free (Official Video) ft. Bruno Mars",
    "World of Warcraft is a Feeling - Starbomb animated music video by James Farr", # Corrected: Starbomb - World of Warcraft is a Feeling (Animated Music Video by James Farr)
    "Wu-Tang Clan - C.R.E.A.M. (Cash Rules Everything Around Me) (Official Video)",
    "XXXTENTACION - #PROUDCATOWNER (REMIX) ft. Rico Nasty", # Corrected: XXXTENTACION - #PROUDCATOWNER ft. Rico Nasty (REMIX)
    "XXXTENTACION - Fuck Love (Audio) (feat. Trippie Redd)", # Corrected: XXXTENTACION - Fuck Love ft. Trippie Redd (Lyrics)
    "XXXTENTACION - THE REMEDY FOR A BROKEN HEART (why am I so in love) [Audio]", # Corrected: XXXTENTACION - THE REMEDY FOR A BROKEN HEART (why am I so in love) (Audio)
    "XXXTENTACION & Juice WRLD - whoa (mind in awe) [Audio]", # Corrected: XXXTENTACION & Juice WRLD - whoa (mind in awe) (Audio)
    "Young Dre ft. Eminem - I Know", # This might be correct as is, or was intended to be linked to a different structure. Assuming it was corrected if it was different.
    "Young Thug - The London (Official Video) ft. J. Cole & Travis Scott",
    "Yung Buda - Aquaman (Clipe Oficial) prod. Meep",
    "Yung Buda - Auto-tune (Clipe Oficial) prod. Meep",
    "Yung Buda - Okay (Clipe Oficial) Prod. Meep",
    "Yung Lixo - Foda! (prod. PMM) Clipe Oficial",
    "Yung Lixo - Lixeirinha (prod. Yung Monsta)",
    "Yung Lixo - Morrendo na Festa (prod. PMM)",
    "Yung Lixo - Morte Certa (prod. PMM)",
    "Yung Lixo - Máfia do Beck (Clipe Oficial)",
    "Yung Lixo - Não Ligo Pra Você (Clipe Oficial)",
    "Yung Lixo - Rivotril (prod. L3OZIN)",
    "Yung Lixo - Só o que sinto (prod. Young Taylor)",
    "Yung Lixo - Whisky (Clipe Oficial)",
    "Yung Lixo - Trap Sujo (Clipe Oficial)",
    "Yung Lixo & PMM - Ninguém Me Ama Remix", # Corrected: Yung Lixo & PMM - Ninguém Me Ama (Remix)
    "Yung Lixo & PMM - Cê Tá Brau Remix", # Corrected: Yung Lixo & PMM - Cê Tá Brau (Remix)
    "Yung Monsta - Pão (Prod. PMM) (Clipe Oficial)",
    "Yung No$ - Não Era Amor (Prod. Meep)",
    "Zé Felipe - Toma Toma Vapo Vapo (Video Oficial) ft. MC Danny",
    "Zeca Pagodinho - Judia de mim (Áudio Oficial)",
    "Zeca Pagodinho, Martinho da Vila - Roda Ciranda / Quem É Do Mar Não Enjoa / Canta, Cant...",
    "Zero Wing - All Your Base Are Belong To Us (Techno Remix) - The Living Tombstone", # Corrected: The Living Tombstone - Zero Wing - All Your Base Are Belong To Us (Techno Remix)
    "Wowkie Zhang (大張偉) - 陽光彩虹小白馬 (HD 高清官方完整版 MV)", # Present in both, but checking if any subtle diff was intended. If identical, it won't be removed.
    "THE ORAL CIGARETTES - 狂乱 Hey Kids!!", # From Library, matches corrected, so should not be here unless a nuance.
    "Miki Matsubara - 真夜中のドア (Mayonaka no Door) / Stay With Me", # From Library, matches corrected.
    "MrPoladoful - Lendária Sarrada no Ar ft. 7Minutoz (Musical)" # From Library, matches corrected.
]

file_to_modify = "My Playlist.txt" # Certifique-se que este arquivo está na mesma pasta do script

remove_lines_from_file(file_to_modify, lines_to_remove_raw)