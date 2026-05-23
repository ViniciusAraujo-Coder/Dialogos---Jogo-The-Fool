import pygame
import sys
import os

# ═══════════════════════════════════════════════════════════════
#  CENA DE DIÁLOGO — NICK (The Fool)
#  Universidade São Judas Tadeu
#
#  Nick não fala — ela só desenha.
#  Cada resposta exibe um sprite de desenho em tela cheia,
#  acompanhado de um som de papel/lápis.
#
#  ★ = seções que você pode editar
# ═══════════════════════════════════════════════════════════════

pygame.init()
pygame.mixer.init()

# ★ Configuração da janela
LARGURA, ALTURA = 1050, 600
FPS             = 60

tela  = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("The Fool — Nick")
clock = pygame.time.Clock()

# Cores
COR_NOME         = (255, 255, 255)
COR_TEXTO        = (220, 220, 220)
COR_OPCAO_NORMAL = (180, 180, 180)
COR_OPCAO_HOVER  = (255, 255, 180)
BORDA            = (200, 200, 200)

# Fontes
fonte_nome  = pygame.font.SysFont("Courier New", 22, bold=True)
fonte_texto = pygame.font.SysFont("Courier New", 26)
fonte_opcao = pygame.font.SysFont("Courier New", 22)
fonte_dica  = pygame.font.SysFont("Courier New", 16)

# ═══════════════════════════════════════════════════════════════
#  ★ PARTE 1 — CAMINHOS DE ASSETS
#
#  Imagens → pasta  imgs_nick/
#  Sons    → pasta  sons_nick/
# ═══════════════════════════════════════════════════════════════

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

def caminho(subpasta, nome_arquivo):
    return os.path.join(PASTA_BASE, subpasta, nome_arquivo)

# Sprites da Nick
SPRITES = {
    # Estados da personagem
    "sentada":    caminho("imgs_nick", "Sentada.png"),
    "desenhando": caminho("imgs_nick", "Desenhando.png"),
    "sorrindo":   caminho("imgs_nick", "Nick_Sorrindo.png"),
    "timida":     caminho("imgs_nick", "Nick_Timida.png"),
    # Desenhos que ela mostra — ocupam a tela inteira como os outros sprites
    "desenho1":   caminho("imgs_nick", "Desenho1.png"),
    "desenho2":   caminho("imgs_nick", "Desenho2.png"),
    "desenho3":   caminho("imgs_nick", "Desenho3.png"),
    "desenho4":   caminho("imgs_nick", "Desenho4.png"),
}

# ── ★ Sons ───────────────────────────────────────────────────
#  Coloque os arquivos em:  sons_nick/
#  Nomes esperados (renomeie à vontade, só ajuste aqui):
#    ambiente_nick.mp3   → toca em loop durante toda a cena
#    mostra_desenho.mp3  → toca quando Nick vira o desenho para você
#    rabisco.mp3         → toca quando ela começa a desenhar
SONS = {
    "ambiente":       caminho("sons_nick", "ambiente_nick.mp3"),
    "mostra_desenho": caminho("sons_nick", "mostra_desenho.mp3"),
    "rabisco":        caminho("sons_nick", "rabisco.mp3"),
}

# ── ★ Volume de cada som (0.0 = mudo, 1.0 = máximo) ─────────
VOLUME = {
    "ambiente":       0.3,
    "mostra_desenho": 0.7,
    "rabisco":        0.5,
}

def carregar_som(chave):
    """Carrega um som com segurança. Retorna None se o arquivo não existir."""
    try:
        som = pygame.mixer.Sound(SONS[chave])
        som.set_volume(VOLUME[chave])
        return som
    except FileNotFoundError:
        print(f"[AVISO] Som não encontrado: {SONS[chave]}")
        return None


# ═══════════════════════════════════════════════════════════════
#  GERENCIADOR DE SPRITES
#  Carrega cada imagem escalada para preencher a tela inteira.
# ═══════════════════════════════════════════════════════════════

class GerenciadorSprite:
    """
    Chaves válidas: 'sentada', 'desenhando', 'sorrindo', 'timida',
                    'desenho1', 'desenho2', 'desenho3', 'desenho4'
    """

    # Chaves que representam desenhos — toca som ao exibir
    CHAVES_DESENHO = {"desenho1", "desenho2", "desenho3", "desenho4"}

    def __init__(self, som_desenho_ref):
        """
        som_desenho_ref: função que retorna o som de mostrar desenho,
        para tocar automaticamente quando um desenho é exibido.
        """
        self.sprites        = {}
        self.atual          = None
        self.chave_atual    = None
        self._som_desenho   = som_desenho_ref
        self._carregar()

    def _carregar(self):
        for chave, path in SPRITES.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (LARGURA, ALTURA))
                self.sprites[chave] = img
            except FileNotFoundError:
                print(f"[AVISO] Imagem não encontrada: {path}")
                placeholder = pygame.Surface((LARGURA, ALTURA))
                placeholder.fill((15, 10, 10))
                self.sprites[chave] = placeholder

        self.set_sprite("sentada")

    def set_sprite(self, chave):
        if chave in self.sprites and chave != self.chave_atual:
            self.atual       = self.sprites[chave]
            self.chave_atual = chave

            # Toca som especial ao mostrar um desenho
            if chave in self.CHAVES_DESENHO:
                som = self._som_desenho()
                if som:
                    som.play()

            # Toca som de rabisco ao mudar para desenhando
            if chave == "desenhando":
                som = carregar_som("rabisco")
                if som:
                    som.play()

    def desenhar(self, superficie):
        if self.atual:
            superficie.blit(self.atual, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  CAIXA DE DIÁLOGO — centralizada na parte inferior da tela
# ═══════════════════════════════════════════════════════════════

class CaixaDialogo:
    VELOCIDADE_PADRAO = 2

    CAIXA_LARGURA = 900
    CAIXA_ALTURA  = 160
    MARGEM_BOTTOM = 24
    PADDING       = 18

    def __init__(self, nome, texto, velocidade=None):
        self.nome          = nome
        self.texto         = texto
        self.velocidade    = velocidade if velocidade is not None else self.VELOCIDADE_PADRAO
        self.texto_visivel = ""
        self.indice        = 0
        self.contador      = 0
        self.completo      = False

    def atualizar(self):
        if self.completo:
            return
        self.contador += 1
        if self.contador >= self.velocidade:
            self.contador = 0
            if self.indice < len(self.texto):
                self.texto_visivel += self.texto[self.indice]
                self.indice        += 1
            else:
                self.completo = True

    def pular(self):
        self.texto_visivel = self.texto
        self.indice        = len(self.texto)
        self.completo      = True

    def desenhar(self, superficie, offset_y=0, alpha=255):
        cw = self.CAIXA_LARGURA
        ch = self.CAIXA_ALTURA
        cx = (LARGURA - cw) // 2
        cy = ALTURA - ch - self.MARGEM_BOTTOM + offset_y
        p  = self.PADDING

        temp = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

        alpha_fundo = int(180 * alpha / 255)
        fundo = pygame.Surface((cw, ch), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, alpha_fundo))
        temp.blit(fundo, (cx, cy))

        cor_borda = (*BORDA, alpha)
        pygame.draw.rect(temp, cor_borda, (cx, cy, cw, ch), 2)

        # Caixinha do nome
        nome_surf = fonte_nome.render(self.nome, True, COR_NOME)
        nb_w = nome_surf.get_width() + 20
        nb_h = nome_surf.get_height() + 8
        nx   = cx
        ny   = cy - nb_h - 2

        nb = pygame.Surface((nb_w, nb_h), pygame.SRCALPHA)
        nb.fill((0, 0, 0, alpha_fundo))
        temp.blit(nb, (nx, ny))
        pygame.draw.rect(temp, cor_borda, (nx, ny, nb_w, nb_h), 2)

        nome_a = pygame.Surface(nome_surf.get_size(), pygame.SRCALPHA)
        nome_a.blit(nome_surf, (0, 0))
        nome_a.set_alpha(alpha)
        temp.blit(nome_a, (nx + 10, ny + 4))

        self._desenhar_texto(
            temp,
            self.texto_visivel,
            x          = cx + p,
            y          = cy + p,
            largura_max= cw - p * 2,
            altura_max = ch - p * 2,
            alpha      = alpha
        )

        if self.completo and alpha == 255:
            if (pygame.time.get_ticks() // 500) % 2:
                dica = fonte_dica.render("▼", True, BORDA)
                temp.blit(dica, (cx + cw - dica.get_width() - p,
                                 cy + ch - dica.get_height() - 8))

        superficie.blit(temp, (0, 0))

    def _desenhar_texto(self, superficie, texto, x, y, largura_max, altura_max, alpha=255):
        palavras     = texto.split(" ")
        linha_atual  = ""
        pos_y        = y
        altura_linha = fonte_texto.get_height() + 5

        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte_texto.size(teste)[0] <= largura_max:
                linha_atual = teste
            else:
                if pos_y + altura_linha > y + altura_max:
                    break
                surf = fonte_texto.render(linha_atual.rstrip(), True, COR_TEXTO)
                surf.set_alpha(alpha)
                superficie.blit(surf, (x, pos_y))
                linha_atual = palavra + " "
                pos_y      += altura_linha

        if linha_atual and pos_y + altura_linha <= y + altura_max:
            surf = fonte_texto.render(linha_atual.rstrip(), True, COR_TEXTO)
            surf.set_alpha(alpha)
            superficie.blit(surf, (x, pos_y))


# ═══════════════════════════════════════════════════════════════
#  MENU DE ESCOLHAS — centralizado na parte inferior da tela
# ═══════════════════════════════════════════════════════════════

class MenuEscolhas:
    ITEM_ALTURA  = 42
    MENU_LARGURA = 900
    MARGEM_BTM   = 24

    def __init__(self, opcoes):
        self.opcoes = opcoes
        self.hover  = -1

    def atualizar_hover(self, pos_mouse):
        self.hover = -1
        for i, rect in enumerate(self._rects()):
            if rect.collidepoint(pos_mouse):
                self.hover = i

    def checar_clique(self, pos_mouse):
        for i, rect in enumerate(self._rects()):
            if rect.collidepoint(pos_mouse):
                return i
        return None

    def checar_teclado(self, tecla):
        return {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}.get(tecla)

    def _rects(self):
        total_h  = len(self.opcoes) * self.ITEM_ALTURA
        inicio_y = ALTURA - total_h - self.MARGEM_BTM
        cx       = (LARGURA - self.MENU_LARGURA) // 2
        return [
            pygame.Rect(cx, inicio_y + i * self.ITEM_ALTURA,
                        self.MENU_LARGURA, self.ITEM_ALTURA - 4)
            for i in range(len(self.opcoes))
        ]

    def desenhar(self, superficie):
        temp  = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        rects = self._rects()

        for i, (rect, opcao) in enumerate(zip(rects, self.opcoes)):
            cor_bg = (40, 40, 20, 200) if i == self.hover else (0, 0, 0, 160)
            bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg.fill(cor_bg)
            temp.blit(bg, (rect.x, rect.y))
            pygame.draw.rect(temp, (*BORDA, 200), rect, 1)

            cor   = COR_OPCAO_HOVER if i == self.hover else COR_OPCAO_NORMAL
            label = f"[{i+1}]  {opcao}"
            surf  = fonte_opcao.render(label, True, cor)
            temp.blit(surf, (rect.x + 14,
                              rect.y + (rect.height - surf.get_height()) // 2))

        superficie.blit(temp, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  ★ PARTE 2 — ÁRVORE DE DIÁLOGOS DA NICK
#
#  Nick não fala. As falas com nome "S/N" são narração/pensamento
#  do jogador. As falas com nome "Nick" são silêncio/ação dela.
#
#  Sprites especiais: quando o sprite é um "desenhoX",
#  a imagem do desenho ocupa a tela inteira automaticamente
#  e um som de papel é tocado.
#
#  "acao" especial: "retorna" → volta ao menu principal (dialogo_1)
#
#  Cada opção tem:
#    "texto"    → texto exibido no menu
#    "delta_san"→ valor de sanidade a repassar ao sistema do grupo
#    "sprite"   → sprite da Nick ao escolher
#    "proximo"  → próximo nó
# ═══════════════════════════════════════════════════════════════

ARVORE = {

    # ── Entrada — Nick sentada, não fala ─────────────────────
    "entrada": {
        "sprite": "sentada",
        "falas": [
            ("S/N", "..."),
            ("S/N", "Uma garota está sentada no chão.", 3),
            ("S/N", "Folhas espalhadas."),
            ("S/N", "Giz quebrado."),
            ("S/N", "..."),
            ("S/N", "Ela não fala.", 4),
            ("S/N", "..."),
            ("S/N", "Você se aproxima.", 3),
            ("S/N", "..."),
            ("S/N", "Ela olha para você.", 3),
        ],
        "proximo": "entrada2",
    },

    "entrada2": {
        "sprite": "sorrindo",
        "falas": [
            ("S/N", "..."),
            ("S/N", "Ela pega uma folha.", 3),
        ],
        "proximo": "dialogo_1",
    },

    # ── Diálogo 1 — menu principal com 4 opções ──────────────
    # Sem "sprite" no menu — mantém o sprite que já estava na tela.
    # O sprite só muda quando o jogador escolhe uma opção e o
    # nó seguinte define o seu próprio sprite.
    "dialogo_1": {
        "falas": [],
        "opcoes": [
            {"texto": "Você sabe o que é esse lugar?", "delta_san": 3, "proximo": "lugar"},
            {"texto": "Como viemos parar aqui?",        "delta_san": 4, "proximo": "como_viemos"},
            {"texto": "Tem como sair?",                 "delta_san": 5, "proximo": "tem_saida"},
            {"texto": "O que controla isso?",           "delta_san": 6, "proximo": "controla"},
        ],
    },

    # ── "Você sabe o que é esse lugar?" ──────────────────────
    # Começa desenhando → mostra o desenho
    "lugar": {
        "sprite": "desenhando",
        "falas": [
            ("S/N",  "..."),
            ("Nick", "(Nicole desenha.)", 4),
        ],
        "proximo": "lugar_desenho",
    },

    "lugar_desenho": {
        "sprite": "desenho1",
        "falas": [
            ("Nick", "\"...\"", 5),
            ("S/N",  "..."),
            ("S/N",  "Você observa."),
            ("S/N",  "Quanto mais olha...", 3),
            ("S/N",  "Menos gosta.", 4),
        ],
        "acao": "retorna",
    },

    # ── "Como viemos parar aqui?" ─────────────────────────────
    # Tímida → desenhando → mostra o desenho
    "como_viemos": {
        "sprite": "timida",
        "falas": [
            ("S/N",  "..."),
            ("Nick", "(Nicole hesita.)", 4),
            ("S/N",  "..."),
        ],
        "proximo": "como_viemos_b",
    },

    "como_viemos_b": {
        "sprite": "desenhando",
        "falas": [
            ("Nick", "(Ela pega outra folha.)", 3),
            ("Nick", "(Desenha.)", 3),
        ],
        "proximo": "como_viemos_desenho",
    },

    "como_viemos_desenho": {
        "sprite": "desenho2",
        "falas": [
            ("Nick", "\"...\"", 5),
            ("S/N",  "..."),
            ("S/N",  "Seu desconforto aumenta.", 4),
        ],
        "acao": "retorna",
    },

    # ── "Tem como sair?" ──────────────────────────────────────
    # Desenhando mais devagar → mostra o desenho → única fala da Nick
    "tem_saida": {
        "sprite": "desenhando",
        "falas": [
            ("S/N",  "..."),
            ("Nick", "(Nicole olha para você.)", 4),
            ("S/N",  "..."),
            ("Nick", "(Ela desenha mais devagar.)", 5),
        ],
        "proximo": "tem_saida_desenho",
    },

    "tem_saida_desenho": {
        "sprite": "desenho3",
        "falas": [
            ("Nick", "\"...Tem um jeito.\"", 5),
            ("S/N",  "..."),
            ("S/N",  "Ou pelo menos...", 3),
            ("S/N",  "Parece ter.", 4),
        ],
        "acao": "retorna",
    },

    # ── "O que controla isso?" ────────────────────────────────
    # Tímida/congela → desenhando com frenesi → mostra o desenho
    "controla": {
        "sprite": "timida",
        "falas": [
            ("S/N",  "..."),
            ("Nick", "(Nicole congela.)", 5),
            ("S/N",  "..."),
        ],
        "proximo": "controla_b",
    },

    "controla_b": {
        "sprite": "desenhando",
        "falas": [
            ("Nick", "(Ela começa a desenhar.)", 3),
            ("S/N",  "..."),
            ("S/N",  "Mais forte.", 3),
            ("S/N",  "Mais rápido.", 3),
            ("S/N",  "...", 4),
        ],
        "proximo": "controla_desenho",
    },

    "controla_desenho": {
        "sprite": "desenho4",
        "falas": [
            ("Nick", "\"...\"", 6),
            ("S/N",  "..."),
            ("S/N",  "Você se arrepende de perguntar.", 5),
        ],
        "acao": "retorna",
    },

    # ── Diálogo 2 — após todas as perguntas ──────────────────
    "dialogo_2": {
        "sprite": "sentada",
        "falas": [
            ("S/N", "Você observa os desenhos.", 3),
            ("S/N", "Cada resposta parece pior."),
            ("S/N", "Cada folha...", 3),
            ("S/N", "Mais pesada.", 4),
            ("S/N", "Nicole não diz nada."),
            ("S/N", "Talvez porque não precise.", 4),
        ],
        "acao": "fim",
    },
}


# ═══════════════════════════════════════════════════════════════
#  CONTROLADOR DA CENA
# ═══════════════════════════════════════════════════════════════

class CenaNick:
    """
    Gerencia o fluxo completo da cena da Nick.

    Diferencial em relação ao Vinny:
      - Nick não fala: as respostas são desenhos.
      - O menu principal (dialogo_1) fica disponível para ser
        revisitado após cada resposta (acao = "retorna").
      - Após todas as 4 perguntas serem feitas, o jogo avança
        automaticamente para o dialogo_2.

    Ao encerrar:
      self.encerrada      → True
      self.delta_san_total → soma dos delta_san das escolhas feitas.
                             Repasse ao sistema de sanidade do grupo.
    """

    def __init__(self):
        # Passa uma função que retorna o som de mostrar desenho
        self.sprite_mgr   = GerenciadorSprite(
            som_desenho_ref=lambda: carregar_som("mostra_desenho")
        )

        self.no_atual_key    = "entrada"
        self.no_atual        = ARVORE["entrada"]
        self.indice_fala     = 0
        self.caixa           = None
        self.menu            = None
        self.saindo          = False
        self.offset_saida    = 0
        self.alpha_saida     = 255
        self.encerrada       = False

        # Controle de perguntas já feitas — quando todas as 4 forem
        # respondidas, o diálogo avança para dialogo_2 automaticamente
        self.perguntas_feitas = set()
        self.TOTAL_PERGUNTAS  = 4   # ★ ajuste se mudar o número de opções

        # ★ Variável de sanidade — repasse ao sistema do grupo no fim
        self.delta_san_total = 0

        self._iniciar_no("entrada")

        # Som ambiente — loop durante toda a cena
        self.som_ambiente = carregar_som("ambiente")
        if self.som_ambiente:
            self.som_ambiente.play(-1)

    # ── Inicialização de nó ───────────────────────────────────

    def _iniciar_no(self, chave):
        self.no_atual_key = chave
        self.no_atual     = ARVORE[chave]
        self.indice_fala  = 0
        self.menu         = None

        # Só troca o sprite se o nó definir um — senão mantém o atual
        sprite_key = self.no_atual.get("sprite")
        if sprite_key:
            self.sprite_mgr.set_sprite(sprite_key)

        falas = self.no_atual.get("falas", [])
        if falas:
            self.caixa = CaixaDialogo(*falas[0])
        else:
            self.caixa = None
            self._abrir_menu()

    # ── Avanço de fala ────────────────────────────────────────

    def _avancar(self):
        if self.caixa and not self.caixa.completo:
            self.caixa.pular()
            return

        falas = self.no_atual.get("falas", [])
        self.indice_fala += 1

        if self.indice_fala < len(falas):
            self.caixa = CaixaDialogo(*falas[self.indice_fala])
            return

        # Acabaram as falas — trata ação
        acao = self.no_atual.get("acao")

        if acao == "retorna":
            # Verifica se todas as perguntas já foram feitas
            if len(self.perguntas_feitas) >= self.TOTAL_PERGUNTAS:
                self._iniciar_no("dialogo_2")
            else:
                # Volta ao menu principal, removendo opções já escolhidas
                self._iniciar_no("dialogo_1")

        elif acao == "fim":
            self.saindo = True
            if self.som_ambiente:
                self.som_ambiente.stop()

        elif self.no_atual.get("opcoes"):
            self.caixa = None
            self._abrir_menu()

        elif "proximo" in self.no_atual:
            self._iniciar_no(self.no_atual["proximo"])

    def _abrir_menu(self):
        opcoes = self.no_atual.get("opcoes", [])
        if opcoes:
            # Filtra opções já respondidas para não repetir
            opcoes_disponiveis = [
                op for op in opcoes
                if op["proximo"] not in self.perguntas_feitas
            ]
            if opcoes_disponiveis:
                self.menu = MenuEscolhas([op["texto"] for op in opcoes_disponiveis])
                # Guarda referência para saber qual opção original foi escolhida
                self._opcoes_filtradas = opcoes_disponiveis
            else:
                # Não há mais opções — avança
                self._iniciar_no("dialogo_2")

    def _escolher_opcao(self, indice):
        if not hasattr(self, "_opcoes_filtradas"):
            return
        opcoes = self._opcoes_filtradas
        if indice >= len(opcoes):
            return
        opcao = opcoes[indice]

        # Marca pergunta como feita
        self.perguntas_feitas.add(opcao["proximo"])

        # Acumula delta de sanidade
        self.delta_san_total += opcao.get("delta_san", 0)

        self.menu = None
        self._iniciar_no(opcao["proximo"])

    # ── Eventos ───────────────────────────────────────────────

    def processar_evento(self, evento):
        if self.encerrada or self.saindo:
            return

        if evento.type == pygame.MOUSEMOTION and self.menu:
            self.menu.atualizar_hover(evento.pos)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.menu:
                idx = self.menu.checar_clique(evento.pos)
                if idx is not None:
                    self._escolher_opcao(idx)
            else:
                self._avancar()

        if evento.type == pygame.KEYDOWN:
            if self.menu:
                idx = self.menu.checar_teclado(evento.key)
                if idx is not None:
                    self._escolher_opcao(idx)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._avancar()

    # ── Atualização por frame ─────────────────────────────────

    def atualizar(self):
        if self.caixa and not self.encerrada:
            self.caixa.atualizar()

        if self.saindo:
            self.offset_saida += 10
            self.alpha_saida   = max(0, self.alpha_saida - 12)
            if self.alpha_saida <= 0 or self.offset_saida >= 250:
                self.encerrada = True
                self.saindo    = False

    # ── Desenho ───────────────────────────────────────────────

    def desenhar(self, superficie):
        self.sprite_mgr.desenhar(superficie)

        if not self.encerrada:
            alpha = self.alpha_saida if self.saindo else 255
            if self.caixa:
                self.caixa.desenhar(superficie, offset_y=self.offset_saida, alpha=alpha)
            if self.menu:
                self.menu.desenhar(superficie)


# ═══════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    cena = CenaNick()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Após encerrar, ENTER fecha / conecta próxima cena
            if cena.encerrada and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # ★ Repasse cena.delta_san_total ao sistema de sanidade
                    # e inicie a próxima cena aqui.
                    print(f"[INFO] Cena Nick encerrada.")
                    print(f"       delta_san_total : {cena.delta_san_total}")
                    pygame.quit()
                    sys.exit()

            cena.processar_evento(evento)

        cena.atualizar()
        cena.desenhar(tela)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
